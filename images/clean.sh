#!/bin/sh

cd "$(dirname "$0")"
rm -rf \
    ./nas/photos/* \
    ./db/data

mkdir ./db/data
