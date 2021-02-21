FROM python:3-alpine

WORKDIR /app

# Docker context is images/
COPY ./common .
COPY ./converter .

RUN apk add --no-cache imagemagick bash
RUN pip3 install -r requirements.txt

CMD ["bash", "/app/start.sh" ]
