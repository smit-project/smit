#!/bin/bash
#
#
# Stop the experiment via IPv6.
#
#

        
echo "Stopping client fdde:ad00:beef:0:904d:a4e2:760b:706b"
sshpass -p raspberry ssh -o "StrictHostKeyChecking no" pi@fdde:ad00:beef:0:904d:a4e2:760b:706b "echo fdde:ad00:beef:0:904d:a4e2:760b:706b; sudo pkill python; sudo pkill tcpdump"

        
echo "Stopping router b:b:b:b:1:2:3:4"
sshpass -p raspberry ssh -o "StrictHostKeyChecking no" pi@b:b:b:b:1:2:3:4 "echo b:b:b:b:1:2:3:4; sudo pkill tcpdump"

        
echo "Stopping sink server monitor."
sudo pkill tcpdump
echo "Please terminate the sinkerver manually by Control+C."
        