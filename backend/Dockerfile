FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    git \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements.txt
# Note: build context is the repo root, so paths start from root
COPY requirements.txt .

# Install all Python dependencies from requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Also install FastAPI, uvicorn, and other server dependencies
RUN pip install --no-cache-dir \
    fastapi \
    uvicorn[standard] \
    python-multipart \
    requests \
    sqlalchemy>=2.0.0 \
    "python-jose[cryptography]>=3.3.0" \
    "passlib[bcrypt]>=1.7.4" \
    PyPDF2>=3.0.0 \
    aiofiles>=23.0.0

# Download spaCy model
RUN python -m spacy download en_core_web_sm

# Download NLTK data
RUN python -c "import nltk; nltk.download('punkt'); nltk.download('stopwords')"

# Copy application code
COPY src /app/src
COPY main.py /app/main.py

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
  CMD python -c "import requests; requests.get('http://localhost:8000/health')" || exit 1

# Run application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]

