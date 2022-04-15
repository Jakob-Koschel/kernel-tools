#!/usr/bin/env python3

# call get_maintainer.pl and chose first as 'to' and the rest as 'cc'
# also also optionally to add more people as 'cc'.

import sys, argparse, re, os
from os.path import isfile, join
import subprocess


def main():
    opts = argparse.ArgumentParser(description='call git send-email with correct maintainers')
    opts.add_argument('--patches', type=str, required=True, help='Patches to send')
    opts.add_argument('--cc', type=argparse.FileType('r'), help='Additional cc contacts')
    opts.add_argument('--ignore-cc', type=argparse.FileType('r'), help='Contacts to be blacklisted from cc (can be used for no longer valid emails)')
    opts.add_argument('--no-print-patches', action='store_true')
    opts.add_argument('--to', help='If specified only send to "to"')
    args = opts.parse_args()

    if not os.path.isdir(args.patches):
        print('--patches is not a directory')
        return

    patches = args.patches + '/*'

    if not args.to:
        result = subprocess.run('./scripts/get_maintainer.pl ' + patches,
                shell=True,
                stdout=subprocess.PIPE)
        print(result.stdout.decode('utf-8'))

    if not args.no_print_patches:
        patchfiles = [f for f in os.listdir(args.patches) if isfile(join(args.patches, f))]
        patchfiles.sort()
        for patchfile in patchfiles:
            subprocess.run('pygmentize -g -O style=native,linenos=1 ' + join(args.patches, patchfile),
                    shell=True)


    additional_cmds = []
    if args.to:
        to = args.to
        cc = ''
        additional_cmds = ['--suppress-cc=all']
    else:
        result = subprocess.run('./scripts/get_maintainer.pl --norolestats ' + patches,
                shell=True,
                stdout=subprocess.PIPE)
        maintainers = result.stdout.decode('utf-8').splitlines()
        to = maintainers.pop(0)
        cc = maintainers

        if args.cc:
            with args.cc as file:
                cc.extend(file.read().splitlines())

        if args.ignore_cc:
            ignore_cc = []
            with args.ignore_cc as file:
                ignore_cc.extend(file.read().splitlines())
            cc = [x for x in cc if x not in ignore_cc]
        cc = ', '.join(cc)

    cmd = ['git', 'send-email', '--to', to, '--cc', cc]
    cmd.extend(additional_cmds)
    cmd.append(args.patches)
    result = subprocess.run(cmd)

if __name__ == '__main__':
    main()
