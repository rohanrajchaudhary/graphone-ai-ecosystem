from pathlib import Path
import json
from typing import Any, Optional

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware


# ============================================================
# PATHS
# ============================================================

ROOT_DIR = Path(__file__).resolve().parents[1]

DATA_FILE = (
    ROOT_DIR
    / "data"
    / "processed"
    / "graphone_final_dataset.json"
)


# ============================================================
# APP
# ============================================================

app = FastAPI(
    title="GraphOne AI Ecosystem API",
    description=(
        "API for exploring the GraphOne AI ecosystem dataset."
    ),
    version="1.0.0",
)


# ============================================================
# CORS
# ============================================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================
# DATA LOADING
# ============================================================

DATA: dict[str, Any] = {}


def load_dataset() -> dict[str, Any]:
    global DATA

    if not DATA_FILE.exists():
        raise FileNotFoundError(
            f"Dataset not found: {DATA_FILE}"
        )

    with DATA_FILE.open(
        "r",
        encoding="utf-8"
    ) as file:
        DATA = json.load(file)

    return DATA


@app.on_event("startup")
def startup_event():
    load_dataset()


# ============================================================
# HELPERS
# ============================================================

def get_papers() -> list[dict[str, Any]]:
    return DATA.get("researchPapers", [])


def get_entities() -> list[dict[str, Any]]:
    return DATA.get("aiEntities", [])


def get_links() -> list[dict[str, Any]]:
    return DATA.get("paperEntityLinks", [])


def entity_type(entity: dict[str, Any]) -> str:
    return str(
        entity.get("entityType")
        or entity.get("type")
        or "UNKNOWN"
    )


def entity_name(entity: dict[str, Any]) -> str:
    return str(
        entity.get("entityName")
        or entity.get("name")
        or ""
    )


def paper_title(paper: dict[str, Any]) -> str:
    return str(
        paper.get("title")
        or paper.get("paperTitle")
        or ""
    )


# ============================================================
# ROOT / HEALTH
# ============================================================

@app.get("/")
def root():
    return {
        "name": "GraphOne AI Ecosystem API",
        "version": "1.0.0",
        "status": "running",
    }


@app.get("/api/health")
def health():
    return {
        "status": "healthy",
        "datasetLoaded": bool(DATA),
        "dataset": DATA.get(
            "datasetName",
            "GRAPHONE AI ECOSYSTEM DATASET"
        ),
    }


# ============================================================
# STATS
# ============================================================

@app.get("/api/stats")
def stats():

    papers = get_papers()
    entities = get_entities()
    links = get_links()

    startups = 0
    products = 0
    organizations = 0
    open_source = 0
    unknown = 0

    for entity in entities:

        t = entity_type(entity)

        if t == "STARTUP":
            startups += 1

        elif t == "PRODUCT":
            products += 1

        elif t == "ORGANIZATION":
            organizations += 1

        elif t == "OPEN_SOURCE_PROJECT":
            open_source += 1

        else:
            unknown += 1

    fresh_data = DATA.get(
        "freshAIData",
        {}
    )

    news = fresh_data.get(
        "news",
        []
    )

    jobs = fresh_data.get(
        "jobs",
        []
    )

    return {
        "researchPapers": len(papers),
        "aiEntities": len(entities),
        "startups": startups,
        "products": products,
        "organizations": organizations,
        "openSourceProjects": open_source,
        "unknownEntities": unknown,
        "paperEntityLinks": len(links),
        "freshNews": len(news),
        "jobSources": len(jobs),
        "generatedAt": DATA.get(
            "generatedAt"
        ),
    }


# ============================================================
# PAPERS
# ============================================================

@app.get("/api/papers")
def papers(
    q: Optional[str] = Query(
        default=None
    ),
    limit: int = Query(
        default=50,
        ge=1,
        le=500
    ),
    offset: int = Query(
        default=0,
        ge=0
    ),
):

    records = get_papers()

    if q:

        query = q.lower().strip()

        records = [
            paper
            for paper in records
            if query in paper_title(paper).lower()
            or query in str(
                paper.get("abstract", "")
            ).lower()
        ]

    total = len(records)

    return {
        "total": total,
        "offset": offset,
        "limit": limit,
        "items": records[
            offset: offset + limit
        ],
    }


# ============================================================
# ENTITIES
# ============================================================

@app.get("/api/entities")
def entities(
    q: Optional[str] = Query(
        default=None
    ),
    entity_type_filter: Optional[str] = Query(
        default=None,
        alias="type"
    ),
    limit: int = Query(
        default=50,
        ge=1,
        le=500
    ),
    offset: int = Query(
        default=0,
        ge=0
    ),
):

    records = get_entities()

    if q:

        query = q.lower().strip()

        records = [
            entity
            for entity in records
            if query in entity_name(entity).lower()
            or query in str(
                entity.get("description", "")
            ).lower()
        ]

    if entity_type_filter:

        wanted = entity_type_filter.upper()

        records = [
            entity
            for entity in records
            if entity_type(entity).upper()
            == wanted
        ]

    total = len(records)

    return {
        "total": total,
        "offset": offset,
        "limit": limit,
        "items": records[
            offset: offset + limit
        ],
    }


# ============================================================
# STARTUPS
# ============================================================

@app.get("/api/startups")
def startups(
    q: Optional[str] = Query(
        default=None
    ),
    limit: int = Query(
        default=50,
        ge=1,
        le=500
    ),
):

    records = [
        entity
        for entity in get_entities()
        if entity_type(entity) == "STARTUP"
    ]

    if q:

        query = q.lower().strip()

        records = [
            entity
            for entity in records
            if query in entity_name(entity).lower()
            or query in str(
                entity.get("description", "")
            ).lower()
        ]

    return {
        "total": len(records),
        "items": records[:limit],
    }


# ============================================================
# PRODUCTS
# ============================================================

@app.get("/api/products")
def products(
    q: Optional[str] = Query(
        default=None
    ),
    limit: int = Query(
        default=50,
        ge=1,
        le=500
    ),
):

    records = [
        entity
        for entity in get_entities()
        if entity_type(entity) == "PRODUCT"
    ]

    if q:

        query = q.lower().strip()

        records = [
            entity
            for entity in records
            if query in entity_name(entity).lower()
            or query in str(
                entity.get("description", "")
            ).lower()
        ]

    return {
        "total": len(records),
        "items": records[:limit],
    }


# ============================================================
# ENTITY DETAIL
# ============================================================

@app.get("/api/entities/{name}")
def entity_detail(name: str):

    target = name.lower().strip()

    for entity in get_entities():

        current_name = entity_name(entity).lower()

        if current_name == target:

            related_links = [
                link
                for link in get_links()
                if str(
                    link.get("entityName", "")
                ).lower() == target
            ]

            return {
                "entity": entity,
                "relatedPaperLinks": related_links,
            }

    raise HTTPException(
        status_code=404,
        detail="Entity not found"
    )


# ============================================================
# FRESH AI DATA
# ============================================================

@app.get("/api/fresh")
def fresh():

    return DATA.get(
        "freshAIData",
        {}
    )


# ============================================================
# SEARCH
# ============================================================

@app.get("/api/search")
def search(
    q: str = Query(
        min_length=1
    ),
    limit: int = Query(
        default=20,
        ge=1,
        le=100
    ),
):

    query = q.lower().strip()

    matched_papers = [
        paper
        for paper in get_papers()
        if query in paper_title(paper).lower()
        or query in str(
            paper.get("abstract", "")
        ).lower()
    ]

    matched_entities = [
        entity
        for entity in get_entities()
        if query in entity_name(entity).lower()
        or query in str(
            entity.get("description", "")
        ).lower()
    ]

    return {
        "query": q,
        "papers": matched_papers[:limit],
        "entities": matched_entities[:limit],
        "paperCount": len(matched_papers),
        "entityCount": len(matched_entities),
    }


# ============================================================
# RELOAD DATASET
# ============================================================

@app.post("/api/reload")
def reload_dataset():

    try:
        load_dataset()

        return {
            "status": "reloaded",
            "researchPapers": len(
                get_papers()
            ),
            "aiEntities": len(
                get_entities()
            ),
        }

    except Exception as error:

        raise HTTPException(
            status_code=500,
            detail=str(error)
        )