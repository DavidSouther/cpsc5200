#!/bin/bash

ROOT="$( cd "$(dirname "$0")" >/dev/null 2>&1 ; pwd -P )"
DIRS=( boat carseat desk floor pillow pond )

echo "Reading test data from $ROOT"

for D in ${DIRS[@]} ; do (
    set -x
    sleep $(python -c "import random; print(random.random())")
    ID=$(curl -F "device=${D}" -F "file=@${ROOT}/${D}/image.png" http://localhost:5000/photos 2>/dev/null)
    curl --request POST  --data-binary "@${ROOT}/${D}/operations" "http://localhost:5000${ID}:transform"
) &
done

wait