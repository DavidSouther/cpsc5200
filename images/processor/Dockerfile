FROM python:3-alpine

WORKDIR /app
# Docker context is images/
COPY ./requirements.txt .

RUN \
    apk add --no-cache imagemagick && \
    apk add --no-cache postgresql-libs && \
    apk add --no-cache --virtual .build-deps gcc musl-dev postgresql-dev && \
    python3 -m pip install -r requirements.txt --no-cache-dir && \
    apk --purge del .build-deps

COPY ./common ./common
COPY ./converter .

CMD [ "python", "/app/processor.py" ]
