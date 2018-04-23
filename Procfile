release: python manage.py makemigrations
release: python manage.py migrate
release: python manage.py makemigrations app
release: python manage.py migrate app
release: python manage.py loaddata db.json
web: gunicorn outsourcers.wsgi