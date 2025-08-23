import os
import filetype
from flask import (
    Blueprint, render_template, request, redirect,
    url_for, flash
)
from flask_login import (
    login_user, logout_user, login_required,
    current_user, UserMixin
)
from werkzeug.utils import secure_filename
from PIL import Image
import pytesseract
from ultralytics import YOLO

routes = Blueprint("routes", __name__)

# Upload configuration
UPLOAD_FOLDER = os.path.join("static", "uploads")
RESULTS_FOLDER = os.path.join("static", "results")
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif"}

# Ensure folders exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(RESULTS_FOLDER, exist_ok=True)

# Load YOLOv8 model (tiny version for speed)
yolo_model = YOLO("yolov8n.pt")

# ==========================
# Utility Functions
# ==========================
def allowed_file(filename):
    """Check allowed file extensions."""
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


# ==========================
# Core Routes
# ==========================
@routes.route("/", methods=["GET"])
def index():
    """Landing page with upload form."""
    return render_template("index.html", title="Home")


@routes.route("/upload", methods=["POST"])
def upload_file():
    """Handle file uploads and run analysis pipeline."""
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
            width, height = img.size
            dimensions = f"{width}x{height}"
        except Exception:
            pass

        # === OCR (Text Extraction) ===
        extracted_text = ""
        try:
            img = Image.open(filepath)
            extracted_text = pytesseract.image_to_string(img)
        except Exception as e:
            extracted_text = f"OCR Error: {str(e)}"

        # === YOLO Object Detection ===
        detected_objects = []
        preview_url = None
        try:
            results = yolo_model(filepath)  # Run YOLO
            for r in results:
                for box in r.boxes:
                    cls_id = int(box.cls[0])
                    cls_name = yolo_model.names[cls_id]
                    detected_objects.append(cls_name)

            # Save annotated preview
            preview_filename = f"preview_{filename}"
            preview_path = os.path.join(RESULTS_FOLDER, preview_filename)
            results[0].save(filename=preview_path)
            preview_url = f"/{preview_path}"
        except Exception as e:
            detected_objects = [f"YOLO Error: {str(e)}"]

        # Package results
        result = {
            "filename": filename,
            "type": file_type,
            "dimensions": dimensions,
            "text": extracted_text.strip(),
            "objects": ", ".join(set(detected_objects)) if detected_objects else "None",
            "image_url": f"/{filepath}",
            "preview_url": preview_url,
            "lat": 9.05785,   # Default coords (AI inference will replace later)
            "lng": 7.49508
        }

        return render_template("results.html", result=result)

    else:
        flash("❌ Invalid file type. Please upload an image.", "danger")
        return redirect(url_for("routes.index"))


# ==========================
# Extra Pages
# ==========================
@routes.route("/dashboard")
@login_required
def dashboard():
    return render_template("dashboard.html", title="Dashboard")


@routes.route("/about")
def about():
    return render_template("about.html", title="About")


# ==========================
# Authentication (basic stubs)
# ==========================
@routes.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")

        # Placeholder: replace with DB check
        if email == "test@test.com" and password == "password":
            fake_user = UserMixin()
            fake_user.id = 1
            login_user(fake_user)
            flash("✅ Logged in successfully.", "success")
            return redirect(url_for("routes.dashboard"))
        else:
            flash("❌ Invalid credentials.", "danger")

    return render_template("login.html", title="Login")


@routes.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")

        # Placeholder: save to DB later
        flash("⚠️ Registration system not implemented yet.", "warning")
        return redirect(url_for("routes.register"))

    return render_template("register.html", title="Register")


@routes.route("/logout")
@login_required
def logout():
    logout_user()
    flash("✅ Logged out successfully.", "info")
    return redirect(url_for("routes.index"))


@routes.route("/forgot-password", methods=["GET", "POST"])
def forgot_password():
    if request.method == "POST":
        email = request.form.get("email")
        flash(f"📧 If {email} exists, a reset link was sent.", "info")
        return redirect(url_for("routes.login"))
    return render_template("forgot_password.html", title="Forgot Password")
