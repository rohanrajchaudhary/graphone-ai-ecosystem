import asyncio
import json
import random
from pathlib import Path

from ..llm.groq_provider import GroqProvider
from ..schemas.records import ResearchPaperRecord


# ============================================================
# CONFIG
# ============================================================

INPUT_FILE = Path("data/raw/arxiv_papers_raw.json")
OUTPUT_FILE = Path("data/processed/research_papers_extracted.json")
FAILED_FILE = Path("data/processed/research_papers_failed.json")

# IMPORTANT:
# One request at a time to reduce 429s.
REQUEST_DELAY = 5

# Wait between batches
BATCH_DELAY = 10

# Maximum times we will handle a 429 ourselves
MAX_429_RETRIES = 5

# Initial 429 wait
INITIAL_429_WAIT = 30

# Maximum wait
MAX_429_WAIT = 180


# ============================================================
# SCHEMA
# ============================================================

PAPER_SCHEMA = {
    "recordType": "RESEARCH_PAPER",
    "title": "string",
    "authors": ["string"],
    "abstract": "string or null",
    "sourceUrl": "string",
    "githubUrl": "string or null",
    "githubStars": "integer or null"
}


# ============================================================
# JSON
# ============================================================

def load_json(path, default=None):

    if default is None:
        default = []

    if not path.exists():
        return default

    with open(
        path,
        "r",
        encoding="utf-8"
    ) as file:
        return json.load(file)


def save_json(path, data):

    path.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    temp_file = path.with_suffix(".tmp")

    with open(
        temp_file,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            data,
            file,
            indent=2,
            ensure_ascii=False
        )

    temp_file.replace(path)


# ============================================================
# SOURCE TEXT
# ============================================================

def build_source_text(paper):

    return f"""
TITLE:
{paper.get("title")}

AUTHORS:
{json.dumps(paper.get("authors", []))}

ABSTRACT:
{paper.get("abstract")}

SOURCE URL:
{paper.get("source_url")}

GITHUB URL:
{paper.get("github_url")}

GITHUB STARS:
{paper.get("github_stars")}
"""


# ============================================================
# RATE LIMIT CHECK
# ============================================================

def is_429(error):

    text = str(error).lower()

    return (
        "429" in text
        or "rate limit" in text
        or "too many requests" in text
    )


# ============================================================
# EXTRACT ONE PAPER
# ============================================================

async def process_paper(
    paper,
    provider
):

    rate_attempt = 0

    while True:

        try:

            print(
                "Sending request to Groq..."
            )

            result = await provider.extract(
                build_source_text(paper),
                PAPER_SCHEMA
            )

            if result is None:
                raise RuntimeError(
                    "Empty response from Groq"
                )

            # ------------------------------------------------
            # PRESERVE ORIGINAL DATA
            # ------------------------------------------------

            result["sourceUrl"] = (
                paper.get("source_url")
            )

            result["githubUrl"] = (
                paper.get("github_url")
            )

            result["githubStars"] = (
                paper.get("github_stars")
            )

            # ------------------------------------------------
            # VALIDATE
            # ------------------------------------------------

            validated = (
                ResearchPaperRecord.model_validate(
                    result
                )
            )

            return (
                "SUCCESS",
                validated.model_dump(
                    mode="json"
                ),
                None
            )

        except Exception as error:

            # =================================================
            # 429
            # =================================================

            if is_429(error):

                rate_attempt += 1

                print()
                print(
                    f"⚠️ Groq 429 "
                    f"({rate_attempt}/"
                    f"{MAX_429_RETRIES})"
                )

                if rate_attempt > MAX_429_RETRIES:

                    print(
                        "⏸️ Rate limit still active."
                    )

                    print(
                        "Paper will be retried "
                        "on the next run."
                    )

                    return (
                        "PENDING",
                        None,
                        None
                    )

                # Exponential backoff
                wait = min(
                    MAX_429_WAIT,
                    INITIAL_429_WAIT
                    * (
                        2
                        ** (
                            rate_attempt - 1
                        )
                    )
                )

                # Small random jitter
                wait += random.uniform(
                    0,
                    8
                )

                print(
                    f"⏳ Waiting "
                    f"{wait:.1f}s..."
                )

                await asyncio.sleep(
                    wait
                )

                continue

            # =================================================
            # NORMAL ERROR
            # =================================================

            print(
                f"❌ Failed: {error}"
            )

            return (
                "FAILED",
                None,
                {
                    "source_url":
                        paper.get(
                            "source_url"
                        ),
                    "title":
                        paper.get(
                            "title"
                        ),
                    "error":
                        str(error)
                }
            )


# ============================================================
# MAIN
# ============================================================

async def main():

    print("=" * 60)
    print(
        "GRAPHONE RESEARCH PAPER LLM PIPELINE"
    )
    print("=" * 60)

    # --------------------------------------------------------
    # LOAD ALL PAPERS
    # --------------------------------------------------------

    papers = load_json(
        INPUT_FILE,
        []
    )

    # --------------------------------------------------------
    # LOAD EXISTING SUCCESSFUL RECORDS
    # --------------------------------------------------------

    existing = load_json(
        OUTPUT_FILE,
        []
    )

    processed_urls = {
        item.get("sourceUrl")
        for item in existing
        if item.get("sourceUrl")
    }

    # --------------------------------------------------------
    # FIND REMAINING
    # --------------------------------------------------------

    remaining = [
        paper
        for paper in papers
        if paper.get("source_url")
        not in processed_urls
    ]

    print()
    print(
        f"Total papers     : {len(papers)}"
    )

    print(
        f"Already processed: "
        f"{len(processed_urls)}"
    )

    print(
        f"Remaining        : "
        f"{len(remaining)}"
    )

    if not remaining:

        print()
        print(
            "✅ EVERYTHING IS COMPLETE!"
        )

        return

    # --------------------------------------------------------
    # PROVIDER
    # --------------------------------------------------------

    provider = GroqProvider()

    valid_records = existing.copy()

    failed_records = []

    # --------------------------------------------------------
    # BATCH COUNT
    # --------------------------------------------------------

    total_batches = (
        len(remaining)
        + 9
    ) // 10

    # ========================================================
    # PROCESS
    # ========================================================

    for start in range(
        0,
        len(remaining),
        10
    ):

        batch = remaining[
            start:start + 10
        ]

        batch_number = (
            start // 10
        ) + 1

        print()
        print("=" * 60)
        print(
            f"Batch {batch_number}/"
            f"{total_batches}"
        )
        print("=" * 60)

        batch_success = 0
        batch_failed = 0
        batch_pending = 0

        # ----------------------------------------------------
        # ONE PAPER AT A TIME
        # ----------------------------------------------------

        for i, paper in enumerate(
            batch,
            start=1
        ):

            print()
            print(
                f"Paper {i}/{len(batch)}"
            )

            print(
                f"Title: "
                f"{paper.get('title', '')[:100]}"
            )

            status, result, error = (
                await process_paper(
                    paper,
                    provider
                )
            )

            # ------------------------------------------------
            # SUCCESS
            # ------------------------------------------------

            if status == "SUCCESS":

                valid_records.append(
                    result
                )

                batch_success += 1

                # SAVE IMMEDIATELY
                save_json(
                    OUTPUT_FILE,
                    valid_records
                )

                print(
                    "✅ SUCCESS - SAVED"
                )

            # ------------------------------------------------
            # PENDING
            # ------------------------------------------------

            elif status == "PENDING":

                batch_pending += 1

                print(
                    "⏸️ PENDING"
                )

                # Stop current run instead of
                # hammering the API further.
                print()
                print(
                    "🛑 Rate limit is too high."
                )

                print(
                    "Stopping safely."
                )

                print(
                    "Already saved records "
                    "are safe."
                )

                save_json(
                    OUTPUT_FILE,
                    valid_records
                )

                return

            # ------------------------------------------------
            # FAILED
            # ------------------------------------------------

            else:

                batch_failed += 1

                if error:
                    failed_records.append(
                        error
                    )

                save_json(
                    FAILED_FILE,
                    failed_records
                )

                print(
                    "❌ FAILED"
                )

            # ------------------------------------------------
            # DELAY
            # ------------------------------------------------

            if i < len(batch):

                print(
                    f"Waiting "
                    f"{REQUEST_DELAY}s..."
                )

                await asyncio.sleep(
                    REQUEST_DELAY
                )

        # ----------------------------------------------------
        # SAVE
        # ----------------------------------------------------

        save_json(
            OUTPUT_FILE,
            valid_records
        )

        save_json(
            FAILED_FILE,
            failed_records
        )

        remaining_count = (
            len(remaining)
            - start
            - len(batch)
        )

        # ----------------------------------------------------
        # BATCH SUMMARY
        # ----------------------------------------------------

        print()
        print(
            "BATCH SUMMARY"
        )

        print(
            f"Successful: "
            f"{batch_success}"
        )

        print(
            f"Failed: "
            f"{batch_failed}"
        )

        print(
            f"Pending: "
            f"{batch_pending}"
        )

        print(
            f"Total saved: "
            f"{len(valid_records)}"
        )

        print(
            f"Remaining: "
            f"{remaining_count}"
        )

        # ----------------------------------------------------
        # BATCH DELAY
        # ----------------------------------------------------

        if remaining_count > 0:

            print()
            print(
                f"⏳ Batch cooldown "
                f"{BATCH_DELAY}s..."
            )

            await asyncio.sleep(
                BATCH_DELAY
            )

    # ========================================================
    # FINAL
    # ========================================================

    save_json(
        OUTPUT_FILE,
        valid_records
    )

    save_json(
        FAILED_FILE,
        failed_records
    )

    print()
    print("=" * 60)
    print(
        "PIPELINE COMPLETE"
    )
    print("=" * 60)

    print(
        f"Total papers : "
        f"{len(papers)}"
    )

    print(
        f"Valid records: "
        f"{len(valid_records)}"
    )

    print(
        f"Failed       : "
        f"{len(failed_records)}"
    )

    print(
        f"Output       : "
        f"{OUTPUT_FILE}"
    )

    print(
        f"Failed output: "
        f"{FAILED_FILE}"
    )


if __name__ == "__main__":

    asyncio.run(main())