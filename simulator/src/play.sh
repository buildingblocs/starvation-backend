#!/bin/sh
# play.sh

printf '%s' "$1" > playerLeft.py

if [ $# -eq 2 ]
then
    printf '%s' "$2" > playerRight.py
fi

if [ $# -eq 3 ]
then
    cp "./levels/level$3.py" playerRight.py
fi

python main.py 
# >/dev/null 2>&1

cat results.json
