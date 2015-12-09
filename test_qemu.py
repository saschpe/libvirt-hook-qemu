import imp
import json
import os
import socket
import sys
import unittest

qemu = imp.load_source('qemu', 'qemu')


class QemuTestCase(unittest.TestCase):
    def test_host_ip(self):
        host_ip = qemu.host_ip()
        try:
            socket.inet_aton(host_ip)
        except socket.error:
            pass  # Not legal

    def test_config(self):
        conf = qemu.config(validate=False)
        del qemu.config._conf  # Revert closure

    def test_config_schema_validation(self):
        conf = qemu.config()
        del qemu.config._conf  # Revert closure

    def test_setup(self):
        port_map = {
            "tcp": [[80, 8080], 443]
        }

        qemu.IPTABLES_BINARY = '/bin/echo'
        outfile = "/tmp/ttp"
        orig = os.dup(sys.stdout.fileno())
        try:
            to = open(outfile, "w")
            os.dup2(to.fileno(), sys.stdout.fileno())
            qemu.start_forwarding(port_map, "DNAT-test", "FWD-test", "192.168.1.1", "127.0.0.1")
        finally:
            sys.stdout.flush()
            os.dup2(orig, sys.stdout.fileno())

    def test_teardown(self):
        pass
