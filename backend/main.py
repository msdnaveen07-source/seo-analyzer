from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from backend.routers.audit import router as audit_router
from backend.routers.backlinks import router as backlinks_router
from backend.db.database import engine, Base
import backend.db.models  # Register models
import os

from sqlalchemy import text

def init_db_migrations():
    Base.metadata.create_all(bind=engine)
    with engine.connect() as conn:
        for col_name, col_type in [
            ("author_name", "VARCHAR"),
            ("author_email", "VARCHAR"),
            ("article_title", "VARCHAR"),
            ("content_snippet", "TEXT")
        ]:
            try:
                conn.execute(text(f"ALTER TABLE backlink_submissions ADD COLUMN {col_name} {col_type}"))
                conn.commit()
            except Exception:
                pass

from backend.agent.scheduler import start_background_scheduler

init_db_migrations()
os.makedirs("backups/backlinks", exist_ok=True)
start_background_scheduler()

app = FastAPI(
    title="Local Agentic On-Page SEO Analyzer & Optimizer API",
    description="Autonomous local SEO audit, scoring, keyword research, file fix, and backlink engine.",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/backlinks", StaticFiles(directory="backups/backlinks"), name="backlinks")
app.include_router(audit_router)
app.include_router(backlinks_router, prefix="/api/backlinks")

@app.get("/")
def read_root():
    return {
        "status": "online",
        "service": "Local Agentic On-Page SEO Analyzer API",
        "docs": "/docs",
    }

