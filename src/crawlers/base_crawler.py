import asyncio
from datetime import datetime, timezone

import aiohttp
from bs4 import BeautifulSoup

from src.utils.retry import async_retry


class BaseCrawler:

    def __init__(self, concurrency: int = 10):
        self.concurrency = concurrency
        self.semaphore = asyncio.Semaphore(concurrency)

    @async_retry(
        max_retries=3,
        base_delay=1,
        max_delay=10,
    )
    async def fetch(
        self,
        session: aiohttp.ClientSession,
        url: str,
    ) -> dict:

        async with self.semaphore:

            headers = {
                "User-Agent": (
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                    "AppleWebKit/537.36 "
                    "(KHTML, like Gecko) "
                    "Chrome/151.0.0.0 Safari/537.36"
                )
            }

            async with session.get(
                url,
                headers=headers,
                timeout=aiohttp.ClientTimeout(total=30),
            ) as response:

                # Trigger retry for rate limits/server errors
                if response.status in (429, 500, 502, 503, 504):
                    error = aiohttp.ClientResponseError(
                        request_info=response.request_info,
                        history=response.history,
                        status=response.status,
                        message=f"Retryable HTTP status: {response.status}",
                        headers=response.headers,
                    )

                    raise error

                response.raise_for_status()

                html = await response.text(errors="ignore")

                soup = BeautifulSoup(html, "lxml")

                # Remove unnecessary content
                for element in soup(
                    ["script", "style", "noscript"]
                ):
                    element.decompose()

                title = (
                    soup.title.get_text(strip=True)
                    if soup.title
                    else ""
                )

                text = soup.get_text(" ", strip=True)

                return {
                    "source_url": str(response.url),
                    "status_code": response.status,
                    "title": title,
                    "text": text,
                    "collectedAt": datetime.now(
                        timezone.utc
                    ).isoformat(),
                    "error": None,
                }

    async def crawl(self, urls: list[str]) -> list[dict]:

        connector = aiohttp.TCPConnector(
            limit=self.concurrency
        )

        async with aiohttp.ClientSession(
            connector=connector
        ) as session:

            tasks = [
                self.fetch(session, url)
                for url in urls
            ]

            results = await asyncio.gather(
                *tasks,
                return_exceptions=True,
            )

            final_results = []

            for url, result in zip(urls, results):

                if isinstance(result, Exception):

                    final_results.append(
                        {
                            "source_url": url,
                            "status_code": None,
                            "title": "",
                            "text": "",
                            "collectedAt": datetime.now(
                                timezone.utc
                            ).isoformat(),
                            "error": str(result),
                        }
                    )

                else:
                    final_results.append(result)

            return final_results