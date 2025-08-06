FROM python:3.12-alpine

COPY . /app
WORKDIR /app

RUN pip install -r requirements.txt

CMD [ "flask", "--app", "app", "run", "--host=0.0.0.0", "--port=80"]
