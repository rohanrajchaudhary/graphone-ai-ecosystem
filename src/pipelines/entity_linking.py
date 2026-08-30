import json
import re
from pathlib import Path
from collections import defaultdict

INPUT_FILE = Path(
    "data/processed/research_papers_extracted.json"
)

OUTPUT_FILE = Path(
    "data/processed/research_papers_linked.json"
)

ENTITY_INDEX_FILE = Path(
    "data/processed/entity_index.json"
)


def normalize(text):
    if not text:
        return ""

    text = text.lower().strip()

    # Remove common URL prefixes
    text = re.sub(
        r"^https?://(www\.)?",
        "",
        text
    )

    # Remove trailing slash
    text = text.rstrip("/")

    # Normalize spaces/symbols
    text = re.sub(
        r"[^a-z0-9]+",
        " ",
        text
    )

    return re.sub(
        r"\s+",
        " ",
        text
    ).strip()


def canonical_github(url):
    if not url:
        return None

    url = url.strip().rstrip("/")

    url = re.sub(
        r"\.git$",
        "",
        url,
        flags=re.IGNORECASE
    )

    return url


def make_entity_key(paper):
    """
    Prefer GitHub repository as the strongest deterministic
    identity signal. Otherwise use normalized paper title.
    """

    github = canonical_github(
        paper.get("githubUrl")
    )

    if github:
        return "github:" + normalize(github)

    title = normalize(
        paper.get("title")
    )

    return "paper:" + title


def build_entity(paper, entity_id):

    github = canonical_github(
        paper.get("githubUrl")
    )

    return {
        "entityId": entity_id,
        "entityType": "RESEARCH_ENTITY",
        "canonicalName": paper.get("title"),
        "normalizedName": normalize(
            paper.get("title")
        ),
        "githubUrl": github,
        "githubStars": paper.get(
            "githubStars"
        ),
        "sourceUrls": [
            paper.get("sourceUrl")
        ] if paper.get("sourceUrl") else [],
        "paperCount": 1
    }


def merge_entity(entity, paper):

    source_url = paper.get("sourceUrl")

    if source_url and source_url not in entity["sourceUrls"]:
        entity["sourceUrls"].append(source_url)

    entity["paperCount"] += 1

    stars = paper.get("githubStars")

    if stars is not None:
        current = entity.get("githubStars")

        if current is None or stars > current:
            entity["githubStars"] = stars


def main():

    print("=" * 60)
    print("GRAPHONE ENTITY LINKING")
    print("=" * 60)

    with open(
        INPUT_FILE,
        "r",
        encoding="utf-8"
    ) as f:
        papers = json.load(f)

    print(
        f"Input papers: {len(papers)}"
    )

    entities = {}
    linked_records = []

    for index, paper in enumerate(
        papers,
        start=1
    ):

        key = make_entity_key(paper)

        if key not in entities:

            entity_id = (
                f"entity_{len(entities) + 1:05d}"
            )

            entities[key] = build_entity(
                paper,
                entity_id
            )

        else:

            merge_entity(
                entities[key],
                paper
            )

        linked_records.append({
            **paper,
            "entityId": entities[key]["entityId"]
        })

        if index % 100 == 0:
            print(
                f"Linked: {index}/{len(papers)}"
            )

    entity_list = list(
        entities.values()
    )

    with open(
        OUTPUT_FILE,
        "w",
        encoding="utf-8"
    ) as f:

        json.dump(
            linked_records,
            f,
            indent=2,
            ensure_ascii=False
        )

    with open(
        ENTITY_INDEX_FILE,
        "w",
        encoding="utf-8"
    ) as f:

        json.dump(
            entity_list,
            f,
            indent=2,
            ensure_ascii=False
        )

    print()
    print("=" * 60)
    print("ENTITY LINKING COMPLETE")
    print("=" * 60)

    print(
        f"Input papers : {len(papers)}"
    )

    print(
        f"Unique entities: {len(entity_list)}"
    )

    print(
        f"Linked records: {len(linked_records)}"
    )

    print(
        f"Output: {OUTPUT_FILE}"
    )

    print(
        f"Entity index: {ENTITY_INDEX_FILE}"
    )


if __name__ == "__main__":
    main()