## Welcome to SMIT (Secure and Modular IoT)



## SMIT Project

SMIT package implements a basic IoT platform which consists of sink server, IoT devices, private Certificate Authority (CA) and border router.  With this package, an interested user can build a secure IoT communication network over RaspBerry Pi and openlab 802.14.5 radio easily and quickly.

This package provides the following functionalities:

- Create OS image for raspberry pi (3B).
- Setup private CA as well as supporting components like Online Certificate Status Protocol (OCSP) and time synchronization server.
- Setup border router for the IoT platform which uses Radvd. It supports both wireless (6LoWPAN) and Ethernet (IPv6) networks.
- Setup sink server.
- Create sample server application.
- Create sample client application.
- Security support sub-package which wraps necessary security components like PyDtls.
- Create testbed for network and security performance evaluation. Note that this sub-package is the major part for experiment, while others are for the system preparation.

 

## OpenSSL with [IBIHOP](http://ebooks.iospress.nl/publication/35526)

IBIHOP is considered more efficient than traditional authentication mechanisms DH+signature (at least theoretically). IBIHOP is thus a desirable key exchange mechanism for resource-constrained IoT devices and networks.
This package integrates IBIHOP into DTLS by extending the [OpenSSL](https://www.openssl.org/) implementation. Since DTLS is a standard protocol and widely used in IoT networks, this package improves the usability of IBIHOP by making it as a new security option in the extended OpenSSL implementation. In this package, the compatibility of OpenSSL is kept.


## [IBIHOP](http://ebooks.iospress.nl/publication/35526) in Contiki

[Contiki](http://www.contiki-os.org/index.html) is an open source OS for IoT. With [nano-ecc](https://github.com/iSECPartners/nano-ecc), we implemented IBIHOP in Contiki. The Cooja simulator has been used to evaluate the performance of IBIHOP with Tmote sky.



## Instructions for SMIT package

- [System and environment requirements](docs/system_and_environment_requirements.md)
- [How to setup hardware environment](docs/setup_hardware_environment.md)
- [How to setup software environment on localhost](docs/setup_software_environment_on_localhost.md)
- [How to setup software environment on distributed machines](docs/setup_software_environment_on_distributed_machines.md)
- [Advanced configuration for the software environment](docs/advanced_configuration_for_the_software_environment.md)

 

## Instructions for OpenSSL with IBIHOP

- [Install OpenSSL with IBIHOP](docs/install_openssl_with_ibihop.md)

 

## Instructions for Contiki (Cooja) simulator

- [Use of IBIHOP source code in Contiki (Cooja) simulator](docs/instructions_for_contiki_simulator.md)