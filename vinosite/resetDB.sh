#!/bin/sh

BAK=db.sqlite3.$(date +%Y%m%d-%H%M%S).bak
echo "database saved to $BAK"
mv db.sqlite3 $BAK && \
python manage.py makemigrations sharekernel && \
python manage.py migrate && \
echo "migration OK" && \
python manage.py populate_database && \
echo "database populated"
