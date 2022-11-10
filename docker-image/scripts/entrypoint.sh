#!/bin/sh

set -eu


# We offer to specify optional args to the action
# But when they are not specified, they are passed as an empty string
# This results in an error when passed to cnspec, because it only expects one argument
# Because of that: If the last argument is an empty string, remove it
numArgs=$#
for last_argument in "$@"; do
  true
done
if [ "${last_argument}" = "" ]; then
  echo "Removing last argument, because it is empty"
  echo "before:" "${@}"
  indexSequence=$(seq -s',' 1 ${numArgs})
  set -- $(echo "${@}" | cut -d' ' -f ${indexSequence})
  echo "after:" "${@}"
fi

# Run the action
cnspec "$@"