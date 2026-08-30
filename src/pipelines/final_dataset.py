import json
from pathlib import Path
from datetime import datetime, timezone


PAPERS_FILE = Path(
    "data/processed/research_papers_linked.json"
)

ENTITIES_FILE = Path(
    "data/processed/entity_index.json"
)

FRESH_FILE = Path(
    "data/processed/fresh_ai_data.json"
)

OUTPUT_FILE = Path(
    "data/processed/graphone_final_dataset.json"
)


def load_json(path):
    with open(
        path,
        "r",
        encoding="utf-8"
    ) as f:
        return json.load(f)


def main():

    print("=" * 60)
    print("GRAPHONE FINAL DATASET BUILDER")
    print("=" * 60)

    papers = load_json(
        PAPERS_FILE
    )

    entities = load_json(
        ENTITIES_FILE
    )

    fresh = load_json(
        FRESH_FILE
    )

    generated_at = datetime.now(
        timezone.utc
    ).isoformat()

    final_dataset = {
        "project": "GraphOne AI Ecosystem Intelligence Pipeline",

        "version": "1.0",

        "generatedAt": generated_at,

        "dataPolicy": {
            "realDataOnly": True,
            "fabricatedRecords": 0,
            "unknownValues": "null",
            "sourcePreservation": True
        },

        "statistics": {
            "researchPapers": len(
                papers
            ),
            "uniqueEntities": len(
                entities
            ),
            "freshNewsArticles": len(
                fresh.get(
                    "news",
                    {}
                ).get(
                    "items",
                    []
                )
            ),
            "jobSourcesChecked": len(
                fresh.get(
                    "jobs",
                    {}
                ).get(
                    "items",
                    []
                )
            )
        },

        "researchPapers": papers,

        "entities": entities,

        "freshAI": fresh
    }

    OUTPUT_FILE.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    with open(
        OUTPUT_FILE,
        "w",
        encoding="utf-8"
    ) as f:

        json.dump(
            final_dataset,
            f,
            indent=2,
            ensure_ascii=False
        )

    print()
    print("=" * 60)
    print("FINAL DATASET CREATED")
    print("=" * 60)

    print(
        f"Research papers : "
        f"{len(papers)}"
    )

    print(
        f"Unique entities : "
        f"{len(entities)}"
    )

    print(
        f"Fresh news      : "
        f"{len(fresh.get('news', {}).get('items', []))}"
    )

    print(
        f"Job sources     : "
        f"{len(fresh.get('jobs', {}).get('items', []))}"
    )

    print()
    print(
        f"OUTPUT: {OUTPUT_FILE}"
    )


if __name__ == "__main__":
    main()