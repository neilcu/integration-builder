"""In-memory mock matching MF simulation scenarios (ok, fail-*, rerun-*)."""

from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from typing import Any


PIPELINE_ORDER = [
    "U4BARA01",
    "RUNSFTP",
    "FTPBA",
    "VALFTP",
    "DDL3BIND",
    "BIND",
]

FAIL_AT_STEP = {
    "fail-bind": "BIND",
    "fail-valftp": "VALFTP",
    "fail-runsftp": "RUNSFTP",
    "fail-ddl": "DDL3BIND",
}

RERUN_START = {
    "rerun-bind": "DDL3BIND",
    "rerun-valftp": "FTPBA",
    "rerun-runsftp": "U4BARA01",
}


@dataclass
class MockJob:
    job_id: str
    scenario: str
    status: str = "RUNNING"
    current_step: str | None = None
    failed_step: str | None = None
    completed_steps: list[str] = field(default_factory=list)
    created_at: float = field(default_factory=time.time)
    correlation_id: str = field(default_factory=lambda: str(uuid.uuid4()))


class MockBackend:
    def __init__(self) -> None:
        self._jobs: dict[str, MockJob] = {}

    def submit_batch(self, *, scenario: str, idempotency_key: str | None) -> dict[str, Any]:
        if idempotency_key:
            for job in self._jobs.values():
                if getattr(job, "_idem", None) == idempotency_key:
                    return self._job_payload(job)

        job_id = f"sap-{uuid.uuid4().hex[:12]}"
        job = MockJob(job_id=job_id, scenario=scenario)
        if idempotency_key:
            job._idem = idempotency_key  # type: ignore[attr-defined]

        fail_step = FAIL_AT_STEP.get(scenario)
        rerun_from = RERUN_START.get(scenario)
        steps = PIPELINE_ORDER

        if rerun_from:
            idx = steps.index(rerun_from)
            job.completed_steps = steps[:idx]

        if scenario == "ok" or scenario.startswith("rerun-"):
            job.status = "SUCCEEDED"
            job.completed_steps = steps
        elif fail_step:
            idx = steps.index(fail_step)
            job.completed_steps = steps[:idx]
            job.current_step = fail_step
            job.failed_step = fail_step
            job.status = "FAILED"
        else:
            job.status = "SUCCEEDED"
            job.completed_steps = steps

        self._jobs[job_id] = job
        return self._job_payload(job)

    def get_batch_status(self, job_id: str) -> dict[str, Any]:
        job = self._jobs.get(job_id)
        if not job:
            return {"jobId": job_id, "status": "UNKNOWN", "reason": "not_found"}
        return self._job_payload(job)

    def _job_payload(self, job: MockJob) -> dict[str, Any]:
        return {
            "jobId": job.job_id,
            "correlationId": job.correlation_id,
            "scenario": job.scenario,
            "status": job.status,
            "currentStep": job.current_step,
            "failedStep": job.failed_step,
            "completedSteps": job.completed_steps,
            "pipelineOrder": PIPELINE_ORDER,
        }