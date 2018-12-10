#!/bin/bash
#
#
# Collect data from clients, router and sink server.
#
#

        
echo "Creating log directories."
mkdir -p logs/sink logs/router logs/clients

        
echo "Collecting data from sink server."
cp -r *.log logs/sink/
cp -r exp logs/sink/

        
echo "Collecting data from border router for interface eth0."
sshpass -p raspberry scp -o "StrictHostKeyChecking no" -r pi@\[b:b:b:b:1:2:3:4\]:/home/pi/router-workdir/eth0/eth0.log logs/router/
sshpass -p raspberry scp -o "StrictHostKeyChecking no" -r pi@\[b:b:b:b:1:2:3:4\]:/home/pi/router-workdir/eth0/router.info logs/router/

        
echo "Collecting data from border router for interface wpan0."
sshpass -p raspberry scp -o "StrictHostKeyChecking no" -r pi@\[b:b:b:b:1:2:3:4\]:/home/pi/router-workdir/wpan0/wpan0.log logs/router/
sshpass -p raspberry scp -o "StrictHostKeyChecking no" -r pi@\[b:b:b:b:1:2:3:4\]:/home/pi/router-workdir/wpan0/router.info logs/router/

        
echo "Collecting data from border router for interface lowpan0."
sshpass -p raspberry scp -o "StrictHostKeyChecking no" -r pi@\[b:b:b:b:1:2:3:4\]:/home/pi/router-workdir/lowpan0/lowpan0.log logs/router/
sshpass -p raspberry scp -o "StrictHostKeyChecking no" -r pi@\[b:b:b:b:1:2:3:4\]:/home/pi/router-workdir/lowpan0/router.info logs/router/

        
echo "Collecting data from client on IP: fdde:ad00:beef:0:904d:a4e2:760b:706b."
mkdir -p logs/clients/1
sshpass -p raspberry scp -o "StrictHostKeyChecking no" -r pi@\[fdde:ad00:beef:0:904d:a4e2:760b:706b\]:/home/pi/client-workdir/smit-latest/smit/testbed/*.log logs/clients/1

        