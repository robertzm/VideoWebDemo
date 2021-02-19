#!/bin/bash

if [ -d "venv" ]
then
    source venv/bin/activate
    whereis python
    pip install -r requirements.txt
    mysql.server restart
    mysql -uroot -proot &
    python3 manage.py PROD
else
    virtualenv venv
    source venv/bin/activate
    python3 -m pip install --upgrade pip
    pip install -r requirements.txt
    mysql.server restart
    mysql -uroot -proot &
    python3 manage.py PROD
fi
