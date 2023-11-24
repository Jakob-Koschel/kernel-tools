#!/usr/bin/env bash

set -e

SCRIPTPATH="$( cd -- "$(dirname "$0")" >/dev/null 2>&1 ; pwd -P )"
AUTOSTART_PATH="$SCRIPTPATH/../autostart"
OUT_PATH="$SCRIPTPATH/../out"
AUTOSTART_MAKE="$OUT_PATH/autostart-make"

cd $AUTOSTART_PATH

# The poor man's make. We use the last built /tmp/autostart to track if any
# of the source file has changed. Only if one changed, rebuild and install.
if [ ${AUTOSTART_MAKE} -nt autostart.c ] && \
  [ ${AUTOSTART_MAKE} -nt autostart.sh ] &&
  [ ${AUTOSTART_MAKE} -nt autostart.service ] &&
  [ ${AUTOSTART_MAKE} -nt bashrc ]; then
  exit 0
fi


if test -f autostart.c; then
  clang autostart.c -static -o $OUT_PATH/autostart
  INSTALL_AUTOSTART_C="
    upload $OUT_PATH/autostart /usr/bin/autostart
    chmod 755 /usr/bin/autostart"
fi

if test -f autostart.sh; then
  INSTALL_AUTOSTART_SH="
    upload autostart.sh /usr/bin/autostart.sh
    chmod 755 /usr/bin/autostart.sh"
fi

INSTALL_BASHRC="
  upload bashrc /root/.bashrc"

unreadable_vmlinuz=$(find /boot -maxdepth 1 -type f -name 'vmlinuz-*' ! -readable)
if [[ -n $unreadable_vmlinuz ]]; then
  echo "Make sure kernel is readable"
  sudo chmod +r /boot/vmlinuz-*
fi

echo Installing autostart on `basename ${IMAGE_PATH}`
guestfish --rw -a "${IMAGE_PATH}" << EOF
  run
  mount /dev/sda /

  ${INSTALL_AUTOSTART_C}
  ${INSTALL_AUTOSTART_SH}
  ${INSTALL_BASHRC}

  upload autostart.service /lib/systemd/system/autostart.service
  ln-sf /lib/systemd/system/autostart.sh /etc/systemd/system/multi-user.target.wants/autostart.service
EOF

echo $(date) > $AUTOSTART_MAKE
