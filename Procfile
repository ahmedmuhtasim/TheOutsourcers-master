release: python manage.py migrate
python manage.py loaddata db.json
web: gunicorn outsourcers.wsgi