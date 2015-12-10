import imp
import json
import os
import socket
import sys
import textwrap
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

    def capture_output(self, func):
        outfile = "/tmp/libvirt-hook-qemu-test-output.txt"
        orig_binary = qemu.IPTABLES_BINARY
        orig_out = os.dup(sys.stdout.fileno())

        try:
            qemu.IPTABLES_BINARY = '/bin/echo'
            to = open(outfile, "w")
            os.dup2(to.fileno(), sys.stdout.fileno())
            func()
        finally:
            sys.stdout.flush()
            os.dup2(orig_out, sys.stdout.fileno())
            qemu.IPTABLES_BINARY = orig_binary

        output = open(outfile).read()
        os.remove(outfile)
        return output

    def test_setup(self):
        port_map = {
            "udp": [53],
            "tcp": [[80, 8080], 443]
        }

        expected_output = textwrap.dedent("""
            -t nat -N DNAT-test
            -t filter -N FWD-test
            -t nat -A DNAT-test -p udp -d 192.168.1.1 --dport 53 -j DNAT --to 127.0.0.1:53
            -t filter -A FWD-test -p udp -d 127.0.0.1 --dport 53 -j ACCEPT
            -t nat -A DNAT-test -p tcp -d 192.168.1.1 --dport 80 -j DNAT --to 127.0.0.1:8080
            -t filter -A FWD-test -p tcp -d 127.0.0.1 --dport 8080 -j ACCEPT
            -t nat -A DNAT-test -p tcp -d 192.168.1.1 --dport 443 -j DNAT --to 127.0.0.1:443
            -t filter -A FWD-test -p tcp -d 127.0.0.1 --dport 443 -j ACCEPT
            -t nat -I OUTPUT -d 192.168.1.1 -j DNAT-test
            -t nat -I PREROUTING -d 192.168.1.1 -j DNAT-test
            -t filter -I FORWARD -d 127.0.0.1 -j FWD-test
        """[1:])

        def test_func():
            qemu.start_forwarding(port_map, "DNAT-test", "FWD-test", "192.168.1.1", "127.0.0.1")

        output = self.capture_output(test_func)
        self.maxDiff = None
        self.assertMultiLineEqual(output, expected_output)

    def test_teardown(self):
        expected_output = textwrap.dedent("""
            -t nat -D OUTPUT -d 192.168.1.1 -j DNAT-test
            -t nat -D PREROUTING -d 192.168.1.1 -j DNAT-test
            -t filter -D FORWARD -d 127.0.0.1 -j FWD-test
            -t nat -F DNAT-test
            -t nat -X DNAT-test
            -t filter -F FWD-test
            -t filter -X FWD-test
        """[1:])

        def test_func():
            qemu.stop_forwarding("DNAT-test", "FWD-test", "192.168.1.1", "127.0.0.1")

        output = self.capture_output(test_func)
        self.maxDiff = None
        self.assertMultiLineEqual(output, expected_output)
