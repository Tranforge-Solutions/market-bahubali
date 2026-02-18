FROM python:3.12-slim

# Set working directory
WORKDIR /app

# Install system dependencies for psycopg2, matplotlib, etc.
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code
COPY . .

# Expose port for the API
EXPOSE 8000

# Default: run the FastAPI API server
# (Procfile overrides this for multi-process Railway deployment)
CMD ["uvicorn", "src.api:app", "--host", "0.0.0.0", "--port", "8000"]
