from __future__ import annotations

import json
import os
from dataclasses import dataclass
from typing import Any, Protocol
from urllib import request


class Assistant(Protocol):
    def complete_json(self, instruction: str, payload: dict[str, Any]) -> dict[str, Any]: ...


@dataclass
class OpenAICompatibleAssistant:
    """Minimal adapter for an OpenAI-compatible chat-completions endpoint."""

    base_url: str
    api_key: str
    model: str
    timeout_seconds: int = 30

    @classmethod
    def from_env(cls) -> "OpenAICompatibleAssistant":
        values = {name: os.getenv(name, "").strip() for name in ("LLM_BASE_URL", "LLM_API_KEY", "LLM_MODEL")}
        missing = [name for name, value in values.items() if not value]
        if missing:
            raise ValueError(f"Missing configuration: {', '.join(missing)}")
        return cls(values["LLM_BASE_URL"], values["LLM_API_KEY"], values["LLM_MODEL"])

    def complete_json(self, instruction: str, payload: dict[str, Any]) -> dict[str, Any]:
        endpoint = self.base_url.rstrip("/") + "/chat/completions"
        body = {
            "model": self.model,
            "temperature": 0.1,
            "response_format": {"type": "json_object"},
            "messages": [
                {"role": "system", "content": instruction},
                {"role": "user", "content": json.dumps(payload, ensure_ascii=False)},
            ],
        }
        req = request.Request(
            endpoint,
            data=json.dumps(body).encode("utf-8"),
            headers={"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"},
            method="POST",
        )
        with request.urlopen(req, timeout=self.timeout_seconds) as response:
            result = json.loads(response.read().decode("utf-8"))
        content = result["choices"][0]["message"]["content"]
        return json.loads(content)

