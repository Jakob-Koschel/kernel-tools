#!/usr/bin/env python3

# copy the commit title and commit message from one patch file to all other patches
# this is useful if a commit using the same commit message was split into different
# submodules and you don't need to change all of them manually
#
# Specifically useful to copy the existing cover letter text after rerunning
# format-patch, maybe there are better ways to do that, if so, please let me know ;)

import sys, argparse, re

opts = argparse.ArgumentParser(description='Split single patch by maintainer')
opts.add_argument('template', metavar='TEMPLATE', help='Template patch to copy description and title')
opts.add_argument('patches', metavar='PATCH', nargs='+', help='Patches to update')
args = opts.parse_args()

subject = []
from_name = ''
total_patches = 0
description = []
skip = False
in_description = False
for line in open(args.template):
    if skip:
        if not line.isspace():
            subject.append(line.rstrip())
        else:
            skip = False
        continue
    if line.startswith('From:'):
        p = re.compile("From: (.*) <(.*)>")
        match = p.search(line)
        if match:
            from_name = match.group(1)
    if line.startswith('Subject:'):
        p = re.compile(" (.*)/(.*)]")
        match = p.search(line)
        if match:
            total_patches = int(match.group(2))
        start1 = line.rfind(':')+2
        start2 = line.rfind(']')+2
        start = max(start1, start2)
        subject.append(line[start:].rstrip())
        skip = True
        in_description = True
        continue
    if line.startswith('---'):
        break
    if line.startswith('{} ({}):'.format(from_name, total_patches)):
        break
    if in_description:
        description.append(line)

for patch in args.patches:
    lines = []
    skip = False
    in_description = False
    for line in open(patch):
        if skip:
            if not line.isspace():
                continue
            skip = False
            continue
        if line.startswith('Subject:'):
            # start = line.rfind('[') # used with kees/split-on-maintainer
            start = line.rfind(':')+2
            subject_line = '{}{}\n'.format(line[:start], ''.join(subject))
            lines.append(subject_line)
            skip = True
            in_description = True
            lines.append('\n')
            lines.extend(description)
            continue

        if line.startswith('---'):
            in_description = False
        if line.startswith('{} ({}):'.format(from_name, total_patches)):
            in_description = False
        if in_description:
            continue

        lines.append(line)

    outfile = open(patch, 'w')
    for line in lines:
        outfile.write(line)
    outfile.close()
