from src.validators.data_quality import (
    is_valid_url,
    validate_paper_record,
)


def test_valid_url():

    assert is_valid_url(
        "https://arxiv.org/abs/1234.5678"
    )


def test_invalid_url():

    assert not is_valid_url(
        "not-a-url"
    )


def test_valid_paper():

    paper = {
        "title": "Test Paper",
        "source_url": "https://arxiv.org/abs/1234.5678",
        "arxiv_url": "https://arxiv.org/abs/1234.5678",
        "github_url": "https://github.com/example/repo",
        "github_stars": 100,
    }

    errors = validate_paper_record(paper)

    assert errors == []


def test_invalid_paper():

    paper = {
        "title": "",
        "source_url": "invalid-url",
    }

    errors = validate_paper_record(paper)

    assert "Missing title" in errors
    assert "Invalid source_url" in errors