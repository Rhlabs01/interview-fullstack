from collections.abc import Generator
from urllib.parse import urlparse

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.config import get_settings


def sqlalchemy_url(url: str) -> str:
    if url.startswith("postgres://"):
        url = "postgresql://" + url[len("postgres://") :]
    if url.startswith("postgresql://") and "+psycopg" not in url:
        url = url.replace("postgresql://", "postgresql+psycopg://", 1)
    return url


def connect_args(url: str) -> dict:
    parsed = urlparse(url)
    query = parsed.query or ""
    if "sslmode=" in query:
        return {}
    host = parsed.hostname or ""
    # External Render Postgres hosts require TLS. The Blueprint internal
    # connection string does not include render.com and needs no extra SSL.
    if "render.com" in host:
        return {"sslmode": "require"}
    return {}


def make_engine(url: str):
    return create_engine(
        sqlalchemy_url(url),
        connect_args=connect_args(url),
        pool_pre_ping=True,
    )


settings = get_settings()
engine = make_engine(settings.database_url)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
