import os
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise ValueError("DATABASE_URL is not set in environment variables.")

engine = create_engine(
    DATABASE_URL,
    connect_args={"sslmode": "require"},  # ensure SSL

    pool_pre_ping=True,  # checks if connection is alive before using
    pool_size=10,
    max_overflow=20,
    pool_timeout=30
)


SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
