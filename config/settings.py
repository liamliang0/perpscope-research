from dataclasses import dataclass
import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

ROOT = Path(__file__).resolve().parents[1]


@dataclass(frozen=True)
class Settings:
    root: Path = ROOT
    raw_dir: Path = ROOT / "data" / "raw"
    processed_dir: Path = ROOT / "data" / "processed"
    history_dir: Path = ROOT / "data" / "history"
    output_dir: Path = ROOT / "output"
    request_timeout: int = int(os.getenv("REQUEST_TIMEOUT", "20"))
    request_retries: int = int(os.getenv("REQUEST_RETRIES", "2"))
    log_level: str = os.getenv("LOG_LEVEL", "INFO")
    llm_provider: str = os.getenv("LLM_PROVIDER", "none").lower()
    openai_api_key: str | None = os.getenv("OPENAI_API_KEY")
    openai_base_url: str = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")
    openai_model: str = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
    ollama_base_url: str = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    ollama_model: str = os.getenv("OLLAMA_MODEL", "llama3.1")

    def ensure_directories(self) -> None:
        for path in (self.raw_dir, self.processed_dir, self.history_dir, self.output_dir):
            path.mkdir(parents=True, exist_ok=True)
