import asyncio
import json
from pathlib import Path

from ..llm.gemini_provider import GeminiProvider
from ..llm.groq_provider import GroqProvider
from ..llm.fallback_chain import FallbackChain


INPUT_FILE = Path(
    "data/processed/startups_products_raw.json"
)

OUTPUT_FILE = Path(
    "data/processed/ai_entities_classified.json"
)

FAILED_FILE = Path(
    "data/processed/ai_entities_classification_failed.json"
)

# Keep this modest because Groq has rate limits.
BATCH_SIZE = 5


CLASSIFICATION_SCHEMA = {
    "records": [
        {
            "githubUrl": "string",
            "entityType": "STARTUP | PRODUCT | OPEN_SOURCE_PROJECT | ORGANIZATION | UNKNOWN",
            "entityName": "string",
            "organizationName": "string or null",
            "isAIRelevant": "boolean",
            "confidence": "number",
            "reason": "string"
        }
    ]
}


def load_records():

    with open(
        INPUT_FILE,
        "r",
        encoding="utf-8"
    ) as file:

        data = json.load(file)

    return data.get(
        "records",
        []
    )


def build_prompt(records):

    compact_records = []

    for record in records:

        compact_records.append({
            "githubUrl": record.get(
                "githubUrl"
            ),
            "name": record.get(
                "name"
            ),
            "fullName": record.get(
                "fullName"
            ),
            "description": record.get(
                "description"
            ),
            "homepage": record.get(
                "homepage"
            ),
            "owner": record.get(
                "owner"
            ),
            "ownerType": record.get(
                "ownerType"
            ),
            "language": record.get(
                "language"
            ),
            "stars": record.get(
                "stars"
            ),
            "topics": record.get(
                "topics",
                []
            )
        })

    return f"""
You are a strict AI ecosystem entity classification engine.

Classify EACH GitHub record.

IMPORTANT:

1. Use ONLY information present in the supplied record.
2. Never invent a company, startup, product or organization.
3. If evidence is insufficient, use UNKNOWN.
4. A GitHub repository is NOT automatically a startup.
5. A repository owner is NOT automatically a company.
6. A software library/repository can be OPEN_SOURCE_PROJECT.
7. A commercial AI application/service can be PRODUCT.
8. A company-backed AI organization can be ORGANIZATION.
9. Use STARTUP only when the supplied evidence reasonably indicates
   that the entity is a startup/company.
10. isAIRelevant must be false if the repository is clearly unrelated
    to AI.
11. confidence must be between 0 and 1.
12. Return ONLY valid JSON.
13. Do not add fields outside the schema.

SCHEMA:
{json.dumps(CLASSIFICATION_SCHEMA, indent=2)}

RECORDS:
{json.dumps(compact_records, indent=2, ensure_ascii=False)}
"""


async def classify_batch(
    batch,
    chain
):

    prompt = build_prompt(
        batch
    )

    result = await chain.extract(
        prompt,
        CLASSIFICATION_SCHEMA
    )

    if not isinstance(
        result,
        dict
    ):
        raise RuntimeError(
            "LLM returned invalid batch object"
        )

    records = result.get(
        "records"
    )

    if not isinstance(
        records,
        list
    ):
        raise RuntimeError(
            "LLM response missing records list"
        )

    return records


async def main():

    print("=" * 60)
    print("GRAPHONE AI ENTITY CLASSIFICATION")
    print("=" * 60)

    raw_records = load_records()

    print(
        f"Total raw records: "
        f"{len(raw_records)}"
    )

    gemini = GeminiProvider()
    groq = GroqProvider()

    chain = FallbackChain([
        gemini,
        groq
    ])

    classified = []
    failed = []

    total_batches = (
        len(raw_records)
        + BATCH_SIZE
        - 1
    ) // BATCH_SIZE

    for start in range(
        0,
        len(raw_records),
        BATCH_SIZE
    ):

        batch = raw_records[
            start:start + BATCH_SIZE
        ]

        batch_number = (
            start // BATCH_SIZE
        ) + 1

        print()
        print(
            f"Batch "
            f"{batch_number}/{total_batches}"
        )

        try:

            results = await classify_batch(
                batch,
                chain
            )

            # Map LLM output by GitHub URL.
            result_map = {}

            for item in results:

                url = item.get(
                    "githubUrl"
                )

                if url:
                    result_map[url] = item

            for original in batch:

                url = original.get(
                    "githubUrl"
                )

                classification = result_map.get(
                    url
                )

                if classification is None:

                    failed.append({
                        "githubUrl": url,
                        "name": original.get(
                            "name"
                        ),
                        "error": (
                            "No classification returned"
                        )
                    })

                    continue

                # Preserve authoritative source fields.
                final_record = dict(
                    original
                )

                final_record.update(
                    classification
                )

                final_record[
                    "sourceType"
                ] = "GitHub"

                classified.append(
                    final_record
                )

            print(
                f"Batch classified: "
                f"{len(results)}"
            )

        except Exception as error:

            print(
                f"Batch FAILED: {error}"
            )

            for original in batch:

                failed.append({
                    "githubUrl": original.get(
                        "githubUrl"
                    ),
                    "name": original.get(
                        "name"
                    ),
                    "error": str(error)
                })

        # Give API a small breathing period.
        await asyncio.sleep(2)

        print(
            f"Total classified: "
            f"{len(classified)}"
        )

        print(
            f"Total failed: "
            f"{len(failed)}"
        )

    # --------------------------------------------------------
    # SAVE
    # --------------------------------------------------------

    OUTPUT_FILE.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    with open(
        OUTPUT_FILE,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            {
                "recordType": "AI_ENTITY_CLASSIFICATION",
                "totalInput": len(
                    raw_records
                ),
                "totalClassified": len(
                    classified
                ),
                "records": classified
            },
            file,
            indent=2,
            ensure_ascii=False
        )

    with open(
        FAILED_FILE,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            failed,
            file,
            indent=2,
            ensure_ascii=False
        )

    # --------------------------------------------------------
    # STATISTICS
    # --------------------------------------------------------

    counts = {}

    for record in classified:

        entity_type = record.get(
            "entityType",
            "UNKNOWN"
        )

        counts[entity_type] = (
            counts.get(
                entity_type,
                0
            ) + 1
        )

    print()
    print("=" * 60)
    print("CLASSIFICATION COMPLETE")
    print("=" * 60)

    print(
        f"Input       : {len(raw_records)}"
    )

    print(
        f"Classified  : {len(classified)}"
    )

    print(
        f"Failed      : {len(failed)}"
    )

    print()
    print("ENTITY TYPES")

    for entity_type, count in sorted(
        counts.items()
    ):

        print(
            f"{entity_type}: {count}"
        )

    print()
    print(
        f"Output: {OUTPUT_FILE}"
    )

    print(
        f"Failed: {FAILED_FILE}"
    )


if __name__ == "__main__":
    asyncio.run(main())