from datetime import datetime
import json
import os
import shutil
from typing import List, Optional

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from sqlalchemy.orm import Session

from app import crud, schemas, database
from app.models import Otp, User
from app.crud import UPLOAD_DIR, get_db
from app.service import send_mail
from app import crud, schemas, database

router = APIRouter()

@router.post("/products/", response_model=schemas.Product)
def add_product(
    name: str = Form(...),
    description: str = Form(...),
    price: float = Form(...),
    phone_number: str = Form(...),
    images: List[UploadFile] = File(...),
    db: Session = Depends(get_db),
):
    image_paths = []
    for image in images:
        image_path = os.path.join(UPLOAD_DIR, image.filename)
        with open(image_path, "wb") as buffer:
            shutil.copyfileobj(image.file, buffer)
        image_paths.append(image_path)

    product_data = schemas.ProductCreate(
        name=name,
        description=description,
        price=price,
        image=image_paths,
        phone_number=phone_number,
    )

    db_product = crud.create_product(db, product_data)  # create product in DB
    return crud.product_to_schema(db_product)  # convert DB model to schema and return


@router.get("/products/", response_model=List[schemas.Product])
def list_products(id: Optional[int] = None, db: Session = Depends(get_db)):
    if id:
        product = crud.get_product_by_id(db, id)
        return [product] if product else []
    return crud.get_products(db)

