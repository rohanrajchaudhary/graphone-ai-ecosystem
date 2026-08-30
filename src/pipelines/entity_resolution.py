import json
import re
from pathlib import Path
from difflib import SequenceMatcher


PAPERS_FILE = Path(
    "data/processed/research_papers_extracted.json"
)

ENTITIES_FILE = Path(
    "data/processed/ai_entities_classified.json"
)

OUTPUT_FILE = Path(
    "data/processed/entity_resolution.json"
)


STOPWORDS = {
    "a", "an", "the", "and", "or", "for", "of",
    "to", "in", "on", "with", "from", "by",
    "using", "based", "via", "towards",
    "under", "over", "into", "through"
}


def normalize(text):

    if not text:
        return ""

    text = str(text).lower()

    text = re.sub(
        r"[^a-z0-9]+",
        " ",
        text
    )

    return " ".join(
        text.split()
    )


def tokens(text):

    return {
        word
        for word in normalize(text).split()
        if word not in STOPWORDS
        and len(word) > 2
    }


def similarity(a, b):

    a = normalize(a)
    b = normalize(b)

    if not a or not b:
        return 0.0

    return SequenceMatcher(
        None,
        a,
        b
    ).ratio()


def token_overlap(a, b):

    ta = tokens(a)
    tb = tokens(b)

    if not ta or not tb:
        return 0.0

    intersection = len(
        ta & tb
    )

    smaller = min(
        len(ta),
        len(tb)
    )

    return intersection / smaller


def load_json(path):

    with open(
        path,
        "r",
        encoding="utf-8"
    ) as file:

        return json.load(file)


def get_records(data):

    if isinstance(
        data,
        list
    ):
        return data

    return data.get(
        "records",
        []
    )


def find_best_entity(
    paper,
    entities
):

    title = paper.get(
        "title",
        ""
    )

    abstract = paper.get(
        "abstract",
        ""
    )

    best = None
    best_score = 0.0

    for entity in entities:

        name = entity.get(
            "name",
            entity.get(
                "entityName",
                ""
            )
        )

        description = entity.get(
            "description",
            ""
        )

        topics = " ".join(
            entity.get(
                "topics",
                []
            )
        )

        # ----------------------------------------------------
        # Name/title similarity
        # ----------------------------------------------------

        name_score = max(
            similarity(
                title,
                name
            ),
            token_overlap(
                title,
                name
            )
        )

        # ----------------------------------------------------
        # Description/title overlap
        # ----------------------------------------------------

        description_score = token_overlap(
            title,
            description
        )

        # ----------------------------------------------------
        # Topics/title overlap
        # ----------------------------------------------------

        topic_score = token_overlap(
            title,
            topics
        )

        # ----------------------------------------------------
        # Abstract/repository description
        # ----------------------------------------------------

        abstract_score = token_overlap(
            abstract,
            description
        )

        # ----------------------------------------------------
        # Weighted score
        # ----------------------------------------------------

        score = (
            name_score * 0.55
            + description_score * 0.20
            + topic_score * 0.15
            + abstract_score * 0.10
        )

        if score > best_score:

            best_score = score
            best = entity

    return best, best_score


def main():

    print("=" * 60)
    print("GRAPHONE ENTITY RESOLUTION")
    print("=" * 60)

    papers_data = load_json(
        PAPERS_FILE
    )

    entities_data = load_json(
        ENTITIES_FILE
    )

    papers = get_records(
        papers_data
    )

    entities = get_records(
        entities_data
    )

    print(
        f"Research papers : {len(papers)}"
    )

    print(
        f"GitHub entities : {len(entities)}"
    )

    resolved = []
    unresolved = []

    exact = 0
    strong = 0

    # --------------------------------------------------------
    # GitHub URL index
    # --------------------------------------------------------

    github_index = {}

    for entity in entities:

        url = entity.get(
            "githubUrl"
        )

        if url:

            github_index[
                url.rstrip("/").lower()
            ] = entity

    # --------------------------------------------------------
    # RESOLUTION
    # --------------------------------------------------------

    for index, paper in enumerate(
        papers,
        start=1
    ):

        paper_github = paper.get(
            "githubUrl"
        )

        # ----------------------------------------------------
        # Exact URL match if available
        # ----------------------------------------------------

        if paper_github:

            entity = github_index.get(
                paper_github.rstrip(
                    "/"
                ).lower()
            )

            if entity:

                resolved.append({
                    "paperTitle":
                        paper.get("title"),

                    "paperSourceUrl":
                        paper.get(
                            "sourceUrl",
                            paper.get(
                                "source_url"
                            )
                        ),

                    "githubUrl":
                        entity.get(
                            "githubUrl"
                        ),

                    "entityName":
                        entity.get(
                            "entityName",
                            entity.get(
                                "name"
                            )
                        ),

                    "entityType":
                        entity.get(
                            "entityType"
                        ),

                    "matchType":
                        "EXACT_GITHUB_URL",

                    "matchScore":
                        1.0
                })

                exact += 1

                continue

        # ----------------------------------------------------
        # Metadata matching
        # ----------------------------------------------------

        entity, score = find_best_entity(
            paper,
            entities
        )

        # Conservative threshold.
        if (
            entity is not None
            and score >= 0.72
        ):

            resolved.append({
                "paperTitle":
                    paper.get("title"),

                "paperSourceUrl":
                    paper.get(
                        "sourceUrl",
                        paper.get(
                            "source_url"
                        )
                    ),

                "githubUrl":
                    entity.get(
                        "githubUrl"
                    ),

                "entityName":
                    entity.get(
                        "entityName",
                        entity.get(
                            "name"
                        )
                    ),

                "entityType":
                    entity.get(
                        "entityType"
                    ),

                "matchType":
                    "STRONG_METADATA_MATCH",

                "matchScore":
                    round(
                        score,
                        4
                    )
            })

            strong += 1

        else:

            unresolved.append({
                "paperTitle":
                    paper.get("title"),

                "paperSourceUrl":
                    paper.get(
                        "sourceUrl",
                        paper.get(
                            "source_url"
                        )
                    )
            })

        if (
            index % 100 == 0
            or index == len(papers)
        ):

            print(
                f"Processed: "
                f"{index}/{len(papers)}"
            )

    # --------------------------------------------------------
    # SAVE
    # --------------------------------------------------------

    OUTPUT_FILE.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    output = {

        "datasetType":
            "GRAPHONE_ENTITY_RESOLUTION",

        "method":
            "EXACT_URL_AND_CONSERVATIVE_METADATA_MATCH",

        "statistics": {

            "researchPapers":
                len(papers),

            "githubEntities":
                len(entities),

            "resolved":
                len(resolved),

            "unresolved":
                len(unresolved),

            "exactMatches":
                exact,

            "strongMetadataMatches":
                strong
        },

        "paperEntityLinks":
            resolved,

        "unresolvedPapers":
            unresolved
    }

    with open(
        OUTPUT_FILE,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            output,
            file,
            indent=2,
            ensure_ascii=False
        )

    # --------------------------------------------------------
    # FINAL REPORT
    # --------------------------------------------------------

    print()
    print("=" * 60)
    print("ENTITY RESOLUTION COMPLETE")
    print("=" * 60)

    print(
        f"Research papers : {len(papers)}"
    )

    print(
        f"GitHub entities : {len(entities)}"
    )

    print(
        f"Resolved        : {len(resolved)}"
    )

    print(
        f"Unresolved      : {len(unresolved)}"
    )

    print(
        f"Exact matches   : {exact}"
    )

    print(
        f"Strong matches  : {strong}"
    )

    print()
    print(
        f"Output: {OUTPUT_FILE}"
    )


if __name__ == "__main__":
    main()