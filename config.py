import os

class Config:
    # Secret key for forms (change in production)
    SECRET_KEY = os.getenv("SECRET_KEY", "dev_secret_key")

    # File upload settings
    UPLOAD_FOLDER = os.path.join(os.getcwd(), "uploads")
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16 MB

    # Database (later: PostgreSQL + PostGIS)
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL", "sqlite:///site.db")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
