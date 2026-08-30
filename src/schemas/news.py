from pydantic import BaseModel, Field, HttpUrl


class News(BaseModel):
    title: str = Field(min_length=1)

    summary: str | None = None
    source_name: str | None = None

    published_at: str | None = None

    article_url: HttpUrl

    source_url: HttpUrl
    collected_at: str