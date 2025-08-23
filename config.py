import os
from datetime import timedelta

class Config:
    # === Security ===
    SECRET_KEY = os.getenv("SECRET_KEY", "dev_secret_key")  # Change in production!
    
    # === File Uploads ===
    BASE_DIR = os.path.abspath(os.path.dirname(__file__))
    UPLOAD_FOLDER = os.path.join(BASE_DIR, "static", "uploads")
    RESULTS_FOLDER = os.path.join(BASE_DIR, "static", "results")
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16 MB upload limit
    ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif"}

    # === Database ===
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL", "sqlite:///site.db")
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # === Authentication / Sessions ===
    REMEMBER_COOKIE_DURATION = timedelta(days=7)  # "Remember me" session time
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SECURE = False  # Set True in production (HTTPS)
    SESSION_COOKIE_SAMESITE = "Lax"

    # === Maps / Geolocation ===
    DEFAULT_LAT = float(os.getenv("DEFAULT_LAT", 9.05785))  # Abuja, Nigeria
    DEFAULT_LNG = float(os.getenv("DEFAULT_LNG", 7.49508))
    DEFAULT_ZOOM = int(os.getenv("DEFAULT_ZOOM", 6))

    # === AI / Models ===
    YOLO_MODEL_PATH = os.getenv("YOLO_MODEL_PATH", "yolov8n.pt")
    OCR_ENGINE = os.getenv("OCR_ENGINE", "pytesseract")  # future switchable engines

    # === Logging ===
    LOG_FILE = os.path.join(BASE_DIR, "logs", "app.log")
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
