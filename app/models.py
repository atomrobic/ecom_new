from datetime import datetime, timedelta
import json
from sqlalchemy import Boolean, Column, DateTime, Integer, String, Float, ForeignKey, Text
from sqlalchemy.orm import relationship
from app.database import Base  # Import the single Base from your database module
from sqlalchemy.ext.hybrid import hybrid_property

# User model
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    name = Column(String)
    otp = Column(String, nullable=True)  # Store OTP if needed

    orders = relationship("Order", back_populates="user")

class Seller(Base):
    __tablename__ = "sellers"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    products = relationship("Product", back_populates="seller")
    refresh_token = Column(String, nullable=True)
    refresh_token_expires_at = Column(DateTime, nullable=True)
# Product model

class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    description = Column(String)
    price = Column(Float)
    _image = Column("image", Text)  # JSON stored as text
    phone_number = Column(String)
    seller_id = Column(Integer, ForeignKey("sellers.id"))  # <-- fix here

    seller = relationship("Seller", back_populates="products")
    orders = relationship("Order", back_populates="product")


    @hybrid_property
    def image(self):
        if isinstance(self._image, str):
            return json.loads(self._image) if self._image else []
        return []

    @image.setter
    def image(self, value):
        self._image = json.dumps(value)

# OTP model
class Otp(Base):
    __tablename__ = "otps"
    email = Column(String, primary_key=True)
    code = Column(String)
    expires_at = Column(DateTime, default=lambda: datetime.utcnow() + timedelta(minutes=5))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


# Order model
class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    product_id = Column(Integer, ForeignKey("products.id"))
    quantity = Column(Integer)
    address = Column(String)
    pincode = Column(String)
    status = Column(String, default="pending")  # e.g., pending, completed, cancelled
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    deleted = Column(Boolean, default=False)  # Default to False
    user = relationship("User", back_populates="orders")
    product = relationship("Product", back_populates="orders")
