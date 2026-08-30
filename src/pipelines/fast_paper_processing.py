import json
from pathlib import Path

from ..schemas.records import ResearchPaperRecord


INPUT_FILE = Path("data/raw/arxiv_papers_raw.json")
OUTPUT_FILE = Path("data/processed/research_papers_extracted.json")
FAILED_FILE = Path("data/processed/research_papers_failed.json")


def load_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def save_json(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)

    with open(path, "w", encoding="utf-8") as f:
        json.dump(
            data,
            f,
            indent=2,
            ensure_ascii=False
        )


def build_record(paper):

    record = {
        "recordType": "RESEARCH_PAPER",
        "title": paper.get("title"),
        "authors": paper.get("authors", []),
        "abstract": paper.get("abstract"),
        "sourceUrl": paper.get("source_url"),
        "githubUrl": paper.get("github_url"),
        "githubStars": paper.get("github_stars")
    }

    return record


def main():

    print("=" * 60)
    print("GRAPHONE FAST REAL-DATA PAPER PROCESSOR")
    print("=" * 60)

    papers = load_json(INPUT_FILE)

    print(f"Input papers: {len(papers)}")

    valid_records = []
    failed_records = []

    for index, paper in enumerate(papers, start=1):

        try:

            record = build_record(paper)

            validated = (
                ResearchPaperRecord
                .model_validate(record)
            )

            valid_records.append(
                validated.model_dump(
                    mode="json"
                )
            )

            if index % 100 == 0:
                print(
                    f"Processed: {index}/{len(papers)}"
                )

        except Exception as error:

            failed_records.append({
                "title": paper.get("title"),
                "source_url": paper.get("source_url"),
                "error": str(error)
            })

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
    print("PROCESSING COMPLETE")
    print("=" * 60)

    print(
        f"Total input : {len(papers)}"
    )

    print(
        f"Valid       : {len(valid_records)}"
    )

    print(
        f"Failed      : {len(failed_records)}"
    )

    print(
        f"Output      : {OUTPUT_FILE}"
    )

    print(
        f"Failed      : {FAILED_FILE}"
    )


if __name__ == "__main__":
    main()