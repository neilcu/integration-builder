#!/bin/bash
set -euo pipefail
DIR="$(cd "$(dirname "$0")" && pwd)"
REPO="$(cd "$DIR/../../.." && pwd)"
exec "$REPO/toolkit/build_ctmai.sh" "$DIR/SAPIENS.ctmai.template.json" "$DIR/SAPIENS.ctmai"