#!/bin/sh
# play.sh

echo "$1" > playerLeft.py

# if (( $# == 2 )); then
#     echo "$2" > playerRight.py
# fi

python main.py

cat results.json