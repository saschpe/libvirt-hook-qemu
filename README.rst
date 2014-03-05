Libvirt port-forwarding hook
============================

LibVirt hook for setting up iptables port-forwarding rules when using NAT-ed
networking for qemu domains.


Installation
------------

To install the hooks script, you may have to create the appropriate directory
first:

.. code-block:: bash

    $ sudo mkdir -p /etc/libvirt/hooks

Afterwards, just copy the script and the example configuration file into
:file:`/etc/libvirt/hooks` and set the executable bit: 

.. code-block:: bash

    $ sudo cp qemu qemu.json /etc/libvirt/hooks/
    $ sudo chmod +x /etc/libvirt/hooks/qemu

Make sure to customize :file:`/etc/libvirt/hooks/qemu.json` to your needs.
Finally, restart libvirt:

.. code-block:: bash

    $ sudo service libvirtd restart

This should work across distros, otherwise use rclibvirtd or systemd.


Author
------

Sascha Peilicke
