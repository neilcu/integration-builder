#!/bin/bash
# Run a named Control-M / Sapiens batch scenario (mock or live ACE Runtime).
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
SAPIENS_ROOT="$REPO_ROOT/sapiens"
RESOLVE="$SAPIENS_ROOT/scripts/ctm-sapiens-rerun-resolve-step.sh"
STATUS="$SAPIENS_ROOT/scripts/ctm-sapiens-job-status.sh"

usage() {
  cat <<EOF
Usage: $0 <scenario>

Scenarios (parity with ctm-run-scenario.sh):
  ok            Full pipeline success
  fail-bind     Fail STEP.BIND
  fail-valftp   Fail STEP.VALFTP
  fail-runsftp  Fail STEP.RUNSFTP
  fail-ddl      Fail STEP.DDL3BIND
  rerun-bind    Rerun fragment from DDL3BIND
  rerun-valftp  Rerun fragment from FTPBA
  rerun-runsftp Rerun fragment from U4BARA01
  map <step>    Print Launcher restart step only

Environment:
  SAPIENS_USE_MOCK=1 (default) uses in-process mock backend.
  Set SAPIENS_USE_MOCK=0 and SAPIENS_BASE_URL for live ACE Runtime.

EOF
  exit 2
}

[[ $# -lt 1 ]] && usage

SCENARIO="$1"
case "$SCENARIO" in
  ok|fail-bind|fail-valftp|fail-runsftp|fail-ddl|rerun-bind|rerun-valftp|rerun-runsftp) ;;
  map)
    shift
    [[ $# -eq 1 ]] || usage
    "$RESOLVE" "$1"
    exit 0
    ;;
  *) usage ;;
esac

echo "=== Submit scenario=$SCENARIO ==="
export PYTHONPATH="${SAPIENS_ROOT}${PYTHONPATH:+:$PYTHONPATH}"
set +e
OUTPUT=$(python3 -m sapiens_ctm submit --scenario "$SCENARIO" 2>&1)
RC=$?
set -e
echo "$OUTPUT"
echo "=== sapiens submit exit RC=$RC ==="

JOB_ID=$(echo "$OUTPUT" | awk -F= '/^JOB_ID=/{print $2}')
if [[ -n "$JOB_ID" && -x "$STATUS" ]] || [[ -n "$JOB_ID" && -f "$STATUS" ]]; then
  "$STATUS" "$JOB_ID" || true
fi

case "$SCENARIO" in
  fail-bind)    echo "Launcher should restart at: $("$RESOLVE" STEP.BIND)" ;;
  fail-valftp)  echo "Launcher should restart at: $("$RESOLVE" STEP.VALFTP)" ;;
  fail-runsftp) echo "Launcher should restart at: $("$RESOLVE" STEP.RUNSFTP)" ;;
  fail-ddl)     echo "Launcher should restart at: STEP.DDL3BIND (default = failed step)" ;;
esac

exit "$RC"