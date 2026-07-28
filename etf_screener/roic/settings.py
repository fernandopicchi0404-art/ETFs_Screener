from __future__ import annotations

import os
from pathlib import Path

from etf_screener.config import PROJECT_ROOT

DEFAULT_REQUESTS_PER_MINUTE = 300


def _read_env_file() -> dict[str, str]:
    env_path = PROJECT_ROOT / ".env"
    if not env_path.exists():
        return {}
    values: dict[str, str] = {}
    for line in env_path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        values[key.strip()] = value.strip()
    return values


def load_requests_per_minute() -> int:
    file_values = _read_env_file()
    raw = (
        os.getenv("ROIC_REQUESTS_PER_MINUTE")
        or file_values.get("ROIC_REQUESTS_PER_MINUTE")
        or str(DEFAULT_REQUESTS_PER_MINUTE)
    )
    try:
        return max(1, int(raw))
    except ValueError:
        return DEFAULT_REQUESTS_PER_MINUTE


def request_interval_seconds(requests_per_minute: int | None = None) -> float:
    rpm = requests_per_minute if requests_per_minute is not None else load_requests_per_minute()
    return 60.0 / rpm
