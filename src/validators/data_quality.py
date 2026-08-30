from urllib.parse import urlparse


def is_valid_url(url: str | None) -> bool:
    if not url:
        return False

    try:
        parsed = urlparse(url)

        return parsed.scheme in ("http", "https") and bool(
            parsed.netloc
        )

    except Exception:
        return False


def validate_paper_record(record: dict) -> list[str]:

    errors = []

    # Required title
    if not record.get("title"):
        errors.append("Missing title")

    # Required source URL
    source_url = record.get("source_url")

    if not is_valid_url(source_url):
        errors.append("Invalid source_url")

    # arXiv URL
    arxiv_url = record.get("arxiv_url")

    if arxiv_url and not is_valid_url(arxiv_url):
        errors.append("Invalid arxiv_url")

    # GitHub consistency
    github_url = record.get("github_url")
    github_stars = record.get("github_stars")

    if github_url and not is_valid_url(github_url):
        errors.append("Invalid github_url")

    if github_stars is not None:

        if not isinstance(github_stars, int):
            errors.append(
                "github_stars must be integer"
            )

        elif github_stars < 0:
            errors.append(
                "github_stars cannot be negative"
            )

    return errors