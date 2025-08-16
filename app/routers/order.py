from datetime import datetime
import json
import os
import shutil
from typing import List, Optional

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from sqlalchemy.orm import Session

from app.crud import generate_otp, get_db, verify_otp
from app.models import Otp, User
from app import crud, schemas, database
router = APIRouter()
# Order Routes
@router.post("/orders/", response_model=schemas.Order)
def place_order(order: schemas.OrderCreate, db: Session = Depends(get_db)):
    return crud.create_order(db, order)


@router.get("/orders/", response_model=List[schemas.Order])
def list_orders(db: Session = Depends(get_db)):
    return crud.get_orders(db)
