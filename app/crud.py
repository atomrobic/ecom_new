from datetime import time
import json
import os
import jwt
from sqlalchemy.orm import Session
from app.models import User  # SQLAlchemy model
from app.schemas import Product, UserCreate  # Pydantic schema for input
from app.database import SessionLocal
from . import models, schemas
import random
import datetime
import time
# import time
# otp_store = {}  # temp in-memory, use Redis/DB in production
otp_store = {}  # temp in-memory, use Redis/DB in production
# Users
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_user_by_email(db: Session, email: str):
    return db.query(models.User).filter(models.User.email == email).first()



# UPLOAD_DIR = "uploaded_images"
def product_to_schema(db_product: models.Product) -> schemas.Product:
    return schemas.Product(
        id=db_product.id,
        name=db_product.name,
        description=db_product.description,
        price=db_product.price,
        image=json.loads(db_product.image),
        phone_number=db_product.phone_number,
        seller_id=db_product.seller_id  # ✅ Add this
    )

def update_product(db: Session, product_id: int, update_data: dict):
    db_product = db.query(models.Product).filter(models.Product.id == product_id).first()
    if not db_product:
        return None  # Product not found
    
    for key, value in update_data.items():
        if hasattr(db_product, key):
            setattr(db_product, key, value)
    
    db.commit()
    db.refresh(db_product)
    return db_product

print (Product)
def create_product(db: Session, product: schemas.ProductCreate):
    db_product = models.Product(
        name=product.name,
        description=product.description,
        price=product.price,
        image=json.dumps(product.image) if product.image else "[]",  # ✅ store as string
        phone_number=product.phone_number,
        seller_id=product.seller_id
    )
    db.add(db_product)
    db.commit()
    db.refresh(db_product)
    return db_product

def get_products_by_seller(db: Session, seller_id: int):
    return db.query(models.Product).filter(models.Product.seller_id == seller_id).all()

import json

product_to_schema = lambda p: schemas.Product(
    id=p.id,
    name=p.name,
    description=p.description,
    price=p.price,
    image=json.loads(p.image) if isinstance(p.image, str) else (p.image if isinstance(p.image, list) else []),
    phone_number=p.phone_number,
    seller_id=p.seller_id
)


# Orders
def create_order(db: Session, order: schemas.OrderCreate):
    db_order = models.Order(**order.dict())
    db.add(db_order)
    db.commit()
    db.refresh(db_order)
    return db_order

def get_orders(db: Session):
    return db.query(models.Order).all()


def generate_otp(email: str) -> str:
    otp = str(random.randint(100000, 999999))
    otp_store[email] = {"otp": otp, "timestamp": time.time()}
    return otp

def verify_otp(email: str, entered_otp: str) -> bool:
    if email in otp_store:
        data = otp_store[email]
        if time.time() - data["timestamp"] > 300:  # OTP valid for 5 mins
            return False
        return data["otp"] == entered_otp
    return False

# UPLOAD_DIR = "uploaded_images"
# os.makedirs(UPLOAD_DIR, exist_ok=True)
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_password_hash(password: str):
    return pwd_context.hash(password)



def create_user(db: Session, user: UserCreate):
    hashed_password = get_password_hash(user.password)
    db_user = User(
        email=user.email,
        hashed_password=hashed_password,
        name=user.name
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

######seller######

