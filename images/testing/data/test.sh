#!/bin/bash

DIRS=( boat carseat desk floor pillow pond )

for D in ${DIRS[@]} ; do 
    curl http://localhost:5000/photo -F 'file=@${D}/image.png' > ./id
    ID=$(<./id)
    curl --header "Content-Type: application/json" \
        --request POST \
        --data $(<${D}/convert.json) \
        http://localhost:5000/${ID}:transform
done