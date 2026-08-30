from src.schemas.startup import Startup
from src.schemas.product import Product
from src.schemas.research_paper import ResearchPaper
from src.schemas.job import Job
from src.schemas.news import News


def test_startup():
    startup = Startup(
        name="Example AI",
        description="AI startup",
        source_url="https://example.com",
        collected_at="2026-08-27T14:00:00Z",
    )

    assert startup.name == "Example AI"


def test_product():
    product = Product(
        name="Example AI Product",
        source_url="https://example.com",
        collected_at="2026-08-27T14:00:00Z",
    )

    assert product.name == "Example AI Product"


def test_research_paper():
    paper = ResearchPaper(
        title="Example Research Paper",
        source_url="https://arxiv.org/abs/1234.5678",
        arxiv_url="https://arxiv.org/abs/1234.5678",
        collected_at="2026-08-27T14:00:00Z",
    )

    assert paper.title == "Example Research Paper"


def test_job():
    job = Job(
        title="AI Engineer",
        company_name="Example AI",
        application_url="https://example.com/apply",
        source_url="https://example.com/job",
        collected_at="2026-08-27T14:00:00Z",
    )

    assert job.title == "AI Engineer"


def test_news():
    news = News(
        title="AI News Example",
        article_url="https://example.com/news",
        source_url="https://example.com/news",
        collected_at="2026-08-27T14:00:00Z",
    )

    assert news.title == "AI News Example"