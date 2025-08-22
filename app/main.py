# import logging
# from fastapi import FastAPI, Depends
# from fastapi.middleware.cors import CORSMiddleware
# from fastapi.staticfiles import StaticFiles
# from sqlalchemy.orm import Session
# from sqlalchemy import text

# from app import models
# from app.database import engine, Base, get_db
# from app.routers import auth, banner, order, seller
# from app.config import UPLOAD_DIR

# # Suppress verbose SQL logs
# logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)

# # Create all tables
# Base.metadata.create_all(bind=engine)

# app = FastAPI()

# # Serve static uploads
# app.mount("/uploads", StaticFiles(directory=UPLOAD_DIR), name="uploads")
# origins = [
#     # "http://localhost",
#     # "http://localhost:3000",
#     "https://ekart-azure-kappa.vercel.app",   # ✅ Production frontend
# ]


# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=origins,
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )


# # ✅ Test DB connection once at startup
# try:
#     with engine.connect() as conn:
#         result = conn.execute(text("SELECT NOW();"))
#         print("✅ Database connected. Current time:", result.scalar())
# except Exception as e:
#     print("❌ Database connection failed:", e)

# # Routers
# app.include_router(auth.router)
# app.include_router(order.router)
# app.include_router(seller.router, prefix="/seller", tags=["seller"])
# app.include_router(banner.router)


# # Root endpoint
# @app.get("/")
# def home(db: Session = Depends(get_db)):
#     return {"message": "Database connected successfully 🚀"}

import logging
from fastapi import FastAPI, Depends, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import List

from app import models
from app.database import engine, Base, get_db
from app.routers import auth, banner, order, seller
from app.config import UPLOAD_DIR

# Suppress verbose SQL logs
logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)

# Create all tables
Base.metadata.create_all(bind=engine)

app = FastAPI()

# Serve static uploads
app.mount("/uploads", StaticFiles(directory=UPLOAD_DIR), name="uploads")

# CORS setup
origins = [
    "https://ekart-azure-kappa.vercel.app",  # Production frontend
    "http://localhost:5173",                  # Optional: local dev
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Test DB connection at startup
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
app.include_router(banner.router)

# Root endpoint
@app.get("/")
def home(db: Session = Depends(get_db)):
    return {"message": "Database connected successfully 🚀"}

# ✅ Sort products endpoint
@app.get("/sort", response_model=List[models.Product])
def sort_products(
    sort_by: str = Query("price", enum=["price", "name"]),
    db: Session = Depends(get_db)
):
    query = db.query(models.Product).filter(models.Product.is_deleted == False)
    if sort_by == "price":
        return query.order_by(models.Product.price).all()
    elif sort_by == "name":
        return query.order_by(models.Product.name).all()
    return query.all()
