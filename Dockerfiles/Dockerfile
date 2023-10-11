# docker file for production
FROM python:3.8-alpine

WORKDIR /flask-app
COPY requirements.txt /flask-app
RUN pip install -r requirements.txt
COPY . /flask-app

ENV FLASK_APP=run.py
ENV FLASK_ENV=production

EXPOSE 5000

CMD ["flask", "run"]