FROM python:3-alpine

WORKDIR /app

COPY . .

RUN pip3 install -r requirements.txt

ENV FLASK_APP "api.py"
EXPOSE 5000

CMD [ "python", "api.py", "--host", "0.0.0.0" ]
