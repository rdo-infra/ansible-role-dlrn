#!/bin/bash
DISABLED="/usr/local/share/disabled"
if [ "$#" -ne 1 ]
then
  echo "It's only required one argument: lock or unlock"
  exit 1
fi

if [ $1 = "lock" ]
then
    if [ -e $DISABLED ]
    then
        echo "Already locked"
        exit 1
    else
        echo "Locking DLRN execution for all builders"
        touch $DISABLED
        exit 0
    fi
fi

if [ $1 = "unlock" ]
then
    if [ -e $DISABLED ]
    then
        echo "Unlocking DLRN execution for all builders"
        rm $DISABLED
        exit 0
    else
        echo "Already unlocked"
        exit 1
    fi
fi

echo "Only lock or unlock argument are accepted"
exit 1