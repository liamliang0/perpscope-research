import logging
import time
from typing import Any

import requests

log = logging.getLogger(__name__)


class PublicAPIClient:
    def __init__(self, timeout: int = 20, retries: int = 2):
        self.timeout = timeout
        self.retries = retries
        self.session = requests.Session()
        self.session.headers.update({"User-Agent": "PerpScope/1.0 (+public-research)"})

    def json(self, method: str, url: str, **kwargs: Any) -> Any:
        last_error: Exception | None = None
        for attempt in range(self.retries + 1):
            try:
                response = self.session.request(method, url, timeout=self.timeout, **kwargs)
                response.raise_for_status()
                return response.json()
            except (requests.RequestException, ValueError) as exc:
                last_error = exc
                if attempt < self.retries:
                    time.sleep(0.5 * (2**attempt))
        assert last_error is not None
        raise last_error
