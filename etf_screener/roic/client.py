from __future__ import annotations

import hashlib
import json
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any

from etf_screener.config import CACHE_DIR, MAX_RETRIES, ROIC_BASE_URL
from etf_screener.roic.settings import load_requests_per_minute, request_interval_seconds


class RoicClient:
    def __init__(
        self,
        api_key: str,
        cache_dir: Path | None = None,
        requests_per_minute: int | None = None,
    ) -> None:
        self.api_key = api_key
        self.cache_dir = cache_dir or CACHE_DIR
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self._last_request_at = 0.0
        self._requests_per_minute = requests_per_minute or load_requests_per_minute()

    @property
    def request_interval_seconds(self) -> float:
        return request_interval_seconds(self._requests_per_minute)

    def _cache_path(self, path: str, params: dict[str, Any] | None = None) -> Path:
        payload = json.dumps({"path": path, "params": params or {}}, sort_keys=True)
        digest = hashlib.sha256(payload.encode("utf-8")).hexdigest()
        return self.cache_dir / f"{digest}.json"

    def _throttle(self) -> None:
        interval = self.request_interval_seconds
        elapsed = time.time() - self._last_request_at
        if elapsed < interval:
            time.sleep(interval - elapsed)

    def get(self, path: str, params: dict[str, Any] | None = None, use_cache: bool = True) -> dict[str, Any]:
        cache_path = self._cache_path(path, params)
        if use_cache and cache_path.exists():
            return json.loads(cache_path.read_text(encoding="utf-8"))

        query = urllib.parse.urlencode(params or {})
        url = f"{ROIC_BASE_URL}{path}"
        if query:
            url = f"{url}?{query}"

        last_error: Exception | None = None
        for attempt in range(MAX_RETRIES):
            self._throttle()
            request = urllib.request.Request(
                url,
                headers={"Authorization": f"Bearer {self.api_key}"},
            )
            try:
                with urllib.request.urlopen(request, timeout=60) as response:
                    payload = json.loads(response.read().decode("utf-8"))
                self._last_request_at = time.time()
                cache_path.write_text(json.dumps(payload), encoding="utf-8")
                return payload
            except urllib.error.HTTPError as exc:
                body = exc.read().decode("utf-8", errors="replace")
                last_error = RuntimeError(f"HTTP {exc.code} em {path}: {body}")
                if exc.code == 429:
                    retry_after = int(exc.headers.get("Retry-After", self.request_interval_seconds))
                    time.sleep(max(retry_after, self.request_interval_seconds))
                    continue
                if exc.code in {500, 502, 503, 504}:
                    time.sleep(self.request_interval_seconds * (attempt + 1))
                    continue
                raise last_error from exc
            except (urllib.error.URLError, TimeoutError) as exc:
                last_error = RuntimeError(f"Erro de rede em {path}: {exc}")
                time.sleep(self.request_interval_seconds * (attempt + 1))

        raise last_error or RuntimeError(f"Falha ao consultar {path}")
