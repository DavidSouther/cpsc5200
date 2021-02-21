#!/bin/bash

HOST=bus
PORT=5672

HAS_RABBIT=0
while [[ $HAS_RABBIT -eq 0 ]] ; do
    sleep 1
    timeout 1 bash -c "cat < /dev/null > /dev/tcp/$HOST/$PORT"
    if [[ $? -eq 0 ]] ; then HAS_RABBIT=1 ; fi
done

python app.py