#!/bin/bash
# Encode a .ctmai.template.json -> base64+gzip .ctmai (IFA / Application Integrator layout).
set -euo pipefail
SRC="${1:?template JSON path}"
OUT="${2:?output .ctmai path}"

python3 - "$SRC" "$OUT" <<'PY'
import base64, gzip, json, pathlib, sys

src = pathlib.Path(sys.argv[1])
out = pathlib.Path(sys.argv[2])
data = json.loads(src.read_text(encoding="utf-8"))
payload = json.dumps(data, separators=(",", ":")).encode("utf-8")
blob = base64.b64encode(gzip.compress(payload))
out.write_bytes(blob)
print(f"Wrote {out} ({out.stat().st_size} bytes)")
PY
