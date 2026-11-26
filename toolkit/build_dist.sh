#!/bin/bash
# Assemble an installable Application Integrator bundle directory + zip (IFDBX-style layout).
set -euo pipefail

INTEGRATION_DIR="${1:?integration application-integrator directory}"
BUNDLE_NAME="${2:?bundle folder name under dist/}"
DIST_ROOT="${3:-$(cd "$(dirname "$INTEGRATION_DIR")" && pwd)/dist}"

AI="$(cd "$INTEGRATION_DIR" && pwd)"
DIST="$DIST_ROOT/$BUNDLE_NAME"
rm -rf "$DIST"
mkdir -p "$DIST"

shopt -s nullglob
files=("$AI"/*.ctmai "$AI"/descriptor_*.json "$AI"/*_plugin.*.json)
if ((${#files[@]} == 0)); then
  echo "No bundle artifacts in $AI" >&2
  exit 1
fi
for f in "${files[@]}"; do
  cp "$f" "$DIST/"
done

mkdir -p "$DIST_ROOT"
(cd "$DIST_ROOT" && zip -r -q "${BUNDLE_NAME}.zip" "$BUNDLE_NAME")
echo "DIST=$DIST"
echo "ZIP=$DIST_ROOT/${BUNDLE_NAME}.zip"
ls -la "$DIST" "$DIST_ROOT/${BUNDLE_NAME}.zip"
