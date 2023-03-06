#!/bin/sh
# play.sh

echo "$1" > playerLeft.py

if [ $# -eq 2 ]
then
    echo "$2" > playerRight.py
fi

python main.py > /dev/null 2>&1

cat results.json