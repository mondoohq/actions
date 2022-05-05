#!/bin/sh

echo ${INPUT_SERVICE_ACCOUNT_CREDENTIALS} | base64 -d > mondoo.json
mondoo scan -t $INPUT_SCAN_TYPE --path $INPUT_PATH --config mondoo.json