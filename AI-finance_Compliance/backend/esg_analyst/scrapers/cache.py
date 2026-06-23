import json
import time
from pathlib import Path
from typing import Any, Optional


class ScraperCache:
    """
    Simple JSON-file cache for scraped data.
    Prevents re-scraping on every API request.
    """

    def __init__(self, cache_dir: Path, default_ttl_hours: int = 24):
        self.cache_dir = cache_dir
        self.default_ttl_hours = default_ttl_hours
        self.cache_dir.mkdir(parents=True, exist_ok=True)

    def _cache_path(self, key: str) -> Path:
        """Returns the file path for a cache key."""
        safe_key = key.replace("/", "_").replace(":", "_").replace("?", "_")
        return self.cache_dir / f"{safe_key}.json"

    def get(self, key: str, max_age_hours: Optional[int] = None) -> Optional[Any]:
        """
        Returns cached data if it exists and is fresh.
        Returns None if cache miss or expired.
        """
        ttl = max_age_hours if max_age_hours is not None else self.default_ttl_hours
        path = self._cache_path(key)

        if not path.exists():
            return None

        try:
            with open(path, "r", encoding="utf-8") as f:
                cached = json.load(f)

            cached_at = cached.get("cached_at", 0)
            age_hours = (time.time() - cached_at) / 3600

            if age_hours > ttl:
                return None  # Expired

            return cached.get("data")
        except Exception:
            return None

    def set(self, key: str, data: Any) -> None:
        """Saves data to cache with a timestamp."""
        path = self._cache_path(key)
        payload = {
            "cached_at": time.time(),
            "key": key,
            "data": data
        }
        try:
            with open(path, "w", encoding="utf-8") as f:
                json.dump(payload, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"[ScraperCache] Failed to write cache for '{key}': {e}")

    def invalidate(self, key: str) -> None:
        """Removes a cached entry."""
        path = self._cache_path(key)
        if path.exists():
            try:
                path.unlink()
            except Exception:
                pass

    def clear_all(self) -> None:
        """Clears all cached entries."""
        for path in self.cache_dir.glob("*.json"):
            try:
                path.unlink()
            except Exception:
                pass
