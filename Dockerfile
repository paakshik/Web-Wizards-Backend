# ============================================================
# Dockerfile — Production-ready FastAPI image for Render
# ============================================================

# Use official slim Python image (smaller size = faster deploys)
FROM python:3.11-slim

# Set working directory inside the container
WORKDIR /app

# --- Install system dependencies ---
# libpq-dev is needed for psycopg2 (PostgreSQL driver)
RUN apt-get update && apt-get install -y \
    libpq-dev \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# --- Install Python dependencies ---
# Copy requirements first (Docker caches this layer — speeds up rebuilds)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# --- Copy application source code ---
COPY . .

# Create runtime directories (Render's filesystem is ephemeral, but needed for startup)
RUN mkdir -p user_data/uploads user_data/resolutions logs

# Expose the port FastAPI will run on
EXPOSE 8000

# --- Start command ---
# --host 0.0.0.0 makes it accessible outside the container
# --workers 2 handles multiple requests concurrently (adjust based on plan)
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "2"]