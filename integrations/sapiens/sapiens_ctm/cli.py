"""CLI entrypoints for Control-M command jobs: python -m sapiens_ctm.cli <cmd> ..."""

from __future__ import annotations

import argparse
import json
import sys

from sapiens_ctm.client import SapiensClient
from sapiens_ctm.exit_codes import CtmExitCode
from sapiens_ctm.rerun import resolve_restart_step


def _echo_status(key: str, value: str) -> None:
    print(f"{key}={value}")


def cmd_submit(args: argparse.Namespace) -> int:
    client = SapiensClient()
    idem = args.idempotency_key or args.idempotency_from_env
    result = client.submit_batch(
        flow_name=args.flow,
        scenario=args.scenario,
        idempotency_key=idem,
    )
  # MF pattern: echo scenario + job id + RC
    _echo_status("JOB_ID", str(result.get("jobId", "")))
    _echo_status("SCENARIO", args.scenario)
    _echo_status("HTTP_STATUS", "200")
    status = str(result.get("status", "")).upper()
    _echo_status("BATCH_STATUS", status)
    if status == "FAILED":
        fail = result.get("failedStep") or result.get("currentStep")
        if fail:
            _echo_status("FAILED_STEP", f"STEP.{fail}")
            _echo_status("LAUNCHER_RESTART", resolve_restart_step(f"STEP.{fail}"))
        return int(CtmExitCode.ERROR)
    if status in ("SUCCEEDED", "RUNNING"):
        return int(CtmExitCode.OK)
    return int(CtmExitCode.SOFT_FAIL)


def cmd_status(args: argparse.Namespace) -> int:
    client = SapiensClient()
    if not args.job_id:
        _echo_status("STATUS", "UNKNOWN")
        _echo_status("REASON", "missing_job_id")
        return int(CtmExitCode.USAGE)

    result = client.get_batch_status(args.job_id)
    status = str(result.get("status", "UNKNOWN")).upper()
    if status == "SUCCEEDED":
        _echo_status("STATUS", "OK")
        _echo_status("JOB_ID", args.job_id)
        return int(CtmExitCode.OK)
    if status == "FAILED":
        _echo_status("STATUS", "ERROR")
        _echo_status("JOB_ID", args.job_id)
        fail = result.get("failedStep")
        if fail:
            _echo_status("HINT", f"STEP.{fail}")
        return int(CtmExitCode.ERROR)
    if status == "RUNNING":
        _echo_status("STATUS", "RUNNING")
        _echo_status("JOB_ID", args.job_id)
        return int(CtmExitCode.SOFT_FAIL)
    _echo_status("STATUS", "UNKNOWN")
    _echo_status("JOB_ID", args.job_id)
    return int(CtmExitCode.SOFT_FAIL)


def cmd_poll(args: argparse.Namespace) -> int:
    client = SapiensClient()
    result = client.poll_until_terminal(
        args.job_id,
        poll_interval_sec=args.interval,
        max_attempts=args.attempts,
    )
    print(json.dumps(result, indent=2))
    status = str(result.get("status", "")).upper()
    if status == "SUCCEEDED":
        return int(CtmExitCode.OK)
    if status == "FAILED":
        return int(CtmExitCode.ERROR)
    return int(CtmExitCode.SOFT_FAIL)


def cmd_resolve(args: argparse.Namespace) -> int:
    step = resolve_restart_step(args.failed_step)
    print(step)
    return int(CtmExitCode.OK)


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(prog="sapiens-ctm")
    sub = parser.add_subparsers(dest="command", required=True)

    p_submit = sub.add_parser("submit", help="Submit batch flow (maps mfbsijcl submit)")
    p_submit.add_argument("--flow", default="ctm-pipeline-batch")
    p_submit.add_argument("--scenario", required=True)
    p_submit.add_argument("--idempotency-key")
    p_submit.add_argument(
        "--idempotency-from-env",
        default=None,
        help="Read Control-M %%ORDERID style key from SAPIENS_IDEMPOTENCY_KEY",
    )
    p_submit.set_defaults(func=cmd_submit)

    p_status = sub.add_parser("status", help="Reconnect validation (maps ctm-mf-job-status)")
    p_status.add_argument("job_id", nargs="?")
    p_status.set_defaults(func=cmd_status)

    p_poll = sub.add_parser("poll", help="Poll until terminal batch state")
    p_poll.add_argument("job_id")
    p_poll.add_argument("--interval", type=float, default=2.0)
    p_poll.add_argument("--attempts", type=int, default=30)
    p_poll.set_defaults(func=cmd_poll)

    p_resolve = sub.add_parser("resolve-restart", help="Launcher restart step mapping")
    p_resolve.add_argument("failed_step")
    p_resolve.set_defaults(func=cmd_resolve)

    args = parser.parse_args(argv)
    import os

    if args.command == "submit" and getattr(args, "idempotency_from_env", None) is None:
        args.idempotency_from_env = os.getenv("SAPIENS_IDEMPOTENCY_KEY")
    rc = args.func(args)
    sys.exit(rc)


if __name__ == "__main__":
    main()