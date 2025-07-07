FROM python:3.11-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
 && rm -rf /var/lib/apt/lists/*

# RUN useradd -m -s /bin/bash buildpiper
# RUN mkdir -p /home/buildpiper /bp/workspace

# RUN chown -R buildpiper:buildpiper /home/buildpiper /bp/workspace

# USER buildpiper

# WORKDIR /home/buildpiper

# COPY --chown=buildpiper:buildpiper requirements.txt .
# COPY --chown=buildpiper:buildpiper build.py .

RUN pip install --no-cache-dir -r requirements.txt
ENTRYPOINT ["python", "/home/buildpiper/build.py"]
