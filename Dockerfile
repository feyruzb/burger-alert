FROM python:3.12-alpine

COPY . /app
WORKDIR /app

RUN pip install -r requirements.txt

CMD [ "flask", "--app", "app", "run" ]
