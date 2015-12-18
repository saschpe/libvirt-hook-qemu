Libvirt port-forwarding hook
============================

Libvirt hook for setting up iptables port-forwarding rules when using NAT-ed
networking.


Installation
------------

To install the hook script and it's configuration files, simply use the
:file:`Makefile`:

.. code-block:: bash

    $ sudo make install

Afterwards customize :file:`/etc/libvirt/hooks/qemu.json` to your needs.
This Makefile target can be invoked multiple times, already installed
configuration files won't be touched. The files can be removed again with:

.. code-block:: bash

    $ sudo make clean


Testing
-------

.. code-block:: python

    python -m unittest discover


Networking
----------

This section describes the theory behind the generated iptables statements.
To see a real-world example, the test_setup function (in test_qemu.py)
shows a simple JSON configuration and the iptables rules that it produces.

Packets arriving on the public interface are DNATed to the virtual machine.
This implements the actual port-forwarding.  Due to the way iptables is
implemented, the DNAT must occur in two chains: nat:PREROUTING for packets
arriving on the public interface, and nat:OUTPUT for packets originating on
the host.

We also add rules to the FORWARD chain to ensure the repsonses to the
DNATed packets return to the public IP address.

Finally, packets originating on the guest and sent to the host's public IP
address are lost.  They are DNATed back to the guest like any other packet but,
because the destination is now the same as the source, the reply is swallowed.
Therefore, the host SNATs these packets to ensure the guest sends its reply
back over the bridge.


Author
------

Sascha Peilicke
