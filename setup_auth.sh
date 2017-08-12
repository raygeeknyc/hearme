#!/bin/bash
echo "authenticating"
GOOGLE_APPLICATION_CREDENTIALS=../ohgee-923e3db09269.json
if [[ ! -r "$GOOGLE_APPLICATION_CREDENTIALS" ]]; then
  echo "falling back to interactive authentication"
  gcloud auth application-default login
else
  export GOOGLE_APPLICATION_CREDENTIALS
  export GOOGLE_CLOUD_PROJECT=ohgee-176600
fi
echo "authenticated"
