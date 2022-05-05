#!/bin/sh

if [ -z "$MONDOO_AGENT_ACCOUNT" ]; then
  echo "The Mondoo service account was not set with the MONDOO_AGENT_ACCOUNT env var in the GitHub action configuration. Cannot continue."
  exit 1
fi

echo ${MONDOO_AGENT_ACCOUNT} | base64 -d > mondoo.json
mondoo scan -t $INPUT_SCAN_TYPE --path $INPUT_PATH --config mondoo.json