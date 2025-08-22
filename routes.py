import os
import filetype
from flask import Blueprint, render_template, request, redirect, url_for, flash
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

# Load YOLOv8 model
yolo_model = YOLO("yolov8n.pt")


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

        # === OCR (Text Extraction) ===
        extracted_text = ""
        try:
            img = Image.open(filepath)
            extracted_text = pytesseract.image_to_string(img)
        except Exception as e:
            extracted_text = f"OCR Error: {str(e)}"

        # === YOLO Object Detection ===
        detected_objects = []
        preview_path = None
        try:
            results = yolo_model(filepath)  # Run YOLO
            for r in results:
                for box in r.boxes:
                    cls_id = int(box.cls[0])
                    cls_name = yolo_model.names[cls_id]
                    detected_objects.append(cls_name)

            # Save annotated preview image
            preview_filename = f"preview_{filename}"
            preview_path = os.path.join(RESULTS_FOLDER, preview_filename)
            results[0].save(filename=preview_path)  # YOLO saves with boxes
            preview_url = f"/{preview_path}"  # URL for Flask template
        except Exception as e:
            detected_objects = [f"YOLO Error: {str(e)}"]
            preview_url = None

        # Package results
        result = {
            "filename": filename,
            "type": file_type,
            "dimensions": dimensions,
            "text": extracted_text.strip(),
            "objects": ", ".join(set(detected_objects)) if detected_objects else "None",
            "filepath": filepath,
            "preview_url": preview_url,
        }

        return render_template("results.html", result=result)

    else:
        flash("❌ Invalid file type. Please upload an image.")
        return redirect(url_for("routes.home"))
