"""Exit codes aligned with Micro Focus stub scripts (ctm-mf-job-status.sh, ctm-run-scenario.sh)."""

from enum import IntEnum


class CtmExitCode(IntEnum):
    """Shell / agent wrapper return codes."""

  # Success paths
    OK = 0
    # Operational / validation
    USAGE = 2
    # Connect, auth, missing resource, unknown state
    SOFT_FAIL = 1
    # Business failure, failed batch/API status
    ERROR = 3