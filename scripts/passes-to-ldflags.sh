#!/usr/bin/env bash

if [ -z $1 ]; then
  echo "No passes supplied"
  exit 1
fi

PASSES_ARRAY=( "$@" )
LD_FLAGS=

for (( n=0; n < ${#PASSES_ARRAY[*]}; n++))
do
  PASS=${PASSES_ARRAY[n]}
  if [[ "$PASS" == "lto:"* ]]; then
    PASS=${PASS#"lto:"}
    # extremely ugly way to turn pass-name into PassName
    CAMEL_CASE_PASS=$(sed -E 's/-([a-z])/\U\1/g' <<< $PASS | sed -e "s/\b\(.\)/\u\1/g")
    LD_FLAGS+=" -mllvm=-load=${KERNEL_LLVM_PASSES}/build/passes/${PASS}/LLVM${CAMEL_CASE_PASS}Pass.so"
  fi
done

echo $LD_FLAGS
