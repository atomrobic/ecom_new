from django.db import router
from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
import logging
from app.routers import auth, product, order, seller
from app import  models, database,crud, schemas
from app.database import engine

# Suppress verbose SQLAlchemy info logs
logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)

models.Base.metadata.create_all(bind=database.engine)

app = FastAPI()

app.mount("/uploaded_images", StaticFiles(directory="uploaded_images"), name="uploaded_images")

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    allow_origins=["*"],  # Or restrict to ["http://localhost:3000"]

)

@app.get("/")
def home():
    return {"message": "FastAPI + SQLite + Alembic"}

app.include_router(auth.router)
app.include_router(product.router)
app.include_router(order.router)
app.include_router(seller.router, prefix="/seller", tags=["seller"])
