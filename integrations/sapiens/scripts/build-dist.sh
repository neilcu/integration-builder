#!/bin/bash
# Sapiens bundle: copies AI artifacts + README, then zips (see toolkit/build_dist.sh for generic layout).
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
AI="$ROOT/application-integrator"
DIST="$ROOT/dist/IFSAPIENS.0.1.00_placeholder"
rm -rf "$DIST"
mkdir -p "$DIST"

for f in SAPIENS.ctmai \
  descriptor_SAPIENS.Linux.json \
  descriptor_SAPIENS.Windows.json \
  SAPIENS_plugin.Linux.json \
  SAPIENS_plugin.Windows.json; do
  cp "$AI/$f" "$DIST/$f"
done

cat > "$DIST/README.txt" <<'EOF'
Sapiens ACE Batch — Control-M Application Integrator plugin (scaffold)

Install on EM with Application Integrator >= DRAIT.9.0.20.101.
Import descriptor_SAPIENS.Linux.json (or Windows) and SAPIENS.ctmai.

Job idempotency: Control-M-Idem_%%ORDERID (IFDBX pattern).

Rebuild from repo: see integrations/sapiens/BUILD.md
EOF

(cd "$ROOT/dist" && zip -r -q "IFSAPIENS.0.1.00_placeholder.zip" "$(basename "$DIST")")
echo "DIST=$DIST"
echo "ZIP=$ROOT/dist/IFSAPIENS.0.1.00_placeholder.zip"
ls -la "$DIST" "$ROOT/dist/IFSAPIENS.0.1.00_placeholder.zip"