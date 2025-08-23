from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()

# =========================
# User Model
# =========================
class User(UserMixin, db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(200), nullable=False)
    role = db.Column(db.String(20), default="user")  # "user" or "admin"
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    analyses = db.relationship("Analysis", back_populates="user", cascade="all, delete-orphan")
    audit_logs = db.relationship("AuditLog", back_populates="user", cascade="all, delete-orphan")

    # Password helpers
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def is_admin(self):
        return self.role == "admin"

    def __repr__(self):
        return f"<User {self.email} ({self.role})>"


# =========================
# Analysis Model
# =========================
class Analysis(db.Model):
    __tablename__ = "analysis"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    filename = db.Column(db.String(200), nullable=False)
    file_type = db.Column(db.String(50))
    dimensions = db.Column(db.String(50))
    extracted_text = db.Column(db.Text)
    detected_objects = db.Column(db.Text)
    image_url = db.Column(db.String(250))
    preview_url = db.Column(db.String(250))
    lat = db.Column(db.Float)   # Predicted latitude
    lng = db.Column(db.Float)   # Predicted longitude
    confidence = db.Column(db.Float, default=0.0)  # AI confidence score (0–1)
    method_used = db.Column(db.String(50))  # e.g., "YOLO+OCR+CLIP"
    status = db.Column(db.String(20), default="pending")  # pending/completed/failed
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationship
    user = db.relationship("User", back_populates="analyses")

    def __repr__(self):
        return f"<Analysis {self.filename} ({self.status}, {self.confidence:.2f})>"


# =========================
# Audit Log Model
# =========================
class AuditLog(db.Model):
    __tablename__ = "audit_logs"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    action = db.Column(db.String(255))  # e.g., "Uploaded file", "Viewed result"
    details = db.Column(db.Text)  # extra info (filename, analysis id, etc.)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationship
    user = db.relationship("User", back_populates="audit_logs")

    def __repr__(self):
        return f"<AuditLog User={self.user_id} Action={self.action}>"
