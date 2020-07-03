#!/bin/bash

URL=${1}
RQUID="${2}"

curl --header "Content-Type: application/json" \
  --request GET \
  "${URL}/api/status?uid=${RQUID}"
