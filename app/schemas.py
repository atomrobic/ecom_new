from pydantic import BaseModel
from typing import List

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
    image: List[str]
    phone_number: str

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
    
    
