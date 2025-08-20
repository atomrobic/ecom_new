from pydantic import BaseModel
from typing import List, Optional

# User models
class UserBase(BaseModel):
    email: str

class UserCreate(UserBase):
    name: str
    password: str

class UserLogin(UserBase):
    password: str

class User(UserBase):
    id: int

    model_config = {
        "from_attributes": True
    }
#
# Seller models
from pydantic import BaseModel

class SellerBase(BaseModel):
    email: str

class SellerSignup(SellerBase):
    name: str
    password: str  # plain password entered by user

class SellerLogin(BaseModel):
    email: str
    password: str  # plain password entered by user

# Product models
class ProductBase(BaseModel):
    name: str
    description: str
    price: float
    image: List[str]  # Pydantic expects a list of strings here
    phone_number: str
    seller_id: int  # seller reference
    category_id: int  # <- requires category, not category_id


class ProductCreate(ProductBase):
    pass

class Product(ProductBase):
    id: int

    model_config = {
        "from_attributes": True
    }

# Order models
class OrderBase(BaseModel):
    product_id: int
    quantity: int

class OrderCreate(OrderBase):
    user_id: int

class Order(OrderBase):
    id: int
    user: User
    product: Product

    model_config = {
        "from_attributes": True
    }

# OTP verification schema
class OTPVerifySchema(BaseModel):
    email: str
    otp: str
    
    

class Token(BaseModel):
    access_token: str
    token_type: str
    
    
class CategoryBase(BaseModel):
    name: str

class CategoryCreate(CategoryBase):
    pass

class Category(CategoryBase):
    id: int


class BannerBase(BaseModel):
    image_url: str
    redirect_url: Optional[str] = None

class BannerCreate(BannerBase):
    pass

class BannerUpdate(BaseModel):
    image_url: Optional[str] = None
    redirect_url: Optional[str] = None

class Banner(BannerBase):
    id: int