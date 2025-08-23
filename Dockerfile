# ----------------------------
# Use slim Python image
# ----------------------------
FROM python:3.11-slim

# ----------------------------
# Set working directory
# ----------------------------
WORKDIR /app

# ----------------------------
# Install system dependencies
# ----------------------------
RUN apt-get update && apt-get install -y --no-install-recommends \
    tesseract-ocr \
    libtesseract-dev \
    libjpeg-dev \
    zlib1g-dev \
    libpng-dev \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# ----------------------------
# Copy and install Python dependencies
# ----------------------------
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# ----------------------------
# Copy application code
# ----------------------------
COPY . .

# ----------------------------
# Expose port (Flask default)
# ----------------------------
EXPOSE 5000

# ----------------------------
# Use gunicorn for production
# ----------------------------
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "app:app", "--workers", "3", "--threads", "2", "--timeout", "120"]
