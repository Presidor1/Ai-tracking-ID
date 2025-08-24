import os
import filetype
from datetime import datetime
from flask import (
    Blueprint, render_template, request, redirect,
    url_for, flash, send_from_directory
)
from flask_login import (
    login_user, logout_user, login_required,
    current_user
)
from werkzeug.utils import secure_filename
from PIL import Image
import pytesseract
import torch
from ultralytics import YOLO

from models import db, User, Analysis

routes = Blueprint("routes", __name__)

# Upload configuration
UPLOAD_FOLDER = os.path.join("static", "uploads")
RESULTS_FOLDER = os.path.join("static", "results")
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif"}

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(RESULTS_FOLDER, exist_ok=True)

# ==========================
# Lazy-loading YOLO
# ==========================
_yolo_model = None

def get_yolo_model():
    global _yolo_model
    if _yolo_model is None:
        _yolo_model = YOLO("yolov8n.pt")  # Small model for memory efficiency
    return _yolo_model

# ==========================
# Utility Functions
# ==========================
def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS

# ==========================
# Core Routes
# ==========================
@routes.route("/", methods=["GET"])
def index():
    return render_template("index.html", title="Home")

@routes.route("/upload", methods=["POST"])
@login_required
def upload_file():
    if "file" not in request.files:
        flash("❌ No file uploaded", "danger")
        return redirect(url_for("routes.index"))

    file = request.files["file"]
    if file.filename == "":
        flash("❌ Empty filename", "danger")
        return redirect(url_for("routes.index"))

    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        filepath = os.path.join(UPLOAD_FOLDER, filename)
        file.save(filepath)

        # Detect file type
        kind = filetype.guess(filepath)
        file_type = kind.mime if kind else "Unknown"

        # Image dimensions
        dimensions = None
        try:
            img = Image.open(filepath)
            dimensions = f"{img.width}x{img.height}"
        except Exception:
            pass

        # OCR
        extracted_text = ""
        try:
            img = Image.open(filepath)
            extracted_text = pytesseract.image_to_string(img)
        except Exception as e:
            extracted_text = f"OCR Error: {str(e)}"

        # YOLO Object Detection (lazy load)
        detected_objects = []
        preview_url = None
        try:
            model = get_yolo_model()
            with torch.no_grad():  # Save memory
                results = model(filepath)

            for r in results:
                for box in r.boxes:
                    cls_id = int(box.cls[0])
                    cls_name = model.names[cls_id]
                    detected_objects.append(cls_name)

            # Save annotated preview
            preview_filename = f"preview_{filename}"
            preview_path = os.path.join(RESULTS_FOLDER, preview_filename)
            results[0].save(filename=preview_path)
            preview_url = f"/{preview_path}"

        except Exception as e:
            detected_objects = [f"YOLO Error: {str(e)}"]

        # Save to DB
        analysis = Analysis(
            user_id=current_user.id,
            filename=filename,
            file_type=file_type,
            dimensions=dimensions,
            extracted_text=extracted_text.strip(),
            detected_objects=", ".join(set(detected_objects)) if detected_objects else "None",
            image_url=f"/{filepath}",
            preview_url=preview_url,
            lat=9.05785,
            lng=7.49508,
            created_at=datetime.utcnow()
        )
        db.session.add(analysis)
        db.session.commit()

        return redirect(url_for("routes.view_result", id=analysis.id))

    else:
        flash("❌ Invalid file type. Please upload an image.", "danger")
        return redirect(url_for("routes.index"))

# ==========================
# Result View
# ==========================
@routes.route("/results/<int:id>")
@login_required
def view_result(id):
    analysis = Analysis.query.get_or_404(id)
    if analysis.user_id != current_user.id:
        flash("🚫 Unauthorized access.", "danger")
        return redirect(url_for("routes.dashboard"))

    result = {
        "filename": analysis.filename,
        "type": analysis.file_type,
        "dimensions": analysis.dimensions,
        "text": analysis.extracted_text,
        "objects": analysis.detected_objects,
        "image_url": analysis.image_url,
        "preview_url": analysis.preview_url,
        "lat": analysis.lat,
        "lng": analysis.lng,
    }
    return render_template("results.html", result=result)

# ==========================
# Extra Pages & Auth (unchanged)
# ==========================
# ... Keep all dashboard, login, register, logout, forgot-password routes as they are

# ==========================
# Error Handlers
# ==========================
@routes.app_errorhandler(404)
def not_found(e):
    return render_template("error.html", title="404", message="Page not found"), 404

@routes.app_errorhandler(500)
def server_error(e):
    return render_template("error.html", title="500", message="Internal server error"), 500

# ==========================
# Static File Serving
# ==========================
@routes.route("/uploads/<path:filename>")
def uploaded_file(filename):
    return send_from_directory(UPLOAD_FOLDER, filename)

@routes.route("/results_files/<path:filename>")
def result_file(filename):
    return send_from_directory(RESULTS_FOLDER, filename)
