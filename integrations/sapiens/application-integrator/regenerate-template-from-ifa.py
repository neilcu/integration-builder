#!/usr/bin/env python3
"""Regenerate SAPIENS.ctmai.template.json and SAPIENS.ctmai from IFA reference zips."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent


def main() -> int:
    subprocess.check_call([sys.executable, str(HERE / "build_sapiens_template_from_ifa.py")])
    subprocess.check_call([str(HERE / "build-ctmai.sh")])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())