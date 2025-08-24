# ===== Base Image =====
FROM python:3.11-slim

# ===== System Dependencies =====
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    tesseract-ocr \
    libtesseract-dev \
    libgl1 \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# ===== Set Working Directory =====
WORKDIR /app

# ===== Copy and Install Python Dependencies =====
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# ===== Copy Application Code =====
COPY . .

# ===== Expose Port =====
EXPOSE 5000

# ===== Command to Run Application =====
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "wsgi:app"]
