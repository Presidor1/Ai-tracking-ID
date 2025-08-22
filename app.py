import os
from flask import Flask, render_template, request, jsonify
from werkzeug.utils import secure_filename
import filetype
from PIL import Image

# Initialize Flask
app = Flask(__name__)

# Configurations
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB upload limit

# Ensure upload folder exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

@app.route('/')
def index():
    return "✅ ID Tracking AI is running!"

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "Empty filename"}), 400

    filename = secure_filename(file.filename)
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(filepath)

    # Detect file type
    kind = filetype.guess(filepath)
    if not kind:
        return jsonify({"error": "Unsupported file type"}), 400

    # If it's an image, try to open with Pillow
    if "image" in kind.mime:
        try:
            img = Image.open(filepath)
            width, height = img.size
            return jsonify({
                "filename": filename,
                "type": kind.mime,
                "dimensions": f"{width}x{height}"
            })
        except Exception as e:
            return jsonify({"error": str(e)}), 500

    return jsonify({"filename": filename, "type": kind.mime})

# Run locally
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
