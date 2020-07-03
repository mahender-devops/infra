#!/bin/sh

export RELSRVC_API_PORT=5000
export RELSRVC_WORK_QUEUE='RelevanceTestRequests'
export RELSRVC_DYNAMODB_TABLE='relevanceService'

# Get AWS credentials to pass to docker container
export AWS_ACCESS_KEY_ID="$(aws --profile Enrich-Jarvis.EnrichTeam.PowerUser configure get aws_access_key_id )"
export AWS_SECRET_ACCESS_KEY="$(aws --profile Enrich-Jarvis.EnrichTeam.PowerUser configure get aws_secret_access_key )"
export AWS_SESSION_TOKEN="$(aws --profile Enrich-Jarvis.EnrichTeam.PowerUser configure get aws_session_token )"
export AWS_DEFAULT_REGION="$(aws --profile Enrich-Jarvis.EnrichTeam.PowerUser configure get region  )"


