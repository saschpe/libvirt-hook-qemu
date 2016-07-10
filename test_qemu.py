#!/usr/bin/python

import imp
import json
import os
import socket
import sys
import textwrap
import unittest

qemu = imp.load_source('hooks', 'hooks')


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

    def dedent(self, str):
        return textwrap.dedent(str[1:])

    def test_setup(self):
        port_map = {
            "udp": [53],
            "tcp": [[80, 8080], 443]
        }

        # in this test, public_ip is 192.168.1.1 and private_ip is 127.0.0.1
        expected_output = self.dedent("""
            -t nat -N DNAT-test
            -t nat -N SNAT-test
            -t filter -N FWD-test
            -t nat -A DNAT-test -p udp -d 192.168.1.1 --dport 53 -j DNAT --to 127.0.0.1:53
            -t nat -A SNAT-test -p udp -s 127.0.0.1 -d 127.0.0.1 --dport 53 -j MASQUERADE
            -t filter -A FWD-test -p udp -d 127.0.0.1 --dport 53 -j ACCEPT -o virbr0
            -t nat -A DNAT-test -p tcp -d 192.168.1.1 --dport 80 -j DNAT --to 127.0.0.1:8080
            -t nat -A SNAT-test -p tcp -s 127.0.0.1 -d 127.0.0.1 --dport 80 -j MASQUERADE
            -t filter -A FWD-test -p tcp -d 127.0.0.1 --dport 8080 -j ACCEPT -o virbr0
            -t nat -A DNAT-test -p tcp -d 192.168.1.1 --dport 443 -j DNAT --to 127.0.0.1:443
            -t nat -A SNAT-test -p tcp -s 127.0.0.1 -d 127.0.0.1 --dport 443 -j MASQUERADE
            -t filter -A FWD-test -p tcp -d 127.0.0.1 --dport 443 -j ACCEPT -o virbr0
            -t nat -I OUTPUT -d 192.168.1.1 -j DNAT-test
            -t nat -I PREROUTING -d 192.168.1.1 -j DNAT-test
            -t nat -I POSTROUTING -s 127.0.0.1 -d 127.0.0.1 -j SNAT-test
            -t filter -I FORWARD -d 127.0.0.1 -j FWD-test
        """)

        # stub out the disable_bridge_filtering call
        self.bridge_nf = False
        def disable_bridge_filtering():
            self.bridge_nf = True
        self.old_bridge_filtering = qemu.disable_bridge_filtering
        qemu.disable_bridge_filtering = disable_bridge_filtering

        def test_func():
            domain = { "port_map": port_map, "interface": "virbr0" }
            qemu.start_forwarding("DNAT-test", "SNAT-test", "FWD-test", "192.168.1.1", "127.0.0.1", domain)

        output = self.capture_output(test_func)
        self.maxDiff = None
        self.assertMultiLineEqual(output, expected_output)
        self.assertTrue(self.bridge_nf)

        qemu.disable_bridge_filtering = self.old_bridge_filtering

    def test_teardown(self):
        expected_output = self.dedent("""
            -t nat -D OUTPUT -d 192.168.1.1 -j DNAT-test
            -t nat -D PREROUTING -d 192.168.1.1 -j DNAT-test
            -t nat -D POSTROUTING -s 127.0.0.1 -d 127.0.0.1 -j SNAT-test
            -t filter -D FORWARD -d 127.0.0.1 -j FWD-test
            -t nat -F DNAT-test
            -t nat -X DNAT-test
            -t nat -F SNAT-test
            -t nat -X SNAT-test
            -t filter -F FWD-test
            -t filter -X FWD-test
        """)

        def test_func():
            qemu.stop_forwarding("DNAT-test", "SNAT-test", "FWD-test", "192.168.1.1", "127.0.0.1")

        output = self.capture_output(test_func)
        self.maxDiff = None
        self.assertMultiLineEqual(output, expected_output)
