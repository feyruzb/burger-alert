FROM python:3.12-alpine

ARG TZ=Europe/Budapest
ENV TZ=$TZ
RUN apk add --no-cache tzdata
ENV TZ=$TZ
RUN ln -sf /usr/share/zoneinfo/$TZ /etc/localtime
COPY requirements.txt /app/requirements.txt
WORKDIR /app

RUN pip install -r requirements.txt

COPY . /app

CMD [ "flask", "--app", "app", "run", "--host=0.0.0.0", "--port=80"]
