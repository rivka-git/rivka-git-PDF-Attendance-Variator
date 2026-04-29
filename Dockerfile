FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    TESSDATA_PREFIX=/usr/share/tesseract-ocr/5/tessdata

WORKDIR /app

# System dependencies required by the assignment:
# - Tesseract + Hebrew language package
# - Poppler tools for PDF rasterization
RUN apt-get update && apt-get install -y --no-install-recommends \
    ca-certificates \
    tesseract-ocr \
    tesseract-ocr-heb \
    poppler-utils \
    libglib2.0-0 \
    libsm6 \
    libxrender1 \
    libxext6 \
    && update-ca-certificates \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt ./
RUN pip install \
    --trusted-host pypi.org \
    --trusted-host pypi.python.org \
    --trusted-host files.pythonhosted.org \
    -r requirements.txt

COPY attendance_report ./attendance_report
COPY main.py ./main.py

ENTRYPOINT ["python", "main.py"]
