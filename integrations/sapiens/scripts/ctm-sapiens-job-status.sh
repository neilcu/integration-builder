#!/bin/bash
# Reconnect validation stub for Sapiens batch (maps ctm-mf-job-status.sh echo pattern).
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
SAPIENS_ROOT="$REPO_ROOT/sapiens"
export PYTHONPATH="${SAPIENS_ROOT}${PYTHONPATH:+:$PYTHONPATH}"

JOB_ID="${1:-}"
if [[ -z "$JOB_ID" ]]; then
  echo "Usage: $0 <jobId>" >&2
  exit 2
fi

set +e
OUTPUT=$(python3 -m sapiens_ctm status "$JOB_ID" 2>&1)
RC=$?
set -e
echo "$OUTPUT"
exit "$RC"