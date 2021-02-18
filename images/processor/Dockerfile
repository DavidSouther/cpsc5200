FROM python:3-alpine

WORKDIR /app

COPY . .

RUN apk add imagemagick
RUN pip3 install -r requirements.txt

CMD [ "python", "app.py" ]
