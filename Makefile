LIBVIRT_HOOKS_DIR=/etc/libvirt/hooks

install:
	mkdir -p ${LIBVIRT_HOOKS_DIR}
	cp qemu qemu.json qemu.schema.json ${LIBVIRT_HOOKS_DIR}
	chmod +x ${LIBVIRT_HOOKS_DIR}/qemu
	service libvirtd restart

clean:
	rm ${LIBVIRT_HOOKS_DIR}/qemu{,.json,.schema.json}
	service libvirtd restart
