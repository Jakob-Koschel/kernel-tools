#!/bin/bash

# Credit goes to: https://gist.github.com/mdawaffe/529e6b3ee820e777c2cfd2f8255d187f
#
# Call like you would for `git diff`
# `./git-diff-changed-lines`
# `./git-diff-changed-lines master...HEAD`
# `./git-diff-changed-lines branch1 branch2`
# etc.

# Outputs the lines numbers of the new file
# that are not present in the old file.
# That is, outputs line numbers for new lines and changed lines
# and does not output line numbers deleted or unchanged lines.

# FORMAT: One file per line
# FILE:LINE_NUMBERS
# Where LINE_NUMBERS is a comma separated list of line numbers

# https://stackoverflow.com/a/246128
SOURCE="${BASH_SOURCE[0]}"
while [ -h "$SOURCE" ]; do # resolve $SOURCE until the file is no longer a symlink
  DIR="$( cd -P "$( dirname "$SOURCE" )" >/dev/null 2>&1 && pwd )"
  SOURCE="$(readlink "$SOURCE")"
  [[ $SOURCE != /* ]] && SOURCE="$DIR/$SOURCE" # if $SOURCE was a relative symlink, we need to resolve it relative to the path where the symlink file was located
done
DIR="$( cd -P "$( dirname "$SOURCE" )" >/dev/null 2>&1 && pwd )"

git difftool --no-prompt --extcmd "$DIR/git-difftool-changed-lines.sh" "$@"
