import sys
import os
import pexpect
import argparse
import getpass
from time import sleep

from common import getch, exec_command, expect

parser = argparse.ArgumentParser(description='pexpect run spectrestar with qemu')
parser.add_argument('--target', dest='target', default="syzkaller", type=str)
parser.add_argument('--gdb', dest='gdb', action='store_const', const=sum)
parser.add_argument('--interactive', '-i', dest='interactive', action='store_const', const=sum)
parser.add_argument('--execprog', dest='execprog', type=str)
args = parser.parse_args()

print('target: {}'.format(args.target))
if args.target == 'syzkaller':
    PROMPT = "root@syzkaller:~#"
else:
    PROMPT = "/ #"

env = os.environ

if args.gdb:
    env['ATTACH_GDB'] = '1'

qemu = pexpect.spawn('scripts/run-qemu.sh {}'.format(args.target),
        env=env,
        encoding='utf-8',
        codec_errors='backslashreplace')
qemu.logfile = sys.stdout

sudo = '\[sudo\] password for jkl:'

# login
if args.target == 'syzkaller':
    index = expect(qemu, ['syzkaller login:', sudo], timeout=None)
    if index == 2: # sudo
        qemu.logfile = None
        password = getpass.getpass(prompt='')
        qemu.sendline(password)
        qemu.logfile = sys.stdout
        # wait again
        expect(qemu, 'syzkaller login:', timeout=None)
        qemu.sendline('root')
    else:
        qemu.sendline('root')

# setup
index = expect(qemu, [PROMPT, sudo], timeout=None)
if index == 2: # sudo
    qemu.logfile = None
    password = getpass.getpass(prompt='')
    qemu.sendline(password)
    qemu.logfile = sys.stdout
    # wait again
    expect(qemu, PROMPT, timeout=None)

qemu.sendline('mount -t debugfs none /sys/kernel/debug')
expect(qemu, PROMPT)
# mount the shared folder if present
if args.target == 'syzkaller':
    qemu.sendline('mkdir /mnt-syzkaller')
    expect(qemu, PROMPT)
    qemu.sendline('mount /dev/sdb1 /mnt-syzkaller')
    expect(qemu, PROMPT)
if os.environ.get('VM_SHARED_FOLDER', None) is not None:
    qemu.sendline('mount /dev/sdc1 /mnt')
    expect(qemu, PROMPT)
sleep(1)

qemu.sendline('alias execprog="/mnt-syzkaller/syz-execprog -executor=/mnt-syzkaller/syz-executor -repeat=0 -procs=1 -cover=1 -debug "')

if args.execprog and args.target == 'syzkaller':
    # somehow there are bugs if the executables are run from the mount
    qemu.sendline('mkdir /syzkaller')
    expect(qemu, PROMPT)
    qemu.sendline('cp /mnt-syzkaller/* /syzkaller')
    expect(qemu, PROMPT)
    qemu.sendline('cd /syzkaller')
    expect(qemu, 'root@syzkaller:/syzkaller#')
    qemu.sendline(f'./syz-execprog -executor=./syz-executor -repeat=0 -procs=1 -cover=1 /mnt/{args.execprog}')
    expect(qemu, PROMPT, timeout=None)

if args.interactive:
    qemu.logfile = None
    qemu.interact()

print('expect successful!')
