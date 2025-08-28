import os
import io
from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from datetime import datetime
from models import db, Analysis, AuditLog
import pytesseract
from PIL import Image

# Blueprint
routes = Blueprint("routes", __name__)

# =====================
# Helper Functions
# =====================

def log_action(user_id, action, details=""):
    """Save user actions to audit logs"""
    log = AuditLog(user_id=user_id, action=action, details=details)
    db.session.add(log)
    db.session.commit()

def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in {"png", "jpg", "jpeg"}


# =====================
# Routes
# =====================

@routes.route("/ping", methods=["GET"])
def ping():
    """Health check endpoint"""
    return jsonify({"status": "ok", "time": datetime.utcnow().isoformat()}), 200


@routes.route("/upload", methods=["POST"])
@login_required
def upload_file():
    """Handle file uploads for analysis"""
    if "file" not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    file = request.files["file"]
    if file.filename == "":
        return jsonify({"error": "Empty filename"}), 400

    if not allowed_file(file.filename):
        return jsonify({"error": "Invalid file type"}), 400

    filename = secure_filename(file.filename)
    file_path = os.path.join("uploads", filename)
    os.makedirs("uploads", exist_ok=True)
    file.save(file_path)

    # Create analysis record
    analysis = Analysis(
        user_id=current_user.id,
        filename=filename,
        file_type=filename.rsplit(".", 1)[1].lower(),
        status="pending"
    )
    db.session.add(analysis)
    db.session.commit()

    log_action(current_user.id, "Uploaded file", f"File: {filename}")

    return jsonify({"message": "File uploaded successfully", "analysis_id": analysis.id})


@routes.route("/analyze/<int:analysis_id>", methods=["POST"])
@login_required
def analyze_file(analysis_id):
    """Run OCR + YOLO detection on uploaded file"""
    analysis = Analysis.query.get_or_404(analysis_id)
    file_path = os.path.join("uploads", analysis.filename)

    try:
        # OCR
        img = Image.open(file_path)
        extracted_text = pytesseract.image_to_string(img)

        # YOLO (lazy import – avoids startup slowdown)
        from ultralytics import YOLO
        model = YOLO("yolov8n.pt")  # use nano model for speed
        results = model(file_path)

        detected_objects = [r.names[int(cls)] for r in results for cls in r.boxes.cls]

        # Save results
        analysis.extracted_text = extracted_text.strip()
        analysis.detected_objects = ", ".join(set(detected_objects))
        analysis.status = "completed"
        analysis.confidence = float(results[0].boxes.conf.mean()) if results[0].boxes.conf.numel() > 0 else 0.0
        analysis.method_used = "YOLOv8+OCR"
        db.session.commit()

        log_action(current_user.id, "Analyzed file", f"Analysis ID: {analysis.id}")

        return jsonify({
            "message": "Analysis completed",
            "text": analysis.extracted_text,
            "objects": analysis.detected_objects,
            "confidence": analysis.confidence
        })

    except Exception as e:
        analysis.status = "failed"
        db.session.commit()
        log_action(current_user.id, "Analysis failed", str(e))
        return jsonify({"error": str(e)}), 500


@routes.route("/results/<int:analysis_id>", methods=["GET"])
@login_required
def get_results(analysis_id):
    """Fetch results of analysis"""
    analysis = Analysis.query.get_or_404(analysis_id)

    return jsonify({
        "id": analysis.id,
        "filename": analysis.filename,
        "text": analysis.extracted_text,
        "objects": analysis.detected_objects,
        "confidence": analysis.confidence,
        "status": analysis.status,
        "created_at": analysis.created_at.isoformat()
    })
