# Use Python 3.11 slim image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy project files
COPY . .

# Collect static files (skip if fails - will be handled at runtime if needed)
RUN python manage.py collectstatic --noinput || echo "Collectstatic skipped"

# Expose port (Railway will override this)
EXPOSE 8000

# Start command - Railway will use Procfile if available, otherwise this CMD
CMD sh -c "gunicorn rag_chatbot.wsgi:application --bind 0.0.0.0:\${PORT:-8000} --workers 1 --threads 2 --timeout 180 --max-requests 100 --max-requests-jitter 20 --log-level info --access-logfile - --error-logfile -"

