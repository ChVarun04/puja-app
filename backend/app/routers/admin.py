from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from pydantic import BaseModel
from sqlalchemy import or_
from sqlalchemy.orm import Session
from ..database import get_db
from ..deps import admin_only
from ..models import User, Deity, PujaCategory, WeekdayMapping, Media, UserContent
from ..storage import upload_file

router = APIRouter(prefix="/admin", tags=["admin"], dependencies=[Depends(admin_only)])


# ---------- helpers to turn DB rows into JSON ----------
def deity_out(d: Deity):
    return {"id": d.id, "name": d.name, "description": d.description, "is_active": d.is_active}


def category_out(c: PujaCategory):
    return {"id": c.id, "name": c.name, "description": c.description,
            "instructions": c.instructions, "deity_id": c.deity_id, "is_active": c.is_active}


def media_out(m: Media):
    return {"id": m.id, "title": m.title, "description": m.description, "language": m.language,
            "content_type": m.content_type, "deity_id": m.deity_id,
            "puja_category_id": m.puja_category_id, "weekday": m.weekday,
            "status": m.status, "access_type": m.access_type,
            "created_at": m.created_at.isoformat()}


# ---------- dashboard stats ----------
@router.get("/stats")
def stats(db: Session = Depends(get_db)):
    return {
        "users": db.query(User).filter(User.role == "user").count(),
        "audio": db.query(Media).filter_by(content_type="audio", status="active").count(),
        "video": db.query(Media).filter_by(content_type="video", status="active").count(),
        "categories": db.query(PujaCategory).count(),
        "recent": [{"id": m.id, "title": m.title} for m in
                   db.query(Media).order_by(Media.created_at.desc()).limit(5)],
    }


# ---------- users ----------
@router.get("/users")
def list_users(search: str = "", skip: int = 0, limit: int = 20, db: Session = Depends(get_db)):
    q = db.query(User).filter(User.role == "user")
    if search:
        like = f"%{search}%"
        q = q.filter(or_(User.full_name.ilike(like), User.email.ilike(like)))
    q = q.order_by(User.id.desc()).offset(skip).limit(limit)
    return [{"id": u.id, "name": u.full_name, "email": u.email,
             "mobile": u.mobile, "is_active": u.is_active} for u in q]


@router.get("/users/{uid}")
def user_detail(uid: int, db: Session = Depends(get_db)):
    u = db.get(User, uid)
    if not u:
        raise HTTPException(404, "User not found")
    p = u.profile
    # Only limited profile info is exposed to admins
    return {"id": u.id, "name": u.full_name, "email": u.email, "is_active": u.is_active,
            "gotram": p.gotram, "nakshatram": p.nakshatram, "rashi": p.rashi,
            "preferred_language": p.preferred_language, "city": p.city, "country": p.country}


@router.patch("/users/{uid}/status")
def set_user_status(uid: int, is_active: bool, db: Session = Depends(get_db)):
    u = db.get(User, uid)
    if not u:
        raise HTTPException(404, "User not found")
    if u.role == "admin":
        raise HTTPException(400, "Cannot change an admin account")
    u.is_active = is_active
    db.commit()
    return {"id": uid, "is_active": is_active}


# ---------- deities ----------
class DeityIn(BaseModel):
    name: str
    description: str | None = None
    is_active: bool = True


@router.get("/deities")
def list_deities(db: Session = Depends(get_db)):
    return [deity_out(d) for d in db.query(Deity).order_by(Deity.id)]


@router.post("/deities", status_code=201)
def add_deity(data: DeityIn, db: Session = Depends(get_db)):
    if db.query(Deity).filter_by(name=data.name).first():
        raise HTTPException(409, "Deity already exists")
    obj = Deity(**data.model_dump())
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return deity_out(obj)


@router.put("/deities/{did}")
def edit_deity(did: int, data: DeityIn, db: Session = Depends(get_db)):
    obj = db.get(Deity, did)
    if not obj:
        raise HTTPException(404, "Deity not found")
    for k, v in data.model_dump().items():
        setattr(obj, k, v)
    db.commit()
    return deity_out(obj)


# ---------- puja categories ----------
class CategoryIn(BaseModel):
    name: str
    description: str | None = None
    instructions: str | None = None
    deity_id: int | None = None
    is_active: bool = True


@router.get("/puja-categories")
def list_categories(db: Session = Depends(get_db)):
    return [category_out(c) for c in db.query(PujaCategory).order_by(PujaCategory.id)]


@router.post("/puja-categories", status_code=201)
def add_category(data: CategoryIn, db: Session = Depends(get_db)):
    obj = PujaCategory(**data.model_dump())
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return category_out(obj)


@router.put("/puja-categories/{cid}")
def edit_category(cid: int, data: CategoryIn, db: Session = Depends(get_db)):
    obj = db.get(PujaCategory, cid)
    if not obj:
        raise HTTPException(404, "Category not found")
    for k, v in data.model_dump().items():
        setattr(obj, k, v)
    db.commit()
    return category_out(obj)


# ---------- weekday -> deity mapping ----------
class MappingIn(BaseModel):
    weekday: int  # 0 = Monday ... 6 = Sunday
    deity_id: int


@router.get("/weekday-mappings")
def list_mappings(db: Session = Depends(get_db)):
    return [{"weekday": m.weekday, "deity_id": m.deity_id, "deity": m.deity.name}
            for m in db.query(WeekdayMapping).order_by(WeekdayMapping.weekday)]


@router.put("/weekday-mappings")
def set_mapping(data: MappingIn, db: Session = Depends(get_db)):
    if not 0 <= data.weekday <= 6:
        raise HTTPException(400, "weekday must be 0 (Monday) to 6 (Sunday)")
    if not db.get(Deity, data.deity_id):
        raise HTTPException(404, "Deity not found")
    obj = db.query(WeekdayMapping).filter_by(weekday=data.weekday).first()
    if obj:
        obj.deity_id = data.deity_id
    else:
        db.add(WeekdayMapping(weekday=data.weekday, deity_id=data.deity_id))
    db.commit()
    return {"message": "saved"}


# ---------- media ----------
@router.post("/media", status_code=201)
async def upload_media(
    title: str = Form(...),
    content_type: str = Form(...),  # audio | video
    description: str = Form(None),
    language: str = Form(None),
    deity_id: int = Form(None),
    puja_category_id: int = Form(None),
    weekday: int = Form(None),
    access_type: str = Form("common"),  # common | user_specific
    status: str = Form("draft"),        # draft | active | inactive
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    if content_type not in ("audio", "video"):
        raise HTTPException(400, "content_type must be audio or video")
    if access_type not in ("common", "user_specific"):
        raise HTTPException(400, "access_type must be common or user_specific")
    if status not in ("draft", "active", "inactive"):
        raise HTTPException(400, "status must be draft, active or inactive")

    # Swagger sends 0 for empty id fields, so treat 0 as "not provided".
    # Do NOT do this for weekday, because 0 is Monday.
    deity_id = deity_id or None
    puja_category_id = puja_category_id or None

    if deity_id is not None and not db.get(Deity, deity_id):
        raise HTTPException(400, "Deity not found")
    if puja_category_id is not None and not db.get(PujaCategory, puja_category_id):
        raise HTTPException(400, "Puja category not found")
    if weekday is not None and not (0 <= weekday <= 6):
        raise HTTPException(400, "weekday must be between 0 (Monday) and 6 (Sunday)")

    # All validation is done before the upload, so a rejected request leaves no orphan file in the bucket
    try:
        path = upload_file(await file.read(), file.filename, file.content_type or "application/octet-stream")
    except RuntimeError as e:
        raise HTTPException(502, str(e))

    m = Media(title=title, content_type=content_type, description=description, language=language,
              deity_id=deity_id, puja_category_id=puja_category_id, weekday=weekday,
              access_type=access_type, status=status, file_path=path)
    db.add(m)
    db.commit()
    db.refresh(m)
    return media_out(m)

@router.get("/media")
def list_all_media(db: Session = Depends(get_db)):
    return [media_out(m) for m in db.query(Media).order_by(Media.created_at.desc())]


@router.patch("/media/{mid}")
def edit_media(mid: int, status: str | None = None, title: str | None = None,
               access_type: str | None = None, db: Session = Depends(get_db)):
    m = db.get(Media, mid)
    if not m:
        raise HTTPException(404, "Media not found")
    if status:
        if status not in ("draft", "active", "inactive"):
            raise HTTPException(400, "Invalid status")
        m.status = status
    if title:
        m.title = title
    if access_type:
        if access_type not in ("common", "user_specific"):
            raise HTTPException(400, "Invalid access_type")
        m.access_type = access_type
    db.commit()
    return media_out(m)


@router.delete("/media/{mid}")
def delete_media(mid: int, db: Session = Depends(get_db)):
    m = db.get(Media, mid)
    if not m:
        raise HTTPException(404, "Media not found")
    db.query(UserContent).filter_by(media_id=mid).delete()
    db.delete(m)
    db.commit()
    return {"message": "deleted"}


@router.post("/media/{mid}/assign/{uid}")
def assign_media(mid: int, uid: int, db: Session = Depends(get_db)):
    if not db.get(Media, mid) or not db.get(User, uid):
        raise HTTPException(404, "Media or user not found")
    if not db.query(UserContent).filter_by(media_id=mid, user_id=uid).first():
        db.add(UserContent(media_id=mid, user_id=uid))
        db.commit()
    return {"message": "assigned"}


@router.delete("/media/{mid}/assign/{uid}")
def unassign_media(mid: int, uid: int, db: Session = Depends(get_db)):
    db.query(UserContent).filter_by(media_id=mid, user_id=uid).delete()
    db.commit()
    return {"message": "unassigned"}