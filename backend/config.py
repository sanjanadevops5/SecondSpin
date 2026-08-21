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
