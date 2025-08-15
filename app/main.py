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
import psycopg2
from app.routers import auth, order, seller
from app import models, database
from app.database import engine
import logging
from .supabase_client import supabase

# Suppress verbose SQLAlchemy logs
logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)

# Create DB tables
models.Base.metadata.create_all(bind=engine)

app = FastAPI()

# Directory for uploaded files
UPLOAD_DIR = "uploaded"
os.makedirs(UPLOAD_DIR, exist_ok=True)

# Serve static files at /uploads
app.mount("/uploads", StaticFiles(directory=UPLOAD_DIR), name="uploads")


import psycopg2


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

# Endpoint to upload a product image
@app.post("/seller/upload-product-image")
async def upload_product_image(file: UploadFile = File(...)):
    # Generate a unique filename
    file_ext = os.path.splitext(file.filename)[1]
    unique_name = f"{uuid4()}{file_ext}"
    file_path = os.path.join(UPLOAD_DIR, unique_name)

    try:
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save file: {str(e)}")
    finally:
        file.file.close()

    # Return the URL to store in the DB
    return {"url": f"/uploads/{unique_name}"}
