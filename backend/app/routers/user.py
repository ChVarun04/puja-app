from datetime import datetime, date
from zoneinfo import ZoneInfo
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import select, or_
from sqlalchemy.orm import Session
from ..config import settings
from ..database import get_db
from ..deps import current_user
from ..models import User, Media, UserContent, WeekdayMapping, Deity
from ..storage import signed_url

router = APIRouter(tags=["user"])


class ProfileIn(BaseModel):
    dob: date | None = None
    gotram: str | None = None
    nakshatram: str | None = None
    rashi: str | None = None
    gender: str | None = None
    preferred_language: str | None = None
    country: str | None = None
    state: str | None = None
    city: str | None = None


@router.get("/me/profile")
def get_profile(user: User = Depends(current_user)):
    p = user.profile
    return {
        "full_name": user.full_name,
        "email": user.email,
        "mobile": user.mobile,
        **{field: getattr(p, field) for field in ProfileIn.model_fields},
    }


@router.put("/me/profile")
def update_profile(data: ProfileIn, user: User = Depends(current_user), db: Session = Depends(get_db)):
    for key, value in data.model_dump().items():
        setattr(user.profile, key, value)
    db.commit()
    return {"message": "Profile updated"}


def visible_media(user: User):
    """Active media that is common, or specifically assigned to this user."""
    assigned = select(UserContent.media_id).where(UserContent.user_id == user.id)
    return select(Media).where(
        Media.status == "active",
        or_(Media.access_type == "common", Media.id.in_(assigned)),
    )


def media_out(m: Media):
    return {
        "id": m.id,
        "title": m.title,
        "description": m.description,
        "language": m.language,
        "content_type": m.content_type,
        "deity_id": m.deity_id,
        "weekday": m.weekday,
    }


@router.get("/me/dashboard")
def dashboard(user: User = Depends(current_user), db: Session = Depends(get_db)):
    now = datetime.now(ZoneInfo(settings.TIMEZONE))
    mapping = db.query(WeekdayMapping).filter_by(weekday=now.weekday()).first()
    deity = db.get(Deity, mapping.deity_id) if mapping else None

    query = visible_media(user)
    if deity:
        query = query.where(or_(Media.deity_id == deity.id, Media.weekday == now.weekday()))

    p = user.profile
    return {
        "welcome": f"Namaste, {user.full_name}",
        "gotram": p.gotram,
        "nakshatram": p.nakshatram,
        "rashi": p.rashi,
        "date": now.strftime("%d %b %Y"),
        "weekday": now.strftime("%A"),
        "deity": {"name": deity.name, "description": deity.description} if deity else None,
        "media": [media_out(m) for m in db.scalars(query).all()],
    }


@router.get("/media")
def list_media(skip: int = 0, limit: int = 20, user: User = Depends(current_user), db: Session = Depends(get_db)):
    query = visible_media(user).order_by(Media.created_at.desc()).offset(skip).limit(limit)
    return [media_out(m) for m in db.scalars(query).all()]


@router.get("/media/{media_id}/play-url")
def play_url(media_id: int, user: User = Depends(current_user), db: Session = Depends(get_db)):
    media = db.scalars(visible_media(user).where(Media.id == media_id)).first()
    if not media:
        raise HTTPException(403, "You do not have access to this content")
    return {"url": signed_url(media.file_path), "content_type": media.content_type}