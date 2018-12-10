#!/bin/bash
#
#
# Upload file/directory to remote clients via IPv4.
#
#
        
echo "Running commands on 192.168.0.7"
sshpass -p raspberry ssh -o "StrictHostKeyChecking no" pi@192.168.0.7 "mkdir -p /home/pi/client-workdir"
sshpass -p raspberry scp -o "StrictHostKeyChecking no" -r /Boeing/nan/smit-latest pi@\[192.168.0.7\]:/home/pi/client-workdir
sleep 1

        