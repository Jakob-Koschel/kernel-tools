#!/bin/bash

awk --field-separator=":" '{print "vim +"$2" "$1}'
