# Use official Python slim image
FROM python:3.11-slim

# Set environment to non-interactive to avoid hangs
ENV DEBIAN_FRONTEND=noninteractive

# Install system dependencies for Tesseract OCR and multiple languages
# Languages: English, Arabic, French, Spanish, German
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    tesseract-ocr \
    tesseract-ocr-osd \
    tesseract-ocr-eng \
    tesseract-ocr-ara \
    tesseract-ocr-fra \
    tesseract-ocr-spa \
    tesseract-ocr-deu \
    libtesseract-dev \
    libleptonica-dev \
    pkg-config \
    ca-certificates \
    wget \
    git && \
    rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Default command to run your app
CMD ["python", "app.py"]
