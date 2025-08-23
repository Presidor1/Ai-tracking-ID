#!/bin/bash
# Update system packages and install dependencies for Python packages
apt-get update
apt-get install -y build-essential python3-dev libpq-dev tesseract-ocr libleptonica-dev pkg-config

# Upgrade pip, setuptools, wheel
pip install --upgrade pip setuptools wheel

# Install Python dependencies
pip install -r requirements.txt
