#!/usr/bin/env bash
# startsvr.sh
if [ -n "$DJANGO_SUPERUSER_USERNAME" ] && [ -n "$DJANGO_SUPERUSER_PASSWORD" ] ; then
    (cd martor_demo; python manage.py createsuperuser --no-input)
fi
(cd locallibrary; gunicorn locallibrary.wsgi --bind 0.0.0.0:8000 --workers 3) &
nginx -g "daemon off;"