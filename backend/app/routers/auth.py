import re
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, EmailStr, Field, model_validator
from sqlalchemy.orm import Session
from ..database import get_db
from ..models import User, UserProfile
from ..security import hash_password, verify_password, create_token, decode_token

router = APIRouter(prefix="/auth", tags=["auth"])


class RegisterIn(BaseModel):
    full_name: str = Field(min_length=2, max_length=120)
    email: EmailStr
    mobile: str = Field(pattern=r"^\+\d{8,15}$")  # must include country code, e.g. +919876543210
    password: str = Field(min_length=8, max_length=72)
    confirm_password: str

    @model_validator(mode="after")
    def check_passwords(self):
        if self.password != self.confirm_password:
            raise ValueError("Passwords do not match")
        if not (re.search(r"[A-Za-z]", self.password) and re.search(r"\d", self.password)):
            raise ValueError("Password must contain letters and digits")
        return self


class LoginIn(BaseModel):
    email: EmailStr
    password: str


@router.post("/register", status_code=201)
def register(data: RegisterIn, db: Session = Depends(get_db)):
    email = data.email.lower()
    if db.query(User).filter(User.email == email).first():
        raise HTTPException(409, "Email already registered")
    user = User(
        full_name=data.full_name,
        email=email,
        mobile=data.mobile,
        password_hash=hash_password(data.password),
    )
    user.profile = UserProfile()
    db.add(user)
    db.commit()
    return {"message": "Registration successful"}


def _login(db: Session, data: LoginIn, need_admin: bool):
    user = db.query(User).filter(User.email == data.email.lower()).first()
    if not user or not verify_password(data.password, user.password_hash):
        raise HTTPException(401, "Invalid email or password")
    if not user.is_active:
        raise HTTPException(403, "Account deactivated")
    if need_admin and user.role != "admin":
        raise HTTPException(403, "Not an admin account")
    return {
        "access_token": create_token(user.id, user.role),
        "role": user.role,
        "name": user.full_name,
    }


@router.post("/login")
def login(data: LoginIn, db: Session = Depends(get_db)):
    return _login(db, data, need_admin=False)


@router.post("/admin-login")
def admin_login(data: LoginIn, db: Session = Depends(get_db)):
    return _login(db, data, need_admin=True)


# Demo-level password reset: the token is returned in the response.
# In production you would email it to the user instead.
@router.post("/forgot-password")
def forgot_password(email: EmailStr, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == email.lower()).first()
    token = create_token(user.id, user.role, minutes=15, purpose="reset") if user else None
    return {"message": "If the email exists, a reset token was generated", "reset_token": token}


class ResetIn(BaseModel):
    token: str
    new_password: str = Field(min_length=8, max_length=72)


@router.post("/reset-password")
def reset_password(data: ResetIn, db: Session = Depends(get_db)):
    try:
        payload = decode_token(data.token)
    except Exception:
        raise HTTPException(400, "Invalid or expired token")
    if payload.get("purpose") != "reset":
        raise HTTPException(400, "Invalid token")
    user = db.get(User, int(payload["sub"]))
    if not user:
        raise HTTPException(404, "User not found")
    user.password_hash = hash_password(data.new_password)
    db.commit()
    return {"message": "Password updated"}