FROM python:3.11-slim
WORKDIR /app
RUN apt-get update && apt-get install -y \
    libzbar0 \
    libzbar-dev \
    && rm -rf /var/lib/apt/lists/*
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY start_server.py .
COPY config/ config/
EXPOSE 7860
CMD ["python", "start_server.py"]
