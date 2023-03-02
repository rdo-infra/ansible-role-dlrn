#!/bin/bash
DISABLED="/usr/local/share/dlrn/disabled"
if [ "$#" -ne 1 ]
then
    echo "It's only required one argument: lock or unlock"
    exit 1
fi

option="${1}"
case ${option} in
    "lock")
        if [ -e $DISABLED ]
        then
            echo "Already locked"
            exit 0
        else
            echo "Locking DLRN execution for all builders"
            touch $DISABLED
            exit $?
        fi
        ;;
    "unlock")
        if [ -e $DISABLED ]
        then
            echo "Unlocking DLRN execution for all builders"
            rm $DISABLED
            exit $?
        else
            echo "Already unlocked"
            exit 0
        fi
        ;;
    *)
        echo "Only lock or unlock argument are accepted"
        exit 1
      ;;
esac