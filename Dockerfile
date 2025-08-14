FROM python:3.12-alpine

ARG TZ=Europe/Budapest
ENV TZ=$TZ

COPY requirements.txt /app/requirements.txt
WORKDIR /app

RUN pip install -r requirements.txt

COPY . /app

CMD [ "flask", "--app", "app", "run", "--host=0.0.0.0", "--port=80"]
