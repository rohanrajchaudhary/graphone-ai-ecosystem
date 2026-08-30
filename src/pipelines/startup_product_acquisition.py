import json
import time
from pathlib import Path
from datetime import datetime, timezone

import requests


OUTPUT_FILE = Path(
    "data/processed/startups_products_raw.json"
)

GITHUB_API = "https://api.github.com/search/repositories"

HEADERS = {
    "Accept": "application/vnd.github+json",
    "User-Agent": "GraphOne-AI-Pipeline"
}


# ============================================================
# AI SEARCH QUERIES
# ============================================================

QUERIES = [
    "artificial intelligence",
    "machine learning",
    "generative ai",
    "large language model",
    "computer vision",
    "natural language processing",
    "multimodal ai",
    "ai agent",
    "robotics ai",
    "deep learning",
]


def github_search(query, page=1, per_page=100):

    params = {
        "q": query,
        "sort": "stars",
        "order": "desc",
        "page": page,
        "per_page": per_page
    }

    response = requests.get(
        GITHUB_API,
        headers=HEADERS,
        params=params,
        timeout=30
    )

    if response.status_code == 403:
        raise RuntimeError(
            "GitHub API rate limit reached"
        )

    if response.status_code != 200:
        raise RuntimeError(
            f"GitHub API error "
            f"{response.status_code}: "
            f"{response.text[:300]}"
        )

    return response.json()


def repository_to_record(repo):

    owner = repo.get(
        "owner",
        {}
    )

    return {
        "recordType": "AI_PROJECT",
        "name": repo.get("name"),
        "fullName": repo.get("full_name"),
        "description": repo.get("description"),
        "githubUrl": repo.get("html_url"),
        "homepage": repo.get("homepage"),
        "owner": owner.get(
            "login"
        ),
        "ownerType": owner.get(
            "type"
        ),
        "language": repo.get(
            "language"
        ),
        "stars": repo.get(
            "stargazers_count"
        ),
        "forks": repo.get(
            "forks_count"
        ),
        "openIssues": repo.get(
            "open_issues_count"
        ),
        "license": (
            repo.get("license") or {}
        ).get("spdx_id"),
        "createdAt": repo.get(
            "created_at"
        ),
        "updatedAt": repo.get(
            "updated_at"
        ),
        "topics": repo.get(
            "topics",
            []
        )
    }


def main():

    print("=" * 60)
    print("GRAPHONE AI STARTUP / PRODUCT ACQUISITION")
    print("=" * 60)

    records = {}
    collected_at = datetime.now(
        timezone.utc
    ).isoformat()

    for query in QUERIES:

        print()
        print(
            f"Searching GitHub: {query}"
        )

        try:

            # First two pages = up to 200 results/query.
            # Deduplication happens below.
            for page in range(1, 3):

                data = github_search(
                    query,
                    page=page,
                    per_page=100
                )

                repositories = data.get(
                    "items",
                    []
                )

                print(
                    f"  Page {page}: "
                    f"{len(repositories)} repositories"
                )

                for repo in repositories:

                    github_url = repo.get(
                        "html_url"
                    )

                    if not github_url:
                        continue

                    if github_url not in records:

                        record = repository_to_record(
                            repo
                        )

                        record["collectedAt"] = (
                            collected_at
                        )

                        records[
                            github_url
                        ] = record

                # Avoid hammering API
                time.sleep(1)

        except Exception as error:

            print(
                f"  ERROR: {error}"
            )

            # Continue with other queries
            continue

    final_records = list(
        records.values()
    )

    output = {
        "generatedAt": collected_at,

        "dataPolicy": {
            "realDataOnly": True,
            "source": "GitHub API",
            "deduplicated": True
        },

        "statistics": {
            "queries": len(QUERIES),
            "uniqueRecords": len(
                final_records
            )
        },

        "records": final_records
    }

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
            output,
            file,
            indent=2,
            ensure_ascii=False
        )

    print()
    print("=" * 60)
    print("ACQUISITION COMPLETE")
    print("=" * 60)

    print(
        f"Queries        : {len(QUERIES)}"
    )

    print(
        f"Unique records : {len(final_records)}"
    )

    print(
        f"Output         : {OUTPUT_FILE}"
    )


if __name__ == "__main__":
    main()