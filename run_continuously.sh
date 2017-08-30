#!/bin/bash
until bot.py; do
   echo "Bot crashed with exit code $?. Restarting..." >&2
   sleep 5
done
echo "Bot exited with code $?"
