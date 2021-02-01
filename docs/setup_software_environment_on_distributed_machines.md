## How to setup software environment on distributed machines



The software environment setup on distributed machines (Raspberry Pis) are slightly different from the simulation on localhost. There are also five steps, while the files like certificate and keys are tranmitted physically among devices.

1. Start five Raspberry Pis.

   - Unzip the file “CSIRO.zip” to “CSIRO” and copy it to a USB drive:
   - Create directories for different devices. If directories exists, please remove all of them.
     - Pi 1 (Manufacturer): ~/testdir/manufacturer/
     - Pi 2 (Global CA): ~/testdir/global-ca/
     - Pi 3 (Private CA): ~/testdir/private-ca/
     - Pi 4 (Server): ~/testdir/server/
     - Pi 5 (Client): ~/testdir/client/
   - Copy “CSIRO” folder to each Pi on the above paths, respectively.

   

   **Note:** In the following steps, Raspberry Pis need Internet connection to install some dependencies like PyDTLS. This is required for ALL Raspberry Pis.

   

   **Note:** It is important that the system time on ALL Pis MUST be synchronized. You could do it via Internet (e.g., ntp) or manually set the date by using sudo date --set='MM/DD/YYYY' .

   

   **Note:** Troubleshootings for the above localhost simulation are also available in this distributed envrionment.

2. Set up manufacturer.

   - On Pi 1, go to the directory “<path/to/Manufacturer/home>/CSIRO/smit” (~/testdir/manufacturer/CSIRO/smit ) and run (generate manufacturer’s CSR and private key):
```shell
$ sudo python smit_deploy.py -install p44 -workpath ~/testdir/manufacturer -CN manu.sg.ca.com -email manu.sg@ca.com
```

   - Generate and deliver a signature for a device. To transmit files between devices, you could use USB drive or other methods (e.g., scp).
     - Generate signature for server device.
```shell
$ python smit_deploy.py -install p45 -msg 
~/testdir/manufacturer/CSIRO/smit/appserver/msg
```

     - Copy the signature file ~/testdir/manufacturer/sig to Pi 4 by using USB drive, the destination path on Pi 4 is: ~/testdir/server/CSIRO/smit/appserver/sig
     - Generate signature for client device.
```shell
$ python smit_deploy.py -install p45 -msg ~/testdir/manufacturer/CSIRO/smit/appclient/msg
```

     - Copy the signature file ~/testdir/manufacturer/sig to Pi 5 by using USB drive, the destination path on Pi 5 is: ~/testdir/client/CSIRO/smit/appclient/sig
   - Copy (via USB drive) manufacturer’s CSR (on Pi 1, ~/testdir/manufacturer/manu.sg.ca.com.csr ) to the simulated global CA (on Pi 2, ~/testdir/global-ca/ ). This step is to request a certificate from global CA.

3. Set up simulated global CA.

   - On Pi 2, go to the directory “<path/to/global-ca/home>/CSIRO/smit” (~/testdir/global-ca/CSIRO/smit ) and run:

```shell
$ sudo python smit_deploy.py -install p42 -a -CN sg.ca.com -email sg@ca.com -CApath ~/testdir/global-ca/SG-CA -opensslpath /etc/ssl/sg.openssl.cnf
```

   - The default OCSP URI (

     http://127.0.0.1:8888

      ) is set in global CA’s OpenSSL configuration file (e.g.,

      

     /etc/ssl/sg.openssl.cnf

      ). To change OCSP server URI:

     - Find (in /etc/ssl/sg.openssl.cnf ) the line like authorityInfoAccess = OCSP;URI:http://127.0.0.1:8888 .
     - Change the URI to your prefered URI (e.g., http://192.168.0.12:6789 ) for OCSP service, i.e, authorityInfoAccess = OCSP;URI:http://192.168.0.12:6789 .

   - Create certificate for manufacturer.

```shell
$ sudo python smit_deploy.py -install p46 -CApath ~/testdir/global-ca/SG-CA/ -certpath ~/testdir/global-ca/manu.sg.ca.com.cert.pem -csr ~/testdir/global-ca/manu.sg.ca.com.csr -opensslpath /etc/ssl/sg.openssl.cnf
```

   - Copy (via USB drive) manufacturer’s certificate (on Pi 2, ~/testdir/global-ca/manu.sg.ca.com.cert.pem ) to Pi 1 at ~/testdir/manufacturer/ . This step is to deliver a certificate from global CA to manufacturer.

   - Set up OCSP service

```shell
$ sudo python smit_deploy.py -install p43 -new -workpath ~/testdir/global-ca/OCSP -ocspport 6789 -CN ocsp.sg.ca.com -email ocsp.sg@ca.com -extensions v3_ocsp
```

   **Note:** To (re)run existing OCSP server, remove the option -new from the above command, or simply run (if configurations are correct):


```shell
$ sudo python smit_deploy.py -install p43 -workpath ~/testdir/global-ca/OCSP
```

4. Set up private CA.

   - On Pi 3, go to the directory “<path/to/private-ca/home>/CSIRO/smit” (~/testdir/private-ca/CSIRO/smit ).
   - Copy (via USB drive) the certificates from Pi 1 and Pi 2 to home folder (on Pi 3) ~/testdir/private-ca/ . The step simulates that the private CA obtains global CA and manufacturer’s certificates.
     - From Pi 1:copy ~/testdir/manufacturer/manu.sg.ca.com.cert.pem
     - From Pi 2: copy ~/testdir/global-ca/SG-CA/cacert.pem (Rename it on Pi 3: e.g., from cacert.pem to sg.ca.cert.pem )
   - To create and start private CA, run:
```shell
$ sudo python smit_deploy.py -install p5 -a -new -CN smit.ca.com -email smit@ca.com -CApath ~/testdir/private-ca/SMIT-CA -opensslpath /etc/ssl/smit.openssl.cnf -caip 192.168.0.13 -caport 12345 -signercert ~/testdir/private-ca/manu.sg.ca.com.cert.pem -signerchain ~/testdir/private-ca/sg.ca.cert.pem -ocsp http://192.168.0.12:6789
```

   **Note:** To (re)run existing private CA, remove the option -new from the above command, or simply run (if configurations are correct):


```shell
$ sudo python smit_deploy.py -install p5 -a
```

5. Run server program.

   - On Pi 4, go to the directory “<path/to/server/home>/CSIRO/smit” (~/testdir/server/CSIRO/smit ).
   - If the IPv6 address for `lowpan0` has not been assgiend, run the following command on Pi 4.
```shell
$ sudo ip -6 addr add a:a:a:a:1:2:3:4/64 dev lowpan0
```

   - Start the server
```shell
$ python smit_deploy.py -run p6 -caip 192.168.0.13 -caport 12345 -serverip a:a:a:a:1:2:3:4 -serverport 56789 -CN server.smit.ca.com -email server.smit@ca.com
```

6. Run client program.

   - On Pi 5, go to the directory “<path/to/client/home>/CSIRO/smit” (~/testdir/client/CSIRO/smit ).
   - If the IPv6 address for `lowpan0` has not been assgiend, run the following command on Pi 4.
```shell
$ sudo ip -6 addr add a:a:a:a:1:2:3:5/64 dev lowpan0
```

   - Start the client
```shell
$ python smit_deploy.py -run p7 -caip 192.168.0.13 -caport 12345 -serverip a:a:a:a:1:2:3:4 -serverport 56789 -CN client.smit.ca.com -email client.smit@ca.com
```
