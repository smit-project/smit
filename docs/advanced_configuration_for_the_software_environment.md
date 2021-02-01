## Advanced configuration for the software environment



This section shows the way to change system configuration via editing configuration files.



**Note:** To run the programs, the command are similar to the above respectively, except removing options and parameters. This section only shows the way to change different configuration files.

1. Set up manufacturer.

   - Go to the directory “<path/to/Manufacturer/home>/CSIRO/smit/casetup”.
   - Edit the configuration file “certcnf” for manufacturer certificate generation.
     - CSR information must be different from the previous CSRs. For example, set “/CN” as "manu.sg.ca.com" and set “/emailAddress” as "manu.sg@ca.com" .
     - Set “CERT” to manufacturer’s certificate, e.g., "~/Manufac/manu.sg.ca.com.cert.pem" . (Assume the manufacturer’s directory is “~/Manufac”.)
     - Set “SK” to manufacturer’s private key, e.g., "~/Manufac/private/manu.sg.ca.com.key.pem" .
     - Comment setting “EXTENSIONS”.
     - Set “OPENSSL_PATH”, e.g., "/etc/ssl/sg.openssl.cnf" to the one used by SG-CA.
     - Set “SELFSIGN” to ‘`n`‘.
     - Save the file.

2. Set up simulated global CA for manufacturer authentication.

   - Go to the directory “<path/to/Manufacturer/home>/CSIRO/smit/casetup”.

   - Edit the configuration file “opensslcnf” for SG-CA.

     - Set the value of “SMIT-CA” to the preferred SG-CA path, e.g., "~/SG-CA" . Note that this path MUST be different from the root CA set previously.

     - Set the value of “OPENSSL_PATH” to the preferred openssl configuration path for this CA, for example, "/etc/ssl/sg.openssl.cnf" . Note that this path MUST be different from the corresponding path set in Step 2.

       Specifically, there are two sample settings as following.

       For root CA: SMIT-CA="~/SMIT-CA" OPENSSL_PATH="/etc/ssl/smit.openssl.cnf"

       For SG-CA: SMIT-CA="~/SG-CA" OPENSSL_PATH="/etc/ssl/sg.openssl.cnf"

     - Find the keyword “authorityInfoAccess” and change the followed URI if needed, for example, set “URI” as "http://127.0.0.1:8888" . This URI will be used to run Online Certificate Status Protocol (OCSP) for certificate revocation check. By default, it is set to the localhost at port 8888.

     - Save the file.

   - Edit the configuration file “certcnf” for SG-CA certificate generation.

     - Change the CSR section to specify SG-CA information, for example, set “/CN” as "sg.ca.com" and set “/emailAddress” as "sg@ca.com" . Note that this CSR information should be different from previous CSR information.

     - Set “SELFSIGN” to 'y' .

     - Set the path to SG-CA certificate “CERT”, e.g., "~/SG-CA/cacert.pem" . Note that SG-CA certificate (i.e, cacert.pem) should be placed in the SG-CA directory.

       For example, if SG-CA directory SMIT-CA="~/SG-CA" , then SG-CA certificate path should be CERT="~/SG-CA/cacert.pem"

     - Set the path to SG-CA private key “SK”, e.g., "/SG-CA/private/cakey.pem" . SG-CA’s private key (i.e, cakey.pem) should be placed in the “private” directory under SG-CA directory.

       For example, if SG-CA directory SMIT-CA="~/SG-CA" , then SG-CA private key path should be SK="~/SG-CA/private/cakey.pem"

     - Set the path to certificate database “CERTDB”, e.g., “~/SG-CA/index.txt”. The certificate database (i.e, index.txt) should be placed in the SG-CA directory.

       For example, if SG-CA directory SMIT-CA="~/SG-CA" , then certificate database path should be CERTDB="~/SG-CA/index.txt"

     - Set the path to store generated certificates “CERTS”, e.g., "~/SG-CA/newcerts" . The directory (i.e, newcerts) of certificates should be placed in the SG-CA directory.

       For example, if SG-CA directory SMIT-CA="~/SG-CA" , then directory of certificates should be CERTS="~/SG-CA/newcerts"

     - Set the setting for “OPENSSL_PATH” to be the same as that used by the simulate global CA (SG-CA), for example, set “OPENSSL_PATH” as "/etc/ssl/sg.openssl.cnf" .

     - Save the file.

   - Go to the directory “<path/to/global-ca/home>/CSIRO/smit/casetup”.

   - Edit the configuration file “certcnf” for OCSP server certificate generation.

     - CSR information must be different from the previous CSRs. For example, set “/CN” as "ocsp.sg.ca.com" and set `"/emailAddress" as "ocsp.sg@ca.com" `.
     - Set “CERT” to "~/OCSP/ocsp.sg.ca.com.cert.pem" .
     - Set “SK” to "~/OCSP/private/ocsp.sg.ca.com.key.pem" .
     - Uncomment setting “EXTENSIONS”.
     - Set “OPENSSL_PATH”, e.g., "/etc/ssl/sg.openssl.cnf" to the one used by SG-CA.
     - Set “SELFSIGN” to 'n' .
     - Save the file.

3. Set up root CA.

   - Go to the directory “<path/to/private-ca/home>/CSIRO/smit/casetup”.

   - Edit the configuration file “opensslcnf” for root CA (SMIT-CA).

     - Change the value of “SMIT-CA” to the preferred CA path, e.g., "~/SMIT-CA" .
     - Change the value of “OPENSSL_PATH” to the preferred openssl configuration path for this CA, e.g., "/etc/ssl/smit.openssl.cnf" .
     - The Openssl configuration section usually does not need to be modified for root CA.
     - Save the file.

   - Edit the configuration file “certcnf” for root CA certificate generation.

     - Change the CSR section to specify root CA information. For example set “/CN” as "smit.ca.com" and set “/emailAddress” as "smit@ca.com"

     - Set “SELFSIGN” to 'y' .

     - Set the path to CA certificate “CERT”. Note that CA certificate (i.e, cacert.pem) should be placed in the CA directory.

       For example, if CA directory SMIT-CA="~/SMIT-CA" , then CA certificate path should be CERT="~/SMIT-CA/cacert.pem"

     - Set the path to CA private key “SK”. CA’s private key (i.e, cakey.pem) should be placed in the “private” directory under CA directory.

       For example, if CA directory SMIT-CA="~/SMIT-CA" , then CA private key path should be SK="~/SMIT-CA/private/cakey.pem"

     - Set the path to certificate database “CERTDB”. The certificate database (i.e, index.txt) should be placed in the CA directory.

       For example, if CA directory SMIT-CA="~/SMIT-CA" , then certificate database path should be CERTDB="~/SMIT-CA/index.txt"

     - Set the path to store generated certificates “CERTS”. The directory (i.e, newcerts) of certificates should be placed in the CA directory.

       For example, if CA directory SMIT-CA="~/SMIT-CA" , then directory of certificates should be CERTS="~/SMIT-CA/newcerts"

     - Set the setting for “OPENSSL_PATH” accordingly to be the same as that used by root CA, i.e, “OPENSSL_PATH” in “opensslcnf” for root CA, for example, "/etc/ssl/smit.openssl.cnf" .

     - Save the file.

     This is interpreted asdgtext using an explicit role.

   - Go to the directory “<path/to/private-ca/home>/CSIRO/smit/appca”.

   - Edit the configuration file “appcacnf” for CA.

     - Set “SIGCERT” to the path of manufacturer’s certificate, e.g, "~/Manufac/manu.cert.pem" .
     - Set “SIGCHAIN” to the path of certificate chain of manufacturer’s CA. In this experiment, the certificate chain is identical to the manufacturer’s CA certificate, e.g., "~/SG-CA/cacert.pem" .
     - Set “CACERT” to the path of private CA certificate, e.g., "~/SMIT-CA/caert.pem" .
     - Set “CACHAIN” to the path of private CA certificate, e.g., "~/SMIT-CA/cacert.pem" , because they are identical in this experiment.
     - Set “OPENSSL_PATH” to the one (e.g., "/etc/ssl/smit.openssl.cnf" ) used by private CA but simulated global CA.
     - Set “CERTDB” to the certificate database (e.g., "~/SMIT-CA/index.txt" ) of private CA.
     - Set “CERTS” to the directory (e.g., "~/SMIT-CA/newcerts" ) stores certificates on private CA.
     - Set “IP” address (e.g., "127.0.0.1" ) as needed.
     - Set “PORT” number (e.g., "12345" ) as needed.
     - Save the file.

4. Run server program.

   - Go to the directory “<path/to/server/home>/CSIRO/smit/appserver”.
   - Edit the configuration file “servercnf” for server.
     - Change CSR information which must be different from the previous CSRs. For example, set “/CN” as "server.smit.ca.com" and set “/emailAddress” as "server.smit@ca.com" .
     - Save the file.

5. Run client program.

   - Open a terminal and go to the directory “<path/to/client/home>/CSIRO/smit/appclient”.
   - Edit the configuration file “clientcnf” for client.
     - Change CSR information which must be different from the previous ones. For example, set “/CN” as "client.smit.ca.com" and set “/emailAddress” as "client.smit@ca.com" .
     - Save the file.