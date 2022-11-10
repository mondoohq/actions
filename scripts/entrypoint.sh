#!/usr/bin/env bash

set -Eeuo pipefail

# We offer to specify optional args to the action
# But when they are not specified, they are passed as an empty string
# This results in an error when passed to cnspec, because it only expects one argument
# Because of that: If the last argument is an empty string, remove it
if [[ "${@: -1}" == "" ]]; then
  set -- "${@:1:$(($#-1))}"
fi

# Run the action
cnspec "$@"