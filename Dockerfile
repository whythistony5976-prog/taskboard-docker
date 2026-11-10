FROM python:3.12-slim

# No .pyc files, and logs appear immediately in `docker logs`
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    DB_PATH=/data/tasks.db

WORKDIR /app

# Install dependencies first so Docker can cache this layer
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app.py .
COPY templates/ templates/
COPY static/ static/

# Run as a non-root user; /data holds the SQLite database
RUN useradd --create-home appuser && mkdir /data && chown appuser /data
USER appuser
VOLUME /data

EXPOSE 5000

HEALTHCHECK --interval=30s --timeout=3s \
  CMD python -c "import urllib.request as u; u.urlopen('http://localhost:5000/health')" || exit 1

# gunicorn is a production server; Flask's built-in one is for development only
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "2", "app:app"]
