import json
import re
from pathlib import Path


INPUT_FILE = Path(
    "data/processed/startups_products_raw.json"
)

OUTPUT_FILE = Path(
    "data/processed/ai_entities_classified.json"
)

FAILED_FILE = Path(
    "data/processed/ai_entities_classification_failed.json"
)


# ============================================================
# KEYWORDS
# ============================================================

AI_KEYWORDS = {
    "ai",
    "artificial intelligence",
    "machine learning",
    "deep learning",
    "generative ai",
    "genai",
    "llm",
    "large language model",
    "language model",
    "nlp",
    "natural language processing",
    "computer vision",
    "deep neural network",
    "neural network",
    "transformer",
    "multimodal",
    "multimodal ai",
    "rag",
    "retrieval augmented generation",
    "ai agent",
    "agentic ai",
    "robotics",
    "reinforcement learning",
    "diffusion",
    "speech recognition",
    "image generation",
    "text generation",
    "embedding",
    "vector database",
}


PRODUCT_KEYWORDS = {
    "api",
    "platform",
    "saas",
    "service",
    "application",
    "app",
    "dashboard",
    "assistant",
    "copilot",
    "chatbot",
    "search engine",
    "automation",
    "developer tool",
    "sdk",
    "cloud",
}


OPEN_SOURCE_KEYWORDS = {
    "open source",
    "opensource",
    "library",
    "framework",
    "toolkit",
    "implementation",
    "research",
    "benchmark",
    "paper",
    "pytorch",
    "tensorflow",
    "huggingface",
    "langchain",
    "llama",
    "model",
    "dataset",
}


STARTUP_KEYWORDS = {
    "startup",
    "company",
    "inc.",
    "inc",
    "labs",
    "laboratory",
    "technologies",
    "technology",
    "corp",
    "corporation",
    "ai lab",
}


def normalize(text):

    if text is None:
        return ""

    return str(text).lower().strip()


def contains_keyword(text, keywords):

    text = normalize(text)

    matched = []

    for keyword in keywords:

        if keyword in text:
            matched.append(keyword)

    return matched


def classify(record):

    name = normalize(
        record.get("name")
    )

    description = normalize(
        record.get("description")
    )

    homepage = normalize(
        record.get("homepage")
    )

    owner = normalize(
        record.get("owner")
    )

    owner_type = normalize(
        record.get("ownerType")
    )

    topics = " ".join(
        normalize(x)
        for x in record.get(
            "topics",
            []
        )
    )

    combined = " ".join([
        name,
        description,
        homepage,
        owner,
        topics
    ])

    # --------------------------------------------------------
    # AI RELEVANCE
    # --------------------------------------------------------

    ai_matches = contains_keyword(
        combined,
        AI_KEYWORDS
    )

    is_ai = len(ai_matches) > 0

    if not is_ai:

        return {
            "entityType": "UNKNOWN",
            "entityName": (
                record.get("name")
                or "Unknown"
            ),
            "organizationName": (
                record.get("owner")
            ),
            "isAIRelevant": False,
            "confidence": 0.95,
            "reason": (
                "No AI-related keyword found "
                "in available GitHub metadata."
            )
        }

    # --------------------------------------------------------
    # OPEN SOURCE / RESEARCH
    # --------------------------------------------------------

    open_matches = contains_keyword(
        combined,
        OPEN_SOURCE_KEYWORDS
    )

    # --------------------------------------------------------
    # PRODUCT
    # --------------------------------------------------------

    product_matches = contains_keyword(
        combined,
        PRODUCT_KEYWORDS
    )

    # --------------------------------------------------------
    # STARTUP / ORGANIZATION
    # --------------------------------------------------------

    startup_matches = contains_keyword(
        combined,
        STARTUP_KEYWORDS
    )

    # --------------------------------------------------------
    # DECISION LOGIC
    # --------------------------------------------------------

    # Strong open-source/research signals.
    if (
        len(open_matches) >= 2
        and len(product_matches) == 0
    ):

        entity_type = (
            "OPEN_SOURCE_PROJECT"
        )

        confidence = 0.90

        reason = (
            "Repository metadata contains "
            "strong open-source/research indicators."
        )

    # Product signals.
    elif len(product_matches) >= 2:

        entity_type = "PRODUCT"

        confidence = 0.85

        reason = (
            "Repository metadata contains "
            "multiple product/service indicators."
        )

    # Explicit company/startup signals.
    elif len(startup_matches) >= 1:

        entity_type = "STARTUP"

        confidence = 0.75

        reason = (
            "Repository metadata contains "
            "company/startup indicators."
        )

    # GitHub user/org information.
    elif owner_type == "organization":

        entity_type = "ORGANIZATION"

        confidence = 0.70

        reason = (
            "Repository owner is identified "
            "by GitHub as an organization."
        )

    # AI repositories without enough evidence.
    else:

        entity_type = (
            "OPEN_SOURCE_PROJECT"
        )

        confidence = 0.65

        reason = (
            "AI-related repository with "
            "insufficient evidence for a commercial entity."
        )

    return {
        "entityType": entity_type,

        "entityName": (
            record.get("name")
            or record.get("fullName")
            or "Unknown"
        ),

        "organizationName": (
            record.get("owner")
        ),

        "isAIRelevant": True,

        "confidence": confidence,

        "reason": reason
    }


def load_input():

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


def main():

    print("=" * 60)
    print("GRAPHONE LOCAL AI ENTITY CLASSIFIER")
    print("=" * 60)

    records = load_input()

    print(
        f"Input records: {len(records)}"
    )

    classified = []
    failed = []

    for index, record in enumerate(
        records,
        start=1
    ):

        try:

            classification = classify(
                record
            )

            final_record = dict(
                record
            )

            final_record.update(
                classification
            )

            final_record[
                "classificationMethod"
            ] = "DETERMINISTIC_GITHUB_METADATA"

            final_record[
                "sourceVerified"
            ] = True

            classified.append(
                final_record
            )

        except Exception as error:

            failed.append({
                "record": record,
                "error": str(error)
            })

        # Progress every 100 records.
        if (
            index % 100 == 0
            or index == len(records)
        ):

            print(
                f"Processed: "
                f"{index}/{len(records)}"
            )

    # --------------------------------------------------------
    # SAVE CLASSIFIED
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
                "recordType":
                    "AI_ENTITY_CLASSIFICATION",

                "classificationMethod":
                    "DETERMINISTIC_GITHUB_METADATA",

                "totalInput":
                    len(records),

                "totalClassified":
                    len(classified),

                "totalFailed":
                    len(failed),

                "records":
                    classified
            },
            file,
            indent=2,
            ensure_ascii=False
        )

    # --------------------------------------------------------
    # SAVE FAILURES
    # --------------------------------------------------------

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

    stats = {}

    ai_count = 0

    for record in classified:

        entity_type = record.get(
            "entityType",
            "UNKNOWN"
        )

        stats[entity_type] = (
            stats.get(
                entity_type,
                0
            ) + 1
        )

        if record.get(
            "isAIRelevant"
        ):
            ai_count += 1

    print()
    print("=" * 60)
    print("CLASSIFICATION COMPLETE")
    print("=" * 60)

    print(
        f"Total input : {len(records)}"
    )

    print(
        f"Classified  : {len(classified)}"
    )

    print(
        f"Failed      : {len(failed)}"
    )

    print(
        f"AI relevant : {ai_count}"
    )

    print()
    print("ENTITY BREAKDOWN")

    for entity_type in sorted(
        stats
    ):

        print(
            f"{entity_type}: "
            f"{stats[entity_type]}"
        )

    print()
    print(
        f"Output: {OUTPUT_FILE}"
    )

    print(
        f"Failed: {FAILED_FILE}"
    )


if __name__ == "__main__":
    main()