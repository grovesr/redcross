#!/bin/bash

# Replace these three settings.
PROJDIR="/var/www/html/redcross/redcross"
PIDFILE="$PROJDIR/mysite.pid"
SOCKET="$PROJDIR/mysite.sock"
#export REDCROSS_SECRET='y0u_z$+wy6qtn--6qgau+h3&he5i#is35e^r*w&m&a^1hvt+a9'
#export REDCROSS_DB_USER='grovesr'
#export REDCROSS_DB_PASS='zse45rdx'
cd $PROJDIR
if [ -f $PIDFILE ]; then
    kill `cat -- $PIDFILE`
    rm -f -- $PIDFILE
fi

exec /usr/bin/env - \
  PYTHONPATH="/home/grovesr/.virtualenvs/redcross-prod/bin/python" \
  ./manage.py runfcgi socket=$SOCKET pidfile=$PIDFILE

