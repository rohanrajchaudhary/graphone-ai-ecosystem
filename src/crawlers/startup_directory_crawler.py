import asyncio
import json
from datetime import datetime, timezone
from pathlib import Path

import aiohttp
from bs4 import BeautifulSoup


OUTPUT_FILE = Path(
    "data/raw/startups_real_test.json"
)

BASE_URL = "https://www.startuphub.ai/startups"


class StartupDirectoryCrawler:

    def __init__(self):
        self.headers = {
            "User-Agent": (
                "Mozilla/5.0 "
                "(Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 "
                "Chrome/131.0 Safari/537.36"
            ),
            "Accept": (
                "text/html,application/xhtml+xml,"
                "application/xml;q=0.9,*/*;q=0.8"
            ),
        }

    async def fetch(self, session, url):

        async with session.get(
            url,
            headers=self.headers,
            timeout=aiohttp.ClientTimeout(
                total=30
            ),
        ) as response:

            print(
                f"HTTP {response.status}: {url}"
            )

            if response.status != 200:
                return None

            return await response.text()

    def parse(self, html, source_url):

        soup = BeautifulSoup(
            html,
            "html.parser",
        )

        records = []
        seen = set()

        for link in soup.find_all(
            "a",
            href=True,
        ):

            href = link["href"].strip()

            name = link.get_text(
                " ",
                strip=True,
            )

            if not name:
                continue

            # Convert relative URL to absolute.
            if href.startswith("/"):
                full_url = (
                    "https://www.startuphub.ai"
                    + href
                )

            elif href.startswith(
                "https://www.startuphub.ai"
            ):
                full_url = href

            else:
                continue

            # Only keep likely startup profile pages.
            if "/startup/" not in full_url.lower():
                continue

            if full_url in seen:
                continue

            seen.add(full_url)

            records.append(
                {
                    "name": name,
                    "description": None,
                    "website": None,
                    "industry": None,
                    "location": None,
                    "founded_year": None,
                    "source_url": full_url,
                    "collected_at": datetime.now(
                        timezone.utc
                    ).isoformat(),
                }
            )

        return records

    async def crawl(self):

        connector = aiohttp.TCPConnector(
            limit=3
        )

        async with aiohttp.ClientSession(
            connector=connector
        ) as session:

            html = await self.fetch(
                session,
                BASE_URL,
            )

            if not html:
                return []

            records = self.parse(
                html,
                BASE_URL,
            )

            return records


async def main():

    print(
        "========================================"
    )
    print(
        "STARTUP DIRECTORY TEST"
    )
    print(
        "========================================"
    )

    crawler = StartupDirectoryCrawler()

    records = await crawler.crawl()

    # Test only: keep first 10.
    records = records[:10]

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
        "========================================"
    )
    print(
        "TEST COMPLETE"
    )
    print(
        f"Real records: {len(records)}"
    )
    print(
        f"Saved: {OUTPUT_FILE}"
    )

    if records:
        print()
        print("FIRST RECORD:")
        print(
            json.dumps(
                records[0],
                indent=2,
                ensure_ascii=False,
            )
        )


if __name__ == "__main__":
    asyncio.run(main())