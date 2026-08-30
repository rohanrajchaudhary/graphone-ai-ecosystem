from pathlib import Path
import json
import shutil
from datetime import datetime


# ============================================================
# GRAPHONE FINAL DATASET BUILDER
# ============================================================

ROOT = Path(__file__).resolve().parent

RAW_DIR = ROOT / "data" / "raw"
PROCESSED_DIR = ROOT / "data" / "processed"
REPORT_DIR = ROOT / "data" / "reports"

PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
REPORT_DIR.mkdir(parents=True, exist_ok=True)


FINAL_FILE = PROCESSED_DIR / "graphone_final_dataset.json"
REPORT_FILE = REPORT_DIR / "data_quality_report.json"


# ============================================================
# HELPERS
# ============================================================

def load_json(path: Path):
    """Safely load JSON file."""

    if not path.exists():
        return None

    try:
        with path.open("r", encoding="utf-8") as f:
            return json.load(f)

    except Exception as e:
        print(f"[WARNING] Could not load {path}: {e}")
        return None


def find_first(candidates):
    """Return first existing candidate file."""

    for path in candidates:
        if path.exists():
            return path

    return None


def extract_list(data, possible_keys):
    """
    Extract a list from either:
        [...]
    or:
        {"items": [...]}
        {"papers": [...]}
        {"entities": [...]}
    """

    if isinstance(data, list):
        return data

    if isinstance(data, dict):

        for key in possible_keys:

            value = data.get(key)

            if isinstance(value, list):
                return value

    return []


def unique_records(records, key_candidates):
    """
    Remove duplicates using available identifiers.
    """

    seen = set()
    result = []

    for record in records:

        if not isinstance(record, dict):
            continue

        identifier = None

        for key in key_candidates:

            value = record.get(key)

            if value:
                identifier = str(value).strip().lower()
                break

        if identifier is None:

            identifier = json.dumps(
                record,
                sort_keys=True,
                ensure_ascii=False
            )

        if identifier not in seen:

            seen.add(identifier)
            result.append(record)

    return result


def backup_existing_file():

    if not FINAL_FILE.exists():
        return None

    timestamp = datetime.now().strftime(
        "%Y%m%d_%H%M%S"
    )

    backup = (
        PROCESSED_DIR
        / f"graphone_final_dataset_backup_{timestamp}.json"
    )

    shutil.copy2(
        FINAL_FILE,
        backup
    )

    print(f"[BACKUP] {backup}")

    return backup


# ============================================================
# PAPERS
# ============================================================

print()
print("=" * 70)
print("GRAPHONE FINAL DATASET BUILDER")
print("=" * 70)
print()


paper_file = find_first([
    RAW_DIR / "arxiv_papers_raw.json",
    RAW_DIR / "research_papers.json",
    PROCESSED_DIR / "research_papers_extracted.json",
    PROCESSED_DIR / "research_papers.json",
])


if not paper_file:

    raise FileNotFoundError(
        "No research paper dataset found."
    )


print(f"[PAPERS] Source: {paper_file}")


paper_data = load_json(paper_file)


papers = extract_list(
    paper_data,
    [
        "papers",
        "researchPapers",
        "items",
        "records",
        "data",
    ]
)


papers = unique_records(
    papers,
    [
        "id",
        "paperId",
        "arxiv_id",
        "arxivId",
        "arxiv_url",
        "arxivUrl",
        "url",
        "sourceUrl",
        "title",
    ]
)


print(f"[PAPERS] Unique papers: {len(papers)}")


# ============================================================
# ENTITIES
# ============================================================

entity_candidates = [

    PROCESSED_DIR / "ai_entities.json",
    PROCESSED_DIR / "entities.json",
    PROCESSED_DIR / "extracted_entities.json",
    PROCESSED_DIR / "entity_extraction.json",

    RAW_DIR / "ai_entities.json",
    RAW_DIR / "entities.json",
]


entity_file = find_first(entity_candidates)


entities = []


if entity_file:

    print(f"[ENTITIES] Source: {entity_file}")

    entity_data = load_json(entity_file)

    entities = extract_list(
        entity_data,
        [
            "entities",
            "aiEntities",
            "items",
            "records",
            "data",
        ]
    )

else:

    print(
        "[ENTITIES] No separate entity file found."
    )


entities = unique_records(
    entities,
    [
        "id",
        "entityId",
        "entityName",
        "name",
    ]
)


print(f"[ENTITIES] Unique entities: {len(entities)}")


# ============================================================
# ENTITY LINKS
# ============================================================

link_candidates = [

    PROCESSED_DIR / "entity_resolution.json",
    PROCESSED_DIR / "entity_links.json",
    PROCESSED_DIR / "paper_entity_links.json",
    PROCESSED_DIR / "paperEntityLinks.json",

    RAW_DIR / "entity_resolution.json",
    RAW_DIR / "entity_links.json",
]


link_file = find_first(link_candidates)


links = []


if link_file:

    print(f"[LINKS] Source: {link_file}")

    link_data = load_json(link_file)

    links = extract_list(
        link_data,
        [
            "links",
            "paperEntityLinks",
            "entityLinks",
            "items",
            "records",
            "data",
        ]
    )

else:

    print(
        "[LINKS] No entity-link file found."
    )


links = unique_records(
    links,
    [
        "id",
        "linkId",
        "paperId",
        "entityId",
    ]
)


print(f"[LINKS] Unique links: {len(links)}")


# ============================================================
# FRESH AI DATA
# ============================================================

fresh_candidates = [

    PROCESSED_DIR / "fresh_ai_data.json",
    PROCESSED_DIR / "freshAIData.json",
    PROCESSED_DIR / "fresh_intelligence.json",

    RAW_DIR / "fresh_ai_data.json",
    RAW_DIR / "freshAIData.json",
    RAW_DIR / "fresh_intelligence.json",
]


fresh_file = find_first(fresh_candidates)


fresh_data = {
    "news": [],
    "jobs": [],
}


if fresh_file:

    print(f"[FRESH] Source: {fresh_file}")

    loaded_fresh = load_json(fresh_file)

    if isinstance(loaded_fresh, dict):

        fresh_data = {
            "news": loaded_fresh.get(
                "news",
                []
            ),
            "jobs": loaded_fresh.get(
                "jobs",
                []
            ),
        }

else:

    print(
        "[FRESH] No separate fresh intelligence file found."
    )


news = (
    fresh_data.get("news", [])
    if isinstance(
        fresh_data.get("news", []),
        list
    )
    else []
)


jobs = (
    fresh_data.get("jobs", [])
    if isinstance(
        fresh_data.get("jobs", []),
        list
    )
    else []
)


print(f"[FRESH] News: {len(news)}")
print(f"[FRESH] Jobs: {len(jobs)}")


# ============================================================
# BACKUP
# ============================================================

backup_existing_file()


# ============================================================
# FINAL DATASET
# ============================================================

generated_at = datetime.now().astimezone().isoformat()


final_dataset = {

    "datasetName":
        "GRAPHONE AI ECOSYSTEM DATASET",

    "version":
        "1.0.0",

    "generatedAt":
        generated_at,

    "statistics": {

        "researchPapers":
            len(papers),

        "aiEntities":
            len(entities),

        "paperEntityLinks":
            len(links),

        "freshNews":
            len(news),

        "freshJobs":
            len(jobs),

    },

    "researchPapers":
        papers,

    "aiEntities":
        entities,

    "paperEntityLinks":
        links,

    "freshAIData": {

        "news":
            news,

        "jobs":
            jobs,

    },

}


# ============================================================
# WRITE FINAL DATASET
# ============================================================

with FINAL_FILE.open(
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
print("=" * 70)
print("FINAL DATASET CREATED")
print("=" * 70)

print(
    f"Research Papers : {len(papers):,}"
)

print(
    f"AI Entities     : {len(entities):,}"
)

print(
    f"Entity Links    : {len(links):,}"
)

print(
    f"Fresh News      : {len(news):,}"
)

print(
    f"Fresh Jobs      : {len(jobs):,}"
)

print()
print(
    f"Saved to: {FINAL_FILE}"
)


# ============================================================
# DATA QUALITY REPORT
# ============================================================

quality_report = {

    "generatedAt":
        generated_at,

    "dataset":
        "GRAPHONE AI ECOSYSTEM DATASET",

    "status":
        "completed",

    "files": {

        "paperSource":
            str(paper_file.relative_to(ROOT)),

        "entitySource":
            (
                str(entity_file.relative_to(ROOT))
                if entity_file
                else None
            ),

        "linkSource":
            (
                str(link_file.relative_to(ROOT))
                if link_file
                else None
            ),

        "freshSource":
            (
                str(fresh_file.relative_to(ROOT))
                if fresh_file
                else None
            ),

    },

    "counts": {

        "researchPapers":
            len(papers),

        "aiEntities":
            len(entities),

        "paperEntityLinks":
            len(links),

        "freshNews":
            len(news),

        "freshJobs":
            len(jobs),

    },

    "validation": {

        "papersPresent":
            len(papers) > 0,

        "paperTarget1000Reached":
            len(papers) >= 1000,

        "entitiesPresent":
            len(entities) > 0,

        "linksPresent":
            len(links) > 0,

        "freshNewsPresent":
            len(news) > 0,

        "freshJobsPresent":
            len(jobs) > 0,

    },

}


with REPORT_FILE.open(
    "w",
    encoding="utf-8"
) as f:

    json.dump(
        quality_report,
        f,
        indent=2,
        ensure_ascii=False
    )


print(
    f"Quality report: {REPORT_FILE}"
)

print()
print("=" * 70)
print("BUILD COMPLETE")
print("=" * 70)