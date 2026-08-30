import json
import os
import requests
from dotenv import load_dotenv

from .base_llm import BaseLLM
from ..utils.retry import async_retry

load_dotenv()


class GeminiProvider(BaseLLM):

    def __init__(self):
        self.api_key = os.getenv("GEMINI_API_KEY")

        if not self.api_key:
            raise RuntimeError(
                "GEMINI_API_KEY not found in .env"
            )

        # self.model = "gemini-1.5-flash"
        self.model = "gemini-3.6-flash"

        self.url = (
            "https://generativelanguage.googleapis.com/"
            f"v1beta/models/{self.model}:generateContent"
        )

    @async_retry(
        max_attempts=1,
        base_delay=1.0,
        max_delay=10.0
    )
    async def extract(self, text, schema):

        prompt = f"""
You are a strict data extraction engine.

Extract information from the supplied text.

IMPORTANT RULES:
1. Return ONLY valid JSON.
2. Never invent information.
3. If a field is unavailable, use null.
4. Follow the requested schema exactly.
5. Do not add unsupported facts.

TARGET SCHEMA:
{json.dumps(schema, indent=2)}

SOURCE TEXT:
{text}
"""

        payload = {
            "contents": [
                {
                    "parts": [
                        {
                            "text": prompt
                        }
                    ]
                }
            ],
            "generationConfig": {
                "responseMimeType": "application/json"
            }
        }

        response = requests.post(
            self.url,
            params={
                "key": self.api_key
            },
            json=payload,
            timeout=60
        )

        if response.status_code == 429:
            raise RuntimeError(
                "Gemini rate limit: 429"
            )

        if response.status_code != 200:
            raise RuntimeError(
                f"Gemini API error "
                f"{response.status_code}: "
                f"{response.text[:500]}"
            )

        data = response.json()

        try:
            text_output = (
                data["candidates"][0]
                ["content"]["parts"][0]
                ["text"]
            )
        except (KeyError, IndexError) as e:
            raise RuntimeError(
                f"Invalid Gemini response: {data}"
            ) from e

        try:
            return json.loads(text_output)

        except json.JSONDecodeError as e:
            raise RuntimeError(
                "Gemini returned invalid JSON"
            ) from e