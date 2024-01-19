#!/usr/bin/env python3

import argparse
import json
import os
import subprocess

script_path = os.path.dirname(os.path.realpath(__file__))

def main():
    parser = argparse.ArgumentParser(description='check if autostart config changed and image needs to be modified again')
    parser.add_argument('--target', dest='target', default="syzkaller", type=str)
    parser.add_argument('--execprog', dest='execprog', type=str)
    parser.add_argument('--config', dest='config_file', required=True, type=str)
    args = parser.parse_args()

    if args.target != 'syzkaller':
        return

    json_config = {}
    new_config = {}
    if os.path.exists(args.config_file):
        with open(args.config_file, 'r') as f:
            json_config = json.load(f)

    if args.execprog:
        new_config['execprog'] = args.execprog
    if os.environ.get('QEMU_9P_SHARED_FOLDER', None) is not None:
        new_config['vm_shared_folder'] = True

    if new_config != json_config:
        with open(args.config_file, 'w') as f:
            json.dump(new_config, f)

        # create the autostart.sh
        with open(f"{script_path}/autostart.sh", 'w') as f:
            f.write("#!/bin/bash\n\n")
            f.write('mount -t debugfs none /sys/kernel/debug\n\n')
            f.write("mkdir /mnt-syzkaller\n")
            f.write("mount /dev/sdb1 /mnt-syzkaller\n")

            if 'vm_shared_folder' in new_config:
                f.write('\n')
                f.write('mount -t 9p -o trans=virtio test_mount /mnt -oversion=9p2000.L,posixacl,msize=104857600,cache=loose\n')

            if 'execprog' in new_config:
                execprog = new_config['execprog']
                f.write('\n')
                f.write('mkdir /syzkaller\n')
                f.write('cp /mnt-syzkaller/* /syzkaller\n')
                f.write('cd /syzkaller\n')
                f.write(f'./syz-execprog -executor=./syz-executor -repeat=0 -procs=1 -cover=1 /mnt/{execprog}\n')

    subprocess.run(['bash', f"{script_path}/install-autostart.sh"])

if __name__ == '__main__':
    main()
