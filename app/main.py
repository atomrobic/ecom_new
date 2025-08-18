import logging
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
from sqlalchemy import text

from app import models
from app.database import engine, Base, get_db
from app.routers import auth, order, seller
from app.config import UPLOAD_DIR

# Suppress verbose SQL logs
logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)

# Create all tables
Base.metadata.create_all(bind=engine)

app = FastAPI()

# Serve static uploads
app.mount("/uploads", StaticFiles(directory=UPLOAD_DIR), name="uploads")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    allow_origins=["*"],  # replace with frontend URL in production
)

# ✅ Test DB connection once at startup
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

# Root endpoint
@app.get("/")
def home(db: Session = Depends(get_db)):
    return {"message": "Database connected successfully 🚀"}
