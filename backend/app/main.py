from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .database import Base, engine
from .routers import auth, user, admin

# Creates the tables if they don't exist (Alembic would be used for real migrations)
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Puja Guidance API", version="1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(user.router)
app.include_router(admin.router)


@app.get("/")
def health():
    return {"status": "ok"}