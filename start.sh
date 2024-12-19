#!/bin/bash

if [ "$1" == "dev" ]; then
    fastapi dev
elif [ "$1" == "run" ]; then
    fastapi run
else
    echo "Usage: $0 {dev|run}"
    exit 1
fi
