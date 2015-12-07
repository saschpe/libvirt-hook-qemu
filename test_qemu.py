import imp
import json
import socket
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
