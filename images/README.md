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