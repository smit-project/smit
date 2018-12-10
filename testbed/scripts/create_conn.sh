#!/bin/bash
#
#
# Create network connection to router via link-layer addresses.
#
#
        
echo "Running commands on fe80::cc1c:954d:e4e6:364f"
sshpass -p raspberry ssh -o "StrictHostKeyChecking no" pi@fe80::cc1c:954d:e4e6:364f%wpan0 "echo fe80::cc1c:954d:e4e6:364f; sudo rdisc6 wpan0"
sleep 1

        