from pydantic import BaseModel, Field, HttpUrl


class Product(BaseModel):
    name: str = Field(min_length=1)
    description: str | None = None
    company_name: str | None = None
    category: str | None = None
    website: HttpUrl | None = None

    source_url: HttpUrl
    collected_at: str