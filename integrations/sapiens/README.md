# Sapiens Control-M integration (scaffold)

HTTP / **Application Integrator** integration to **Sapiens ACE Runtime**, with mock backend for offline testing. Mirrors Neil's Micro Focus CLI scenarios and the **IFDBX** Databricks plugin layout.

## Quick start (mock, no credentials)

```bash
cd integrations/sapiens
chmod +x scripts/*.sh application-integrator/build-ctmai.sh

# Scenario driver (parity with scripts/ctm-run-scenario.sh)
./scripts/ctm-sapiens-run-scenario.sh ok
./scripts/ctm-sapiens-run-scenario.sh fail-bind

# Direct CLI
PYTHONPATH=. python3 -m sapiens_ctm submit --scenario fail-bind
./scripts/ctm-sapiens-job-status.sh <JOB_ID from output>

# Launcher mapping
./scripts/ctm-sapiens-rerun-resolve-step.sh STEP.BIND
```

Expected: `fail-*` exits **3**, `ok` and `rerun-*` exit **0** (aligned with Control-M agent exit-code conventions; MF CLI baseline lives in `microfocus-configure`).

**Note:** The in-process mock resets per CLI invocation, so a separate `job-status` call immediately after `submit` may show `STATUS=UNKNOWN` until live ACE or a persistent mock store is used.

## Layout

| Path | Purpose |
|------|---------|
| `sapiens_ctm/` | Python client + CLI (`python -m sapiens_ctm`) |
| `scripts/` | Thin bash wrappers for Control-M command jobs |
| `config/` | Env example, rerun step map |
| `openapi/` | Placeholder OpenAPI (replace with customer ACE export) |
| `application-integrator/` | `SAPIENS.ctmai` template, descriptors, `build-ctmai.sh` |
| `control-m/examples/` | Sample AI + command job JSON |

Design: [docs/CONTROL-M-INTEGRATION-ARCHITECTURE.md](../../docs/CONTROL-M-INTEGRATION-ARCHITECTURE.md).  
**Build / smoke:** [BUILD.md](BUILD.md).

## Environment

Copy [`config/sapiens-env.example`](config/sapiens-env.example). Key variables:

| Variable | Default | Notes |
|----------|---------|-------|
| `SAPIENS_USE_MOCK` | `1` | Set `0` for live ACE |
| `SAPIENS_BASE_URL` | placeholder host | Customer ACE Runtime URL |
| `SAPIENS_AUTH_MODE` | `api_key` | `none`, `api_key`, `oauth_client_credentials` |
| `SAPIENS_IDEMPOTENCY_KEY` | — | e.g. `Control-M-Idem_<orderid>` |

Install optional deps: `pip install -e '.[http]'` (stdlib-only for mock).

## Application Integrator plugin

**Prerequisite:** MinAI **DRAIT.9.0.20.101** (same as IFAAF / IFADF / IFAHD / IFDBX).

Template cmd layout is cloned from decoded **IFAAF** (submit + poll) and **IFADF** (OAuth pre-execute). Reference zips live in Project store `media/`.

1. Regenerate from IFA zips: `python3 application-integrator/regenerate-template-from-ifa.py`
2. Or edit `application-integrator/SAPIENS.ctmai.template.json` in AI Designer, then `./application-integrator/build-ctmai.sh` → `SAPIENS.ctmai`.
3. Install via EM plugin import (descriptor `descriptor_SAPIENS.Linux.json` or Windows variant).
4. Set job **Idempotency Token** to `Control-M-Idem_%%ORDERID` (IFDBX ReadMe pattern).

## Control-M job types

| Mode | When |
|------|------|
| **Application Integrator REST** | Production (target) |
| **Command** `python -m sapiens_ctm` | Dev / agent-only sites |

Examples: [`control-m/examples/`](control-m/examples/).

## Operators

- **Submit:** AI job or `submit --scenario <name>`.
- **Reconnect:** `ctm-sapiens-job-status.sh <jobId>` → `STATUS=OK|ERROR|RUNNING|UNKNOWN`.
- **Rerun:** Use Launcher restart step from map; set scenario to matching `rerun-*` or pass `restartFromStep` in ACE flow (customer).

## Developers

- Extend `SapiensClient._request` paths when customer OpenAPI is available.
- Keep exit codes in sync with `sapiens_ctm/exit_codes.py` and AI `returnCodeRules`.
- Regenerate `SAPIENS.ctmai` after template edits; do not hand-edit binary `.ctmai`.