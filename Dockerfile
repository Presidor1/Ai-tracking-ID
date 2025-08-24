# ===== Stage 1: Builder Stage =====
FROM python:3.11-slim AS builder

# ===== Install Build Dependencies =====
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    git \
    tesseract-ocr \
    libtesseract-dev \
    libgl1 \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# ===== Set Working Directory =====
WORKDIR /app

# ===== Copy Only Requirements First for Caching =====
COPY requirements.txt .

# ===== Install CPU-only PyTorch explicitly =====
RUN pip install --upgrade pip \
    && pip install torch==2.3.1+cpu torchvision==0.18.1+cpu torchaudio==2.3.1+cpu --extra-index-url https://download.pytorch.org/whl/cpu \
    && pip install --no-cache-dir --prefix=/install -r requirements.txt

# ===== Stage 2: Runtime Stage =====
FROM python:3.11-slim

# ===== Runtime System Dependencies =====
RUN apt-get update && apt-get install -y --no-install-recommends \
    tesseract-ocr \
    libtesseract-dev \
    libgl1 \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# ===== Set Working Directory =====
WORKDIR /app

# ===== Copy Python Packages from Builder =====
COPY --from=builder /install /usr/local

# ===== Copy Application Code =====
COPY . .

# ===== Expose Port =====
EXPOSE 5000

# ===== Run Gunicorn with Multiple Workers =====
CMD ["gunicorn", "--workers", "4", "--bind", "0.0.0.0:5000", "wsgi:app"]
