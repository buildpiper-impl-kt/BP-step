FROM python:3.10-slim


WORKDIR /app


COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt


COPY app.py .


ENTRYPOINT ["python3", "app.py"]

#docker run --rm -v $(pwd):/data -e INPUT_FILE=/data/ms_details.txt aayush808/txt-csv-to-xlsx:mac-0.2
