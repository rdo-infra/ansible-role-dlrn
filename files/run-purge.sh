#!/bin/bash
LOCK="/home/${USER}/dlrn.lock"
RSYNC_DEST=$(grep rsyncdest /usr/local/share/dlrn/${USER}/projects.ini | awk -F= '{print $2}')
RSYNC_SERVER=$(echo $RSYNC_DEST | awk -F: '{print $1}')
RSYNC_PORT=$(grep rsyncport /usr/local/share/dlrn/${USER}/projects.ini | awk -F= '{print $2}')
set -e

# if any arguments are given, assume console foreground execution
ARG=$1

exec 200>$LOCK
while !  flock -n 200; do
    if [ -n "$ARG" ]
    then
        echo "DLRN ${USER} running, waiting 30 seconds before retrying."
    fi
    sleep 30
done

if [ ! -d /home/${USER}/dlrn-logs ]; then
    mkdir -p /home/${USER}/dlrn-logs
fi

source ~/.venv/bin/activate
if [ -n "$ARG" ]; then
    LOGFILE=/home/${USER}/dlrn-logs/dlrn-purge.console.$(date +%s).log
    ARGUMENTS=""
else
    LOGFILE=/home/${USER}/dlrn-logs/dlrn-purge.$(date +%s).log
    ARGUMENTS="--older-than 60 -y --exclude-dirs /home/${USER}/data/repos/current,/home/${USER}/data/repos/consistent,/home/${USER}/data/repos/current-passed-ci,/home/${USER}/data/repos/current-tripleo,/home/${USER}/data/repos/previous-current-tripleo,/home/${USER}/data/repos/current-tripleo-rdo,/home/${USER}/data/repos/previous-current-tripleo-rdo,/home/${USER}/data/repos/puppet-passed-ci,/home/${USER}/data/repos/current-tripleo-rdo-internal,/home/${USER}/data/repos/tripleo-ci-testing,/home/${USER}/data/repos/promoted-components,/home/${USER}/data/repos/component-ci-testing,/home/${USER}/data/repos/podified-ci-testing,/home/${USER}/data/repos/current-podified"
fi
cd ~/dlrn

set +e
echo "$(date) Starting DLRN-purge run." >> $LOGFILE
# Purge as needed
dlrn-purge --config-file /usr/local/share/dlrn/${USER}/projects.ini ${ARGUMENTS} "$@" 2>> $LOGFILE
RET=$?
echo `date` "DLRN-purge run complete." >> $LOGFILE

# If the purge operation was successful, synchronize to the backup node
if [ ${RET} -eq 0 ]; then
    # The sync process can be slow, let's do it only once a week, on Sunday
    if [ "$(date +%u)" = "7" ]; then
        echo `date` "Starting synchronization to backup server." >> $LOGFILE
        if [ -n "${RSYNC_DEST}" ]; then
            rsync -avz --delete-delay --exclude="*.htaccess" --exclude="/deps" --exclude="/build-deps" -e "ssh -p ${RSYNC_PORT} -o StrictHostKeyChecking=no" /home/${USER}/data/repos/* ${RSYNC_DEST} 2>> $LOGFILE
        fi
        echo `date` "Synchronization to backup server completed." >> $LOGFILE
    fi
fi

if [ -n "$ARG" ]; then
    echo Arguments: "$@"
    cat $LOGFILE
fi
exit $RET
