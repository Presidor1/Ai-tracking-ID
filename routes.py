import os
from flask import Blueprint, request, jsonify
from werkzeug.utils import secure_filename
from utils import extract_exif, detect_file_type, run_ocr
from config import Config

routes = Blueprint("routes", __name__)

@routes.route("/upload", methods=["POST"])
def upload_file():
    if "file" not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    file = request.files["file"]
    if file.filename == "":
        return jsonify({"error": "Empty filename"}), 400

    filename = secure_filename(file.filename)
    filepath = os.path.join(Config.UPLOAD_FOLDER, filename)
    os.makedirs(Config.UPLOAD_FOLDER, exist_ok=True)
    file.save(filepath)

    # Run analysis
    file_type = detect_file_type(filepath)
    exif = extract_exif(filepath)
    ocr_text = run_ocr(filepath) if "image" in file_type else ""

    return jsonify({
        "filename": filename,
        "type": file_type,
        "exif": exif,
        "ocr_text": ocr_text
    })
