import asyncio
import json
from datetime import datetime, timezone
from pathlib import Path

import aiohttp
from bs4 import BeautifulSoup

from src.schemas.startup import Startup


OUTPUT_FILE = Path("data/raw/startups_raw.json")


class StartupCrawler:

    def __init__(self):
        self.session = None

    async def fetch(self, url: str) -> str:

        async with self.session.get(
            url,
            timeout=aiohttp.ClientTimeout(total=30),
            headers={
                "User-Agent": (
                    "Mozilla/5.0 "
                    "(Windows NT 10.0; Win64; x64) "
                    "AppleWebKit/537.36 "
                    "Chrome/131.0 Safari/537.36"
                )
            },
        ) as response:

            response.raise_for_status()

            return await response.text()

    def parse_page(
        self,
        html: str,
        source_url: str,
    ) -> dict:

        soup = BeautifulSoup(
            html,
            "html.parser",
        )

        title = soup.title.string.strip() if soup.title else ""

        description_tag = soup.find(
            "meta",
            attrs={"name": "description"},
        )

        description = None

        if description_tag:
            description = description_tag.get(
                "content"
            )

        return {
            "name": title,
            "description": description,
            "website": source_url,
            "industry": None,
            "location": None,
            "founded_year": None,
            "source_url": source_url,
            "collected_at": datetime.now(
                timezone.utc
            ).isoformat(),
        }

    async def crawl(
        self,
        urls: list[str],
    ):

        records = []

        connector = aiohttp.TCPConnector(
            limit=5
        )

        async with aiohttp.ClientSession(
            connector=connector
        ) as session:

            self.session = session

            for url in urls:

                print(
                    f"Fetching: {url}"
                )

                try:

                    html = await self.fetch(
                        url
                    )

                    record = self.parse_page(
                        html,
                        url,
                    )

                    validated = Startup.model_validate(
                        record
                    )

                    records.append(
                        validated.model_dump(
                            mode="json"
                        )
                    )

                except Exception as exc:

                    print(
                        f"Error: {exc}"
                    )

        return records


async def main():

    print(
        "================================"
    )
    print(
        "STARTUP CRAWLER TEST"
    )
    print(
        "================================"
    )

    # TEST ONLY
    urls = [
        "https://example.com",
        "https://example.org",
        "https://example.net",
    ]

    crawler = StartupCrawler()

    records = await crawler.crawl(
        urls
    )

    OUTPUT_FILE.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    with open(
        OUTPUT_FILE,
        "w",
        encoding="utf-8",
    ) as file:

        json.dump(
            records,
            file,
            indent=2,
            ensure_ascii=False,
        )

    print()
    print(
        f"Records collected: {len(records)}"
    )
    print(
        f"Saved: {OUTPUT_FILE}"
    )


if __name__ == "__main__":
    asyncio.run(main())