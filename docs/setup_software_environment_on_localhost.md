## How to setup software environment on localhost



The software environment simulates a system which contains at least five machine. To simulate different machines locally, the following instruction creates multiple terminals to represent machine.

1. Open terminals and create directories.

   - Open five terminals.
   - Create directories for different devices. If directories exists, please remove all of them.
```shell
$ mkdir -p ~/testdir/private-ca ~/testdir/global-ca ~/testdir/manufacturer ~/testdir/server ~/testdir/client
```
   - Unzip the file “CSIRO.zip” to “CSIRO” and copy it to the “home” folder of each machine:
     - Terminal 1 (Manufacturer): ~/testdir/manufacturer/
     - Terminal 2 (Global CA): ~/testdir/global-ca/
     - Terminal 3 (Private CA): ~/testdir/private-ca/
     - Terminal 4 (Server): ~/testdir/server/
     - Terminal 5 (Client): ~/testdir/client/
   - Go to the “home” folder of each machine.

2. Set up manufacturer.

   - In Terminal 1, go to the directory “<path/to/Manufacturer/home>/CSIRO/smit” (~/testdir/manufacturer/CSIRO/smit ) and run (generate manufacturer’s CSR and private key):
```shell
$ sudo python smit_deploy.py -install p44 -workpath ~/testdir/manufacturer -CN manu.sg.ca.com -email manu.sg@ca.com
```

   - Generate and deliver a signature for a device. To simulate signature delivery, the generated signature is copied to device home directory.

     - Generate signature for server device.
```shell
$ python smit_deploy.py -install p45 -msg ~/testdir/manufacturer/CSIRO/smit/appserver/msg
```

     - Deliver signature to server device.

```shell
$ cp ~/testdir/manufacturer/sig ~/testdir/server/CSIRO/smit/appserver/sig
```


       **Note:** The above two steps should be repeated for each client and/or server devices. In practice, the generated signature should be transmitted by using some methods, such as USB and network. The two steps below are to create and deliver siganture to a client device. To do the task, the path to the msg file (~/testdir/client/CSIRO/smit/appclient/msg ) and the destination of “sig” file (~/testdir/client/CSIRO/smit/appclient/sig ) are changed accordingly to the path on client device.
    
     - Generate signature for client device.
```shell
$ python smit_deploy.py -install p45 -msg ~/testdir/manufacturer/CSIRO/smit/appclient/msg
```

     - Deliver signature to client device.
```shell
$ cp ~/testdir/manufacturer/sig ~/testdir/client/CSIRO/smit/appclient/sig
```

   - Copy manufacturer’s CSR to the simulated global CA. This step is to simulate a certificate request in practiece where the CSR file is sent to global CA for certificate generation.
```shell
$ cp ~/testdir/manufacturer/manu.sg.ca.com.csr ~/testdir/global-ca/
```

3. Set up simulated global CA.

   - In Terminal 2, go to the directory “<path/to/global-ca/home>/CSIRO/smit” (~/testdir/global-ca/CSIRO/smit ) and run:
```shell
$ sudo python smit_deploy.py -install p42 -a -CN sg.ca.com -email sg@ca.com -CApath ~/testdir/global-ca/SG-CA -opensslpath /etc/ssl/sg.openssl.cnf
```

   - (Optional) The default OCSP URI (

     http://127.0.0.1:8888

      ) is set in global CA’s OpenSSL configuration file (e.g.,

      

     /etc/ssl/sg.openssl.cnf

      ). In this simulated environment, OCSP server and global CA are running on the same host, so the IP address cannot be changed, but the port number is changable. If you need change the port number:

     - Find (in /etc/ssl/sg.openssl.cnf ) the line like authorityInfoAccess = OCSP;URI:http://127.0.0.1:8888 .
     - Change the port number to your prefered port (e.g., `6789`) for OCSP service, i.e, authorityInfoAccess = OCSP;URI:http://127.0.0.1:6789 .

   - Create certificate for manufacturer.
```shell
$ sudo python smit_deploy.py -install p46 -CApath ~/testdir/global-ca/SG-CA/ -certpath ~/testdir/global-ca/manu.sg.ca.com.cert.pem -csr ~/testdir/global-ca/manu.sg.ca.com.csr -opensslpath /etc/ssl/sg.openssl.cnf
```

   - Deliver certificate to manufacturer.
```shell
$ cp ~/testdir/global-ca/manu.sg.ca.com.cert.pem ~/testdir/manufacturer/
```
   - Set up OCSP service
```shell
$ sudo python smit_deploy.py -install p43 -new -workpath ~/testdir/global-ca/OCSP -ocspport 8888 -CN ocsp.sg.ca.com -email ocsp.sg@ca.com -extensions v3_ocsp
```

   - Troubleshooting: If it is failed to start OCSP server, a possible reason could be mismatch of private key and certificate. To solve the problem:

     - Remove OCSP server working directory (e.g., ~/testdir/global-ca/OCSP ).
     - Change OCSP’s CSR information (e.g., change common name to ocsp2.sg.ca.com ) and run the above command to create new OCSP server.

   Please make sure the same CSR information (e.g., common name) has not been used. Otherwise, the private key and certificate will not match. For each time you run the above command, the common name is suggested to be different.

   

   **Note:** To (re)run existing OCSP server, remove the option -new from the above command, or simply run (if configurations are correct):


```shell
$ sudo python smit_deploy.py -install p43 -workpath ~/testdir/global-ca/OCSP
```


4. Set up private CA.

   - In Terminal 3, go to the directory “<path/to/private-ca/home>/CSIRO/smit” (~/testdir/private-ca/CSIRO/smit ) and copy the certificates to home folder. The step simulates that the private CA obtains global CA and manufacturer’s certificates.

```shell
$ cp ~/testdir/manufacturer/manu.sg.ca.com.cert.pem ~/testdir/private-ca/
$ cp ~/testdir/global-ca/SG-CA/cacert.pem ~/testdir/private-ca/sg.ca.cert.pem
```

   - To create and start private CA, run:
```shell
$ sudo python smit_deploy.py -install p5 -a -new -CN smit.ca.com -email smit@ca.com -CApath ~/testdir/private-ca/SMIT-CA -opensslpath /etc/ssl/smit.openssl.cnf -caip 127.0.0.1 -caport 12345 -signercert ~/testdir/private-ca/manu.sg.ca.com.cert.pem -signerchain ~/testdir/private-ca/sg.ca.cert.pem -ocspport 8888
```


   **Note:** To (re)run existing private CA, remove the option -new from the above command, or simply run (if configurations are correct):


```shell
$ sudo python smit_deploy.py -install p5 -a.
```


5. Run server program.

   - In Terminal 4, go to the directory “<path/to/server/home>/CSIRO/smit” (~/testdir/server/CSIRO/smit ) and run:

     

     **Note:** If there exists directories for private key (~/testdir/server/CSIRO/smit/appserver/private ) and certificate (~/testdir/server/CSIRO/smit/appserver/private ), please remove them before run the following command. Also, if the same CSR information (e.g., common name) has been used, you need to change the CSR information, otherwise the certificate and private key will not match.

     - $ python smit_deploy.py -run p6 -caip 127.0.0.1 -caport 12345 -serverip ::1 -serverport 56789 -CN server.smit.ca.com -email server.smit@ca.com

   - Troubleshooting: If certificates delivered successfully, but DTLS handshake failed, a possible reason could be the private key does not match to the certificate. To solve the problem:

     - Remove server device certificate (e.g., ~/testdir/server/CSIRO/smit/appserver/cert ) and private key (e.g., ~/testdir/server/CSIRO/smit/appserver/private ).
     - Change CSR information (e.g., common name) and run the above command to re-enroll and obtain new certificate.

6. Run client program.

   - In Terminal 5, go to the directory “<path/to/client/home>/CSIRO/smit” (~/testdir/client/CSIRO/smit ) and run:

     

     **Note:** If there exists directories for private key (~/testdir/client/CSIRO/smit/appsclient/private ) and certificate (~/testdir/client/CSIRO/smit/appclient/cert ), please remove them before run the following command. Also, if the same CSR information (e.g., change common name to server2.smit.ca.com) has been used, you need to change the CSR information, otherwise the certificate and private key will not match.

```shell
$ python smit_deploy.py -run p7 -caip 127.0.0.1 -caport 12345 -serverip ::1 -serverport 56789 -CN client.smit.ca.com -email client.smit@ca.com
```

   - Troubleshooting: If certificates delivered successfully, but DTLS handshake failed, a possible reason could be the private key does not match to the certificate. To solve the problem:

     - Remove server device certificate (e.g., ~/testdir/client/CSIRO/smit/appclient/cert ) and private key (e.g., ~/testdir/client/CSIRO/smit/appclient/private ).
     - Change CSR information (e.g., change common name to client2.smit.ca.com ) and run the above command to re-enroll and obtain new certificate.