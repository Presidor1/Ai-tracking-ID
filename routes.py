import os
import uuid
from datetime import datetime
from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, current_app, send_from_directory
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.utils import secure_filename
import pytesseract
from ultralytics import YOLO
import cv2

from models import db, User, Analysis, AuditLog

# =========================
# Blueprint
# =========================
routes = Blueprint("routes", __name__)

# Load YOLO model once (improves performance)
yolo_model = YOLO("yolov8n.pt")  # can be swapped for custom model


# =========================
# Helpers
# =========================
def allowed_file(filename):
    ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg"}
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


def log_action(user_id, action, details=""):
    """Save an audit log entry"""
    audit = AuditLog(user_id=user_id, action=action, details=details)
    db.session.add(audit)
    db.session.commit()


# =========================
# Routes
# =========================
@routes.route("/")
def index():
    return render_template("index.html", title="Home")


@routes.route("/about")
def about():
    return render_template("about.html", title="About")


@routes.route("/dashboard")
@login_required
def dashboard():
    history = Analysis.query.filter_by(user_id=current_user.id).order_by(Analysis.created_at.desc()).all()
    return render_template("dashboard.html", title="Dashboard", history=history)


@routes.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        name = request.form["name"]
        email = request.form["email"]
        password = request.form["password"]

        if User.query.filter_by(email=email).first():
            flash("❌ Email already registered.", "danger")
            return redirect(url_for("routes.register"))

        user = User(name=name, email=email)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        flash("✅ Registration successful. Please login.", "success")
        return redirect(url_for("routes.login"))

    return render_template("register.html", title="Register")


@routes.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        user = User.query.filter_by(email=email).first()
        if user and user.check_password(password):
            login_user(user)
            flash("✅ Login successful!", "success")
            log_action(user.id, "Login", f"User {email} logged in")
            return redirect(url_for("routes.dashboard"))
        else:
            flash("❌ Invalid email or password.", "danger")

    return render_template("login.html", title="Login")


@routes.route("/logout")
@login_required
def logout():
    log_action(current_user.id, "Logout", "User logged out")
    logout_user()
    flash("✅ Logged out successfully.", "info")
    return redirect(url_for("routes.index"))


@routes.route("/upload", methods=["POST"])
@login_required
def upload():
    if "file" not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    file = request.files["file"]

    if file.filename == "":
        return jsonify({"error": "Empty filename"}), 400

    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        unique_id = str(uuid.uuid4())
        save_name = f"{unique_id}_{filename}"
        save_path = os.path.join(current_app.static_folder, "uploads", save_name)
        file.save(save_path)

        # Run OCR with pytesseract
        try:
            image = cv2.imread(save_path)
            text = pytesseract.image_to_string(image)
        except Exception as e:
            text = f"OCR Error: {e}"

        # Run YOLO detection
        try:
            results = yolo_model(save_path)
            detected_objects = [result.names[int(cls)] for r in results for cls in r.boxes.cls]
        except Exception as e:
            detected_objects = [f"YOLO Error: {e}"]

        # Save analysis to DB
        analysis = Analysis(
            user_id=current_user.id,
            filename=save_name,
            file_type=file.mimetype,
            dimensions=f"{image.shape[1]}x{image.shape[0]}" if image is not None else "N/A",
            extracted_text=text,
            detected_objects=", ".join(detected_objects),
            image_url=f"/static/uploads/{save_name}",
            preview_url=f"/static/uploads/{save_name}",
            status="completed",
            confidence=0.85,  # fake placeholder, could parse from YOLO results
            method_used="YOLO+OCR",
        )
        db.session.add(analysis)
        db.session.commit()

        log_action(current_user.id, "Uploaded file", f"File={save_name}")

        return jsonify({
            "message": "✅ File uploaded and analyzed",
            "filename": save_name,
            "text": text,
            "objects": detected_objects,
            "image_url": analysis.image_url
        })

    return jsonify({"error": "Invalid file format"}), 400


@routes.route("/result/<int:id>")
@login_required
def view_result(id):
    analysis = Analysis.query.get_or_404(id)
    if analysis.user_id != current_user.id and not current_user.is_admin():
        flash("❌ Unauthorized access.", "danger")
        return redirect(url_for("routes.dashboard"))

    return render_template("result.html", title="Analysis Result", analysis=analysis)
