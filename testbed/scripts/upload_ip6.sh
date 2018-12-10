#!/bin/bash
#
#
# Upload file/directory to remote clients via IPv6.
#
#
        
echo "Running commands on fdde:ad00:beef:0:904d:a4e2:760b:706b"
sshpass -p raspberry ssh -o "StrictHostKeyChecking no" pi@fdde:ad00:beef:0:904d:a4e2:760b:706b "mkdir -p /home/pi/client-workdir"
sshpass -p raspberry scp -o "StrictHostKeyChecking no" -r /Boeing/nan/smit-latest pi@\[fdde:ad00:beef:0:904d:a4e2:760b:706b\]:/home/pi/client-workdir
sleep 1

        