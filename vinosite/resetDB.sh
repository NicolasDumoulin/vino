#!/bin/sh

[ -f db.sqlite3 ] && {
    BAK=db.sqlite3.$(date +%Y%m%d-%H%M%S).bak
    echo "database saved to $BAK"
    echo 'la'
    mv db.sqlite3 $BAK || exit 1
}
python manage.py makemigrations sharekernel && \
python manage.py migrate && \
echo "migration OK" && \
python manage.py populate_database && \
echo "database populated"
