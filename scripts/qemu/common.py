import sys
import os
import argparse
import subprocess
import pexpect
from time import sleep

def getch():
    import sys, tty, termios
    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)
    try:
        tty.setraw(sys.stdin.fileno())
        ch = sys.stdin.read(1)
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
    return ch

def expect(qemu, expect, kill_on_timeout=True, kill_on_panic=True, timeout=30):
    if type(expect) != list:
        expect = [expect]
    i = qemu.expect([pexpect.TIMEOUT] + expect,
        timeout=timeout)
    if i == 0 and kill_on_timeout:
        print('TIMEOUT')
        sys.exit(-1)
    if i >= len([pexpect.TIMEOUT] + expect) and kill_on_panic:
        print('PANIC')
        sys.exit(-1)
    return i

def exec_command(command):
    process = subprocess.Popen(command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE)
    stdout, stderr = process.communicate()
    if stderr:
        print('error: {}'.format(stderr))
        return None
    return stdout.decode("utf-8").splitlines()
