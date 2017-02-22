#!/bin/bash
py_cmd="/home/worker/OpShell/cron/sync_machine/env/bin/python"
if [ -e /home/worker/OpShell/cron/sync_machine/run.lock ]
    then
    exit
else
    touch /home/worker/OpShell/cron/sync_machine/run.lock
    $py_cmd /home/worker/OpShell/cron/sync_machine/sync_machine.py
    rm /home/worker/OpShell/cron/sync_machine/run.lock
fi
