import json
import logging
from typing import Any

from config.settings import Settings
from src.data_sources.http import PublicAPIClient

log = logging.getLogger(__name__)

SYSTEM = """You are a protocol research editor. Use ONLY the supplied JSON. Never add facts.
Return Markdown with three short headings: Facts, Interpretation, Unknowns. Clearly separate them.
No investment advice and no buy/sell language."""


def enhance(settings: Settings, payload: dict[str, Any]) -> str | None:
    if settings.llm_provider == "none":
        return None
    client = PublicAPIClient(settings.request_timeout, settings.request_retries)
    try:
        if settings.llm_provider == "openai":
            if not settings.openai_api_key:
                raise ValueError("OPENAI_API_KEY is not set")
            raw = client.json("POST", f"{settings.openai_base_url.rstrip('/')}/chat/completions",
                headers={"Authorization": f"Bearer {settings.openai_api_key}"}, json={
                    "model": settings.openai_model,
                    "temperature": 0,
                    "messages": [{"role": "system", "content": SYSTEM},
                                 {"role": "user", "content": json.dumps(payload)}],
                })
            return raw["choices"][0]["message"]["content"]
        if settings.llm_provider == "ollama":
            raw = client.json("POST", f"{settings.ollama_base_url.rstrip('/')}/api/generate", json={
                "model": settings.ollama_model, "system": SYSTEM,
                "prompt": json.dumps(payload), "stream": False,
            })
            return raw.get("response")
        raise ValueError(f"Unsupported LLM_PROVIDER={settings.llm_provider}")
    except Exception as exc:
        log.warning("LLM enhancement unavailable; using deterministic report: %s", exc)
        return None
