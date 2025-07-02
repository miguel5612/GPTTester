import logging
import os
from sqlalchemy import create_engine, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://postgres:%40bcd1234.%2A@localhost:5432/testdb"
)

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

logger = logging.getLogger(__name__)

try:
    with engine.connect() as conn:
        conn.execute(text("SELECT 1"))
    logger.info("Connected to database %s", DATABASE_URL)
except Exception:
    logger.exception("Database connection failed")
