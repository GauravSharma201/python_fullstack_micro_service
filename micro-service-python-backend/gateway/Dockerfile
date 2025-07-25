FROM python:3.11-slim

WORKDIR /app

# Install system dependencies (if needed)
RUN apt-get update && apt-get install -y curl gcc && rm -rf /var/lib/apt/lists/*

# Install Python dependencies for THIS service
COPY gateway/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy shared code
COPY shared ./shared

# Copy service code into /app
COPY gateway/. .

ENV PYTHONPATH="${PYTHONPATH}:/app/shared"

# The following three lines can/should be customized for each service:
# Replace 800X with the correct port for this service
EXPOSE 8000  

HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

CMD ["python", "main.py"]
