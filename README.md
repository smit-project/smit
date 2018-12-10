# smit
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
