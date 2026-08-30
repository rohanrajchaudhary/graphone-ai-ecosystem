import asyncio
import json
from pathlib import Path

from src.crawlers.paper_crawler import PaperCrawler
from src.crawlers.github_crawler import GitHubCrawler
from src.schemas.research_paper import ResearchPaper


OUTPUT_DIR = Path("data/raw")
OUTPUT_FILE = OUTPUT_DIR / "research_papers.json"


async def main():

    print("========================================")
    print("   GRAPHONE RESEARCH PAPER PIPELINE")
    print("========================================")

    # -------------------------------------
    # 1. Fetch papers from arXiv
    # -------------------------------------

    print("\n[1/4] Fetching papers from arXiv...")

    paper_crawler = PaperCrawler(max_results=10)

    papers = await paper_crawler.fetch_papers()

    print(f"Fetched: {len(papers)} papers")

    # -------------------------------------
    # 2. GitHub enrichment
    # -------------------------------------

    print("\n[2/4] Enriching GitHub information...")

    github_crawler = GitHubCrawler()

    enriched_papers = await github_crawler.enrich_papers(
        papers
    )

    print(
        f"Enriched: {len(enriched_papers)} papers"
    )

    # -------------------------------------
    # 3. Pydantic validation
    # -------------------------------------

    print("\n[3/4] Validating records...")

    valid_records = []
    invalid_records = []

    for paper in enriched_papers:

        try:

            validated = ResearchPaper.model_validate(
                paper
            )

            valid_records.append(
                validated.model_dump(mode="json")
            )

        except Exception as exc:

            invalid_records.append(
                {
                    "paper": paper,
                    "error": str(exc),
                }
            )

    print(
        f"Valid records: {len(valid_records)}"
    )

    print(
        f"Invalid records: {len(invalid_records)}"
    )

    # -------------------------------------
    # 4. Deduplication
    # -------------------------------------

    print("\n[4/4] Removing duplicates...")

    unique_records = {}

    for record in valid_records:

        key = record["source_url"]

        if key not in unique_records:
            unique_records[key] = record

    final_records = list(
        unique_records.values()
    )

    print(
        f"Final unique records: {len(final_records)}"
    )

    # -------------------------------------
    # Save JSON
    # -------------------------------------

    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    with open(
        OUTPUT_FILE,
        "w",
        encoding="utf-8",
    ) as file:

        json.dump(
            final_records,
            file,
            indent=2,
            ensure_ascii=False,
        )

    print("\n========================================")
    print("PIPELINE COMPLETE")
    print("========================================")

    print(
        f"Output: {OUTPUT_FILE}"
    )


if __name__ == "__main__":
    asyncio.run(main())