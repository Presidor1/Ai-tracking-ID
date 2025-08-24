# === Base Image ===
FROM python:3.11-slim

# === System Dependencies ===
RUN apt-get update && apt-get install -y \
    tesseract-ocr \
    libtesseract-dev \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# === Set Working Directory ===
WORKDIR /app

# === Copy & Install Python Dependencies ===
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# === Copy Application Code ===
COPY . .

# === Ensure Upload Folders Exist ===
RUN mkdir -p static/uploads static/results

# === Set Environment Variables ===
ENV PYTHONUNBUFFERED=1 \
    FLASK_ENV=production \
    PORT=5000

# === Expose Port ===
EXPOSE 5000

# === Start the App with Gunicorn ===
CMD ["gunicorn", "--bind", "0.0.0.0:5000", \
     "--workers", "2", \
     "--threads", "2", \
     "--timeout", "120", \
     "app:app"]
