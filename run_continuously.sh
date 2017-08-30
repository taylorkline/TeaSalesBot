#!/bin/bash
SCRIPT=$(readlink -f "$0")
SCRIPTPATH=$(dirname "$SCRIPT")
echo $SCRIPTPATH
cd $SCRIPTPATH
source teasalesenv/bin/activate
until python bot.py; do
   echo "Bot crashed with exit code $?. Restarting..." >&2
   sleep 5
done
echo "Bot exited with code $?"
