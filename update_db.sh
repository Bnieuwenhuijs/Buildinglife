#!/bin/bash

echo 'Removing existing app.db and migrations directory'

rm -r app.db
rm -r migrations/

echo 'Updating current database' 
python -m flask db init 
python -m flask db migrate
python -m flask db revision
python -m flask db upgrade
