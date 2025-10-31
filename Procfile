web: (python manage.py collectstatic --noinput || true); gunicorn rag_chatbot.wsgi:application --bind 0.0.0.0:$PORT --workers 1 --threads 2 --timeout 180 --max-requests 100 --max-requests-jitter 20 --log-level info --access-logfile - --error-logfile -

