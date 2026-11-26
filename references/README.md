# External references (not vendored in this repo)

BMC **Application Integrator** reference plugin packages inform layout and REST op patterns only. Obtain current zips from BMC / your EM media kit; do **not** commit them here.

| Package | Product | Use in this factory |
|---------|---------|---------------------|
| IFAAF | Apache Airflow | Submit + poll REST op skeleton |
| IFADF | Azure Data Factory | OAuth pre-execute, post-execute, reruns |
| IFAHD | Azure HDInsight | Basic-auth REST fallback pattern |
| IFDBX | Databricks | OAuth OIDC, idempotency token, dual `restURLs` |

**Project store (Cursor):** IFA zips for decode/regeneration are kept under `/cursor/stores/self/media/` in the Control-M Sapiens Project — not copied into git.

**Micro Focus baseline:** Agent-side JCL/CLI patterns live only in [`neil-cullum/microfocus-configure`](https://origin.cursor.com/neil-cullum/microfocus-configure) (`mfbsijcl`, rerun simulation). This repo does not vendor MF JCL.
