import json
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


class OllamaClient:
    """Client for communicating with a local Ollama server."""

    DEFAULT_API_URL = "http://localhost:11434/api/generate"
    DEFAULT_MODEL = "qwen2.5-coder:3b"

    def __init__(self, model: str | None = None, api_url: str | None = None, timeout: int = 15) -> None:
        self.MODEL = model or self.DEFAULT_MODEL
        self.API_URL = api_url or self.DEFAULT_API_URL
        self.timeout = timeout

    def generate(self, prompt: str) -> str:
        """Generate text from the local Ollama server using the configured model.

        Args:
            prompt: The prompt text to send to Ollama.

        Returns:
            The generated text returned by Ollama.

        Raises:
            RuntimeError: If the request fails or the response cannot be parsed.
        """
        payload = {
            "model": self.MODEL,
            "prompt": prompt,
            "stream": False,
        }

        request = Request(
            self.API_URL,
            data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST",
        )

        try:
            with urlopen(request, timeout=self.timeout) as response:
                raw_data = response.read().decode("utf-8")
        except HTTPError as exc:
            message = exc.read().decode("utf-8", errors="ignore")
            raise RuntimeError(
                f"Ollama server returned HTTP {exc.code}: {message.strip() or exc.reason}"
            ) from exc
        except URLError as exc:
            raise RuntimeError(
                f"Failed to connect to Ollama server at {self.API_URL}: {exc.reason}"
            ) from exc
        except Exception as exc:
            raise RuntimeError(f"Ollama request timed out or failed: {exc}") from exc

        try:
            data: Any = json.loads(raw_data)
        except json.JSONDecodeError as exc:
            raise RuntimeError("Received invalid JSON from Ollama") from exc

        if not isinstance(data, dict):
            raise RuntimeError("Unexpected response format from Ollama")

        response = data.get("response")
        if isinstance(response, str) and response.strip():
            return response

        raise RuntimeError("Ollama response did not contain generated text in the 'response' field")
