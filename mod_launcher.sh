#!/bin/bash

if ps -ef | grep -v grep | grep my_own_domoticz ; then
    echo "MOD already running"
else 
    nohup python3.4 /home/pi/mod/my_own_domoticz.py &

fi
