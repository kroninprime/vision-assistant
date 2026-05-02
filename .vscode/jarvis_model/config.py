import os
from dataclasses import dataclass
from dotenv import load_dotenv

load_dotenv()

@dataclass
class Settings:
    host: str = os.getenv("JARVIS_HOST", "127.0.0.1")
    port: int = int(os.getenv("JARVIS_PORT", "8000"))
    wake_word: str = os.getenv("JARVIS_WAKE_WORD", "hey jarvis")
    enable_wake_word: bool = os.getenv("JARVIS_ENABLE_WAKE_WORD", "false").lower() == "true"
    tesseract_cmd: str = os.getenv("TESSERACT_CMD", "")
    memory_db: str = os.getenv("JARVIS_MEMORY_DB", "jarvis_memory.db")
    openai_api_key: str = os.getenv("OPENAI_API_KEY", "")
    openai_model: str = os.getenv("OPENAI_MODEL", "gpt-4.1-mini")
    ollama_base_url: str = os.getenv("OLLAMA_BASE_URL", "http://127.0.0.1:11434")
    ollama_model: str = os.getenv("OLLAMA_MODEL", "llama3.1:8b")


settings = Settings()
