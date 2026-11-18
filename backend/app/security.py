from datetime import datetime, timedelta, timezone
import bcrypt
import jwt
from .config import settings


def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()


def verify_password(password: str, hashed: str) -> bool:
    return bcrypt.checkpw(password.encode(), hashed.encode())


def create_token(user_id: int, role: str, minutes: int | None = None, purpose: str = "access") -> str:
    expire = datetime.now(timezone.utc) + timedelta(minutes=minutes or settings.JWT_EXPIRE_MINUTES)
    payload = {"sub": str(user_id), "role": role, "purpose": purpose, "exp": expire}
    return jwt.encode(payload, settings.JWT_SECRET, algorithm="HS256")


def decode_token(token: str) -> dict:
    return jwt.decode(token, settings.JWT_SECRET, algorithms=["HS256"])