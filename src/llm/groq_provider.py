import json
import os
import requests
from dotenv import load_dotenv

from .base_llm import BaseLLM
from ..utils.retry import async_retry

load_dotenv()


class GroqProvider(BaseLLM):

    def __init__(self):
        self.api_key = os.getenv("GROQ_API_KEY")

        if not self.api_key:
            raise RuntimeError(
                "GROQ_API_KEY not found in .env"
            )

        # Active production models on Groq
        # self.model = "llama-3.3-70b-versatile"
        self.model = "openai/gpt-oss-120b"
        # self.model = "llama-3.1-8b-instant"

        self.url = "https://api.groq.com/openai/v1/chat/completions"

    @async_retry(
        max_attempts=3,
        base_delay=1.0,
        max_delay=10.0
    )
    async def extract(
        self,
        text,
        schema
    ):
        prompt = f"""
You are a strict data extraction engine.

Extract ONLY information supported by the source.

Rules:
- Never invent facts.
- Unknown values must be null.
- Return ONLY valid JSON.
- Follow the schema exactly.

SCHEMA:
{json.dumps(schema, indent=2)}

SOURCE:
{text}
"""

        payload = {
            "model": self.model,
            "messages": [
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "temperature": 0,
            "response_format": {
                "type": "json_object"
            }
        }

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        response = requests.post(
            self.url,
            headers=headers,
            json=payload,
            timeout=60
        )

        if response.status_code == 429:
            raise RuntimeError("Groq HTTP 429")

        if response.status_code == 413:
            raise RuntimeError("Groq HTTP 413 Payload Too Large")

        if response.status_code != 200:
            raise RuntimeError(
                f"Groq API error "
                f"{response.status_code}: "
                f"{response.text[:500]}"
            )

        data = response.json()

        try:
            output = (
                data["choices"][0]
                ["message"]["content"]
            )

            return json.loads(output)

        except (
            KeyError,
            IndexError,
            json.JSONDecodeError
        ) as e:
            raise RuntimeError(
                "Invalid JSON response from Groq"
            ) from e