from datetime import datetime, timedelta
import logging
import os
import json
import secrets
import shutil
import random
import time
from typing import List, Optional
import uuid

import cloudinary
from fastapi import APIRouter, Depends, File, Form, HTTPException, Header, UploadFile, status
from fastapi.params import Query
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError
import jwt
from sqlalchemy.orm import Session
from passlib.context import CryptContext

from app import crud, models, schemas, database
from app import auths
from app.config import ACCESS_TOKEN_EXPIRE_MINUTES, REFRESH_TOKEN_EXPIRE_DAYS
from app.config import UPLOAD_DIR
from app.cloudinary_config import cloudinary

# ---------------------- CONFIG ----------------------
router = APIRouter()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")




oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# ---------------------- LOGGING ----------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# ---------------------- DB DEPENDENCY ----------------------
def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ---------------------- PASSWORD UTILS ----------------------
def get_password_hash(password: str):
    return pwd_context.hash(password)

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

# ---------------------- TOKEN UTILS ----------------------
def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, auths.SECRET_KEY, algorithm=auths.ALGORITHM)



# ---------------------- SELLER ROUTES ----------------------
@router.post("/signup")
def seller_signup(data: schemas.SellerSignup, db: Session = Depends(get_db)):
    if db.query(models.Seller).filter(models.Seller.email == data.email).first():
        raise HTTPException(status_code=400, detail="Email already registered")

    hashed_pw = get_password_hash(data.password)
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
    # 🔍 Find seller by email
    seller = db.query(models.Seller).filter(models.Seller.email == data.email).first()

    # 🚫 Validate credentials
    if not seller or not auths.verify_password(data.password, seller.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
 # 🕒 Access token expiration
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = auths.create_access_token(
        data={"sub": seller.email},
        expires_delta=access_token_expires
    )

    # 🔁 Generate refresh token
    refresh_token = secrets.token_urlsafe(32)
    hashed_refresh_token = auths.hash_token(refresh_token)

    try:
        seller.refresh_token = hashed_refresh_token
        seller.refresh_token_expires_at = datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
        db.commit()
        db.refresh(seller)
    except Exception:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to save session. Please try again."
        )

    # ✅ Return tokens and seller info
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "refresh_token": refresh_token,  # send once
        "seller": {
            "id": seller.id,
            "name": seller.name,
            "email": seller.email
        }
    }


ALLOWED_EXTENSIONS = {"jpg", "jpeg", "png", "webp"}

def allowed_file(filename: str):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


# Configure Cloudinary


UPLOAD_LIMIT = 5

@router.post("/products")
def manage_product(
    action: str = Form(...),  # 'add', 'update', 'delete'
    product_id: Optional[int] = Form(None),
    name: Optional[str] = Form(None),
    description: Optional[str] = Form(None),
    price: Optional[float] = Form(None),
    phone_number: Optional[str] = Form(None),
    images: Optional[List[UploadFile]] = File(None),
    db: Session = Depends(get_db),
    current_seller: models.Seller = Depends(auths.get_current_seller)
):
    seller_id = current_seller.id

    # ------------------- ADD -------------------
    if action == "add":
        if not name or not description or price is None or not phone_number or not images:
            raise HTTPException(
                status_code=400,
                detail="Missing required fields for adding product"
            )

        if len(images) == 0:
            raise HTTPException(status_code=400, detail="At least one image is required")
        if len(images) > UPLOAD_LIMIT:
            raise HTTPException(status_code=400, detail=f"You can upload up to {UPLOAD_LIMIT} images")

        image_urls = []
        for image in images:
            if not allowed_file(image.filename):
                raise HTTPException(status_code=400, detail=f"Unsupported file type: {image.filename}")
            try:
                result = cloudinary.uploader.upload(image.file)
                image_url = result.get("secure_url")
                image_urls.append(image_url)
            except Exception as e:
                raise HTTPException(status_code=500, detail=f"Image upload failed: {e}")

        product_data = schemas.ProductCreate(
            name=name,
            description=description,
            price=price,
            image=image_urls,
            phone_number=phone_number,
            seller_id=seller_id
        )
        db_product = crud.create_product(db, product_data)
        return crud.product_to_schema(db_product)

    # ------------------- UPDATE -------------------
    elif action == "update":
        if not product_id:
            raise HTTPException(status_code=400, detail="product_id is required for update")

        db_product = db.query(models.Product).filter(models.Product.id == product_id).first()
        if not db_product:
            raise HTTPException(status_code=404, detail="Product not found")
        if db_product.seller_id != seller_id:
            raise HTTPException(status_code=403, detail="You do not own this product")

        update_data = {}
        if name:
            update_data["name"] = name
        if description:
            update_data["description"] = description
        if price is not None:
            update_data["price"] = price
        if phone_number:
            update_data["phone_number"] = phone_number

        if images:
            if len(images) > UPLOAD_LIMIT:
                raise HTTPException(status_code=400, detail=f"You can upload up to {UPLOAD_LIMIT} images")
            image_urls = []
            for image in images:
                if not allowed_file(image.filename):
                    raise HTTPException(status_code=400, detail=f"Unsupported file type: {image.filename}")
                try:
                    result = cloudinary.uploader.upload(image.file)
                    image_url = result.get("secure_url")
                    image_urls.append(image_url)
                except Exception as e:
                    raise HTTPException(status_code=500, detail=f"Image upload failed: {e}")
            update_data["image"] = image_urls

        db_product = crud.update_product(db, product_id, update_data)
        return crud.product_to_schema(db_product)

    # ------------------- DELETE -------------------
    elif action == "delete":
        if not product_id:
            raise HTTPException(status_code=400, detail="product_id is required for delete")

        db_product = db.query(models.Product).filter(models.Product.id == product_id).first()
        if not db_product:
            raise HTTPException(status_code=404, detail="Product not found")
        if db_product.seller_id != seller_id:
            raise HTTPException(status_code=403, detail="You do not own this product")

        db.delete(db_product)
        db.commit()
        return {"detail": "Product deleted successfully"}

    else:
        raise HTTPException(status_code=400, detail="Invalid action. Must be 'add', 'update', or 'delete'.")
# @router.post("/products")
# def manage_product(
#     action: str = Form(...),  # 'add', 'update', 'delete'
#     product_id: Optional[int] = Form(None),
#     name: Optional[str] = Form(None),
#     description: Optional[str] = Form(None),
#     price: Optional[float] = Form(None),
#     phone_number: Optional[str] = Form(None),
#     images: Optional[List[UploadFile]] = File(None),
#     db: Session = Depends(get_db),
#     current_seller: models.Seller = Depends(auths.get_current_seller)
# ):
#     seller_id = current_seller.id

#     # ------------------- ADD -------------------
#     if action == "add":
#         if not name or not description or price is None or not phone_number or not images:
#             raise HTTPException(
#                 status_code=400,
#                 detail="Missing required fields for adding product"
#             )

#         if len(images) == 0:
#             raise HTTPException(status_code=400, detail="At least one image is required")

#         if len(images) > 5:
#             raise HTTPException(status_code=400, detail="You can upload up to 5 images")

#         # image_urls = []
#         # for image in images:
#         #     if not allowed_file(image.filename):
#         #         raise HTTPException(status_code=400, detail=f"Unsupported file type: {image.filename}")

#         #     ext = image.filename.rsplit(".", 1)[1].lower()
#         #     filename = f"{uuid.uuid4()}.{ext}"
#         #     image_path = os.path.join(UPLOAD_DIR, filename)
#         #     image_url = f"/uploads/{filename}"

#         #     with open(image_path, "wb") as buffer:
#         #         shutil.copyfileobj(image.file, buffer)
#         #     image_urls.append(image_url)
#         import uuid

#         image_urls = []

#         for image in images:
#             if not allowed_file(image.filename):
#                 raise HTTPException(status_code=400, detail=f"Unsupported file type: {image.filename}")

#             try:
#                 # Upload to Cloudinary instead of local disk
#                 result = cloudinary.uploader.upload("path/to/image.jpg")
#                 # result = cloudinary.uploader.upload(image.file)
#                 image_url = result.get("secure_url")  # Cloudinary public URL
#                 image_urls.append(image_url)
#             except Exception as e:
#                 raise HTTPException(status_code=500, detail=f"Image upload failed: {e}")


#             image_urls.append(image_url)
#         product_data = schemas.ProductCreate(
#             name=name,
#             description=description,
#             price=price,
#             image=image_urls,
#             phone_number=phone_number,
#             seller_id=seller_id
#         )
#         db_product = crud.create_product(db, product_data)
#         return crud.product_to_schema(db_product)

#     # ------------------- UPDATE -------------------
#     elif action == "update":
#         if not product_id:
#             raise HTTPException(status_code=400, detail="product_id is required for update")

#         # Step 1: Find the product
#         db_product = db.query(models.Product).filter(models.Product.id == product_id).first()
#         if not db_product:
#             raise HTTPException(status_code=404, detail="Product not found")

#         # Step 2: Check ownership
#         if db_product.seller_id != seller_id:
#             raise HTTPException(status_code=403, detail="You do not own this product")

#         # Step 3: Prepare updates
#         update_data = {}
#         if name:
#             update_data["name"] = name
#         if description:
#             update_data["description"] = description
#         if price is not None:
#             update_data["price"] = price
#         if phone_number:
#             update_data["phone_number"] = phone_number

#         if images:
#             if len(images) > 5:
#                 raise HTTPException(status_code=400, detail="You can upload up to 5 images")

#             image_urls = []
#             for image in images:
#                 if not allowed_file(image.filename):
#                     raise HTTPException(status_code=400, detail=f"Unsupported file type: {image.filename}")

#                 ext = image.filename.rsplit(".", 1)[1].lower()
#                 filename = f"{uuid.uuid4()}.{ext}"
#                 image_path = os.path.join(UPLOAD_DIR, filename)
#                 image_url = f"/uploads/{filename}"

#                 with open(image_path, "wb") as buffer:
#                     shutil.copyfileobj(image.file, buffer)
#                 image_urls.append(image_url)
#             update_data["image"] = image_urls

#         db_product = crud.update_product(db, product_id, update_data)
#         return crud.product_to_schema(db_product)

#     # ------------------- DELETE -------------------
#     elif action == "delete":
#         if not product_id:
#             raise HTTPException(status_code=400, detail="product_id is required for delete")

#         db_product = db.query(models.Product).filter(models.Product.id == product_id).first()
#         if not db_product:
#             raise HTTPException(status_code=404, detail="Product not found")

#         if db_product.seller_id != seller_id:
#             raise HTTPException(status_code=403, detail="You do not own this product")

#         db.delete(db_product)
#         db.commit()
#         return {"detail": "Product deleted successfully"}

#     # ------------------- INVALID ACTION -------------------
#     else:
#         raise HTTPException(status_code=400, detail="Invalid action. Use 'add', 'update', or 'delete'")
@router.delete("/products/{product_id}")

@router.get("/products/by-seller/{seller_id}")
async def read_products_by_seller(seller_id: int, db: Session = Depends(get_db)):
    logger.info(f"Fetching products for seller_id={seller_id}")
    products = crud.get_products_by_seller(db, seller_id)
    if not products:
        raise HTTPException(status_code=404, detail="No products found for this seller")
    return products

@router.get("/products", response_model=List[schemas.Product])
def list_products(
    id: Optional[int] = Query(None),
    db: Session = Depends(get_db)
):
    if id is not None:
        db_products = db.query(models.Product).filter(models.Product.seller_id == id).all()
        return [crud.product_to_schema(p) for p in db_products]

    db_products = db.query(models.Product).all()
    return [crud.product_to_schema(p) for p in db_products]
@router.get("/products/{product_id}", response_model=schemas.Product)
def product_details(product_id: int, db: Session = Depends(get_db)):
    db_product = db.query(models.Product).filter(models.Product.id == product_id).first()
    if not db_product:
        raise HTTPException(status_code=404, detail="Product not found")
    return crud.product_to_schema(db_product)
# ---------------------- OTP UTILS ----------------------
otp_store = {}

def generate_otp(email: str) -> str:
    otp = str(random.randint(100000, 999999))
    otp_store[email] = {"otp": otp, "timestamp": time.time()}
    return otp

def verify_otp(email: str, entered_otp: str) -> bool:
    if email in otp_store:
        data = otp_store[email]
        if time.time() - data["timestamp"] > 300:
            return False
        return data["otp"] == entered_otp
    return False
