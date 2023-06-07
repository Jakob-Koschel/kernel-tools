#!/usr/bin/env bash

if [ -z $1 ]; then
  echo "No passes supplied"
  exit 1
fi

REPOS=( $REPOS )

PASSES_ARRAY=( "$@" )
CFLAGS=

for (( n=0; n < ${#PASSES_ARRAY[*]}; n++))
do
  PASS=${PASSES_ARRAY[n]}
  if [[ "$PASS" == "compile:"* ]]; then
    PASS=${PASS#"compile:"}

    IFS=':' read -a PASS_ARRAY <<< $PASS
    if [[ ${#PASS_ARRAY[*]} == 1 ]]; then
      # if no repo was supplied ensure that there is only one repo
      if [[ ${#REPOS[*]} == 1 ]]; then
        PASS_REPO=`basename ${REPOS[0]}`
      else
        echo "with multiple REPOS it needs to be specified"
        exit 1
      fi
    else
      # take repo from argument
      PASS=${PASS_ARRAY[1]}
      PASS_REPO=${PASS_ARRAY[0]}
    fi

    # find repo based on repo:pass
    for (( r=0; r < ${#REPOS[*]}; r++))
    do
      BASENAME=`basename ${REPOS[r]}`
      if [[ $BASENAME == $PASS_REPO ]]; then
        REPO=${REPOS[r]}
      fi
    done

    if [ -z $REPO ]; then
      echo "Couldn't find correct REPO"
      exit 1
    fi


    TMP_PASS_NAME="${PASS%%(*}"
    ARGUMENTS="${PASS#$TMP_PASS_NAME}"
    PASS=$TMP_PASS_NAME

    # remove leading '(' and trailing ')'
    ARGUMENTS="${ARGUMENTS#\(}"
    ARGUMENTS="${ARGUMENTS%\)}"
    PASS_ARGUMENTS=""
    for arg in $ARGUMENTS; do
      PASS_ARGUMENTS+=" -mllvm $arg"
    done

    # extremely ugly way to turn pass-name into PassName
    CAMEL_CASE_PASS=$(sed -E 's/-([a-z])/\U\1/g' <<< $PASS | sed -e "s/\b\(.\)/\u\1/g")

    PASS_PATH=${REPO}/build/passes/${PASS}/LLVM${CAMEL_CASE_PASS}Pass.so
    if [ ! -f ${PASS_PATH} ]; then
      PASS_PATH=${REPO}/build/${PASS}/LLVM${CAMEL_CASE_PASS}Pass.so
      if [ ! -f ${PASS_PATH} ]; then
        echo "[KERNEL TOOLS] couldn't find PASS :("
        exit 1
      fi
    fi

    CFLAGS+=" -Xclang -load -Xclang ${PASS_PATH} -fpass-plugin=${PASS_PATH} ${PASS_ARGUMENTS}"
  fi
done

echo $CFLAGS
