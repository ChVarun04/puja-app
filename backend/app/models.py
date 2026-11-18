from datetime import datetime, date
from sqlalchemy import String, Text, ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .database import Base


class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(primary_key=True)
    full_name: Mapped[str] = mapped_column(String(120))
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    mobile: Mapped[str] = mapped_column(String(20))
    password_hash: Mapped[str] = mapped_column(String(255))
    role: Mapped[str] = mapped_column(String(10), default="user")  # user | admin
    is_active: Mapped[bool] = mapped_column(default=True)
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)
    profile: Mapped["UserProfile"] = relationship(back_populates="user", uselist=False)


class UserProfile(Base):
    __tablename__ = "user_profiles"
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), unique=True)
    dob: Mapped[date | None] = mapped_column(nullable=True)
    gotram: Mapped[str | None] = mapped_column(String(80), nullable=True)
    nakshatram: Mapped[str | None] = mapped_column(String(80), nullable=True)
    rashi: Mapped[str | None] = mapped_column(String(80), nullable=True)
    gender: Mapped[str | None] = mapped_column(String(20), nullable=True)
    preferred_language: Mapped[str | None] = mapped_column(String(40), nullable=True)
    country: Mapped[str | None] = mapped_column(String(80), nullable=True)
    state: Mapped[str | None] = mapped_column(String(80), nullable=True)
    city: Mapped[str | None] = mapped_column(String(80), nullable=True)
    user: Mapped["User"] = relationship(back_populates="profile")


class Deity(Base):
    __tablename__ = "deities"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(120), unique=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    is_active: Mapped[bool] = mapped_column(default=True)


class PujaCategory(Base):
    __tablename__ = "puja_categories"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(120))
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    instructions: Mapped[str | None] = mapped_column(Text, nullable=True)
    deity_id: Mapped[int | None] = mapped_column(ForeignKey("deities.id"), nullable=True)
    is_active: Mapped[bool] = mapped_column(default=True)


class WeekdayMapping(Base):
    __tablename__ = "weekday_mappings"
    id: Mapped[int] = mapped_column(primary_key=True)
    weekday: Mapped[int] = mapped_column(unique=True)  # Monday=0 ... Sunday=6
    deity_id: Mapped[int] = mapped_column(ForeignKey("deities.id"))
    deity: Mapped["Deity"] = relationship()


class Media(Base):
    __tablename__ = "media"
    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(200))
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    language: Mapped[str | None] = mapped_column(String(40), nullable=True)
    content_type: Mapped[str] = mapped_column(String(10))    # audio | video
    file_path: Mapped[str] = mapped_column(String(500))      # path inside the bucket
    deity_id: Mapped[int | None] = mapped_column(ForeignKey("deities.id"), nullable=True)
    puja_category_id: Mapped[int | None] = mapped_column(ForeignKey("puja_categories.id"), nullable=True)
    weekday: Mapped[int | None] = mapped_column(nullable=True)
    status: Mapped[str] = mapped_column(String(10), default="draft")         # draft|active|inactive
    access_type: Mapped[str] = mapped_column(String(15), default="common")   # common|user_specific
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)


class UserContent(Base):
    __tablename__ = "user_content"
    __table_args__ = (UniqueConstraint("user_id", "media_id"),)
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    media_id: Mapped[int] = mapped_column(ForeignKey("media.id"))