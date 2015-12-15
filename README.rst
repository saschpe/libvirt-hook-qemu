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


Author
------

Sascha Peilicke
