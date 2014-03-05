Libvirt port-forwarding hook
============================

LibVirt hook for setting up iptables port-forwarding rules when using NAT-ed
networking for qemu domains.


Installation
------------

To install the hook script and it's configuration files, simply use the
:file:`Makefile`:

.. code-block:: bash

    $ sudo make install

Afterwards customize :file:`/etc/libvirt/hooks/qemu.json` to your needs. The
files can be removed again with:

.. code-block:: bash

    $ sudo make clean


Author
------

Sascha Peilicke
