"""
WSGI config for rag_chatbot project.
"""
import os
import sys

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'rag_chatbot.settings')

try:
    from django.core.wsgi import get_wsgi_application
    application = get_wsgi_application()
except Exception as e:
    # Log the error so we can see it in Railway logs
    print(f"Error loading WSGI application: {e}", file=sys.stderr)
    import traceback
    traceback.print_exc(file=sys.stderr)
    raise

# Vercel requires this
app = application

