import os
import filetype
from flask import Blueprint, render_template, request, redirect, url_for, flash
from werkzeug.utils import secure_filename
from PIL import Image

routes = Blueprint("routes", __name__)

# Upload configuration
UPLOAD_FOLDER = os.path.join("static", "uploads")
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif"}

# Ensure upload folder exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


def allowed_file(filename):
    """Check allowed file extensions."""
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


@routes.route("/", methods=["GET"])
def home():
    """Landing page with upload form."""
    return render_template("index.html")


@routes.route("/upload", methods=["POST"])
def upload_file():
    """Handle file uploads and redirect to results page."""
    if "file" not in request.files:
        flash("❌ No file uploaded")
        return redirect(url_for("routes.home"))

    file = request.files["file"]

    if file.filename == "":
        flash("❌ Empty filename")
        return redirect(url_for("routes.home"))

    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        filepath = os.path.join(UPLOAD_FOLDER, filename)
        file.save(filepath)

        # Detect file type
        kind = filetype.guess(filepath)
        file_type = kind.mime if kind else "Unknown"

        # Extract image dimensions
        dimensions = None
        try:
            img = Image.open(filepath)
            width, height = img.size
            dimensions = f"{width}x{height}"
        except Exception:
            pass

        # Placeholder for OCR / Object detection
        extracted_text = "Detected text placeholder (OCR to be added)"
        detected_objects = "Objects placeholder (YOLO/ML model to be added)"

        # Package results
        result = {
            "filename": filename,
            "type": file_type,
            "dimensions": dimensions,
            "text": extracted_text,
            "objects": detected_objects,
            "filepath": filepath,
        }

        return render_template("results.html", result=result)

    else:
        flash("❌ Invalid file type. Please upload an image.")
        return redirect(url_for("routes.home"))
