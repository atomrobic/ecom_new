from datetime import datetime
import json
import os
import shutil
from typing import List, Optional

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from sqlalchemy.orm import Session
from app.database import get_db

from app.crud import generate_otp, verify_otp
from app.models import Otp, User
from app.service import send_email
from app import crud, schemas, database
router = APIRouter()
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime
from app.database import get_db
from app.models import User, Otp
from app.service import generate_otp, send_email

router = APIRouter()
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
import random

from app.database import get_db
from app.models import Otp, User
from app.service import send_email

router = APIRouter()

# In-memory cache
otp_store = {}  # { "email": {"otp": "123456", "expires": datetime } }
OTP_EXPIRY_MINUTES = 10


def generate_otp():
    return str(random.randint(100000, 999999))


@router.post("/send-otp")
async def send_otp(email: str, db: Session = Depends(get_db)):
    # ✅ Check if email exists
    user = db.query(User).filter(User.email == email).first()
    if not user:
        raise HTTPException(status_code=404, detail="Email not registered")

    otp_code = generate_otp()
    expiry = datetime.utcnow() + timedelta(minutes=OTP_EXPIRY_MINUTES)

    # ✅ Save in memory
    otp_store[email] = {"otp": otp_code, "expires": expiry}

    # ✅ Save in DB (delete old, insert new)
    db.query(Otp).filter(Otp.email == email).delete()
    new_otp = Otp(email=email, code=otp_code, created_at=datetime.utcnow())
    db.add(new_otp)
    db.commit()

    # ✅ Send via email
    subject = "Your OTP Code"
    body = f"<h2>Your OTP is: {otp_code}</h2><p>It will expire in {OTP_EXPIRY_MINUTES} minutes.</p>"
    send_email(email, subject, body)

    return {"message": "OTP sent successfully"}

@router.post("/verify-otp")
def verify_otp(email: str, otp: str, db: Session = Depends(get_db)):
    # Fetch the latest OTP for the given email
    otp_entry = db.query(Otp).filter(Otp.email == email).order_by(Otp.created_at.desc()).first()

    if not otp_entry:
        raise HTTPException(status_code=404, detail="No OTP found for this email")

    # Check OTP match
    if otp_entry.code != otp:
        raise HTTPException(status_code=400, detail="Invalid OTP")

    # Optional: check if OTP expired (5 minutes validity)
    if otp_entry.created_at < datetime.utcnow() - timedelta(minutes=5):
        raise HTTPException(status_code=400, detail="OTP expired")

    return {"message": "OTP verified successfully"}


# User Routes
@router.post("/signup", response_model=schemas.User)
def signup(user: schemas.UserCreate, db: Session = Depends(get_db)):
    existing_user = crud.get_user_by_email(db, user.email)
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    return crud.create_user(db, user)


@router.post("/login")
def login(user: schemas.UserLogin, db: Session = Depends(get_db)):
    db_user = crud.get_user_by_email(db, user.email)
    if not db_user or not crud.verify_password(user.password, db_user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    return {"message": "Login successful"}
