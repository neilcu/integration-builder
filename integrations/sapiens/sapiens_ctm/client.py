"""HTTP client for Sapiens ACE Runtime batch endpoints (OpenAPI placeholders)."""

from __future__ import annotations

import json
import ssl
import urllib.error
import urllib.parse
import urllib.request
from typing import Any

from sapiens_ctm.config import SapiensConfig
from sapiens_ctm.mock_backend import MockBackend

_MOCK = MockBackend()


class SapiensClient:
    """Thin REST wrapper; switches to :class:`MockBackend` when ``SAPIENS_USE_MOCK=1``."""

    def __init__(self, config: SapiensConfig | None = None) -> None:
        self.config = config or SapiensConfig.from_env()
        self._access_token: str | None = None

    def submit_batch(
        self,
        *,
        flow_name: str,
        scenario: str,
        idempotency_key: str | None = None,
        parameters: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        body = {
            "flowName": flow_name,
            "scenario": scenario,
            "parameters": parameters or {},
        }
        if self.config.use_mock:
            return _MOCK.submit_batch(scenario=scenario, idempotency_key=idempotency_key)

        path = "/v1/batch/jobs"
        return self._request("POST", path, body=body, idempotency_key=idempotency_key)

    def get_batch_status(self, job_id: str) -> dict[str, Any]:
        if self.config.use_mock:
            return _MOCK.get_batch_status(job_id)
        return self._request("GET", f"/v1/batch/jobs/{job_id}")

    def poll_until_terminal(
        self,
        job_id: str,
        *,
        poll_interval_sec: float = 2.0,
        max_attempts: int = 30,
    ) -> dict[str, Any]:
        import time

        last: dict[str, Any] = {"status": "UNKNOWN"}
        for _ in range(max_attempts):
            last = self.get_batch_status(job_id)
            status = str(last.get("status", "")).upper()
            if status in ("SUCCEEDED", "FAILED", "CANCELLED", "UNKNOWN"):
                if status != "RUNNING":
                    return last
            time.sleep(poll_interval_sec)
        last["status"] = last.get("status", "RUNNING")
        last["reason"] = "poll_timeout"
        return last

    def health_check(self) -> dict[str, Any]:
        if self.config.use_mock:
            return {"status": "OK", "mode": "mock"}
        try:
            self._request("GET", "/health", auth=False)
            return {"status": "OK", "mode": "live"}
        except Exception as exc:  # noqa: BLE001 — surface to Control-M as SOFT_FAIL
            return {"status": "ERROR", "reason": str(exc)}

    def _request(
        self,
        method: str,
        path: str,
        *,
        body: dict[str, Any] | None = None,
        idempotency_key: str | None = None,
        auth: bool = True,
    ) -> dict[str, Any]:
        url = f"{self.config.base_url}{path}"
        headers = {"Accept": "application/json", "Content-Type": "application/json"}
        if idempotency_key:
            headers[self.config.idempotency_header] = idempotency_key
        if auth:
            headers.update(self._auth_headers())

        data = None if body is None else json.dumps(body).encode("utf-8")
        req = urllib.request.Request(url, data=data, headers=headers, method=method)
        ctx = ssl.create_default_context()
        try:
            with urllib.request.urlopen(req, timeout=self.config.request_timeout_sec, context=ctx) as resp:
                raw = resp.read().decode("utf-8")
                if not raw.strip():
                    return {"httpStatus": resp.status}
                return json.loads(raw)
        except urllib.error.HTTPError as exc:
            detail = exc.read().decode("utf-8", errors="replace")
            raise RuntimeError(f"HTTP {exc.code} {method} {path}: {detail}") from exc

    def _auth_headers(self) -> dict[str, str]:
        mode = self.config.auth_mode
        if mode == "none":
            return {}
        if mode == "api_key":
            if not self.config.api_key:
                raise RuntimeError("SAPIENS_API_KEY required when SAPIENS_AUTH_MODE=api_key")
            return {"Authorization": f"Bearer {self.config.api_key}"}
        if mode == "oauth_client_credentials":
            token = self._ensure_oauth_token()
            return {"Authorization": f"Bearer {token}"}
        raise RuntimeError(f"Unsupported SAPIENS_AUTH_MODE: {mode}")

    def _ensure_oauth_token(self) -> str:
        if self._access_token:
            return self._access_token
        if not self.config.oauth_token_url:
            raise RuntimeError("SAPIENS_OAUTH_TOKEN_URL required for oauth_client_credentials")
        form = {
            "grant_type": "client_credentials",
            "client_id": self.config.oauth_client_id or "",
            "client_secret": self.config.oauth_client_secret or "",
        }
        if self.config.oauth_scope:
            form["scope"] = self.config.oauth_scope
        encoded = urllib.parse.urlencode(form).encode("utf-8")  # type: ignore[name-defined]
        req = urllib.request.Request(
            self.config.oauth_token_url,
            data=encoded,
            headers={"Content-Type": "application/x-www-form-urlencoded"},
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=self.config.request_timeout_sec) as resp:
            payload = json.loads(resp.read().decode("utf-8"))
        token = payload.get("access_token")
        if not token:
            raise RuntimeError("OAuth token response missing access_token")
        self._access_token = str(token)
        return self._access_token