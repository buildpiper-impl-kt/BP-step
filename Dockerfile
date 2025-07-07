FROM python:3.11-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
 && rm -rf /var/lib/apt/lists/*

# Copy requirements before installing
COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

# Then copy the actual app
COPY build.py .

ENTRYPOINT ["python", "build.py"]

