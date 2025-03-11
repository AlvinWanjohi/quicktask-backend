import os
from dotenv import load_dotenv


load_dotenv()

class Config:
    """Application Configuration"""

    
    SECRET_KEY = os.getenv("SECRET_KEY", "default_secret_key")

    
    DB_USER = os.getenv("DB_USER")
    DB_PASSWORD = os.getenv("DB_PASSWORD")
    DB_HOST = os.getenv("DB_HOST")
    DB_PORT = os.getenv("DB_PORT", "5432") 
    DB_NAME = os.getenv("DB_NAME")

    
    if not all([DB_USER, DB_PASSWORD, DB_HOST, DB_NAME]):
        missing_vars = [var for var in ["DB_USER", "DB_PASSWORD", "DB_HOST", "DB_NAME"] if not os.getenv(var)]
        raise ValueError(f"Missing required database environment variables: {', '.join(missing_vars)}")

    
    SQLALCHEMY_DATABASE_URI = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY")

    
    if not JWT_SECRET_KEY:
        raise ValueError("Missing JWT_SECRET_KEY in environment variables.")

