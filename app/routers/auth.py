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
from app.service import send_mail
from app import crud, schemas, database
router = APIRouter()
@router.post("/send-otp")
async def send_otp(email: str, db: Session = Depends(get_db)):
    print("Sending OTP to:", email)

    user = db.query(User).filter(User.email == email).first()
    if not user:
        raise HTTPException(status_code=404, detail="Email not registered")

    otp_code = generate_otp(email)

    db.query(Otp).filter(Otp.email == email).delete()

    new_otp = Otp(email=email, code=otp_code, created_at=datetime.utcnow())
    db.add(new_otp)
    db.commit()

    try:
        send_mail(
            to=email,
            subject="Your OTP Code",
            html=f"<p>Your OTP is: <b>{otp_code}</b></p>",
        )
    except Exception as e:
        print("Failed to send email:", e)
        raise HTTPException(status_code=500, detail="Failed to send email")

    return {"message": "OTP sent"}


@router.post("/verify-otp")
async def verify_otp_route(email: str, otp: str, db: Session = Depends(get_db)):
    otp_entry = db.query(Otp).filter(Otp.email == email, Otp.code == otp).first()
    if otp_entry:
        db.delete(otp_entry)
        db.commit()
        return {"message": "OTP verified successfully"}
    return {"error": "Invalid OTP"}


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
