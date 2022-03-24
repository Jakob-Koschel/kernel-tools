#!/usr/bin/env python3

# call get_maintainer.pl and chose first as 'to' and the rest as 'cc'
# also also optionally to add more people as 'cc'.

import sys, argparse, re, os
import subprocess


def main():
    opts = argparse.ArgumentParser(description='call git send-email with correct maintainers')
    opts.add_argument('--patches', type=str, required=True, help='Patches to send')
    opts.add_argument('--cc', type=argparse.FileType('r'), help='Additional cc contacts')
    opts.add_argument('--no-print-patches', action='store_true')
    args = opts.parse_args()

    if not os.path.isdir(args.patches):
        print('--patches is not a directory')
        return

    patches = args.patches + '/*'

    result = subprocess.run('./scripts/get_maintainer.pl ' + patches,
            shell=True,
            stdout=subprocess.PIPE)
    print(result.stdout.decode('utf-8'))

    if not args.no_print_patches:
        subprocess.run('pygmentize -g -O style=native,linenos=1 ' + patches,
                shell=True)


    result = subprocess.run('./scripts/get_maintainer.pl --norolestats ' + patches,
            shell=True,
            stdout=subprocess.PIPE)
    maintainers = result.stdout.decode('utf-8').splitlines()
    to = maintainers.pop(0)
    cc = maintainers

    if args.cc:
        with args.cc as file:
            cc.extend(file.read().splitlines())

    cc = ', '.join(cc)

    result = subprocess.run(
            ['git', 'send-email',
                '--to', to,
                '--cc', cc,
                args.patches])

if __name__ == '__main__':
    main()