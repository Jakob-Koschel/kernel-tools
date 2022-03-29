#!/bin/bash

set -e

# pass in directory with .patch files (use at own caution)
PATCHES=$1

git checkout master
git branch -D rebase
git checkout -b rebase

git am $PATCHES/*.patch
mv $PATCHES $PATCHES.bak
git format-patch --base=origin/master -o $PATCHES origin/master
rm -rf $PATCHES.bak
