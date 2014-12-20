#!/usr/bin/env bash

#
# SSH to the server and cd to the current folder
#

ADDR="${1}"
CURR="$PWD"

ssh -t "$ADDR" "cd $CURR && exec bash -l" 

