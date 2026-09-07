import os

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.engine import URL
from sqlalchemy.orm import declarative_base, sessionmaker

load_dotenv()

DATABASE_URL_ENV = os.getenv("DATABASE_URL")

if DATABASE_URL_ENV:
    # Render Postgres exposes a complete connection string. psycopg2 accepts
    # the standard PostgreSQL URL directly through SQLAlchemy.
    DATABASE_URL = DATABASE_URL_ENV.replace(
        "postgres://", "postgresql+psycopg2://", 1
    ).replace(
        "postgresql://", "postgresql+psycopg2://", 1
    )
else:
    DB_PASSWORD = os.getenv("DB_PASSWORD")
    if not DB_PASSWORD:
        raise RuntimeError(
            "Database configuration is missing. Set DATABASE_URL or create backend/.env from .env.example"
        )

    DATABASE_URL = URL.create(
        drivername="postgresql+psycopg2",
        username=os.getenv("DB_USER", "postgres"),
        password=DB_PASSWORD,
        host=os.getenv("DB_HOST", "localhost"),
        port=int(os.getenv("DB_PORT", "5432")),
        database=os.getenv("DB_NAME", "oceannova"),
    )

engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
    future=True,
)

SessionLocal = sessionmaker(
    bind=engine,
    autocommit=False,
    autoflush=False,
)

Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
