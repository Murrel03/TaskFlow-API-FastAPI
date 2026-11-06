"""TaskFlow API entry point. Run: uvicorn app.main:app --reload"""
from fastapi import FastAPI

from .database import Base, engine
from .routers import auth, projects, tasks

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="TaskFlow API",
    description="A FastAPI REST API for task and project management, with JWT auth.",
    version="1.0.0",
)

app.include_router(auth.router)
app.include_router(projects.router)
app.include_router(tasks.router)


@app.get("/health", tags=["health"])
def health():
    return {"status": "ok"}
