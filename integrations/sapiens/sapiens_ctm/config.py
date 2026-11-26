"""Environment-driven configuration (no proprietary secrets in repo)."""

from __future__ import annotations

import os
from dataclasses import dataclass


@dataclass(frozen=True)
class SapiensConfig:
    base_url: str
    auth_mode: str  # none | api_key | oauth_client_credentials
    api_key: str | None
    oauth_token_url: str | None
    oauth_client_id: str | None
    oauth_client_secret: str | None
    oauth_scope: str | None
    idempotency_header: str
    use_mock: bool
    request_timeout_sec: int

    @classmethod
    def from_env(cls) -> "SapiensConfig":
        use_mock = os.getenv("SAPIENS_USE_MOCK", "1").strip().lower() in ("1", "true", "yes")
        return cls(
            base_url=os.getenv("SAPIENS_BASE_URL", "https://ace-runtime.example.invalid").rstrip("/"),
            auth_mode=os.getenv("SAPIENS_AUTH_MODE", "api_key").strip().lower(),
            api_key=os.getenv("SAPIENS_API_KEY"),
            oauth_token_url=os.getenv("SAPIENS_OAUTH_TOKEN_URL"),
            oauth_client_id=os.getenv("SAPIENS_OAUTH_CLIENT_ID"),
            oauth_client_secret=os.getenv("SAPIENS_OAUTH_CLIENT_SECRET"),
            oauth_scope=os.getenv("SAPIENS_OAUTH_SCOPE"),
            idempotency_header=os.getenv("SAPIENS_IDEMPOTENCY_HEADER", "X-Idempotency-Key"),
            use_mock=use_mock,
            request_timeout_sec=int(os.getenv("SAPIENS_HTTP_TIMEOUT", "60")),
        )