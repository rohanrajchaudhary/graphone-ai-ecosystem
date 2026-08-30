import asyncio
import json
import re
from pathlib import Path

import aiohttp


INPUT_FILE = Path("data/raw/arxiv_papers_raw.json")
OUTPUT_FILE = Path("data/enriched/research_papers.json")
CHECKPOINT_FILE = Path(
    "data/checkpoints/github_enrichment.json"
)

GITHUB_API = "https://api.github.com"


class GitHubEnricher:

    def __init__(
        self,
        token: str | None = None,
        delay: float = 1.0,
    ):
        self.token = token
        self.delay = delay

    def headers(self):

        headers = {
            "Accept": "application/vnd.github+json",
            "User-Agent": "GraphOne-AI-Pipeline/1.0",
        }

        if self.token:
            headers["Authorization"] = (
                f"Bearer {self.token}"
            )

        return headers

    @staticmethod
    def normalize_title(title: str) -> str:

        title = title.lower()

        title = re.sub(
            r"[^a-z0-9\s]",
            " ",
            title,
        )

        title = re.sub(
            r"\s+",
            " ",
            title,
        )

        return title.strip()

    @staticmethod
    def title_tokens(title: str) -> set[str]:

        stop_words = {
            "a",
            "an",
            "the",
            "of",
            "for",
            "and",
            "to",
            "in",
            "on",
            "with",
            "from",
            "using",
            "via",
            "based",
            "towards",
            "toward",
        }

        normalized = (
            GitHubEnricher.normalize_title(title)
        )

        return {
            word
            for word in normalized.split()
            if word not in stop_words
        }

    def similarity(
        self,
        paper_title: str,
        repo: dict,
    ) -> float:

        paper_tokens = self.title_tokens(
            paper_title
        )

        repo_text = " ".join(
            [
                repo.get("name", ""),
                repo.get("description") or "",
            ]
        )

        repo_tokens = self.title_tokens(
            repo_text
        )

        if not paper_tokens or not repo_tokens:
            return 0.0

        intersection = (
            paper_tokens & repo_tokens
        )

        return len(intersection) / len(
            paper_tokens
        )

    async def search_repository(
        self,
        session,
        title: str,
    ):

        params = {
            "q": title,
            "per_page": 10,
        }

        url = (
            f"{GITHUB_API}/search/repositories"
        )

        async with session.get(
            url,
            params=params,
            headers=self.headers(),
            timeout=aiohttp.ClientTimeout(
                total=30
            ),
        ) as response:

            if response.status == 403:
                print(
                    "GitHub rate limit reached."
                )
                return []

            if response.status != 200:
                return []

            data = await response.json()

            return data.get("items", [])

    async def enrich_one(
        self,
        session,
        paper: dict,
    ):

        candidates = await self.search_repository(
            session,
            paper["title"],
        )

        best_repo = None
        best_score = 0.0

        for repo in candidates:

            score = self.similarity(
                paper["title"],
                repo,
            )

            if score > best_score:

                best_score = score
                best_repo = repo

        # Conservative threshold.
        if (
            best_repo is not None
            and best_score >= 0.60
        ):

            paper["github_url"] = (
                best_repo.get("html_url")
            )

            paper["github_stars"] = (
                best_repo.get("stargazers_count")
            )

            paper["github_match_method"] = (
                "title_similarity"
            )

            paper["github_match_confidence"] = round(
                best_score,
                3,
            )

        else:

            paper["github_url"] = None
            paper["github_stars"] = None
            paper["github_match_method"] = None
            paper["github_match_confidence"] = 0.0

        return paper

    async def run(
        self,
        papers: list[dict],
    ):

        results = []

        connector = aiohttp.TCPConnector(
            limit=2
        )

        async with aiohttp.ClientSession(
            connector=connector
        ) as session:

            for index, paper in enumerate(
                papers,
                start=1,
            ):

                print(
                    f"[{index}/{len(papers)}] "
                    f"{paper['title'][:80]}"
                )

                try:

                    result = await self.enrich_one(
                        session,
                        paper,
                    )

                    results.append(result)

                except Exception as exc:

                    print(
                        f"  Error: {exc}"
                    )

                    paper["github_url"] = None
                    paper["github_stars"] = None
                    paper[
                        "github_match_method"
                    ] = None
                    paper[
                        "github_match_confidence"
                    ] = 0.0

                    results.append(paper)

                await asyncio.sleep(
                    self.delay
                )

        return results


async def main():

    print(
        "Loading arXiv dataset..."
    )

    with open(
        INPUT_FILE,
        "r",
        encoding="utf-8",
    ) as file:

        papers = json.load(file)

    print(
        f"Loaded {len(papers)} papers"
    )

    OUTPUT_FILE.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    CHECKPOINT_FILE.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    enricher = GitHubEnricher()

    results = await enricher.run(
        papers
    )

    with open(
        OUTPUT_FILE,
        "w",
        encoding="utf-8",
    ) as file:

        json.dump(
            results,
            file,
            indent=2,
            ensure_ascii=False,
        )

    github_matches = sum(
        1
        for paper in results
        if paper.get("github_url")
    )

    print()
    print(
        "========================================"
    )
    print(
        "GITHUB ENRICHMENT COMPLETE"
    )
    print(
        "========================================"
    )
    print(
        f"Total papers : {len(results)}"
    )
    print(
        f"GitHub matches: {github_matches}"
    )
    print(
        f"Saved: {OUTPUT_FILE}"
    )


if __name__ == "__main__":
    asyncio.run(main())