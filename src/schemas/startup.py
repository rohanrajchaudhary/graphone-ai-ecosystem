from pydantic import BaseModel, Field, HttpUrl


class Startup(BaseModel):
    name: str = Field(min_length=1)
    description: str | None = None
    website: HttpUrl | None = None
    industry: str | None = None
    location: str | None = None
    founded_year: int | None = None

    source_url: HttpUrl
    collected_at: str
    