# docker/Dockerfile (lightweight build)
FROM python:3.11-slim

WORKDIR /app

# Keep installs minimal to avoid heavy compilation in the image
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Use a small, faster requirements file for container builds
COPY requirements.docker.txt /app/requirements.docker.txt
RUN pip install --no-cache-dir -r /app/requirements.docker.txt

# Copy application code
COPY . /app

EXPOSE 8000

# Default command to run the app
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
