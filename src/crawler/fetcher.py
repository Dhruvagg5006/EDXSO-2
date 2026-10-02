"""
HTTP Fetcher Module with Retries, Caching, and Robust Fallbacks.
Saves raw crawled documents to data/raw_crawled/ for verifiable audit trails.
"""

import requests
import hashlib
import time
from typing import Optional, Tuple
from pathlib import Path
import config


class PageFetcher:
    """
    Fetches web pages with custom headers, retries, and local audit caching.
    """

    def __init__(self, cache_dir: Optional[Path] = None, timeout: int = config.REQUEST_TIMEOUT):
        self.cache_dir = cache_dir or config.RAW_CRAWLED_DIR
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.timeout = timeout
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": config.CRAWLER_USER_AGENT,
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.9",
        })

    def _get_cache_path(self, url: str) -> Path:
        url_hash = hashlib.sha256(url.encode("utf-8")).hexdigest()[:16]
        safe_name = "".join(c if c.isalnum() else "_" for c in url.split("//")[-1])[:40]
        return self.cache_dir / f"{safe_name}_{url_hash}.html"

    def fetch_page(self, url: str, force_refresh: bool = False) -> Tuple[int, str, bool]:
        """
        Fetches a URL and caches raw HTML to disk.
        Returns: (http_status_code, html_content, from_cache)
        """
        cache_file = self._get_cache_path(url)
        if not force_refresh and cache_file.exists():
            try:
                content = cache_file.read_text(encoding="utf-8")
                return 200, content, True
            except Exception:
                pass

        # Perform live HTTP request
        for attempt in range(1, config.MAX_RETRIES + 1):
            try:
                response = self.session.get(url, timeout=self.timeout, allow_redirects=True)
                if response.status_code == 200:
                    html = response.text
                    # Save snapshot
                    cache_file.write_text(html, encoding="utf-8")
                    return 200, html, False
                elif response.status_code in (404, 410):
                    return response.status_code, "", False
            except (requests.RequestException, Exception):
                if attempt == config.MAX_RETRIES:
                    break
                time.sleep(1.0)

        # Fallback to cache if available
        if cache_file.exists():
            try:
                return 200, cache_file.read_text(encoding="utf-8"), True
            except Exception:
                pass

        return 503, "", False

    def save_snapshot(self, url: str, html_content: str) -> Path:
        cache_file = self._get_cache_path(url)
        cache_file.write_text(html_content, encoding="utf-8")
        return cache_file
