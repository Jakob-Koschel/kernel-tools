#!/usr/bin/env bash

if [ -z $1 ]; then
  echo "No passes supplied"
  exit 1
fi

PASSES_ARRAY=( "$@" )
CFLAGS=

for (( n=0; n < ${#PASSES_ARRAY[*]}; n++))
do
  PASS=${PASSES_ARRAY[n]}
  if [[ "$PASS" == "compile:"* ]]; then
    PASS=${PASS#"compile:"}
    # extremely ugly way to turn pass-name into PassName
    CAMEL_CASE_PASS=$(sed -E 's/-([a-z])/\U\1/g' <<< $PASS | sed -e "s/\b\(.\)/\u\1/g")
    CFLAGS+=" -Xclang -load -Xclang ${KERNEL_LLVM_PASSES}/build/${PASS}/LLVM${CAMEL_CASE_PASS}Pass.so"
  fi
done

echo $CFLAGS
