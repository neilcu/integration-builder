# integration-builder

Generic **Control-M Application Integrator** factory: shared toolkit + per-product folders under `integrations/`. BMC reference plugins (IFAAF, IFADF, IFAHD, IFDBX) inform architecture only — see [references/README.md](references/README.md).

## Layout

```
integrations/sapiens/   # Sapiens ACE batch (scaffold + mock client)
toolkit/                # IFA decode, ctmai encode, dist helpers
docs/                   # Reusable integration patterns
references/             # External IFA / baseline pointers (no vendored JCL)
```

## Quick start (Sapiens mock smoke)

```bash
cd integrations/sapiens
pip install -e .
./scripts/ctm-sapiens-run-scenario.sh ok
```

Build Application Integrator artifacts: [integrations/sapiens/BUILD.md](integrations/sapiens/BUILD.md).

Architecture: [docs/CONTROL-M-INTEGRATION-ARCHITECTURE.md](docs/CONTROL-M-INTEGRATION-ARCHITECTURE.md).

## Origin

Canonical remote: `https://origin.cursor.com/git/neil-cullum/integration-builder.git`

Sapiens / Control-M integration work was **moved out of** `neil-cullum/microfocus-configure` (Micro Focus ES runbook only).
