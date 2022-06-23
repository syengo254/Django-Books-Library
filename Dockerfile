FROM python:3.10-buster

# install nginx
RUN apt-get update && apt-get install nginx vim -y --no-install-recommends
COPY nginx.default /etc/nginx/sites-available/default
RUN ln -sf /dev/stdout /var/log/nginx/access.log \
    && ln -sf /dev/stderr /var/log/nginx/error.log

# copy source and install dependencies
WORKDIR /usr/src/app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

WORKDIR /usr/src/app/locallibrary

EXPOSE 8000

RUN python manage.py collectstatic

RUN nginx -g "daemon off;"

CMD [ "gunicorn", "locallibrary.wsgi", "--user www-data", "--bind 0.0.0.0:8000", "--workers 2" ]