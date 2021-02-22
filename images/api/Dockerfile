FROM python:3-alpine

WORKDIR /app

# Docker context is images/
COPY ./requirements.txt .
COPY ./common ./common
COPY ./api .

RUN pip3 install -r requirements.txt

ENV FLASK_APP "api.py"
EXPOSE 5000

CMD [ "python", "api.py", "--host", "0.0.0.0" ]
