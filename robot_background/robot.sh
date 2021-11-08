#!/bin/bash
echo '123456' | sudo /usr/bin/pulseaudio --start --log-target=syslog
./robot_message_trans > mylog.out 2>&1 &

