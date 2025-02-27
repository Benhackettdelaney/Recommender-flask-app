import os

class Config:
    """Base configuration"""
    SECRET_KEY = os.getenv("SECRET_KEY", "your_secret_key_here")  # change this in production!
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "your_jwt_secret_key_here")  # for JWT authentication

class DevelopmentConfig(Config):
    """Configuration for development"""
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = "sqlite:///dev_database.db"

class ProductionConfig(Config):
    """Configuration for production"""
    DEBUG = False
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL", "sqlite:///prod_database.db")

class TestingConfig(Config):
    """Configuration for testing"""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = "sqlite:///test_database.db"
