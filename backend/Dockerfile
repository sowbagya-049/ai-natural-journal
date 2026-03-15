# ── Backend Dockerfile ────────────────────────────────────────────────────────
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install dependencies first (layer-cached)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Expose FastAPI port
EXPOSE 8000

# Run uvicorn
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
