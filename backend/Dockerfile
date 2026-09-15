FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Install Tesseract OCR
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        tesseract-ocr \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .

RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# Copy Django project
COPY . .

# Collect static files
RUN python manage.py collectstatic --no-input

EXPOSE 10000

CMD ["sh", "-c", "python manage.py migrate && gunicorn config.wsgi:application --workers 1 --threads 4 --timeout 120 --bind 0.0.0.0:${PORT:-10000}"]