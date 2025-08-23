import os
from datetime import timedelta

class Config:
    # === Security ===
    SECRET_KEY = os.getenv("SECRET_KEY", "dev_secret_key")  # ⚠️ Change in production
    WTF_CSRF_ENABLED = True  # Enable CSRF protection for forms

    # === File Uploads ===
    BASE_DIR = os.path.abspath(os.path.dirname(__file__))
    UPLOAD_FOLDER = os.path.join(BASE_DIR, "static", "uploads")
    RESULTS_FOLDER = os.path.join(BASE_DIR, "static", "results")
    LOGS_FOLDER = os.path.join(BASE_DIR, "logs")
    
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16 MB upload limit
    ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif"}

    # Ensure required folders exist
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    os.makedirs(RESULTS_FOLDER, exist_ok=True)
    os.makedirs(LOGS_FOLDER, exist_ok=True)

    # === Database ===
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL", "sqlite:///site.db")
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # === Authentication / Sessions ===
    REMEMBER_COOKIE_DURATION = timedelta(days=7)  # "Remember me" session time
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SECURE = os.getenv("SESSION_COOKIE_SECURE", "False").lower() == "true"  # ✅ Secure in production
    SESSION_COOKIE_SAMESITE = "Lax"

    # === Maps / Geolocation Defaults ===
    DEFAULT_LAT = float(os.getenv("DEFAULT_LAT", 9.05785))  # Abuja, Nigeria
    DEFAULT_LNG = float(os.getenv("DEFAULT_LNG", 7.49508))
    DEFAULT_ZOOM = int(os.getenv("DEFAULT_ZOOM", 6))

    # === AI / Models ===
    YOLO_MODEL_PATH = os.getenv("YOLO_MODEL_PATH", "yolov8n.pt")
    OCR_ENGINE = os.getenv("OCR_ENGINE", "pytesseract")  # Switchable OCR engine
    ENABLE_YOLO = os.getenv("ENABLE_YOLO", "true").lower() == "true"
    ENABLE_OCR = os.getenv("ENABLE_OCR", "true").lower() == "true"

    # === Logging ===
    LOG_FILE = os.path.join(LOGS_FOLDER, "app.log")
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
