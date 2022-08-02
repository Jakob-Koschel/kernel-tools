#!/usr/bin/env bash

KERNEL="-kernel ${KERNEL}/arch/x86/boot/bzImage"
APPEND="console=ttyS0 nokaslr nosmp maxcpus=1 rcu_nocbs=0 nmi_watchdog=0 ignore_loglevel modules=sd-mod,usb-storage,ext4 rootfstype=ext4 earlyprintk=serial"
APPEND+=" biosdevname=0 kvm-intel.emulate_invalid_guest_state=1 kvm-intel.enable_apicv=1 kvm-intel.enable_shadow_vmcs=1 kvm-intel.ept=1 kvm-intel.eptad=1 kvm-intel.fasteoi=1 kvm-intel.flexpriority=1 kvm-intel.nested=1 kvm-intel.pml=1 kvm-intel.unrestricted_guest=1 kvm-intel.vmm_exclusive=1 kvm-intel.vpid=1 net.ifnames=0"
MEMORY="8192"
QEMU_SYSTEM_x86_64="${QEMU_SYSTEM_x86_64:=qemu-system-x86_64}"
QEMU_CPU="${QEMU_CPU:=qemu64,+smep,+smap}"

TYPE=$1
if [[ $TYPE = "syzkaller" ]]; then
  RAMDISK=
  HDA="file=${SYZKALLER_IMG}/${SYZKALLER_DISTRIBUTION}.img,format=raw"
  APPEND="${APPEND} root=/dev/sda"
  if [ -n "${SYZKALLER_SSH_PORT}" ]; then
    NET1="nic,model=e1000"
    NET2="user,host=10.0.2.10,hostfwd=tcp::${SYZKALLER_SSH_PORT}-:22"
  fi
  SYZKALLER_BINARIES="-hdb fat:${SYZKALLER_BIN}/linux_amd64"
else
  RAMDISK="${INITRAMFS}"
  HDA=
fi

set -x

$QEMU_SYSTEM_x86_64 \
  ${KERNEL} \
  ${APPEND:+ -append "${APPEND}"} \
  ${RAMDISK:+ -initrd "${RAMDISK}"} \
  ${HDA:+ -drive "${HDA}"} \
  ${ATTACH_GDB:+ -gdb tcp::${GDB_PORT}} \
  ${ATTACH_GDB:+ -S} \
  ${NET1:+ -net ${NET1}} \
  ${NET2:+ -net ${NET2}} \
  ${ENABLE_KVM:+ -enable-kvm} \
  ${SYZKALLER_BINARIES} \
  ${VM_SHARED_FOLDER:+ -hdc fat:"${VM_SHARED_FOLDER}"} \
  -display none \
  -smp 1 \
  -cpu ${QEMU_CPU} \
  -m ${MEMORY} \
  -echr 17 \
  -serial mon:stdio \
  -snapshot \
  -no-reboot
