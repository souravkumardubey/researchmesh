import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

from dotenv import load_dotenv


@dataclass
class Settings:
    tavily_api_key: str = ""
    mistral_api_key: str = ""
    model: str = "mistral-small-latest"
    tavily_max_results: int = 5

    @classmethod
    def load(cls, env_file: Optional[str] = None) -> "Settings":
        if env_file:
            load_dotenv(env_file)
        else:
            load_dotenv()
        return cls(
            tavily_api_key=os.getenv("TAVILY_API_KEY", ""),
            mistral_api_key=os.getenv("MISTRAL_API_KEY", ""),
            model=os.getenv("MODEL", "mistral-small-latest"),
        )

    def validate(self) -> list[str]:
        missing = []
        if not self.tavily_api_key:
            missing.append("TAVILY_API_KEY")
        if not self.mistral_api_key:
            missing.append("MISTRAL_API_KEY")
        return missing
