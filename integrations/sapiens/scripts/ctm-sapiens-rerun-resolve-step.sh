#!/bin/bash
# Print Sapiens/Launcher restart step for a failed proc step.
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
export PYTHONPATH="${REPO_ROOT}/sapiens${PYTHONPATH:+:$PYTHONPATH}"

FAILED="${1:-}"
if [[ -z "$FAILED" ]]; then
  echo "Usage: $0 <failedStep>" >&2
  echo "  Examples: STEP.BIND  VALFTP  STEP.RUNSFTP" >&2
  exit 2
fi

exec python3 -m sapiens_ctm resolve-restart "$FAILED"