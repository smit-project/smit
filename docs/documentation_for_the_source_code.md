## Documentation for the source code



## DeployPi

The deploypi module provides members and operations to setup a Raspberry Pi.

*class* **deploypi.DeployPi**

For kernel configuration and installation.

**compile_kernel**(*boot_path, root_path, config*)

Compile kernel for Raspberry Pi

| Parameters                                                |
| --------------------------------------------------------- |
| **boot_path** (str.) – mounted boot path                  |
| **root_path** – mounted root path                         |
| **config** (dict.) – configuration for compiling a kernel |

**copy_to_pi**(*dev_path, filename, dest_path=’/opt/src’*)

Copy a file or directory to Pi

| Parameters                                      |
| ----------------------------------------------- |
| **dev_path** (str.) – the mounted device path   |
| **filename** (str.) – file or directory path    |
| **dest_path** (str.) – destination path of file |

| Returns: int. – The return code: |
| -------------------------------- |
| 1 — succeed.                     |
| -1 — source file does not exist. |
| -2 — device does not exist.      |

**enable_radio**()

Enable an IEEE 802.15.4 radio, currently support openlab and MICROCHIP radios.

**gen_mount**(*dev, mnt_path*)

Check and Return mount device information: device name, device path and mount path.

| Parameters                           |
| ------------------------------------ |
| **dev** (str.) – device name         |
| **mnt_path** (str.) – the mount path |

| Returns: dict. – The dictionary contains: |
| ----------------------------------------- |
| DevName – device name.                    |
| DevPath – device path.                    |
| MountPath – mount path.                   |

**get_mount_path**(*dev, mnt_path*)

Set the current mount path. This is an interactive function to set the current mount path for specific device.

| Parameters                               |
| ---------------------------------------- |
| **dev** (str.) – device name             |
| **mnt_path** (str.) – default mount path |

Returns: str. – current mount path.

**Note:** The device should be checked before calling this function.

**initialize_pi**()

Install iwpan and enable radio on Raspberry Pi.

**install_dependency**()

Install dependencies.

**mount**(*dev_path, mnt_path*)

Mount a device.

| Parameters                        |
| --------------------------------- |
| **dev_path** (str.) – device path |
| **mnt_path** (str.) – mount path  |

**setup_pi**(*args*)

Configure the kernel to setup a Raspberry Pi.

| Parameters                        |
| --------------------------------- |
| **args** – command line arguments |

**umount**(*mnt_path*)

Unmount boot and root devices

| Parameters                       |
| -------------------------------- |
| **mnt_path** (str.) – mount path |



## DeployRouter
The deployrt module provides members and operations to setup a Raspberry Pi as border router.

*class* **deployrt.DeployRouter**

For router installation and configuration

**config_static_route**()

Configure static route based on the configuration file.

**install_radvd**()

Install radvd for native 6LoWPAN router

**setup**()

Install and configure a border router with dependent software.



## DeployServer

The deploysv module provides members and operations to setup a server.

*class* **deploysv.DeployServer**

For server configuration.

**setup**()

Configure static route based on the configuration file.



## DeployCA

The deployca module provides members and operatinos to setup a private CA.

*class* **deployca.DeployCA**

For private Certificate Authority (CA) configuration

**create_cert**()

This is a wrapper of the functions from the CertManagment class.

**init_config**(***args*)

Initialize the package configuration according to the configuration file. This function MUST be called before other function call. The acceptable keywords are: CAPATH, OPENSSL_PATH, WORKPATH, CAPATH, C, ST, L, O, OU, CN, emailAddress, SK, CSR, ECCPARAM, OCSPPORT, SELFSIGN, CERT, CERTDB, CERTS, MSG, SIG, CACHAIN, OCSP, MCERT, EXTENSIONS, OPENSSL_PATH. If arguments are passed to this function, the configuration files will be updated.

| Parameters                                        |
| ------------------------------------------------- |
| **args** (str.) – dictionary of passed arguments. |

**ocsp_setup**()

This function setup an OCSP server. Note: This function can be used when the OCSP server and CA are on the same host.

**setup**(*install_all*)

Configure a private Certificate Authority (CA). This function creates a new CA certificate and set directories for the CA.



## InstallCA

The installca module provides members and operatinos to build applications for private CA.

*class* **installca.AppCA**

Build applications for private CA which generate and distribute certificate for other devices.

**build**()

Build an application: ca.



## CA

The ca module provides members and operatinos to run private CA.

*class* **ca.CA**

This class implement CA functions which start CA and handle certificate generation requests. The parameters used by this class is assigned in the configuration file “appcacnf”. The configuration file allows to set the network information, local certificate information and etc. Such information is used to perform request verification and generate certificates. This class depends on the certificate management module which indeed generates certificate.

**connection_handler**(*sock, addr*)

This is a connection handler for subthread. It process a new connection for certificate request.This function takes a client socket for DTLS packets transmission and the parameter addr is used to show the client IP address. This function will be called in individual thread to process a specific client’s connection.

| Parameters                            |
| ------------------------------------- |
| **sock** (int.) – client socket.      |
| **addr** (tuple.) – client IP address |

**init_config**(***args*)

Initialize the package configuration according to the configuration file.
This function MUST be called before other function call. The acceptable keywords are: config, IP, PORT, CERT, CSR, MSG, SIG, CACERT, CACHAIN, OCSP, OCSPPORT, SIGCERT, SIGCHAIN, OCSPCERT, OCSPSK, SELFSIGN, OPENSSL_PATH. Specifically, “config” is to set the path to configuration file. If arguments are passed to this function, the specified configuration file will be updated.

| Parameters                                 |
| ------------------------------------------ |
| **args** – dictionary of passed arguments. |

**start**()

This function starts the CA to process certificate generation requests. This function support multi-thread processing so that requests can be handle in parallel.

**init_config**(*write_file*)

This function write a file in ‘w’ mode.

| Parameters                                      |
| ----------------------------------------------- |
| **data** (str.) – content to write in the file. |
| **filename** (str.) – path to te output file.   |



## OCSP

The ocsp module provides members and operatinos to run Online Certificate Status Protocol (OCSP) server.

*class* **ocsp.OCSP**

This class manipulate OCSP server which responds the online certificate status request. The parameters used by this class is assigned in the configuration file “ocspcnf”. The configuration file allows to set the network information, local certificate information and etc.

**init_config**(***kwargs*)

Initialize the package configuration according to the configuration file.
This function MUST be called before other function call. The acceptable keywords are: config, CACERT, OCSPPORT, OCSPCERT, OCSPSK, CERTDB. Specifically, “config” is to set the path to configuration file. If arguments are passed to this function, the specified configuration file will be updated.

| Parameters                                          |
| --------------------------------------------------- |
| **kwargs** (int.) – dictionary of passed arguments. |

**start**()

This function starts an OCSP server according to the configuration.



## CertManager

The certmngr module provides members and operatinos to support certificate generation, verificate and etc.

*class* **certmngr.CertManager**

This class provides functions to facilitate certificate generation and signature verification, etc. Most arguments used in the class are specified in the configuration file “certcnf”.

**create_cert**()

Create a certificate from a configuration file, which should contains the inforamtion of CSR, private key and paths fo files.

**create_csr**()

Create certificate signing request (CSR) file based on the information of configuration file. To specify the subject of certificate, it is needed to modify the configuration file. This function will output the CSR file to the path specified in the configuration file with keywords “CSR”.

**create_sk**()

This function creates an ECC based private key file. The ECC parameter can be modified in the configuration file, while it must be supported by openssl.

**find_cert**()

This function find a certificate based on the subject information contained in CSR file.
The function is usually called by CA, otherwise it does not mean too much. This function depends on the value of keywords “CSR”, “CERTDB” and “CERTS”. It checks CA’s certificate database and returns the certificate path if found.

| Return: str. – path of certificate on CA’s certificate database. |
| ------------------------------------------------------------ |
| ” – No certificate found.                                    |
| error – raise an error if certificate is not found.          |

**gen_sig**()

This function generates a signature on a given message file by using the private key specified in the configuration. The dependent configuration keywords of this function are “MSG”, “SK” and “SIG”. If succeed, it outputs a signature file to the specified path, i.e “SIG”, otherwise it may raises an error.

**init_config**(***args*)

Initialize the package configuration according to the configuration file.
This function MUST be called before other function call. The acceptable keywords are: config, WORKPATH, C, ST, L, O, OU, CN, emailAddress, SK, CSR, ECCPARAM, SELFSIGN, CERT, CERTDB, CERTS, MSG, SIG, SIGCERT, CACHAIN, OCSP, MCERT, EXTENSIONS, OPENSSL_PATH. Specifically, “config” is to set the path to configuration file. If arguments are passed to this function, the specified configuration file will be updated.

| Parameters                                          |
| --------------------------------------------------- |
| **kwargs** (int.) – dictionary of passed arguments. |

**verify_cert**(*cert_chain, cert, ocsp*)

This function verifies a certificate according to the given certificate chain.

| Parameters                                |
| ----------------------------------------- |
| **cert_chain** (str.) – path to CA chain. |
| **cert** (str.) – path to certificate.    |
| **ocsp** (str.) – URL of OCSP server.     |

Return: True – verification succeeds False/error – otherwise, false or error may be raised.

**verify_cert_key**()

This function checks the validity of a pair of certificate (CERT) and private key (SK). CERT and SK settings can be specified in the configuration file. It raises an error message if the verification failed, that is the private key is not for the subject specified in the certificate.

Return: True – valid pair of certificate and private key. Error – otherwise.

**verify_sig**()

This function verifies a signature on a given message file by using the certificate specified in the configuration.
The dependent configuration keywords of this function are “MSG”, “SIG” and”SIGCERT”.

Return: True – signature is valid. error – otherwise, error may be raised.



## DTLSWrap

The DTLSWrap module provides members and operatinos to support DTLS communication.

*class* **DTLSWrap.DtlsWrap**

This is a wrap class for some functions from PyDTLS. Note that this class only wraps essential functions from PyDTLS. To use the class, it is requried to have the configuration file “dtlscnf”. For more information and available functions, please see the documentation of PyDTLS.

**accept**(**args, **keywords*)

This is a wrapper function to accept DTLS connections. It is used to accept a DTLS connection and return a socket to the client.

**close**(**args, **keywords*)

This is a wrapper function to close DTLS socket. It closes a socket.

**connect**(**args, **keywords*)

This is a wrapper function to connect server via DTLS connection. It is used to connect a DTLS server.

**init_config**(***args*)

Initialize the package configuration according to the configuration file. Usually, this function should be
called before other function calls. It reads the configuration files according to the given keywords list and initialize the DTLS environment. The acceptable keywords are: config, SK, CERT, TYPE, CACERT, CERT_REQS. Specifically, the keyword “config” sets the configuration file of the class. If arguments are passed to this function, the specified configuration file will be updated.

| Parameters                                 |
| ------------------------------------------ |
| **args** – dictionary of passed arguments. |

**listen**(**args, **keywords*)

This is a wrapper function to listen the DTLS connection request. It is used to listen the DTLS handshake request from client devices.

**recvfrom**(**args, **keywords*)

This a wrapper function to receive a message from a DTLS connection. It is used to receive DTLS packets.

**sendto**(**args, **keywords*)

This a wrapper function to send a message string via DTLS which uses UDP connection. It is used to send DTLS packets.

**set_dtls_socket**(*sock*)

This function sets a wrapped DTLS socket. It is usually used to handle a connection established from the
“accept” function. Note that it is unnecessary to call init_config before this function.

| Parameters                                      |
| ----------------------------------------------- |
| **sock** (int.) – a socket for DTLS connection. |

**shutdown**(**args, **keywords*)

This is a wrapper function to shutdown the DTLS socket. It shuts down a socket.

**wrap_socket**(*sock*)

This a wrapper function to wrap a socket for DTLS communication. The DTLS socket is created by using security
configurations including certificate and private key, etc. The created DTLS socket can be used to send and receive DTLS packets for secure communication. This function does not support SSL socket.

| Parameters                |
| ------------------------- |
| **sock** (int.) – socket. |



## Utils

The utils modules provides some common functions.

*class* **utils.Utils**

Common functions

**call**(**args, **keywords*)

Wrapper function for call in subprocess

**check_call**(**args, **keywords*)

Wrapper function for check_call in subprocess

**check_device_exist**(*dev_path*)

Check whether a device exist.

| Parameters                         |
| ---------------------------------- |
| **dev_path** (str.) – device path. |

| Returns: bool – The return value: |
| --------------------------------- |
| True — device exists.             |
| False — device not found.         |

**delete_lines**(*filename, substring, start, end, ignore_spaces=False*)

Delete lines (in file) which contain the specified substring.

| Parameters                                                   |
| ------------------------------------------------------------ |
| **filename** (str.) – a file.                                |
| **substring** (str.) – a specified substring for deleting lines. |
| **start** (int.) – start position of a line in file          |
| **end** (int.) – end position of a line in file              |
| **ignore_spaces** (bool.) – ignore spaces at the start and end of a line |

| Returns: int. – The code value: |
| ------------------------------- |
| -1 — error found                |
| other — number of deleted lines |

**gen_mac**()

Generate a random MAC address for the experimental environment

Returns: str. – mac address.

**Note:** The generated MAC address is with prefix “18:C0:FF:EE”

**get_dev_format**(*dev*)

Return the device format

| Parameters                     |
| ------------------------------ |
| **dev** (str.) – a device path |

Returns: str. – device format. Return ” if the device does not exist.

**Note:** The input device path must be in format e.g., ‘/dev/sdb2’. The input e.g., ‘/dev/sdb’ is invalid and will return ”.

**insert_lines**(*content, filename, keyword*)

Insert lines to a file in the position spcified by keyword.

| Parameters                                          |
| --------------------------------------------------- |
| **content** (list.) – some lines to inserted.       |
| **filename** (string.) – the destination file name. |
| **keyword** (string.) – a keyword to search.        |

**insert_net_interface**(*content, filename=’/etc/network/interfaces’*)

Insert network interface settings to the beginning of the file for network configuration.

| Parameters                                                   |
| ------------------------------------------------------------ |
| **content** (list.) – some settings being inserted to the file. |
| **filename** (string.) – the destination file.               |

**Note:** This function deletes the first block formatted as below



- \### Begin SMIT Config ###
- ​    ...
- \### End SMIT Config ###

**lookup**(*keyword, filename*)

Return the line which contains the keyword.

| Parameters                           |
| ------------------------------------ |
| **keyword** (str.) – the keyword.    |
| **filename** (str.) – the file name. |

| Returns: str. – The return value:                            |
| ------------------------------------------------------------ |
| ” — keyword not found.                                       |
| line — the first line which contains the keyword in the file |

Example:

- \>>> **print** lookup("def enable", "deploypi.py")
- **def** enable_radio(self):

**makedir**(*path*)

Create a directory and its parent directories if necessary.

| Parameters                          |
| ----------------------------------- |
| **path** (str.) – path of directory |

**read_config**(*filename, keywords*)

Read a configuration file with customized recognizable keyword.

| Parameters                               |
| ---------------------------------------- |
| **filename** (str.) – configuration file |
| **keywords** (dict.) – keywords          |

Returns: dict. – The dictionary contains keys and values.

**Note:** Only the last matching [key:value] is stored for different keys. Reading format: Keyword=”value”

**read_config_v2**(*filename, keywords*)

Read a configuration file with customized recognizable keywords. This function is specifically for the format: key = value

| Parameters                               |
| ---------------------------------------- |
| **filename** (str.) – configuration file |
| **keywords** (dict.) – keywords          |

Returns: dict. – The dictionary contains keys and values.

**Note:** Only the last matching [key:value] is stored for different keys.

**read_file**(**args, **keywords*)

Read a file and return the file as a string.

Return: str. – File content.

**update_config**(*filename, keywords*)

Update configuration file with given parameters.

| Parameters                               |
| ---------------------------------------- |
| **filename** (str.) – configuration file |
| **keywords** (dict.) – keywords          |

**write_file**(*content, \*args, **keywords*)

Write a string to the file

| Parameters                                         |
| -------------------------------------------------- |
| **content** (str.) – content to write into a file. |