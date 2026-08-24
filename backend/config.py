import os
from dotenv import load_dotenv

# Load environment variables from .env file if present
load_dotenv()


class Config:
    """Base configuration."""
    MONGODB_URI = os.environ.get('MONGODB_URI')
    MONGODB_DATABASE = os.environ.get('MONGODB_DATABASE', 'secondspin')
    SECRET_KEY = os.environ.get('SECRET_KEY', 'default-secret-key-for-dev')
    FLASK_ENV = os.environ.get('FLASK_ENV', 'development')
    
    # CORS Configuration
    CORS_ORIGINS = os.environ.get('CORS_ORIGINS', '*').split(',')

    # JWT Configuration
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY', SECRET_KEY)
    JWT_EXPIRES_IN = int(os.environ.get('JWT_EXPIRES_IN', 86400)) # Default 24 hours
    
    # Verification Configuration
    ALLOWED_EMAIL_DOMAINS = os.environ.get('ALLOWED_EMAIL_DOMAINS', 'student.college.edu,college.edu').split(',')
