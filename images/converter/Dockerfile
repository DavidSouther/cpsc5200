FROM python:3-alpine

WORKDIR /app

# Docker context is images/
COPY ./requirements.txt .
COPY ./common ./common
COPY ./converter .

RUN apk add --no-cache imagemagick
RUN pip3 install -r requirements.txt

CMD [ "python", "/app/converter.py" ]
