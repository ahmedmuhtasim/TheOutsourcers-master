release: python manage.py loaddata db.json
release: python manage.py migrate
web: gunicorn outsourcers.wsgi