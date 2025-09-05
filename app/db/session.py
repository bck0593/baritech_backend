from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.engine.url import make_url
from typing import Generator

from app.core.config import settings

# Configure connect_args for different databases
connect_args = {}

# Parse URL to determine database type
if "sqlite" in settings.DATABASE_URL:
    connect_args = {"check_same_thread": False}
elif "mysql" in settings.DATABASE_URL and "pymysql" in settings.DATABASE_URL:
    # MySQL with PyMySQL specific configuration
    connect_args = {
        "connect_timeout": 60,
        "read_timeout": 30,
        "write_timeout": 30
    }

# Create SQLAlchemy engine
engine = create_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True,
    pool_recycle=300,
    connect_args=connect_args,
    echo=settings.APP_ENV == "dev"
)

# Create SessionLocal class
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create Base class for models
Base = declarative_base()


def get_db() -> Generator[Session, None, None]:
    """
    Dependency to get database session
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()