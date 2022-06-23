FROM python:3.10-buster

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

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

EXPOSE 8020

# RUN python manage.py collectstatic

# RUN nginx -g "daemon off;"

ENTRYPOINT [ "/usr/local/bin/gunicorn" ]

CMD [ "locallibrary.wsgi", "--bind 127.0.0.1:8000" ]