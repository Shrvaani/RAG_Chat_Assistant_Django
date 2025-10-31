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

# Collect static files
RUN python manage.py collectstatic --noinput || true

# Expose port
EXPOSE $PORT

# Create startup script with error handling
RUN echo '#!/bin/bash\nset -e\necho "Running migrations..."\npython manage.py migrate --noinput || echo "Migration failed, continuing..."\necho "Starting Gunicorn..."\nexec gunicorn rag_chatbot.wsgi:application --bind 0.0.0.0:${PORT:-8000} --timeout 120 --workers 2 --access-logfile - --error-logfile -' > /app/start.sh && chmod +x /app/start.sh

# Run migrations and start server
CMD ["/app/start.sh"]

