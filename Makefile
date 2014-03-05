LIBVIRT_HOOKS_DIR=/etc/libvirt/hooks

install:
	mkdir -p ${LIBVIRT_HOOKS_DIR}
	cp qemu qemu.schema.json ${LIBVIRT_HOOKS_DIR}
	if [ ! -f ${LIBVIRT_HOOKS_DIR}/qemu.json ] ; then cp qemu.json ${LIBVIRT_HOOKS_DIR} ; fi
	chmod +x ${LIBVIRT_HOOKS_DIR}/qemu
	service libvirtd restart

clean:
	rm ${LIBVIRT_HOOKS_DIR}/qemu{,.json,.schema.json}
	service libvirtd restart
