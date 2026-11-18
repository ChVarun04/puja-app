from .database import SessionLocal, Base, engine
from .models import User, UserProfile, Deity, WeekdayMapping
from .security import hash_password

Base.metadata.create_all(bind=engine)
db = SessionLocal()

if not db.query(User).filter_by(email="admin@puja.com").first():
    admin = User(
        full_name="Admin",
        email="admin@puja.com",
        mobile="+910000000000",
        password_hash=hash_password("Admin@123"),
        role="admin",
    )
    admin.profile = UserProfile()
    db.add(admin)

names = [
    "Lord Shiva",                # Monday
    "Lord Hanuman",              # Tuesday
    "Lord Ganesha",              # Wednesday
    "Lord Vishnu / Guru",        # Thursday
    "Goddess Lakshmi",           # Friday
    "Lord Venkateswara Swamy",   # Saturday
    "Lord Surya",                # Sunday
]

if db.query(Deity).count() == 0:
    for i, name in enumerate(names):
        d = Deity(name=name, description=f"Short introduction to {name}.")
        db.add(d)
        db.flush()  # gets d.id before commit
        db.add(WeekdayMapping(weekday=i, deity_id=d.id))

db.commit()
print("seeded")