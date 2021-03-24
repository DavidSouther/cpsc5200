# Image Processor

An image processing system.
Images can be uploaded via an HTTP API.
Clients can then send commands to operate on that uploaded image to the API.
The operations are performed using a cluster of image processing machines.
The system is suitable for use as a normalization component in an Internet-of-Things system, such as running QA cameras in an industrial setting.
See ARCHITECTURE.md for the overall design.

## Running

Each component can be deployed individually with the included Dockerfile.
The system as a whole can be run using docker-compose.
The [docker-compose.yml](./docker-compose.yml) mounts `./bus`, `./db/data`, and `./nas` as durable storage mechanisms for the message bus, SQL database, and NAS filesystem respectively.
They should be included in the git checkout via their respective .gitignore files, but if they are not, you will need to `mkdir` them.
`./clean.sh` cleans them out, restoring the local volumes to their pre-run state.
`./testing/data` has sample images and conversion files.
`./testing/data/test.sh` uses curl to simulate IoT uploading images and conversions.

## Demo

A demo of the cluster coming up and running the test script is available.
https://youtu.be/NT0qyPTsCjo

## 500 Lines or Less

Python files:

```
~ find . -type f -name '*.py' | sort | xargs wc
   60   144  1750 ./api/api.py
   32    81   936 ./api/photos.py
   71   152  1920 ./common/bus.py
   60   167  2015 ./common/db.py
   16    41   388 ./common/wait.py
   91   281  2788 ./converter/converter.py
   99   264  3277 ./processor/processor.py
  429  1130 13074 total
```

And for completeness, the non-py files

```
~ find . -type f -not -name '*.py' | sort | xargs wc
  19   64  441 ./api/Dockerfile
   8   13  107 ./clean.sh
  17   60  424 ./converter/Dockerfile
  62   89 1165 ./docker-compose.yaml
  17   60  424 ./processor/Dockerfile
   8    9  148 ./requirements.txt
   3    5   49 ./testing/data/boat/operations
   3    5   49 ./testing/data/carseat/operations
   3    5   48 ./testing/data/desk/operations
   3    5   47 ./testing/data/floor/operations
   3    5   46 ./testing/data/pillow/operations
   3    5   48 ./testing/data/pond/operations
  15   57  481 ./testing/data/test.sh
 164  382 3477 total
```