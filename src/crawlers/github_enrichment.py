import os
import json
import asyncio
from pathlib import Path
from datetime import datetime, timezone

import aiohttp
from dotenv import load_dotenv

load_dotenv()

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")

INPUT_FILE = Path("data/raw/arxiv_papers_raw.json")
OUTPUT_FILE = Path("data/enriched/research_papers.json")
CHECKPOINT_FILE = Path("data/checkpoints/github_enrichment.json")

GITHUB_API = "https://api.github.com"

MAX_CONCURRENT = 5
SAVE_EVERY = 25


class GitHubEnricher:

    def __init__(self):
        if not GITHUB_TOKEN:
            raise RuntimeError("GITHUB_TOKEN not found in .env")

        self.headers = {
            "Authorization": f"Bearer {GITHUB_TOKEN}",
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
            "User-Agent": "graphone-ai-pipeline",
        }

        self.semaphore = asyncio.Semaphore(MAX_CONCURRENT)

    async def search_repository(self, session, title):
        """
        Search GitHub for a repository related to the paper title.
        """

        query = title.strip()

        url = f"{GITHUB_API}/search/repositories"

        params = {
            "q": query,
            "per_page": 5,
        }

        async with self.semaphore:

            try:

                async with session.get(
                    url,
                    params=params,
                    timeout=aiohttp.ClientTimeout(total=20),
                ) as response:

                    # Rate limit
                    if response.status in (403, 429):

                        remaining = response.headers.get(
                            "X-RateLimit-Remaining"
                        )

                        reset = response.headers.get(
                            "X-RateLimit-Reset"
                        )

                        print(
                            f"GitHub rate limit response: "
                            f"{response.status}, "
                            f"remaining={remaining}, "
                            f"reset={reset}"
                        )

                        return {
                            "github_url": None,
                            "github_stars": None,
                            "error": "rate_limited",
                        }

                    if response.status != 200:

                        return {
                            "github_url": None,
                            "github_stars": None,
                            "error": f"http_{response.status}",
                        }

                    data = await response.json()

                    items = data.get("items", [])

                    if not items:

                        return {
                            "github_url": None,
                            "github_stars": None,
                            "error": None,
                        }

                    repo = items[0]

                    return {
                        "github_url": repo.get("html_url"),
                        "github_stars": repo.get("stargazers_count"),
                        "error": None,
                    }

            except Exception as e:

                return {
                    "github_url": None,
                    "github_stars": None,
                    "error": str(e),
                }

    async def enrich_paper(self, session, paper):

        title = paper.get("title", "").strip()

        if not title:

            return paper

        result = await self.search_repository(
            session,
            title
        )

        paper["github_url"] = result["github_url"]
        paper["github_stars"] = result["github_stars"]
        paper["github_error"] = result["error"]

        paper["github_checked_at"] = datetime.now(
            timezone.utc
        ).isoformat()

        return paper


def load_json(path):

    if not path.exists():
        return []

    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def save_json(path, data):

    path.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    temp_path = path.with_suffix(".tmp")

    with open(
        temp_path,
        "w",
        encoding="utf-8"
    ) as f:

        json.dump(
            data,
            f,
            indent=2,
            ensure_ascii=False
        )

    temp_path.replace(path)


async def main():

    print("=" * 60)
    print("       GITHUB ENRICHMENT PIPELINE")
    print("=" * 60)

    papers = load_json(INPUT_FILE)

    if not papers:
        print("No papers found.")
        return

    print(f"Total papers: {len(papers)}")

    # Load existing checkpoint
    checkpoint = load_json(CHECKPOINT_FILE)

    processed = {
        item.get("source_url"): item
        for item in checkpoint
        if item.get("source_url")
    }

    print(f"Already processed: {len(processed)}")

    # Existing results override raw records
    for i, paper in enumerate(papers):

        url = paper.get("source_url")

        if url in processed:
            papers[i] = processed[url]

    connector = aiohttp.TCPConnector(
        limit=MAX_CONCURRENT
    )

    async with aiohttp.ClientSession(
        headers=GitHubEnricher().headers,
        connector=connector,
    ) as session:

        enricher = GitHubEnricher()

        pending = [
            (i, paper)
            for i, paper in enumerate(papers)
            if not paper.get("github_checked_at")
        ]

        print(f"Pending papers: {len(pending)}")

        for start in range(
            0,
            len(pending),
            SAVE_EVERY
        ):

            batch = pending[
                start:start + SAVE_EVERY
            ]

            tasks = [
                enricher.enrich_paper(
                    session,
                    paper
                )
                for _, paper in batch
            ]

            results = await asyncio.gather(
                *tasks
            )

            for (index, _), result in zip(
                batch,
                results
            ):

                papers[index] = result

                print(
                    f"[{index + 1}/{len(papers)}] "
                    f"{result.get('title', '')[:70]}"
                )

                if result.get("github_url"):
                    print(
                        f"    GitHub: "
                        f"{result['github_url']}"
                    )
                    print(
                        f"    Stars: "
                        f"{result['github_stars']}"
                    )
                else:
                    print(
                        "    GitHub: None"
                    )

            # Checkpoint after every batch
            save_json(
                CHECKPOINT_FILE,
                papers
            )

            save_json(
                OUTPUT_FILE,
                papers
            )

            print(
                f"Checkpoint saved: "
                f"{len(batch)} records"
            )

            await asyncio.sleep(1)

    matches = sum(
        1
        for paper in papers
        if paper.get("github_url")
    )

    print()
    print("=" * 60)
    print("GITHUB ENRICHMENT COMPLETE")
    print("=" * 60)
    print(f"Total papers : {len(papers)}")
    print(f"GitHub matches: {matches}")
    print(f"Saved: {OUTPUT_FILE}")


if __name__ == "__main__":
    asyncio.run(main())