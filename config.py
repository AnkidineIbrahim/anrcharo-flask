import os
from datetime import timedelta

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-secret-change-in-prod')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16 MB max upload

    # Railway fournit DATABASE_URL automatiquement
    DATABASE_URL = os.environ.get('DATABASE_URL', 'sqlite:///anrcharo.db')
    # Railway utilise postgres:// mais SQLAlchemy requiert postgresql://
    if DATABASE_URL.startswith('postgres://'):
        DATABASE_URL = DATABASE_URL.replace('postgres://', 'postgresql://', 1)
    SQLALCHEMY_DATABASE_URI = DATABASE_URL

    # Sessions
    PERMANENT_SESSION_LIFETIME = timedelta(hours=8)
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'

    # Upload (local dev)
    UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), 'app', 'static', 'images')
    ALLOWED_EXTENSIONS = {'jpg', 'jpeg', 'png', 'webp'}

    # Cloudinary (optionnel — pour Railway production)
    CLOUDINARY_CLOUD_NAME = os.environ.get('CLOUDINARY_CLOUD_NAME')
    CLOUDINARY_API_KEY    = os.environ.get('CLOUDINARY_API_KEY')
    CLOUDINARY_API_SECRET = os.environ.get('CLOUDINARY_API_SECRET')
    USE_CLOUDINARY = bool(CLOUDINARY_CLOUD_NAME)

class DevelopmentConfig(Config):
    DEBUG = True

class ProductionConfig(Config):
    DEBUG = False
    SESSION_COOKIE_SECURE = True

config = {
    'development': DevelopmentConfig,
    'production':  ProductionConfig,
    'default':     DevelopmentConfig,
}
