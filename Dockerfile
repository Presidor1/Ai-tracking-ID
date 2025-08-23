# Use slim Python image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install only necessary system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    tesseract-ocr \
    libtesseract-dev \
    libjpeg-dev \
    zlib1g-dev \
    libpng-dev \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy dependency file
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Default command (adjust according to your app)
CMD ["python", "main.py"]
