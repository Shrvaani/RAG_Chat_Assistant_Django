web: (python manage.py collectstatic --noinput || true); gunicorn rag_chatbot.wsgi:application --bind 0.0.0.0:$PORT --timeout 120 --access-logfile - --error-logfile -

