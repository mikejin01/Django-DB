release: python manage.py migrate && python manage.py createsuperuser --noinput --username admin --email admin@example.com --password sf12345
web: gunicorn core.wsgi:application
