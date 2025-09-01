# import os
# from sqlalchemy import create_engine
# from sqlalchemy.orm import declarative_base, sessionmaker
# from sqlalchemy_utils import database_exists, create_database
# from dotenv import load_dotenv

# # Load environment variables
# load_dotenv()

# # Use DATABASE_URL from env, else fallback to local DB
# DATABASE_URL = os.getenv(
#     "DATABASE_URL",
#     "postgresql://postgres:akhil@localhost:5432/new_ecoms"
# )

# if not DATABASE_URL:
#     raise ValueError("DATABASE_URL is not set in environment variables.")

# # Engine setup
# engine = create_engine(
#     DATABASE_URL,
#     connect_args={"sslmode": "require"} if "supabase" in DATABASE_URL or "render" in DATABASE_URL else {},  
#     pool_pre_ping=True,
#     pool_size=5,
#     max_overflow=10,
#     pool_timeout=30,
#     pool_recycle=1800
# )

# # Create database if it does not exist
# if not database_exists(engine.url):
#     create_database(engine.url)
#     print(f"✅ Database created: {engine.url.database}")
# else:
#     print(f"✅ Connected to database: {engine.url.database}")

# # Session and Base
# SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
# Base = declarative_base()

# # Dependency for FastAPI routes
# def get_db():
#     db = SessionLocal()
#     try:
#         yield db
#     finally:
#         db.close()


import os
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy_utils import database_exists, create_database
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Use DATABASE_URL from env
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://postgres:akhil@localhost:5432/new_ecoms"
)

if not DATABASE_URL:
    raise ValueError("DATABASE_URL is not set in environment variables.")

# ✅ Force SSL for Supabase/Render
engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
    pool_size=5,
    max_overflow=10,
    pool_timeout=30,
    pool_recycle=1800
)

# Create database if it does not exist
if not database_exists(engine.url):
    create_database(engine.url)
    print(f"✅ Database created: {engine.url.database}")
else:
    print(f"✅ Connected to database: {engine.url.database}")

# Session and Base
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Dependency for FastAPI routes
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
