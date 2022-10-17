#!/bin/bash
LOCK="/home/${USER}/dlrn-user.lock"
set -e

# if any arguments are given, assume console foreground execution
ARG=$1

exec 200>$LOCK
if !  flock -n 200
then
    if [ -n "$ARG" ]
    then
        echo "dlrn-user is running, please try again after disabling it."
    fi
    exit 1
fi

if [ ! -d /var/log/dlrn-logs/${USER}/user ]
then
    mkdir -p /var/log/dlrn-logs/${USER}/user
fi

source ~/.venv/bin/activate
LOGFILE=/var/log/dlrn-logs/${USER}/user/dlrn-user.$(date +%s).log
cd ~/dlrn

set +e
echo `date` "Starting dlrn-user." >> $LOGFILE
dlrn-user --config-file /usr/local/share/dlrn/${USER}/projects.ini "$@" 2>> $LOGFILE
RET=$?
echo `date` "dlrn-user complete." >> $LOGFILE

if [ -n "$ARG" ]
then
    echo Arguments: "$@"
    cat $LOGFILE
fi
exit $RET
