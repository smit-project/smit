## Install OpenSSL with IBIHOP



The installation instructions for OpenSSL with IBIHOP are as following:

1. Download the [latest version of source code](https://github.com/smit-project/openssl-ibihop), and unzip it into your preferred location.
2. To configure, go to the file location and please use the following command.
```shell
$ make
```
3. Before install the OpenSSL, remove the OpenSSL installed previously.
```shell
$ sudo apt-get remove openssl
```
4. To install the OpenSSL with IBIHOP, simply please use the following command.
```shell
$ sudo make install
```
5. To verify the installation you can use the following commands.
```shell
$ openssl version -v
OpenSSL 1.0.2o-dev  xx XXX xxxx

$ ldd /usr/local/bin/openssl
        linux-vdso.so.1 (0x7ed9b000)
        /usr/lib/arm-linux-gnueabihf/libarmmem.so (0x76f54000)
        libssl.so.1.0.0 => /usr/local/lib/libssl.so.1.0.0 (0x76eec000)
        libcrypto.so.1.0.0 => /usr/local/lib/libcrypto.so.1.0.0 (0x76d60000)
        libdl.so.2 => /lib/arm-linux-gnueabihf/libdl.so.2 (0x76d4d000)
        libc.so.6 => /lib/arm-linux-gnueabihf/libc.so.6 (0x76c0e000)
        /lib/ld-linux-armhf.so.3 (0x76f6a000)
```