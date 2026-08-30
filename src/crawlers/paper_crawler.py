import asyncio
import json
from datetime import datetime, timezone
from pathlib import Path

import aiohttp
from bs4 import BeautifulSoup


ARXIV_API_URL = "https://export.arxiv.org/api/query"


class PaperCrawler:

    def __init__(
        self,
        max_results: int = 1000,
        batch_size: int = 100,
        delay: float = 3.0,
    ):
        self.max_results = max_results
        self.batch_size = batch_size
        self.delay = delay

    async def fetch_batch(
        self,
        session: aiohttp.ClientSession,
        start: int,
        count: int,
    ) -> list[dict]:

        params = {
            "search_query": "cat:cs.AI",
            "start": start,
            "max_results": count,
            "sortBy": "submittedDate",
            "sortOrder": "descending",
        }

        headers = {
            "User-Agent": "GraphOne-AI-Pipeline/1.0"
        }

        async with session.get(
            ARXIV_API_URL,
            params=params,
            headers=headers,
            timeout=aiohttp.ClientTimeout(total=120),
        ) as response:

            response.raise_for_status()
            xml_data = await response.text()

        return self.parse_response(xml_data)

    def parse_response(
        self,
        xml_data: str,
    ) -> list[dict]:

        soup = BeautifulSoup(xml_data, "xml")
        papers = []

        for entry in soup.find_all("entry"):

            title_element = entry.find("title")
            summary_element = entry.find("summary")
            published_element = entry.find("published")
            id_element = entry.find("id")

            if not title_element or not id_element:
                continue

            title = title_element.get_text(
                " ",
                strip=True,
            )

            abstract = (
                summary_element.get_text(
                    " ",
                    strip=True,
                )
                if summary_element
                else None
            )

            published = (
                published_element.get_text(
                    strip=True,
                )
                if published_element
                else None
            )

            arxiv_url = id_element.get_text(
                strip=True,
            )

            authors = []

            for author in entry.find_all("author"):
                name = author.find("name")
                if name:
                    authors.append(name.get_text(strip=True))

            papers.append(
                {
                    "title": title,
                    "authors": authors,
                    "abstract": abstract,
                    "published_date": published,
                    "arxiv_url": arxiv_url,
                    "papers_with_code_url": None,
                    "github_url": None,
                    "github_stars": None,
                    "source_url": arxiv_url,
                    "collected_at": datetime.now(
                        timezone.utc
                    ).isoformat(),
                }
            )

        return papers

    async def fetch_papers(self) -> list[dict]:

        checkpoint_dir = Path("data/checkpoints")
        checkpoint_dir.mkdir(
            parents=True,
            exist_ok=True,
        )

        checkpoint_file = (
            checkpoint_dir / "arxiv_checkpoint.json"
        )

        all_papers = []
        completed_batches = set()

        # -------------------------------------
        # Load checkpoint if available
        # -------------------------------------

        if checkpoint_file.exists():
            try:
                with open(
                    checkpoint_file,
                    "r",
                    encoding="utf-8",
                ) as file:
                    checkpoint = json.load(file)

                all_papers = checkpoint.get("papers", [])
                completed_batches = set(
                    checkpoint.get("completed_batches", [])
                )

                print(
                    f"Checkpoint loaded: {len(all_papers)} papers"
                )

            except Exception as exc:
                print(f"Could not load checkpoint: {exc}")

        connector = aiohttp.TCPConnector(limit=2)

        async with aiohttp.ClientSession(
            connector=connector
        ) as session:

            for start in range(
                0,
                self.max_results,
                self.batch_size,
            ):

                # Skip completed batch
                if start in completed_batches:
                    print(f"Skipping completed batch: {start}")
                    continue

                remaining = self.max_results - start
                count = min(self.batch_size, remaining)

                print(
                    f"\nFetching papers {start + 1} - {start + count}..."
                )

                try:
                    batch = await self.fetch_batch(
                        session,
                        start,
                        count,
                    )

                    all_papers.extend(batch)
                    completed_batches.add(start)

                    print(f"Received: {len(batch)}")

                    # ---------------------------------
                    # Save checkpoint after every batch
                    # ---------------------------------

                    checkpoint = {
                        "completed_batches": sorted(
                            completed_batches
                        ),
                        "papers": all_papers,
                        "updated_at": datetime.now(
                            timezone.utc
                        ).isoformat(),
                    }

                    with open(
                        checkpoint_file,
                        "w",
                        encoding="utf-8",
                    ) as file:
                        json.dump(
                            checkpoint,
                            file,
                            indent=2,
                            ensure_ascii=False,
                        )

                    print(
                        f"Checkpoint saved: {len(all_papers)} papers"
                    )

                except Exception as exc:
                    print(
                        f"Batch failed at start={start}: {exc}"
                    )
                    print("Progress has been saved.")
                    continue

                if start + count < self.max_results:
                    await asyncio.sleep(self.delay)

        # -------------------------------------
        # Deduplicate
        # -------------------------------------

        unique = {}

        for paper in all_papers:
            url = paper.get("source_url")
            if url and url not in unique:
                unique[url] = paper

        return list(unique.values())


async def main():

    # Development test.
    crawler = PaperCrawler(
        max_results=1000,
        batch_size=50,
    )

    papers = await crawler.fetch_papers()

    print()
    print("==============================")
    print("PAPER ACQUISITION COMPLETE")
    print("==============================")
    print("Requested:", crawler.max_results)
    print("Unique:", len(papers))

    output_dir = Path("data/raw")
    output_dir.mkdir(
        parents=True,
        exist_ok=True,
    )

    output_file = output_dir / "arxiv_papers_raw.json"

    with open(
        output_file,
        "w",
        encoding="utf-8",
    ) as file:
        json.dump(
            papers,
            file,
            indent=2,
            ensure_ascii=False,
        )

    print("Saved:", output_file)


if __name__ == "__main__":
    asyncio.run(main())