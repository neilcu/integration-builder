#!/usr/bin/env python3
"""Build SAPIENS.ctmai.template.json by cloning cmd structure from IFA reference zips."""

from __future__ import annotations

import argparse
import copy
import json
import pathlib
import sys

REPO_ROOT = pathlib.Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO_ROOT))

from toolkit.ifa_decode import DEFAULT_MEDIA, load_plugin

HERE = pathlib.Path(__file__).resolve().parent


def build_template(adf: dict, aaf: dict, dbx: dict) -> dict:
    adf_pre = adf["app"]["executionTypes"][0]["ops"][0]["cmds"][0]
    aaf_submit = aaf["app"]["executionTypes"][0]["ops"][1]["cmds"][0]
    aaf_poll = aaf["app"]["executionTypes"][0]["ops"][1]["cmds"][2]

    rest_urls = copy.deepcopy(dbx["app"]["restURLs"][:2])
    for ru in rest_urls:
        ru["restName"] = (
            "SapiensAuth" if ru.get("restAuthentication", {}).get("authenticationTypeName") == "oauth2" else "SapiensRuntime"
        )
        ru["restURL"] = "https://{{sapiens_base_url}}"
        ru["restEndpoint"] = "https://{{sapiens_base_url}}"
        oauth = ru.get("restAuthentication", {}).get("oauthAuthentication")
        if oauth:
            oauth["oauth2APIAuthorizationEndpoint"] = "{{oauth_token_url}}"
            oauth["oauth2ClientId"] = "{{oauth_client_id}}"
            oauth["oauth2ClientSecret"] = "{{oauth_client_secret}}"
            oauth["oauth2tokenParamName"] = "SAPIENS_ACCESS_TOKEN"

    pre_cmd = copy.deepcopy(adf_pre)
    pre_cmd["restName"] = "SapiensAuth"
    pre_cmd["restURLPath"] = "{{oauth_token_path}}"
    pre_cmd["restEndpoint"] = "{{oauth_token_url}}"
    pre_cmd["desc"] = "OAuth client credentials (IFADF/IFDBX pattern)"
    for ei in pre_cmd.get("extractInfo", []) or []:
        for ds in ei.get("doSection", []) or []:
            ed = ds.get("extHandleData", {}).get("extractData", {})
            if ed.get("keepParamName"):
                ed["keepParamName"] = "SAPIENS_ACCESS_TOKEN"

    submit_cmd = copy.deepcopy(aaf_submit)
    submit_cmd["httpMethod"] = "POST"
    submit_cmd["restName"] = "SapiensRuntime"
    submit_cmd["restURLPath"] = "/v1/batch/jobs"
    submit_cmd["restEndpoint"] = "https://{{sapiens_base_url}}"
    submit_cmd["name"] = "Submit Sapiens batch flow"
    submit_cmd["desc"] = "AAF initiate-DAG analog"
    submit_cmd["body"] = '{"flowName":"{{flow_name}}","scenario":"{{scenario}}"}'
    submit_cmd["headersPairs"] = list(submit_cmd.get("headersPairs") or [])
    submit_cmd["headersPairs"].append({"name": "X-Idempotency-Key", "value": "{{idempotency_token}}"})
    submit_cmd["extractInfo"] = [
        {
            "doSection": [
                {
                    "uid": "sapiens-submit-extract",
                    "extHandleData": {
                        "extractData": {
                            "keepParamName": "SAPIENS_JOB_ID",
                            "keepParamInOutput": True,
                            "elementPath": "$.jobId",
                            "value": "",
                        }
                    },
                }
            ]
        }
    ]
    submit_cmd["nrOfRetries"] = "{{attempt_reruns}}"
    submit_cmd["rerunInterval"] = "{{rerun_interval}}"
    submit_cmd["http_codes"] = "{{http_codes}}"
    submit_cmd["RerunStepPairs"] = []

    poll_cmd = copy.deepcopy(aaf_poll)
    poll_cmd["httpMethod"] = "GET"
    poll_cmd["restName"] = "SapiensRuntime"
    poll_cmd["restURLPath"] = "/v1/batch/jobs/{{SAPIENS_JOB_ID}}"
    poll_cmd["name"] = "Poll Sapiens batch status"
    poll_cmd["desc"] = "AAF verify-completion analog"
    poll_cmd["extractInfo"] = [
        {
            "doSection": [
                {
                    "uid": "sapiens-status-extract",
                    "extHandleData": {
                        "extractData": {
                            "keepParamName": "BATCH_STATUS",
                            "keepParamInOutput": True,
                            "elementPath": "$.status",
                            "value": "",
                        }
                    },
                },
                {
                    "uid": "sapiens-failed-step-extract",
                    "extHandleData": {
                        "extractData": {
                            "keepParamName": "FAILED_STEP",
                            "keepParamInOutput": True,
                            "elementPath": "$.failedStep",
                            "value": "",
                        }
                    },
                },
            ]
        }
    ]
    poll_cmd["nrOfRetries"] = "{{attempt_reruns}}"
    poll_cmd["rerunInterval"] = "{{rerun_interval}}"
    poll_cmd["http_codes"] = "{{http_codes}}"

    post_cmd = copy.deepcopy(adf["app"]["executionTypes"][0]["ops"][-1]["cmds"][0])
    post_cmd["restName"] = "SapiensRuntime"
    post_cmd["restURLPath"] = "/v1/batch/jobs/{{SAPIENS_JOB_ID}}"
    post_cmd["desc"] = "Post-execute finalize (IFADF post pattern)"
    post_cmd["name"] = "Finalize Sapiens batch job"

    app = {
        "name": "SAPIENS01112026",
        "displayName": "Sapiens ACE Batch",
        "defaultType": "REST",
        "desc": "PLACEHOLDER Sapiens ACE batch. Structure from IFAAF (submit+poll) + IFADF (OAuth pre-exec).",
        "lastModified": "November 26, 2026",
        "version": "8.0.00.200",
        "deploymentVersion": 2,
        "wsdlURLs": [],
        "restURLs": rest_urls,
        "simluationHost": "",
        "runtimeParams": [],
        "params": [],
        "executionTypes": [
            {
                "executionTypeName": "default",
                "ops": [
                    {"type": "pre-execute", "isEnabled": True, "cmds": [pre_cmd]},
                    {"type": "execute", "isEnabled": True, "cmds": [submit_cmd]},
                    {"type": "execute", "isEnabled": True, "cmds": [poll_cmd]},
                    {"type": "post-execute", "isEnabled": True, "cmds": [post_cmd]},
                ],
            }
        ],
    }
    return {"app": app, "WSDLS": []}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--media", type=pathlib.Path, default=DEFAULT_MEDIA)
    parser.add_argument("-o", type=pathlib.Path, default=HERE / "SAPIENS.ctmai.template.json")
    args = parser.parse_args()
    adf = load_plugin(args.media, "IFADF.1.0.08_f375", "ADF.ctmai")
    aaf = load_plugin(args.media, "IFAAF.1.0.06_c196", "AAF.ctmai")
    dbx = load_plugin(args.media, "IFDBX.1.0.10_DataBricks_14d7", "DBX.ctmai")
    payload = build_template(adf, aaf, dbx)
    args.o.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(args.o, args.o.stat().st_size)


if __name__ == "__main__":
    main()