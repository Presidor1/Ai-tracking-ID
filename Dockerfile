# Use slim Python image
FROM python:3.11-slim

# Install system dependencies for Tesseract and OpenCV
RUN apt-get update && apt-get install -y \
    tesseract-ocr \
    libtesseract-dev \
    libgl1-mesa-glx \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the Flask app
COPY . .

# Expose port
EXPOSE 5000

# Start Gunicorn with 1 worker and increased timeout
CMD ["gunicorn", "-w", "1", "-b", "0.0.0.0:5000", "app:app", "--timeout", "120"]
