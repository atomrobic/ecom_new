# import os
# from django.db import router
# from fastapi import FastAPI, Depends, HTTPException, UploadFile
# from fastapi.middleware.cors import CORSMiddleware
# from fastapi.staticfiles import StaticFiles
# from sqlalchemy.orm import Session
# import logging
# from app.routers import auth,order, seller
# from app import  models, database,crud, schemas
# from app.database import engine

# # Suppress verbose SQLAlchemy info logs
# logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)

# models.Base.metadata.create_all(bind=database.engine)

# app = FastAPI()

# UPLOAD_DIR = "uploaded"
# os.makedirs(UPLOAD_DIR, exist_ok=True)

# def save_uploaded_file(file: UploadFile):
#     file_path = os.path.join(UPLOAD_DIR, file.filename)
#     with open(file_path, "wb") as buffer:
#         buffer.write(file.file.read())
#     return file_path

# app.add_middleware(
#     CORSMiddleware,
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
#     allow_origins=["*"],  # Or restrict to ["http://localhost:3000"]

# )

# @app.get("/")
# def home():
#     return {"message": "FastAPI + SQLite + Alembic"}

# app.include_router(auth.router)
# # app.include_router(product.router)
# app.include_router(order.router)
# app.include_router(seller.router, prefix="/seller", tags=["seller"])
import os
import shutil
from uuid import uuid4
from dotenv import load_dotenv
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from psycopg2 import OperationalError
from app.routers import auth, order, seller
from app import models, database
from app.database import engine
import logging
from .supabase_client import supabase

logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)

# Create DB tables
models.Base.metadata.create_all(bind=engine)

app = FastAPI()


UPLOAD_DIR = "uploaded"
os.makedirs(UPLOAD_DIR, exist_ok=True)
app.mount("/uploaded", StaticFiles(directory=UPLOAD_DIR), name="uploaded")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    allow_origins=["*"],  # Replace with frontend URL in production
)
from sqlalchemy import text

try:
    with engine.connect() as conn:
        result = conn.execute(text("SELECT NOW();"))
        print("✅ Database connected. Current time:", result.scalar())
except Exception as e:
    print("❌ Database connection failed:", e)

# Routers
app.include_router(auth.router)
app.include_router(order.router)
app.include_router(seller.router, prefix="/seller", tags=["seller"])

@app.get("/")
def home():
    return {"message": "FastAPI + SQLite + Alembic"}
