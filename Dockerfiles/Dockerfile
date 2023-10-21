# docker file for development
FROM python:3.9-slim-bullseye

RUN mkdir /fast-app
WORKDIR /fast-app
COPY requirements.txt /fast-app
RUN pip install -r requirements.txt
COPY . /fast-app

EXPOSE 5000

CMD ["uvicorn", "app.main:app", "--reload", "--port", "5000", "--host", "0.0.0.0"]
