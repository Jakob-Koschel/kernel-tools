#!/bin/bash

SCRIPT=$(readlink -f $0)
KERNEL_TOOLS_BIN_PATH=`dirname $SCRIPT`

# dirty hack to execute every line of the output
$KERNEL_TOOLS_BIN_PATH/git-diff-changed-lines.sh HEAD~1 \
  | $KERNEL_TOOLS_BIN_PATH/convert-line-to-vim-cmd.sh > .tmp.txt

bash .tmp.txt
rm .tmp.txt
