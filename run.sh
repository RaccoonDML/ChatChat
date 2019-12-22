sudo nginx -s reload
python manage.py collectstatic
uwsgi --ini uwsgi.ini
