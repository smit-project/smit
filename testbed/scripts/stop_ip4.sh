#!/bin/bash
#
#
# Stop the experiment via IPv4.
#
#

        
echo "Stopping client 192.168.0.7"
sshpass -p raspberry ssh -o "StrictHostKeyChecking no" pi@192.168.0.7 "echo 192.168.0.7; sudo pkill python; sudo pkill tcpdump"

        
echo "Stopping router b:b:b:b:1:2:3:4"
sshpass -p raspberry ssh -o "StrictHostKeyChecking no" pi@b:b:b:b:1:2:3:4 "echo b:b:b:b:1:2:3:4; sudo pkill tcpdump"

        
echo "Stopping sink server monitor."
sudo pkill tcpdump
echo "Please terminate the sinkerver manually by Control+C."
        