import logging
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
from sqlalchemy import text

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

origins = [
    "https://ekart-azure-kappa.vercel.app",  # your deployed frontend
    "http://localhost:3001", 
    "http://localhost:3000"  # local frontend
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,       # allowed origins
    allow_credentials=True,      # allow cookies or auth headers
    allow_methods=["*"],         # allow GET, POST, PUT, DELETE, etc.
    allow_headers=["*"],         # allow all headers
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
app.include_router(banner.router)


# Root endpoint
@app.get("/")
def home(db: Session = Depends(get_db)):
    return {"message": "Database connected successfully 🚀"}
