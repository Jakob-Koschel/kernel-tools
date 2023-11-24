#!/usr/bin/env bash

set -e

SCRIPTPATH="$( cd -- "$(dirname "$0")" >/dev/null 2>&1 ; pwd -P )"
RUN_QEMU_SCRIPT="$SCRIPTPATH/../qemu-tools/scripts/run-qemu.sh"

KERNEL="${KERNEL}/arch/x86/boot/bzImage"
APPEND="console=ttyS0 nokaslr nosmp maxcpus=1 rcu_nocbs=0 nmi_watchdog=0 ignore_loglevel modules=sd-mod,usb-storage,ext4 rootfstype=ext4 earlyprintk=serial"
APPEND+=" biosdevname=0 kvm-intel.emulate_invalid_guest_state=1 kvm-intel.enable_apicv=1 kvm-intel.enable_shadow_vmcs=1 kvm-intel.ept=1 kvm-intel.eptad=1 kvm-intel.fasteoi=1 kvm-intel.flexpriority=1 kvm-intel.nested=1 kvm-intel.pml=1 kvm-intel.unrestricted_guest=1 kvm-intel.vmm_exclusive=1 kvm-intel.vpid=1 net.ifnames=0"
QEMU_MEMORY="${QEMU_MEMORY:=16384}"
QEMU_SYSTEM_x86_64="${QEMU_SYSTEM_x86_64:=qemu-system-x86_64}"
QEMU_CPU="${QEMU_CPU:=qemu64,+smep,+smap}"
ENABLE_SNAPSHOT=1
ARCH="x86_64"

TYPE=$1
if [[ $TYPE = "syzkaller" ]]; then
  INITRD=
  DRIVE="file=${SYZKALLER_IMG}/${SYZKALLER_DISTRIBUTION}.img,format=raw"
  APPEND="${APPEND} root=/dev/sda"
  if [ -n "${SYZKALLER_SSH_PORT}" ]; then
    NET1="nic,model=e1000"
    NET2="user,host=10.0.2.10,hostfwd=tcp::${SYZKALLER_SSH_PORT}-:22"
  fi
  HDB="fat:${SYZKALLER_BIN}/linux_amd64"
else
  INITRD="${INITRAMFS}"
  DRIVE=
fi

. "$RUN_QEMU_SCRIPT"
