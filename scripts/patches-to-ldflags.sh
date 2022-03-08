#!/usr/bin/env bash

if [ -z $1 ]; then
  echo "No passes supplied"
  exit 1
fi

PASSES=$1
LD_FLAGS=

IFS=':'
read -a PASSES_ARRAY <<< "$PASSES"

for (( n=0; n < ${#PASSES_ARRAY[*]}; n++))
do
  PASS=${PASSES_ARRAY[n]}
  # extremely ugly way to turn pass-name into PassName
  CAMEL_CASE_PASS=$(sed -E 's/-([a-z])/\U\1/g' <<< $PASS | sed -e "s/\b\(.\)/\u\1/g")
  LD_FLAGS+=" -mllvm=-load=${KERNEL_LLVM_PASSES}/build/${PASS}/LLVM${CAMEL_CASE_PASS}Pass.so"
done

echo $LD_FLAGS
