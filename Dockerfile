FROM python:3.10-slim

LABEL maintainer="Ghana Legal Scraper <info@glis.gh>"
LABEL description="Ghana Supreme Court Legal Data Scraper"

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    libxml2 \
    libxslt1.1 \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create data directories
RUN mkdir -p data/raw data/processed data/logs data/stats

# Expose API port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8000/health')"

# Default command: start API
CMD ["python", "main.py", "api", "--host", "0.0.0.0", "--port", "8000"]
