from typing import Optional
from pydantic import BaseModel, Field, HttpUrl


class StartupRecord(BaseModel):
    recordType: str = "STARTUP"

    entityName: str = Field(
        min_length=1
    )

    employeeCount: Optional[int] = None

    sourceUrl: HttpUrl


class ResearchPaperRecord(BaseModel):
    recordType: str = "RESEARCH_PAPER"

    title: str = Field(
        min_length=1
    )

    authors: list[str] = Field(
        default_factory=list
    )

    abstract: Optional[str] = None

    sourceUrl: HttpUrl

    githubUrl: Optional[HttpUrl] = None

    githubStars: Optional[int] = None