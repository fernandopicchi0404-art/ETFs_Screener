from __future__ import annotations

import os
from pathlib import Path

from etf_screener.config import PROJECT_ROOT


def load_roic_api_key() -> str:
    env_path = PROJECT_ROOT / ".env"
    if env_path.exists():
        for line in env_path.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if line.startswith("ROIC_API_KEY="):
                value = line.split("=", 1)[1].strip()
                if value:
                    return value

    key = os.getenv("ROIC_API_KEY", "").strip()
    if not key:
        raise RuntimeError(
            "ROIC_API_KEY não encontrada. Configure no arquivo .env na raiz do projeto."
        )
    return key
