#!/bin/bash
#
#
# Start router to monitor the netowrk interfaces.
#
#

echo "Synchronizing time with NTP server."
sudo timedatectl set-timezone Australia/Sydney
sudo date --set="08/22/2018"
sudo ntpdate -u b:b:b:b:5:6:7:8
mkdir -p /home/pi/router-workdir
cd /home/pi/router-workdir
echo "Creating log directories."
mkdir -p eth0 lowpan0 wpan0
echo "Starting tcpdump"
cd eth0
/sbin/ifconfig > router.info
sudo nohup tcpdump -i eth0 -ttttnnvvS -w eth0.log &
cd ../lowpan0
/sbin/ifconfig > router.info
sudo nohup tcpdump -i lowpan0 -ttttnnvvS -w lowpan0.log &
cd ../wpan0
/sbin/ifconfig > router.info
sudo nohup tcpdump -i wpan0 -ttttnnvvS -w wpan0.log &
exit
        