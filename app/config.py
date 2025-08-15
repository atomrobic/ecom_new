import os
from dotenv import load_dotenv

load_dotenv()

ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 60))
REFRESH_TOKEN_EXPIRE_DAYS = int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", 30))
JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "supersecret")
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
