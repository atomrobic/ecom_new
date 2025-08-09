import os
import shutil
from typing import List
from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from sqlalchemy.orm import Session
from app import crud, models, schemas, database
from passlib.context import CryptContext
from app import schemas
router = APIRouter()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_password_hash(password):
    return pwd_context.hash(password)
@router.post("/seller/signup")
def seller_signup(data: schemas.SellerSignup, db: Session = Depends(get_db)):
    # Check if email already exists
    existing_seller = db.query(models.Seller).filter(models.Seller.email == data.email).first()
    if existing_seller:
        raise HTTPException(status_code=400, detail="Email already registered")

    hashed_pw = pwd_context.hash(data.password)
    new_seller = models.Seller(
        name=data.name,
        email=data.email,
        hashed_password=hashed_pw
    )
    db.add(new_seller)
    db.commit()
    db.refresh(new_seller)
    return {"message": "Seller registered successfully", "seller_id": new_seller.id}


@router.post("/seller/login")
def seller_login(data: schemas.SellerLogin, db: Session = Depends(get_db)):
    seller = db.query(models.Seller).filter(models.Seller.email == data.email).first()
    if not seller or not pwd_context.verify(data.password, seller.hashed_password):
        raise HTTPException(status_code=400, detail="Invalid email or password")
    return {"message": "Login successful", "seller_id": seller.id}

@router.post("/seller/{seller_id}/products", response_model=schemas.Product)
def add_product(
    seller_id: int,  # ✅ Link product to seller
    name: str = Form(...),
    description: str = Form(...),
    price: float = Form(...),
    phone_number: str = Form(...),
    images: List[UploadFile] = File(...),
    db: Session = Depends(get_db),
):
    image_paths = []
    for image in images:
        image_path = os.path.join(crud.UPLOAD_DIR, image.filename)
        with open(image_path, "wb") as buffer:
            shutil.copyfileobj(image.file, buffer)
        image_paths.append(image_path)

    # ✅ Add seller_id to product data
    product_data = schemas.ProductCreate(
        name=name,
        description=description,
        price=price,
        image=image_paths,
        phone_number=phone_number,
        seller_id=seller_id  # <-- Added here
    )

    db_product = crud.create_product(db, product_data)
    return crud.product_to_schema(db_product)



@router.get("/seller/{seller_id}/products")
def get_seller_products(seller_id: int, db: Session = Depends(get_db)):
    products = db.query(models.Product).filter(
        models.Product.seller_id == seller_id,
        models.Product.deleted == False
    ).all()
    return products



@router.delete("/seller/{seller_id}/products/{product_id}")
def delete_product(seller_id: int, product_id: int, db: Session = Depends(get_db)):
    product = db.query(models.Product).filter(
        models.Product.id == product_id,
        models.Product.seller_id == seller_id
    ).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    product.deleted = True
    db.commit()
    return {"message": "Product deleted successfully"}
