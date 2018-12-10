'''
SMIT package implements a basic IoT platform.

Copyright 2016-2018 Distributed Systems Security, Data61, CSIRO

This file is part of SMIT package.

SMIT package is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
any later version.

SMIT package is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with SMIT package.  If not, see <https://www.gnu.org/licenses/>.
'''

import os
import subprocess
import pisetup.deploypi
import routersetup.deployrt
import serversetup.deploysv
import casetup.deployca
import appca.installca
import testbed.setupexp
import appca.ca
import appca.ocsp
import argparse
import utils

try:
    import appserver.server
    import appclient.client
    import security.certmngr
except:
    subprocess.call('sudo apt-get -y --force-yes install python-pip', shell=True)
    subprocess.call('pip install Dtls', shell=True)


def main():
    menu = '''\
    Package indexes:
        p1. Setup Raspberry Pi with configured Kernel and radio
            p11. Setup Raspbian system (Do it on Linux host)
            p12. Enable radio (Do it on Raspberry Pi only)
        p2. Setup a border router
        p3. Setup a server
        p4. Setup a CA and OCSP server
            p41. Setup a private CA.
            p42. Setup a simulated global CA.
            p43. Setup an OCSP server
            p44. Generate private key and CSR files.
            p45. Generate signature for device.
            P46. Generate certificate.
        p5. Create and start private CA applications.
        p6. Create and start server application.
        p7. Create and start client application.
        p8. Setup testbed for performance test
            p81. Setup testbed.
            p82. Start sink server.
            p83. Start border router monitor.
            p84. Start clients
            p85. Collect experiment data
            p86. Analyze data
            p87. Stop experiment
    '''
    parser = argparse.ArgumentParser()
    parser.add_argument('-l', dest='list', action='store_true', help='List indexes of packages.')
    parser.add_argument('-d', dest='lb', action='store_true', help='List the devices with partitions.')
    parser.add_argument('-install', dest='package', nargs=1, help='Specify the index of package for installation.')
    parser.add_argument('-run', dest='package', nargs=1, help='Specify the index of package to run.')
    parser.add_argument('-new', dest='new', action='store_true',
                        help='Specify if it is to create an entirely new instance.')
    parser.add_argument('-c', dest='checkout', nargs='*', help='Specify the checkout options for Linux kernel.')
    parser.add_argument('-b', dest='boot', nargs=1,
                        help='Specify the partition (e.g., sdb1) from your SD card for \'boot\'.')
    parser.add_argument('-t', dest='root', nargs=1,
                        help='Specify the partition (e.g., sdb2) from your SD card for \'root\'.')
    parser.add_argument('-a', dest='all', action='store_true', help='Install all dependencies.')
    parser.add_argument('-f', dest='force', nargs=1, help='Erase the specified device and install the Raspbian OS.')
    parser.add_argument('-CN', dest='CN', nargs=1,
                        help='Set a common name of an entity for CSR, e.g., www.smit-ca.com')
    parser.add_argument('-C', dest='C', nargs=1, help='Set country name for CSR.')
    parser.add_argument('-ST', dest='ST', nargs=1, help='Set state for CSR.')
    parser.add_argument('-L', dest='L', nargs=1, help='Set location for CSR.')
    parser.add_argument('-O', dest='O', nargs=1, help='Set organization name for CSR.')
    parser.add_argument('-OU', dest='OU', nargs=1, help='Set organization unit name for CSR.')
    parser.add_argument('-config', dest='config', nargs=1, help='Set path to configuration file.')
    parser.add_argument('-exp_config', dest='exp_config', nargs=2,
                        help='Set path to (two) configuration files for testbed experiment.')
    parser.add_argument('-email', dest='email', nargs=1, help='Specify an email address of an entity.')
    parser.add_argument('-CApath', dest='capath', nargs=1, help='Specify a path to CA.')
    parser.add_argument('-workpath', dest='workpath', nargs=1, help='Specify a working path to store files.')
    parser.add_argument('-sk', dest='sk', nargs=1, help='Set path to private key.')
    parser.add_argument('-csr', dest='csr', nargs=1, help='Set path to CSR file.')
    parser.add_argument('-eccparam', dest='eccparam', nargs=1, help='Set ECC parameters.')
    parser.add_argument('-certpath', dest='certpath', nargs=1, help='Set path to one\'s certificate.')
    parser.add_argument('-certdb', dest='certdb', nargs=1, help='Set path to certificate database on CA.')
    parser.add_argument('-certs', dest='certs', nargs=1, help='Set path to generated certificates on CA.')
    parser.add_argument('-msg', dest='msg', nargs=1, help='Set path to message file on client and server devices.')
    parser.add_argument('-sig', dest='sig', nargs=1, help='Set path to signature file on client and server devices.')
    parser.add_argument('-CAchain', dest='cachain', nargs=1, help='Set path to CA chain.')
    parser.add_argument('-CAcert', dest='cacert', nargs=1, help='Set path to CA certificate.')
    parser.add_argument('-ocsp', dest='ocsp', nargs=1, help='Set OCSP url, e.g, http://127.0.0.1:8888')
    parser.add_argument('-extensions', dest='extensions', nargs=1,
                        help='Set extensions for certificate generation, e.g., v3_ocsp')
    parser.add_argument('-noexten', dest='noexten', action='store_true',
                        help='Disable extensions for certificate generation.')
    parser.add_argument('-opensslpath', dest='opensslpath', nargs=1, help='Set path to openssl configuration.')
    parser.add_argument('-selfsign', dest='selfsign', nargs=1, help='Set [y/n] if the certificate is self-signed.')
    parser.add_argument('-mcert', dest='mcert', nargs=1, help='Set path to manufacturer\'s certificate.')
    parser.add_argument('-ocspport', dest='ocspport', nargs=1, help='Set OCSP server port number.')
    parser.add_argument('-caport', dest='caport', nargs=1, help='Set CA\'s port number.')
    parser.add_argument('-caip', dest='caip', nargs=1, help='Set CA\'s IPv4 address.')
    parser.add_argument('-serverport', dest='serverport', nargs=1, help='Set server\'s port number.')
    parser.add_argument('-serverip', dest='serverip', nargs=1, help='Set server\'s IPv6 address.')
    parser.add_argument('-signercert', dest='sigcert', nargs=1, help='Set signer certificate.')
    parser.add_argument('-signerchain', dest='sigchain', nargs=1, help='Set signer\'s CA certificate chain.')
    parser.add_argument('-type', dest='type', nargs=1, help='Set device type [client|server].')
    parser.add_argument('-certreq', dest='certreq', nargs=1,
                        help='Set certificate requirements for DTLS handshake [CERT_NONE|CERT_OPTIONAL|CERT_REQUIRED].')
    parser.add_argument('-router-ip6', dest='router_ip6', nargs=1, help='Set border router\'s IPv6 address.')
    parser.add_argument('-client-ip6', dest='client_ip6', nargs=1,
                        help='Set the list of client IPv6 addresses. Format: address1,address2,...')
    parser.add_argument('-client-ip4', dest='client_ip4', nargs=1,
                        help='Set the list of client IPv4 addresses. Format: address1,address2,...')
    parser.add_argument('-inet', dest='inet', nargs=1,
                        help='Set IPv4 or IPv6 network to upload files from sink server to client devices. [4|6]')
    parser.add_argument('-payloadlen', dest='payloadlen', nargs=1, help='')
    parser.add_argument('-update-client', dest='update_client', action='store_true',
                        help='Upload files to ALL clients on the (IPv4 or IPv6) address list.')
    parser.add_argument('-nostart', dest='nostart', action='store_true', help='Do not start clients.')
    parser.add_argument('-client-workdir', dest='client_workdir', nargs=1,
                        help='Set work directory on client devices. Updated files will be store in this directory.')
    parser.add_argument('-router-workdir', dest='router_workdir', nargs=1,
                        help='Set work directory on border router. Updated files will be store in this directory.')
    parser.add_argument('-sink2client', dest='sink2client', nargs=1,
                        help='Set source directory/file to be uploaded to client devices.')
    parser.add_argument('-dtls', dest='dtls', action='store_true', help='Enable DTLS on sink server.')
    parser.add_argument('-client-script', dest='client_script', nargs=1,
                        help='Set the path of Python script (on client device) to be executed.')
    parser.add_argument('-user', dest='user', nargs=1, help='Set a username to login client devices and border router.')
    parser.add_argument('-passwd', dest='passwd', nargs=1,
                        help='Set a password to login client devices and border router.')
    parser.add_argument('-sink-interface', dest='sink_interface', nargs=1,
                        help='Set the name of network interface (connects to router) on sink server.')
    parser.add_argument('-date', dest='date', nargs=1, help='Set current date.')
    parser.add_argument('-timezone', dest='timezone', nargs=1, help='Set local timezone.')
    parser.add_argument('-rflowpan', dest='rflowpan', nargs=1,
                        help='Set (for clients) time period to reconnect router.')
    parser.add_argument('-synctime', dest='synctime', nargs=1,
                        help='Set (for clients) time period to syncronize time with NTP server.')
    parser.add_argument('-syswait', dest='syswait', nargs=1,
                        help='Set (for clients) a waitting time for system connection establishment.')
    parser.add_argument('-sendtime', dest='sendtime', nargs=1, help='Set (for clients) time period to send a message.')
    parser.add_argument('-sendrate', dest='sendrate', nargs=1,
                        help='Set (for clients) the number of packets per second sent over the network.')
    parser.add_argument('-devnum', dest='devnum', nargs=1, help='Set the number of client devices.')

    args = parser.parse_args()
    utl = utils.Utils()

    if args.list:
        print menu
        exit(0)

    if args.lb:
        utl.call('sudo lsblk', shell=True)
        exit(0)

    if args.package is None:
        args = parser.parse_args(['-h'])
    elif args.package[0] == 'p1':
        print('Invalid argument: choose from [\'p11\', \'p12\'].')
        exit(1)
    elif args.package[0] == 'p11':
        os.chdir('pisetup')
        pi = pisetup.deploypi.DeployPi()
        if (args.boot is not None and args.root is not None) or args.force is not None:
            pi.setup_pi(args)
        else:
            print('Arguments are missing: specify boot and root partitions.')
    elif args.package[0] == 'p12':
        os.chdir('pisetup')
        pi = pisetup.deploypi.DeployPi()
        pi.enable_radio()
    elif args.package[0] == 'p2':
        os.chdir('routersetup')
        router = routersetup.deployrt.DeployRouter()
        router.setup()
    elif args.package[0] == 'p3':
        os.chdir('serversetup')
        server = serversetup.deploysv.DeployServer()
        server.setup()
    elif args.package[0] == 'p41' or args.package[0] == 'p42':
        os.chdir('casetup')
        ca = casetup.deployca.DeployCA()
        if args.noexten:
            args.extensions = [' ']
        ca.init_config(package=args.package[0], CN=get_value(args.CN), C=get_value(args.C), O=get_value(args.O),
                       L=get_value(args.L),
                       ST=get_value(args.ST), OU=get_value(args.OU), emailAddress=get_value(args.email),
                       SELFSIGN='y', CAPATH=get_value(args.capath),
                       WORKPATH=get_value(args.capath), SK=get_value(args.sk), CSR=get_value(args.csr),
                       ECCPARAM=get_value(args.eccparam), CERT=get_value(args.certpath),
                       CERTDB=get_value(args.certdb), CERTS=get_value(args.certs), MSG=get_value(args.msg),
                       SIG=get_value(args.sig), CACHAIN=get_value(args.cachain), OCSP=get_value(args.ocsp),
                       MCERT=get_value(args.mcert), EXTENSIONS=get_value(args.extensions),
                       OPENSSL_PATH=get_value(args.opensslpath))
        ca.setup(args.all)
    elif args.package[0] == 'p43':
        if args.new:  # Create a new OCSP server.
            os.chdir('casetup')
            ocsp_deploy = casetup.deployca.DeployCA()
            if args.noexten:
                args.extensions = [' ']
            ocsp_deploy.init_config(package=args.package[0], CN=get_value(args.CN), C=get_value(args.C),
                                    O=get_value(args.O), L=get_value(args.L),
                                    ST=get_value(args.ST), OU=get_value(args.OU), emailAddress=get_value(args.email),
                                    SELFSIGN='n', CAPATH=get_value(args.capath),
                                    WORKPATH=get_value(args.workpath), SK=get_value(args.sk), CSR=get_value(args.csr),
                                    ECCPARAM=get_value(args.eccparam), CERT=get_value(args.certpath),
                                    CERTDB=get_value(args.certdb), CERTS=get_value(args.certs), MSG=get_value(args.msg),
                                    SIG=get_value(args.sig), CACHAIN=get_value(args.cachain), OCSP=get_value(args.ocsp),
                                    OCSPPORT=get_value(args.ocspport),
                                    MCERT=get_value(args.mcert), EXTENSIONS=get_value(args.extensions),
                                    OPENSSL_PATH=get_value(args.opensslpath))
            ocsp_deploy.ocsp_setup()
            os.chdir('../appca')
        else:  # Run existing OCSP server.
            os.chdir('appca')
        app = appca.installca.AppCA()
        app.build()
        ocsp = appca.ocsp.OCSP()
        if not args.config or args.config[0] == '':
            args.config = ['ocspcnf']
        ocsp.init_config(config=args.config[0], OCSPSK=get_value(args.sk), OCSPCERT=get_value(args.certpath),
                         CERTDB=get_value(args.certdb), CACERT=get_value(args.cacert),
                         OCSPPORT=get_value(args.ocspport))
        ocsp.start()
    elif args.package[0] == 'p44':
        os.chdir('security')
        cert = security.certmngr.CertManager()
        # ca = casetup.deployca.DeployCA()
        if args.noexten:
            args.extensions = [' ']
        if not args.config or args.config[0] == '':
            args.config = ['certcnf']
        cert.init_config(config=args.config[0], package=args.package[0], CN=get_value(args.CN), C=get_value(args.C),
                         O=get_value(args.O), L=get_value(args.L),
                         ST=get_value(args.ST), OU=get_value(args.OU), emailAddress=get_value(args.email),
                         SELFSIGN='n', CAPATH=get_value(args.capath),
                         WORKPATH=get_value(args.workpath), SK=get_value(args.sk), CSR=get_value(args.csr),
                         ECCPARAM=get_value(args.eccparam), CERT=get_value(args.certpath),
                         CERTDB=get_value(args.certdb), CERTS=get_value(args.certs), MSG=get_value(args.msg),
                         SIG=get_value(args.sig), CACHAIN=get_value(args.cachain), OCSP=get_value(args.ocsp),
                         MCERT=get_value(args.mcert), EXTENSIONS=get_value(args.extensions),
                         OPENSSL_PATH=get_value(args.opensslpath))
        cert.create_csr()
    elif args.package[0] == 'p45':
        os.chdir('security')
        cert = security.certmngr.CertManager()
        # ca = casetup.deployca.DeployCA()
        if args.noexten:
            args.extensions = [' ']
        if not args.config or args.config[0] == '':
            args.config = ['certcnf']
        cert.init_config(config=args.config[0], package=args.package[0], CN=get_value(args.CN),
                         C=get_value(args.C), O=get_value(args.O), L=get_value(args.L),
                         ST=get_value(args.ST), OU=get_value(args.OU), emailAddress=get_value(args.email),
                         SELFSIGN='n', CAPATH=get_value(args.capath),
                         WORKPATH=get_value(args.workpath), SK=get_value(args.sk), CSR=get_value(args.csr),
                         ECCPARAM=get_value(args.eccparam), CERT=get_value(args.certpath),
                         CERTDB=get_value(args.certdb), CERTS=get_value(args.certs), MSG=get_value(args.msg),
                         SIG=get_value(args.sig), CACHAIN=get_value(args.cachain), OCSP=get_value(args.ocsp),
                         MCERT=get_value(args.mcert), EXTENSIONS=get_value(args.extensions),
                         OPENSSL_PATH=get_value(args.opensslpath))
        cert.gen_sig()
    elif args.package[0] == 'p46':
        os.chdir('security')
        cert = security.certmngr.CertManager()
        # ca = casetup.deployca.DeployCA()
        if args.noexten:
            args.extensions = [' ']
        if not args.config or args.config[0] == '':
            args.config = ['certcnf']
        cert.init_config(config=args.config[0], package=args.package[0], CN=get_value(args.CN), C=get_value(args.C),
                         O=get_value(args.O), L=get_value(args.L),
                         ST=get_value(args.ST), OU=get_value(args.OU), emailAddress=get_value(args.email),
                         SELFSIGN='n', CAPATH=get_value(args.capath),
                         WORKPATH=get_value(args.workpath), SK=get_value(args.sk), CSR=get_value(args.csr),
                         ECCPARAM=get_value(args.eccparam), CERT=get_value(args.certpath),
                         CERTDB=get_value(args.certdb), CERTS=get_value(args.certs), MSG=get_value(args.msg),
                         SIG=get_value(args.sig), CACHAIN=get_value(args.cachain), OCSP=get_value(args.ocsp),
                         MCERT=get_value(args.mcert), EXTENSIONS=get_value(args.extensions),
                         OPENSSL_PATH=get_value(args.opensslpath))
        cert.create_cert()
    elif args.package[0] == 'p5':
        if args.new:  # create new private CA.
            os.chdir('casetup')
            cadeploy = casetup.deployca.DeployCA()
            if args.noexten:
                args.extensions = [' ']
            cadeploy.init_config(package=args.package[0], CN=get_value(args.CN), C=get_value(args.C),
                                 O=get_value(args.O),
                                 L=get_value(args.L),
                                 ST=get_value(args.ST), OU=get_value(args.OU), emailAddress=get_value(args.email),
                                 SELFSIGN='y', CAPATH=get_value(args.capath),
                                 WORKPATH=get_value(args.capath), SK=get_value(args.sk), CSR=get_value(args.csr),
                                 ECCPARAM=get_value(args.eccparam), CERT=get_value(args.certpath),
                                 CERTDB=get_value(args.certdb), CERTS=get_value(args.certs), MSG=get_value(args.msg),
                                 SIG=get_value(args.sig), CACHAIN=get_value(args.cachain), OCSP=get_value(args.ocsp),
                                 OCSPPORT=get_value(args.ocspport),
                                 MCERT=get_value(args.mcert), EXTENSIONS=get_value(args.extensions),
                                 OPENSSL_PATH=get_value(args.opensslpath))
            cadeploy.setup(args.all)
            os.chdir('../appca')
        else:
            os.chdir('appca')
        ca = appca.ca.CA()
        if not args.config or args.config[0] == '':
            args.config = ['appcacnf']
        ca.init_config(config=args.config[0], OCSPSK=get_value(args.sk), OCSPCERT=get_value(args.certpath),
                       CACERT=get_value(args.cacert), OCSPPORT=get_value(args.ocspport),
                       CACHAIN=get_value(args.cachain), OCSP=get_value(args.ocsp), IP=get_value(args.caip),
                       PORT=get_value(args.caport), SIGCERT=get_value(args.sigcert), SIGCHAIN=get_value(args.sigchain),
                       SELFSIGN='n', OPENSSL_PATH=get_value(args.opensslpath))
        ca.start()
    elif args.package[0] == 'p6':
        os.chdir('appserver')
        server = appserver.server.Server()
        if not args.config or args.config[0] == '':
            args.config = ['servercnf']
        server.init_config(config=args.config[0], CN=get_value(args.CN), C=get_value(args.C), O=get_value(args.O),
                           L=get_value(args.L), ST=get_value(args.ST), OU=get_value(args.OU),
                           emailAddress=get_value(args.email), SK=get_value(args.sk), CSR=get_value(args.csr),
                           CERT=get_value(args.certpath), MSG=get_value(args.msg), CACERT=get_value(args.cacert),
                           SIG=get_value(args.sig), CACHAIN=get_value(args.cachain), CAIP=get_value(args.caip),
                           CAPORT=get_value(args.caport), SERVERIP=get_value(args.serverip),
                           SERVERPORT=get_value(args.serverport), TYPE='server', CERT_REQS='CERT_REQUIRED')
        server.start(args.all)
    elif args.package[0] == 'p7':
        os.chdir('appclient')
        client = appclient.client.Client()
        if not args.config or args.config[0] == '':
            args.config = ['clientcnf']
        client.init_config(config=args.config[0], CN=get_value(args.CN), C=get_value(args.C), O=get_value(args.O),
                           L=get_value(args.L), ST=get_value(args.ST), OU=get_value(args.OU),
                           emailAddress=get_value(args.email), SK=get_value(args.sk), CSR=get_value(args.csr),
                           CERT=get_value(args.certpath), MSG=get_value(args.msg), CACERT=get_value(args.cacert),
                           SIG=get_value(args.sig), CACHAIN=get_value(args.cachain), CAIP=get_value(args.caip),
                           CAPORT=get_value(args.caport), SERVERIP=get_value(args.serverip),
                           SERVERPORT=get_value(args.serverport), TYPE='client', CERT_REQS='CERT_REQUIRED')
        client.start(args.all)
    elif args.package[0] == 'p81':
        os.chdir('testbed')
        if args.exp_config is not None:
            if len(args.exp_config) != 2 or args.exp_config[0] == '' or args.exp_config[1] == '':
                print ('Error: you should spcified two configuration files for the testbed configuration.\n'
                       'E.g.,: -exp_config client_config_file sink_config_file'
                       '\nNote: order is important, you should specify client configuration then sink configuration.')
                return
        else:
            args.exp_config = ['client_expcnf', 'sink_expcnf']
        exp = testbed.setupexp.SetupExp()
        exp.init_client_config(exp_config=args.exp_config[0], CAIP=get_value(args.caip), CAPORT=get_value(args.caport),
                               CERT=get_value(args.certpath), CSR=get_value(args.csr),
                               CACERT=get_value(args.cacert), SK=get_value(args.sk), SERVERIP=get_value(args.serverip),
                               SERVERPORT=get_value(args.serverport), CACHAIN=get_value(args.cacert),
                               CERT_REQS=get_value(args.certreq), TIMEZONE=get_value(args.timezone),
                               SYNCTIME=get_value(args.synctime), REFLOWPAN=get_value(args.rflowpan),
                               SYSWAIT=get_value(args.syswait), PAYLOADLEN=get_value(args.payloadlen),
                               DATE=get_value(args.date), SENDTIME=get_value(args.sendtime),
                               SENDRATE=get_value(args.sendrate), DEVNUM=get_value(args.devnum), TYPE='client')
        exp.init_sink_config(exp_config=args.exp_config[1], CAIP=get_value(args.caip), CAPORT=get_value(args.caport),
                             CERT=get_value(args.certpath), CSR=get_value(args.csr),
                             CACERT=get_value(args.cacert), SK=get_value(args.sk), SERVERIP=get_value(args.serverip),
                             SERVERPORT=get_value(args.serverport), CACHAIN=get_value(args.cacert),
                             CERT_REQS=get_value(args.certreq), ROUTER_IP6=get_value(args.router_ip6),
                             CLIENT_IP6=get_value(args.client_ip6), CLIENT_IP4=get_value(args.client_ip4),
                             DATE=get_value(args.date), CLIENT_WKD=get_value(args.client_workdir),
                             ROUTER_WKD=get_value(args.router_workdir), SINK2CLIENT=get_value(args.sink2client),
                             PASSWORD=get_value(args.passwd), USER=get_value(args.user),
                             SINK_INTERFACE=get_value(args.sink_interface), CLIENT_SCRIPT=get_value(args.client_script),
                             TYPE='server')
        exp.setup()
    elif args.package[0] == 'p82':
        os.chdir('testbed')
        if args.exp_config is not None:
            if len(args.exp_config) != 2 or args.exp_config[0] == '' or args.exp_config[1] == '':
                print ('Error: you should spcified two configuration files for the testbed configuration. \n'
                       'E.g.,: -exp_config client_config_file sink_config_file'
                       '\nNote: order is important, you should specify client configuration then sink configuration.')
                return
        else:
            args.exp_config = ['client_expcnf', 'sink_expcnf']
        exp = testbed.setupexp.SetupExp()
        exp.init_client_config(exp_config=args.exp_config[0], CAIP=get_value(args.caip), CAPORT=get_value(args.caport),
                               CERT=get_value(args.certpath), CSR=get_value(args.csr),
                               CACERT=get_value(args.cacert), SK=get_value(args.sk), SERVERIP=get_value(args.serverip),
                               SERVERPORT=get_value(args.serverport), CACHAIN=get_value(args.cacert),
                               CERT_REQS=get_value(args.certreq), TIMEZONE=get_value(args.timezone),
                               SYNCTIME=get_value(args.synctime), REFLOWPAN=get_value(args.rflowpan),
                               SYSWAIT=get_value(args.syswait), PAYLOADLEN=get_value(args.payloadlen),
                               DATE=get_value(args.date), SENDTIME=get_value(args.sendtime),
                               SENDRATE=get_value(args.sendrate), DEVNUM=get_value(args.devnum), TYPE='client')
        exp.init_sink_config(exp_config=args.exp_config[1], CAIP=get_value(args.caip), CAPORT=get_value(args.caport),
                             CERT=get_value(args.certpath), CSR=get_value(args.csr),
                             CACERT=get_value(args.cacert), SK=get_value(args.sk), SERVERIP=get_value(args.serverip),
                             SERVERPORT=get_value(args.serverport), CACHAIN=get_value(args.cacert),
                             CERT_REQS=get_value(args.certreq), ROUTER_IP6=get_value(args.router_ip6),
                             CLIENT_IP6=get_value(args.client_ip6), CLIENT_IP4=get_value(args.client_ip4),
                             DATE=get_value(args.date), CLIENT_WKD=get_value(args.client_workdir),
                             ROUTER_WKD=get_value(args.router_workdir), SINK2CLIENT=get_value(args.sink2client),
                             PASSWORD=get_value(args.passwd), USER=get_value(args.user),
                             SINK_INTERFACE=get_value(args.sink_interface), CLIENT_SCRIPT=get_value(args.client_script),
                             TYPE='server')
        exp.start_sink(dtls=args.dtls)
    elif args.package[0] == 'p83':
        os.chdir('testbed')
        if args.exp_config is not None:
            if len(args.exp_config) != 2 or args.exp_config[0] == '' or args.exp_config[1] == '':
                print ('Error: you should spcified two configuration files for the testbed configuration. \n'
                       'E.g.,: -exp_config client_config_file sink_config_file'
                       '\nNote: order is important, you should specify client configuration then sink configuration.')
                return
        else:
            args.exp_config = ['client_expcnf', 'sink_expcnf']
        exp = testbed.setupexp.SetupExp()
        exp.init_client_config(exp_config=args.exp_config[0], CAIP=get_value(args.caip), CAPORT=get_value(args.caport),
                               CERT=get_value(args.certpath), CSR=get_value(args.csr),
                               CACERT=get_value(args.cacert), SK=get_value(args.sk), SERVERIP=get_value(args.serverip),
                               SERVERPORT=get_value(args.serverport), CACHAIN=get_value(args.cacert),
                               CERT_REQS=get_value(args.certreq), TIMEZONE=get_value(args.timezone),
                               SYNCTIME=get_value(args.synctime), REFLOWPAN=get_value(args.rflowpan),
                               SYSWAIT=get_value(args.syswait), PAYLOADLEN=get_value(args.payloadlen),
                               DATE=get_value(args.date), SENDTIME=get_value(args.sendtime),
                               SENDRATE=get_value(args.sendrate), DEVNUM=get_value(args.devnum), TYPE='client')
        exp.init_sink_config(exp_config=args.exp_config[1], CAIP=get_value(args.caip), CAPORT=get_value(args.caport),
                             CERT=get_value(args.certpath), CSR=get_value(args.csr),
                             CACERT=get_value(args.cacert), SK=get_value(args.sk), SERVERIP=get_value(args.serverip),
                             SERVERPORT=get_value(args.serverport), CACHAIN=get_value(args.cacert),
                             CERT_REQS=get_value(args.certreq), ROUTER_IP6=get_value(args.router_ip6),
                             CLIENT_IP6=get_value(args.client_ip6), CLIENT_IP4=get_value(args.client_ip4),
                             DATE=get_value(args.date), CLIENT_WKD=get_value(args.client_workdir),
                             ROUTER_WKD=get_value(args.router_workdir), SINK2CLIENT=get_value(args.sink2client),
                             PASSWORD=get_value(args.passwd), USER=get_value(args.user),
                             SINK_INTERFACE=get_value(args.sink_interface), CLIENT_SCRIPT=get_value(args.client_script),
                             TYPE='server')
        exp.start_router()
    elif args.package[0] == 'p84':  # start client
        os.chdir('testbed')
        if args.exp_config is not None:
            if len(args.exp_config) != 2 or args.exp_config[0] == '' or args.exp_config[1] == '':
                print ('Error: you should spcified two configuration files for the testbed configuration.\n'
                       'E.g.,: -exp_config client_config_file sink_config_file'
                       '\nNote: order is important, you should specify client configuration then sink configuration.')
                return
        else:
            args.exp_config = ['client_expcnf', 'sink_expcnf']
        if args.inet is None:
            args.inet = ['6']
        elif args.inet[0] != '4' and args.inet[0] != '6':
            print ("Error: invalid parameter of \'inet\'. The value should be eigher 4 or 6")
            return
        exp = testbed.setupexp.SetupExp()
        exp.init_client_config(exp_config=args.exp_config[0], CAIP=get_value(args.caip), CAPORT=get_value(args.caport),
                               CERT=get_value(args.certpath), CSR=get_value(args.csr),
                               CACERT=get_value(args.cacert), SK=get_value(args.sk), SERVERIP=get_value(args.serverip),
                               SERVERPORT=get_value(args.serverport), CACHAIN=get_value(args.cacert),
                               CERT_REQS=get_value(args.certreq), TIMEZONE=get_value(args.timezone),
                               SYNCTIME=get_value(args.synctime), REFLOWPAN=get_value(args.rflowpan),
                               SYSWAIT=get_value(args.syswait), PAYLOADLEN=get_value(args.payloadlen),
                               DATE=get_value(args.date), SENDTIME=get_value(args.sendtime),
                               SENDRATE=get_value(args.sendrate), DEVNUM=get_value(args.devnum), TYPE='client')
        exp.init_sink_config(exp_config=args.exp_config[1], CAIP=get_value(args.caip), CAPORT=get_value(args.caport),
                             CERT=get_value(args.certpath), CSR=get_value(args.csr),
                             CACERT=get_value(args.cacert), SK=get_value(args.sk), SERVERIP=get_value(args.serverip),
                             SERVERPORT=get_value(args.serverport), CACHAIN=get_value(args.cacert),
                             CERT_REQS=get_value(args.certreq), ROUTER_IP6=get_value(args.router_ip6),
                             CLIENT_IP6=get_value(args.client_ip6), CLIENT_IP4=get_value(args.client_ip4),
                             DATE=get_value(args.date), CLIENT_WKD=get_value(args.client_workdir),
                             ROUTER_WKD=get_value(args.router_workdir), SINK2CLIENT=get_value(args.sink2client),
                             PASSWORD=get_value(args.passwd), USER=get_value(args.user),
                             SINK_INTERFACE=get_value(args.sink_interface), CLIENT_SCRIPT=get_value(args.client_script),
                             TYPE='server')
        if args.update_client:
            exp.upload_to_clients(args.inet[0])
        if args.nostart is None or args.nostart != True:
            exp.start_clients()
    elif args.package[0] == 'p85':  # collect data
        os.chdir('testbed')
        if args.exp_config is not None:
            if len(args.exp_config) != 2 or args.exp_config[0] == '' or args.exp_config[1] == '':
                print ('Error: you should spcified two configuration files for the testbed configuration. \n'
                       'E.g.,: -exp_config client_config_file sink_config_file'
                       '\nNote: order is important, you should specify client configuration then sink configuration.')
                return
        else:
            args.exp_config = ['client_expcnf', 'sink_expcnf']
        if args.inet is None:
            args.inet = ['6']
        elif args.inet[0] != '4' and args.inet[0] != '6':
            print ("Error: invalid parameter of \'inet\'. The value should be eigher 4 or 6")
            return
        exp = testbed.setupexp.SetupExp()
        exp.init_client_config(exp_config=args.exp_config[0], CAIP=get_value(args.caip), CAPORT=get_value(args.caport),
                               CERT=get_value(args.certpath), CSR=get_value(args.csr),
                               CACERT=get_value(args.cacert), SK=get_value(args.sk), SERVERIP=get_value(args.serverip),
                               SERVERPORT=get_value(args.serverport), CACHAIN=get_value(args.cacert),
                               CERT_REQS=get_value(args.certreq), TIMEZONE=get_value(args.timezone),
                               SYNCTIME=get_value(args.synctime), REFLOWPAN=get_value(args.rflowpan),
                               SYSWAIT=get_value(args.syswait), PAYLOADLEN=get_value(args.payloadlen),
                               DATE=get_value(args.date), SENDTIME=get_value(args.sendtime),
                               SENDRATE=get_value(args.sendrate), DEVNUM=get_value(args.devnum), TYPE='client')
        exp.init_sink_config(exp_config=args.exp_config[1], CAIP=get_value(args.caip), CAPORT=get_value(args.caport),
                             CERT=get_value(args.certpath), CSR=get_value(args.csr),
                             CACERT=get_value(args.cacert), SK=get_value(args.sk), SERVERIP=get_value(args.serverip),
                             SERVERPORT=get_value(args.serverport), CACHAIN=get_value(args.cacert),
                             CERT_REQS=get_value(args.certreq), ROUTER_IP6=get_value(args.router_ip6),
                             CLIENT_IP6=get_value(args.client_ip6), CLIENT_IP4=get_value(args.client_ip4),
                             DATE=get_value(args.date), CLIENT_WKD=get_value(args.client_workdir),
                             ROUTER_WKD=get_value(args.router_workdir), SINK2CLIENT=get_value(args.sink2client),
                             PASSWORD=get_value(args.passwd), USER=get_value(args.user),
                             SINK_INTERFACE=get_value(args.sink_interface), CLIENT_SCRIPT=get_value(args.client_script),
                             TYPE='server')
        exp.collect_data(args.inet[0])
    elif args.package[0] == 'p86':  # analyze data
        os.chdir('testbed')
        if args.exp_config is not None:
            if len(args.exp_config) != 2 or args.exp_config[0] == '' or args.exp_config[1] == '':
                print ('Error: you should spcified two configuration files for the testbed configuration. \n'
                       'E.g.,: -exp_config client_config_file sink_config_file'
                       '\nNote: order is important, you should specify client configuration then sink configuration.')
                return
        else:
            args.exp_config = ['client_expcnf', 'sink_expcnf']
        exp = testbed.setupexp.SetupExp()
        exp.init_client_config(exp_config=args.exp_config[0], CAIP=get_value(args.caip), CAPORT=get_value(args.caport),
                               CERT=get_value(args.certpath), CSR=get_value(args.csr),
                               CACERT=get_value(args.cacert), SK=get_value(args.sk), SERVERIP=get_value(args.serverip),
                               SERVERPORT=get_value(args.serverport), CACHAIN=get_value(args.cacert),
                               CERT_REQS=get_value(args.certreq), TIMEZONE=get_value(args.timezone),
                               SYNCTIME=get_value(args.synctime), REFLOWPAN=get_value(args.rflowpan),
                               SYSWAIT=get_value(args.syswait), PAYLOADLEN=get_value(args.payloadlen),
                               DATE=get_value(args.date), SENDTIME=get_value(args.sendtime),
                               SENDRATE=get_value(args.sendrate), DEVNUM=get_value(args.devnum), TYPE='client')
        exp.init_sink_config(exp_config=args.exp_config[1], CAIP=get_value(args.caip), CAPORT=get_value(args.caport),
                             CERT=get_value(args.certpath), CSR=get_value(args.csr),
                             CACERT=get_value(args.cacert), SK=get_value(args.sk), SERVERIP=get_value(args.serverip),
                             SERVERPORT=get_value(args.serverport), CACHAIN=get_value(args.cacert),
                             CERT_REQS=get_value(args.certreq), ROUTER_IP6=get_value(args.router_ip6),
                             CLIENT_IP6=get_value(args.client_ip6), CLIENT_IP4=get_value(args.client_ip4),
                             DATE=get_value(args.date), CLIENT_WKD=get_value(args.client_workdir),
                             ROUTER_WKD=get_value(args.router_workdir), SINK2CLIENT=get_value(args.sink2client),
                             PASSWORD=get_value(args.passwd), USER=get_value(args.user),
                             SINK_INTERFACE=get_value(args.sink_interface), CLIENT_SCRIPT=get_value(args.client_script),
                             TYPE='server')
        exp.analyze()
    elif args.package[0] == 'p87':  # stop experiment
        os.chdir('testbed')
        if args.exp_config is not None:
            if len(args.exp_config) != 2 or args.exp_config[0] == '' or args.exp_config[1] == '':
                print ('Error: you should spcified two configuration files for the testbed configuration. \n'
                       'E.g.,: -exp_config client_config_file sink_config_file'
                       '\nNote: order is important, you should specify client configuration then sink configuration.')
                return
        else:
            args.exp_config = ['client_expcnf', 'sink_expcnf']
        if args.inet is not None:
            args.inet = ['6']
        elif args.inet[0] != '4' and args.inet[0] != '6':
            print ("Error: invalid parameter of \'inet\'. The value should be eigher 4 or 6")
            return
        exp = testbed.setupexp.SetupExp()
        exp.init_client_config(exp_config=args.exp_config[0], CAIP=get_value(args.caip), CAPORT=get_value(args.caport),
                               CERT=get_value(args.certpath), CSR=get_value(args.csr),
                               CACERT=get_value(args.cacert), SK=get_value(args.sk), SERVERIP=get_value(args.serverip),
                               SERVERPORT=get_value(args.serverport), CACHAIN=get_value(args.cacert),
                               CERT_REQS=get_value(args.certreq), TIMEZONE=get_value(args.timezone),
                               SYNCTIME=get_value(args.synctime), REFLOWPAN=get_value(args.rflowpan),
                               SYSWAIT=get_value(args.syswait), PAYLOADLEN=get_value(args.payloadlen),
                               DATE=get_value(args.date), SENDTIME=get_value(args.sendtime),
                               SENDRATE=get_value(args.sendrate), DEVNUM=get_value(args.devnum), TYPE='client')
        exp.init_sink_config(exp_config=args.exp_config[1], CAIP=get_value(args.caip), CAPORT=get_value(args.caport),
                             CERT=get_value(args.certpath), CSR=get_value(args.csr),
                             CACERT=get_value(args.cacert), SK=get_value(args.sk), SERVERIP=get_value(args.serverip),
                             SERVERPORT=get_value(args.serverport), CACHAIN=get_value(args.cacert),
                             CERT_REQS=get_value(args.certreq), ROUTER_IP6=get_value(args.router_ip6),
                             CLIENT_IP6=get_value(args.client_ip6), CLIENT_IP4=get_value(args.client_ip4),
                             DATE=get_value(args.date), CLIENT_WKD=get_value(args.client_workdir),
                             ROUTER_WKD=get_value(args.router_workdir), SINK2CLIENT=get_value(args.sink2client),
                             PASSWORD=get_value(args.passwd), USER=get_value(args.user),
                             SINK_INTERFACE=get_value(args.sink_interface), CLIENT_SCRIPT=get_value(args.client_script),
                             TYPE='server')
        exp.stop(args.inet[0])
    else:
        print('Invalid argument.')


def get_value(inlist):
    if inlist:
        return inlist[0]
    else:
        return None


if __name__ == '__main__':
    main()
