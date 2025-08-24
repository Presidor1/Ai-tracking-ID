# ===== Base Image =====
FROM python:3.11-slim

# ===== Environment Variables =====
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV LANG=C.UTF-8
ENV LC_ALL=C.UTF-8

# ===== System Dependencies =====
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    tesseract-ocr \
    libtesseract-dev \
    libgl1-mesa-glx \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# ===== Working Directory =====
WORKDIR /app

# ===== Copy & Install Python Dependencies =====
COPY requirements.txt .
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

# ===== Copy App Code =====
COPY . .

# ===== Expose Port =====
EXPOSE 5000

# ===== Default Command =====
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "wsgi:app"]
