# Build: Sapiens Control-M scaffold (Linux agent)

Prerequisites: Python 3.9+, reference IFA zips under `/cursor/stores/self/media/` (for template regeneration).

## 1. Regenerate Application Integrator payload

From repo root or this directory:

```bash
cd integrations/sapiens
python3 application-integrator/regenerate-template-from-ifa.py
```

This runs, in order:

1. `build_sapiens_template_from_ifa.py` — clones cmd structure from IFAAF/IFADF/IFDBX → `application-integrator/SAPIENS.ctmai.template.json`
2. `application-integrator/build-ctmai.sh` — calls `toolkit/build_ctmai.sh` → `application-integrator/SAPIENS.ctmai`

One-shot template build only (if decoded JSON already on disk):

```bash
python3 application-integrator/build_sapiens_template_from_ifa.py
./application-integrator/build-ctmai.sh
```

## 2. Python client (editable install)

```bash
cd integrations/sapiens
pip install -e .
python3 -m sapiens_ctm submit --scenario ok
```

CLI entry point: `sapiens-ctm` (same module as `python3 -m sapiens_ctm`).

Environment: copy `config/sapiens-env.example`; default `SAPIENS_USE_MOCK=1` (no Sapiens credentials).

## 3. Shell smoke scenarios (Control-M parity)

```bash
cd integrations/sapiens
chmod +x scripts/*.sh application-integrator/*.sh application-integrator/*.py

./scripts/ctm-sapiens-run-scenario.sh ok              # expect RC 0
./scripts/ctm-sapiens-run-scenario.sh fail-bind       # expect RC 3
./scripts/ctm-sapiens-run-scenario.sh rerun-bind      # expect RC 0
```

Full matrix:

| Scenario | Expected RC |
|----------|-------------|
| `ok`, `rerun-*` | 0 |
| `fail-*` | 3 |

```bash
for s in ok fail-bind fail-valftp fail-runsftp fail-ddl rerun-bind rerun-valftp rerun-runsftp; do
  ./scripts/ctm-sapiens-run-scenario.sh "$s"; echo "$s RC=$?"
done
```

Expected: `ok` and `rerun-*` → RC **0**; `fail-*` → RC **3**. See `control-m/examples/scenarios-manifest.json`.

## 4. Installable plugin bundle (IFDBX layout)

```bash
./scripts/build-dist.sh
```

Outputs:

- `dist/IFSAPIENS.0.1.00_placeholder/` — `SAPIENS.ctmai`, descriptors, plugin JSON
- `dist/IFSAPIENS.0.1.00_placeholder.zip` — zip for EM import testing

## 5. Related docs

- Operator guide: [README.md](README.md)
- Factory patterns: [../../docs/CONTROL-M-INTEGRATION-ARCHITECTURE.md](../../docs/CONTROL-M-INTEGRATION-ARCHITECTURE.md)
