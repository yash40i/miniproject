FROM python:3.11-slim

WORKDIR /app

ENV PIP_NO_CACHE_DIR=1
ENV PYTHONUNBUFFERED=1

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    git \
    && rm -rf /var/lib/apt/lists/*

# Copy the entire project to avoid context path issues
COPY . /app/repo/

# Move the backend files to /app
RUN if [ -d "/app/repo/backend" ]; then \
      cp -r /app/repo/backend/* /app/; \
    else \
      cp -r /app/repo/* /app/; \
    fi && \
    rm -rf /app/repo

# Install PyTorch CPU version first to prevent downloading the massive 2.5GB CUDA version
RUN pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu

# Install core server dependencies first
RUN pip install \
    fastapi \
    "uvicorn[standard]" \
    python-multipart \
    requests \
    "sqlalchemy>=2.0.0" \
    "python-jose[cryptography]>=3.3.0" \
    "passlib[bcrypt]>=1.7.4" \
    "PyPDF2>=3.0.0" \
    "aiofiles>=23.0.0"

# Install all remaining dependencies from requirements.txt
RUN pip install -r requirements.txt

# Download spaCy model
RUN python -m spacy download en_core_web_sm

# Download NLTK data
RUN python -c "import nltk; nltk.download('punkt'); nltk.download('punkt_tab'); nltk.download('stopwords')"

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
  CMD python -c "import requests; requests.get('http://localhost:8000/health')" || exit 1

# Run application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
