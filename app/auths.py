from datetime import datetime, timedelta
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from sqlalchemy.orm import Session

from app import models
from app.database import get_db

# 🔐 Security Configuration
SECRET_KEY = "54fa6f2703acc4abfc0011784fd33852c96991be7073d2e8fbef0b7f3719da6d"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 600

# ✅ OAuth2 Password Bearer Scheme
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/seller/login")


def create_access_token(data: dict, expires_delta: timedelta | None = None):
    """
    Helper function to create a JWT token.
    """
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)  # ✅ Fixed: was 15
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def get_current_seller(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):
    """
    Dependency to extract and validate the current seller from a JWT token.
    Includes full debugging output.
    """
    print("\n" + "="*50)
    print("🔍 DEBUG: get_current_seller called")
    print(f"📨 Raw Token: {token[:20]}...{token[-20:]}")  # Partial token only
    print(f"🕒 Current UTC Time: {datetime.utcnow()}")

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        print("✅ JWT Decoded Successfully")
        print(f"📄 Payload: {payload}")

        email: str = payload.get("sub")
        if not email:
            print("❌ 'sub' missing in token")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token: missing subject (email)",
                headers={"WWW-Authenticate": "Bearer"},
            )

        exp = payload.get("exp")
        if exp:
            exp_time = datetime.utcfromtimestamp(exp)
            print(f"📅 Token Expiration: {exp_time}")
            if exp_time < datetime.utcnow():
                print("⏰ Token expired!")
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Token has expired",
                    headers={"WWW-Authenticate": "Bearer"},
                )

    except JWTError as e:
        print(f"❌ JWT Error: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    print(f"🔍 Searching for seller with email: {email}")
    try:
        seller = db.query(models.Seller).filter(models.Seller.email == email).first()
        if not seller:
            print(f"❌ Seller not found: {email}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Seller not found in database",
                headers={"WWW-Authenticate": "Bearer"},
            )
        print(f"✅ Authenticated seller: ID={seller.id}, Email={seller.email}")
    except Exception as e:
        print(f"❌ Database error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch seller from database",
        )

    print("🟢 Authentication successful!")
    print("="*50 + "\n")
    return seller

from passlib.context import CryptContext


# Setup password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a plain password against a hashed one.
    Returns True if match.
    """
    return pwd_context.verify(plain_password, hashed_password)


def hash_token(token: str) -> str:
    """
    Hash a token (e.g., refresh token) before storing in DB.
    """
    return pwd_context.hash(token)


def verify_token(plain_token: str, hashed_token: str) -> bool:
    """
    Verify a submitted token against the stored hashed version.
    """
    return pwd_context.verify(plain_token, hashed_token)