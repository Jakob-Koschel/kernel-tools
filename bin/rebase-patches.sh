#!/bin/bash

set -e

# pass in directory with .patch files (use at own caution)
PATCHES=$1
REBASE_BRANCH=$2

if [ -z $REBASE_BRANCH ]; then
  REBASE_BRANCH=rebase
fi

git checkout master
git branch -D $REBASE_BRANCH
git checkout -b $REBASE_BRANCH

git am $PATCHES/*.patch
mv $PATCHES $PATCHES.bak
git format-patch --base=origin/master -o $PATCHES origin/master
rm -rf $PATCHES.bak
