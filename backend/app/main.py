from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.v1.router import api_router
from app.core.config import get_settings
from app.db.base import Base
from app.db.session import engine
from app.db.seed import seed_demo_data
import app.models  # noqa: F401 - registers SQLAlchemy metadata


@asynccontextmanager
async def lifespan(_: FastAPI):
    # Development bootstrap. Replace with Alembic migrations before production deployment.
    Base.metadata.create_all(bind=engine)
    from app.db.session import SessionLocal

    db = SessionLocal()
    try:
        seed_demo_data(db)
    finally:
        db.close()
    yield


settings = get_settings()
app = FastAPI(title=settings.app_name, version="0.1.0", lifespan=lifespan)
app.add_middleware(CORSMiddleware, allow_origins=settings.cors_origin_list, allow_credentials=True, allow_methods=["*"], allow_headers=["*"])
app.include_router(api_router, prefix="/api/v1")
