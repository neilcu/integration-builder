"""Decode BMC Application Integrator packages (IFA reference zips → ctmai JSON)."""

from __future__ import annotations

import base64
import gzip
import json
import pathlib
import zipfile

DEFAULT_MEDIA = pathlib.Path("/cursor/stores/self/media")


def decode_ctmai(path: pathlib.Path) -> dict:
    return json.loads(gzip.decompress(base64.b64decode(path.read_bytes())))


def load_plugin(media: pathlib.Path, zip_stem: str, ctmai_name: str) -> dict:
    zpath = media / f"{zip_stem}.zip"
    with zipfile.ZipFile(zpath) as zf:
        raw = zf.read(ctmai_name)
    return json.loads(gzip.decompress(base64.b64decode(raw)))
