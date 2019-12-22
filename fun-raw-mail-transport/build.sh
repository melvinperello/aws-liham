#!/bin/sh
cp ./fun-raw-mail-transport.py ./dist/fun-raw-mail-transport.py
pip3 install -r ./requirements.txt -t ./dist
cd ./dist
zip -r ../dist.zip .
cd ..
