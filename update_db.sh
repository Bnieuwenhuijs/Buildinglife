#!/bin/bash

echo 'Removing existing app.db and migrations directory'

rm -r app.db
rm -r migrations/

echo 'Updating current database' 
python3 -m flask db init 
python3 -m flask db migrate
python3 -m flask db revision
python3 -m flask db upgrade
