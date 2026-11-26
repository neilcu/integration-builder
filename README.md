# integration-builder

Generic **Control-M Application Integrator** factory: shared `toolkit/` plus per-product folders under `integrations/`. BMC reference plugins (IFAAF, IFADF, IFAHD, IFDBX) and the Micro Focus CLI baseline inform **mapping and architecture only** — see [references/README.md](references/README.md).

## Canonical repository

**GitHub:** https://github.com/neilcu/integration-builder (`main`)

Origin (`neil-cullum/integration-builder`) is an optional mirror, not required for development.

## Layout

```
integrations/sapiens/   # Sapiens ACE batch (scaffold + mock client)
toolkit/                # IFA decode, ctmai encode, dist helpers
docs/                   # Reusable integration patterns
references/             # External IFA / baseline pointers (no vendored JCL)
```

## Quick start (Sapiens mock smoke)

```bash
git clone https://github.com/neilcu/integration-builder.git
cd integration-builder/integrations/sapiens
pip install -e .
./scripts/ctm-sapiens-run-scenario.sh ok
```

Build Application Integrator artifacts: [integrations/sapiens/BUILD.md](integrations/sapiens/BUILD.md).

Architecture: [docs/CONTROL-M-INTEGRATION-ARCHITECTURE.md](docs/CONTROL-M-INTEGRATION-ARCHITECTURE.md).

## History

Sapiens / Control-M integration work was **moved out of** `neil-cullum/microfocus-configure` (Micro Focus ES runbook only).
