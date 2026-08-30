from pydantic import BaseModel, Field, HttpUrl


class ResearchPaper(BaseModel):
    title: str = Field(min_length=1)
    authors: list[str] = Field(default_factory=list)
    abstract: str | None = None

    published_date: str | None = None

    arxiv_url: HttpUrl | None = None
    papers_with_code_url: HttpUrl | None = None
    github_url: HttpUrl | None = None

    github_stars: int | None = None

    source_url: HttpUrl
    collected_at: str