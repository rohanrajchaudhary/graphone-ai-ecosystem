from pydantic import BaseModel, Field, HttpUrl


class Job(BaseModel):
    title: str = Field(min_length=1)
    company_name: str = Field(min_length=1)

    location: str | None = None
    job_type: str | None = None
    description: str | None = None

    published_at: str | None = None
    application_url: HttpUrl

    source_url: HttpUrl
    collected_at: str