# Use official Python slim image
FROM python:3.11-slim

# Set environment to non-interactive to avoid hangs
ENV DEBIAN_FRONTEND=noninteractive

# Install system dependencies for Tesseract OCR and multiple languages
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    tesseract-ocr=5.5.0-1+b1 \
    tesseract-ocr-osd \
    tesseract-ocr-eng \
    tesseract-ocr-ara \   # Arabic
    tesseract-ocr-fra \   # French
    tesseract-ocr-spa \   # Spanish
    tesseract-ocr-deu \   # German
    libtesseract-dev \
    libleptonica-dev \
    pkg-config \
    ca-certificates \
    wget \
    git \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Default command to run your app (adjust as needed)
CMD ["python", "app.py"]
