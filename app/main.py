import logging
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
from sqlalchemy import text

from app.database import engine, Base, get_db
from app.routers import auth, banner, order, seller
from app.config import UPLOAD_DIR

logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)

# Create tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Leapcell FastAPI Demo")

# Serve static files
app.mount("/uploads", StaticFiles(directory=UPLOAD_DIR), name="uploads")

# CORS
origins = [
    "https://ekart-azure-kappa.vercel.app",
    "http://localhost:3000",
    "http://localhost:3001",
    "http://127.0.0.1:5500"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

# Test DB
try:
    with engine.connect() as conn:
        result = conn.execute(text("SELECT NOW();"))
        print("✅ Database connected. Current time:", result.scalar())
except Exception as e:
    print("❌ Database connection failed:", e)

# Include routers
app.include_router(auth.router)
app.include_router(order.router)
app.include_router(seller.router, prefix="/seller", tags=["seller"])
app.include_router(banner.router)

# Root endpoint
@app.get("/")
def root(db: Session = Depends(get_db)):
    return {"message": "Database connected successfully 🚀"}

# Health check
@app.get("/kaithheathcheck")
def health_check():
    return {"status": "ok"}
