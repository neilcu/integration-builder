# Control-M Application Integrator integration factory

Reusable patterns for building **REST Application Integrator** job types (`.ctmai` + descriptors). Reference BMC packages (**IFAAF**, **IFADF**, **IFAHD**, **IFDBX**) supply **structure only** — decoded in the Project store, not committed here. See [references/README.md](../references/README.md).

## Repository layout

| Path | Role |
|------|------|
| `integrations/<product>/` | One customer/product plugin + optional dev client |
| `toolkit/` | IFA zip decode, `build_ctmai.sh`, generic dist helper |
| `docs/` | Cross-integration architecture (this file) |
| `references/` | Pointers to external IFA zips and non-vendored baselines |

**First integration:** [`integrations/sapiens/`](../integrations/sapiens/README.md) — Sapiens ACE batch (placeholder OpenAPI + mock CLI).

## IFA reference matrix (patterns only)

| Package | Product | Ops metaphor | Typical reuse |
|---------|---------|--------------|---------------|
| **IFAAF** | Airflow | `POST` submit → `GET` poll | Long-running batch with status field |
| **IFADF** | Azure Data Factory | OAuth pre-exec, reruns | Token + `RerunStepPairs` |
| **IFAHD** | HDInsight | Basic auth REST | Thin submit/poll when no OAuth |
| **IFDBX** | Databricks | OAuth OIDC, idempotency | `Control-M-Idem_%%ORDERID`, dual `restURLs` |

**Mechanism:** `executionTypes[].ops[]` phases (`pre-execute`, `execute`, `post-execute`) with REST `cmds[]`, `extractInfo` / JSONPath → runtime output variables, `handleRc`, retries.

## Agent shell vs Application Integrator

| Concern | Agent command job | Application Integrator |
|---------|-------------------|-------------------------|
| Submit | Shell / script | REST op in `.ctmai` |
| Status | Log grep / script exit | Poll REST + output vars |
| Auth | OS / local secrets | Connection profile + OAuth pre-op |
| Rerun | Launcher step map | Same map + AI `RerunStepPairs` / job vars |
| Production | Dev / fallback | Target for EM deployment |

Agent scripts under `integrations/*/scripts/` remain for **mock smoke** and parity with legacy CLI tests.

## Build pipeline (per integration)

1. **Template** — Python clones cmd skeletons from decoded IFA JSON (`toolkit/ifa_decode.py` + integration `build_*_template_from_ifa.py`).
2. **Encode** — `toolkit/build_ctmai.sh template.json out.ctmai`.
3. **Bundle** — Copy `.ctmai`, `descriptor_*.json`, `*_plugin.*.json` into `dist/` (integration script or `toolkit/build_dist.sh`).
4. **Smoke** — Integration CLI + scenario shell driver (exit codes 0/1/2/3 aligned with Control-M agent conventions).

IFA media path default: `/cursor/stores/self/media/` (Project store).

## Auth, idempotency, polling

- **Auth:** Prefer OAuth2 client-credentials pre-execute (IFADF/IFDBX). Basic (IFAHD) or API key only when customer requires it.
- **Idempotency:** Job property `Control-M-Idem_%%ORDERID` → HTTP header on submit (IFDBX ReadMeFirst pattern).
- **Status:** Default poll loop in execute ops; webhooks optional per customer.

## Adding a new integration

1. Copy `integrations/sapiens/` layout as a template (rename app id, REST paths, descriptors).
2. Implement `build_<APP>_template_from_ifa.py` choosing IFA clones for submit/poll/auth.
3. Add `BUILD.md`, `control-m/examples/`, and dist bundle name.
4. Document product-specific OpenAPI under `integrations/<product>/openapi/`.

## Related

- Sapiens operator guide: [integrations/sapiens/README.md](../integrations/sapiens/README.md)
- Micro Focus CLI baseline (separate repo): `neil-cullum/microfocus-configure` — JCL rerun simulation only
