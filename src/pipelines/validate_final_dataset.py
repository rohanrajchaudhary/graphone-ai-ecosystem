import json
from pathlib import Path
from collections import Counter


DATASET = Path(
    "data/processed/graphone_final_dataset.json"
)


def main():

    print("=" * 65)
    print("GRAPHONE FINAL DATASET VALIDATION")
    print("=" * 65)

    with open(
        DATASET,
        "r",
        encoding="utf-8"
    ) as f:

        data = json.load(f)

    papers = data.get(
        "researchPapers",
        []
    )

    entities = data.get(
        "aiEntities",
        []
    )

    links = data.get(
        "paperEntityLinks",
        []
    )

    fresh = data.get(
        "freshAIData",
        {}
    )

    news = fresh.get(
        "news",
        {}
    ).get(
        "items",
        []
    )

    jobs = fresh.get(
        "jobs",
        {}
    )

    print()
    print("JSON VALID                 : YES")

    # --------------------------------------------------------
    # PAPER VALIDATION
    # --------------------------------------------------------

    paper_urls = [
        p.get("sourceUrl")
        for p in papers
        if p.get("sourceUrl")
    ]

    paper_titles = [
        p.get("title")
        for p in papers
        if p.get("title")
    ]

    print(
        f"Research papers            : {len(papers)}"
    )

    print(
        f"Papers with source URL    : {len(paper_urls)}"
    )

    print(
        f"Papers with title         : {len(paper_titles)}"
    )

    # --------------------------------------------------------
    # ENTITY VALIDATION
    # --------------------------------------------------------

    entity_names = [
        e.get("entityName")
        for e in entities
        if e.get("entityName")
    ]

    github_urls = [
        e.get("githubUrl")
        for e in entities
        if e.get("githubUrl")
    ]

    duplicate_entities = (
        len(entity_names)
        - len(set(entity_names))
    )

    duplicate_github = (
        len(github_urls)
        - len(set(github_urls))
    )

    print()
    print(
        f"AI entities                : {len(entities)}"
    )

    print(
        f"Entities with GitHub URL   : {len(github_urls)}"
    )

    print(
        f"Duplicate entity names     : {duplicate_entities}"
    )

    print(
        f"Duplicate GitHub URLs      : {duplicate_github}"
    )

    # --------------------------------------------------------
    # ENTITY TYPES
    # --------------------------------------------------------

    types = Counter(
        e.get(
            "entityType",
            "UNKNOWN"
        )
        for e in entities
    )

    print()
    print("ENTITY TYPES")
    print("-" * 65)

    for entity_type, count in sorted(
        types.items()
    ):

        print(
            f"{entity_type:25} : {count}"
        )

    # --------------------------------------------------------
    # FRESH DATA
    # --------------------------------------------------------

    print()
    print(
        f"Fresh AI news             : {len(news)}"
    )

    print(
        f"Job sources configured    : "
        f"{jobs.get('sourcesConfigured', 0)}"
    )

    print(
        f"Job sources checked      : "
        f"{jobs.get('sourcesChecked', 0)}"
    )

    # --------------------------------------------------------
    # LINKS
    # --------------------------------------------------------

    print()
    print(
        f"Paper-entity links       : {len(links)}"
    )

    print(
        f"Unresolved papers        : "
        f"{len(papers) - len(links)}"
    )

    # --------------------------------------------------------
    # CONSISTENCY
    # --------------------------------------------------------

    statistics = data.get(
        "statistics",
        {}
    )

    checks = {

        "paper_count":
            statistics.get(
                "researchPapers"
            ) == len(papers),

        "entity_count":
            statistics.get(
                "aiEntities"
            ) == len(entities),

        "link_count":
            statistics.get(
                "resolvedPaperEntityLinks"
            ) == len(links),

        "news_count":
            statistics.get(
                "freshNews"
            ) == len(news),

        "job_sources":
            statistics.get(
                "jobSourcesChecked"
            )
            == jobs.get(
                "sourcesChecked",
                0
            )
    }

    print()
    print("CONSISTENCY CHECKS")
    print("-" * 65)

    all_passed = True

    for name, passed in checks.items():

        status = (
            "PASS"
            if passed
            else "FAIL"
        )

        print(
            f"{name:25} : {status}"
        )

        if not passed:
            all_passed = False

    print()
    print("=" * 65)

    if all_passed:
        print(
            "FINAL DATASET VALIDATION: PASSED"
        )
    else:
        print(
            "FINAL DATASET VALIDATION: FAILED"
        )

    print("=" * 65)


if __name__ == "__main__":
    main()