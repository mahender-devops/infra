#!/bin/bash

URL=${1}
REQUEST_BODY=${2}

curl --header "Content-Type: application/json" \
  --request POST \
  -d @${REQUEST_BODY} \
  ${URL}/api/start
