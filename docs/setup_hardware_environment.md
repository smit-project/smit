## Install Package 1 – Configuration and installation for Pi
The Raspberry Pi initialization will configure the Raspbian kernel version to 4.7.x and enable IEEE 802.15.4 radio. A successful installed Raspberry Pi is able to use the radio and 6LoWPAN networks. The installation instructions are as following:

1. Plug the SD card (with the Raspbian system) into the SD card reader then connect it to a Linux machine.

2. Copy the deploy package “CSIRO” to a preferred location and go to the location.

3. Edit configuration files in “<location path>/CSIRO/smit/pisetup/”. There are two configuration files: “config” and “config_kernel”. Go to the directory “<location path>/CSIRO/smit” after modification.

   - “config”: contains general configuration for kernel and radio, etc.
   - “config_kernel”: contains configuration for kernel compilation.
   - To recover the default configuration, copy backup configuration files ”.config” and ”.config_kernel” to “config” and “config_kernel”, respectively.

   **Note:** Not all combinations of Raspbian and Linux kernel are working properly. We recommend to use Raspbian 2016-09-23 and Linux kernel 4.7.y.

4. To install the Raspbian and the package on a new SD card, please use the following command.

```shell
$ sudo python smit_deploy.py -install p11 -f xxx
```

   - Specify the device lable “xxx”, such that “sdb” or “mmcblk0” to install the Raspbian system and the package. Note that do not specify the partition lable such as “sdb1” or “mmcblk0p1”.
   - Optional argument ‘-c’ specifies the checkout options for Linux kernel installation.
   - The script (online) installs needed dependencies.
   - If the kernel is successfully configured, a “CSIRO” folder, which is the same as the unzipped folder of Step 2, will be copied to Raspberry Pi at “/opt/src/CSIRO” (by default).
   - Before installation, it is strongly recommended to use “-d” option to check the device name of the SD card. Please ensure the device name is correct, otherwise other disks would be damaged.

5. (Optional) To install package p11 on SD card which already contains Raspbian system.

```shell
$ sudo python smit_deploy.py -install p11 -b sdb1 -t sdb2
```

   - “boot” and “root” partitions (on SD card) must be provided, such that sdb1 and sdb2.

6. Plug the SD card back to a Raspberry Pi and boot the system. Then, set the system timezone to the same as that of the device which will be used as CA later.

7. Go to the directory “/opt/src/CSIRO/smit”.

8. Run the script “smit_deploy.py” and install package p12 to enable IEEE 802.15.4 radio on Raspberry Pi.

```shell
$ sudo python smit_deploy.py -install p12
```

   - To enable the specific radio, modify the configuration file “config” in /smit/pisetup before installation.
   - The radios can only be installed on Raspberry Pi.
   - If kernel configuration is not required for installation, please manually copy the folder “CSIRO” to Raspberry Pi.

9. At the end of installation, please reboot the system before use.

**Note:** The tool ndisc6 will be automatically installed. By default, a client stops communication to the radvd router every 30 minutes (can be modified in “/etc/radvd.conf” that maximum is 9000 seconds). In this case, please run the following command to refresh the connection.

```shell
$ sudo rdisc6 lowpan0
```



## Install Package 2 – Configuration and installation for router
Package 2 installs necessary software (e.g., radvd) for border router on a Raspberry Pi. The Pi should be configured as in Package 1 and the IEEE 802.15.4 radio is assumed to be enable. A successful configured Raspberry Pi is able to act as a border router which connects 6LoWPAN and IPv6 networks. A border router should have two addresses. One is for 6LoWPAN network, the other is for IPv6 network. The installation instructions are as following:

1. Go to the directory “<location path>/CSIRO/smit/routersetup/”.

2. Edit configuration file “config”.

   - Change the value of “ABRO”. This value must be the link local address of lowpan interface (e.g., lowpan0). For example, the local link address of lowpan0 is “fe80::20c:29ff:fe11:7fc8” (use the command “ifconfig” to get the information), then set ABRO=”fe80::20c:29ff:fe11:7fc8”. A sample link layer address is as below.

     - inet6 addr: fe80::20c:29ff:fe11:7fc8/64 Scope:Link

     

     **Note:** This is a mandatory step.

   - The prefix (e.g., `a:a:a:a::/64`) configuration of lowpan interface will be the network prefix of 6LoWPAN network. That is, a Raspberry Pi as client obtains an IP address like `a:a:a:a:6:7:8:9/64`, where “6:7:8:9” is the link local address (without prefix “fe80::”) of client’s radio.

   - Check and/or modify default IP address, netmask and prefix setting. The IP address of Ethernet interface “eth0” is connected to the server through IPv6 network. So that the IP address of “eth0”is recommended to be in the same subnet of server. For example, both “eht0” and server’s IP address are `b:b:b:b:1:2:3:4/64` and `b:b:b:b:6:7:8:9/64`, respectively. The server IP address is configured in Package 3.

   - To recover the default configuration, copy the backup configuration file ”.config” to “config”.

3. Return to the directory “<location path>/CSIRO/smit/routersetup/” and run the Python script “smit_deploy.py”.
```shell
$ sudo python smit_deploy.py -install p2
```

   - If the file “/etc/radvd.conf” exists, it will be copied to “/etc/radvd.sbck” as the backup of original configuration.
   - It is recommended that “radvd.conf” is manually backed up for recovery purpose.
   - Radvd will be added to the system startup that it automatically starts with system boot.

4. Check the installation of radvd.

```shell
$ sudo radvd -c
```

   If there is no any output from the command, radvd installation may not be successful. Please try to install it again and ensure that there is no any interuption during the installation.

5. Reboot the system or manually start Radvd.

```shell
$ sudo radvd
```

   To run radvd in debug mode, please use the following example.
```
$ sudo radvd -d 5 -m stderr -n
```

**Note:** For more configurations on radvd, please see the reference like [radvd configuration](https://www.freebsd.org/cgi/man.cgi?query=radvd.conf&sektion=5&manpath=FreeBSD+Ports+9.0). The path of “radvd.conf” is “/etc/radvd.conf”. The connection between router and client will be disconnected every 30 minutes (by default), please see the note of [Install Package 1 – Configuration and installation for pi](https://www.smit-project.com/docs/instructions/hardware-environment/install-package-1/).



## Install Package 3 – Configuration and installation for server
Package 3 configures the server’s IP and static route. A successful configuration allows the server to connect with the border router (configured in Package 2) through IPv6 connection. The installation instructions are as following:

1. Go to the directory “<location path>/CSIRO/smit/serversetup/”.

2. Edit configuration file “config”.

   - Check and/or change the name of Ethernet interface connected to the border router.
   - Check and/or change the gateway to the border router’s IPv6 address. Do not use the router’s 6LoWPAN address.
   - To recover the default configuration, copy the back up configuration file ”.config” to “config”.

3. Run the Python script “smit_deploy.py” to install package p3.
```shell
$ sudo python smit_deploy.py -install p3
```

4. Reboot the system or restart the network.
```shell
$ sudo service networking restart
```

   **Note:** Sometimes the static route will be removed due to the change of network environment. Please run the above command to refresh the network settings.

5. Check the route table to see if the static route has been added. Run the above command if the static route disappeared from the routing table.
```shell
$ route -6
```
