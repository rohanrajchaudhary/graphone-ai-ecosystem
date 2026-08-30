import json
import time
from datetime import datetime, timedelta, timezone
from email.utils import parsedate_to_datetime
from pathlib import Path

import feedparser
import requests


OUTPUT_FILE = Path(
    "data/processed/fresh_ai_data.json"
)


# ============================================================
# REAL RSS SOURCES
# ============================================================

NEWS_FEEDS = {
    "TechCrunch AI": (
        "https://techcrunch.com/category/artificial-intelligence/feed/"
    ),
    "VentureBeat AI": (
        "https://venturebeat.com/category/ai/feed/"
    ),
    "MIT Technology Review AI": (
        "https://www.technologyreview.com/topic/artificial-intelligence/"
    ),
    "The Verge AI": (
        "https://www.theverge.com/rss/ai-artificial-intelligence/index.xml"
    ),
    "Ars Technica AI": (
        "https://feeds.arstechnica.com/arstechnica/technology-lab"
    ),
}


JOB_SOURCES = {
    "LinkedIn AI Jobs": (
        "https://www.linkedin.com/jobs/search/?keywords=AI"
    ),
    "Indeed AI Jobs": (
        "https://www.indeed.com/jobs?q=AI"
    ),
    "Wellfound AI Jobs": (
        "https://wellfound.com/jobs"
    ),
    "ZipRecruiter AI Jobs": (
        "https://www.ziprecruiter.com/jobs-search?search=AI"
    ),
    "SimplyHired AI Jobs": (
        "https://www.simplyhired.com/search?q=AI"
    ),
}


HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 Chrome/151.0 Safari/537.36"
    )
}


# ============================================================
# HELPERS
# ============================================================

def parse_date(entry):

    for field in (
        "published_parsed",
        "updated_parsed",
    ):

        value = entry.get(field)

        if value:

            return datetime.fromtimestamp(
                time.mktime(value),
                tz=timezone.utc
            )

    for field in (
        "published",
        "updated",
    ):

        value = entry.get(field)

        if value:

            try:
                dt = parsedate_to_datetime(value)

                if dt.tzinfo is None:
                    dt = dt.replace(
                        tzinfo=timezone.utc
                    )

                return dt.astimezone(
                    timezone.utc
                )

            except Exception:
                pass

    return None


def clean_text(value):

    if not value:
        return None

    return " ".join(
        str(value).split()
    )


# ============================================================
# NEWS
# ============================================================

def collect_news():

    print()
    print("=" * 60)
    print("COLLECTING REAL AI NEWS")
    print("=" * 60)

    now = datetime.now(timezone.utc)

    cutoff = now - timedelta(hours=24)

    articles = []

    for source, feed_url in NEWS_FEEDS.items():

        print()
        print(f"Source: {source}")

        try:

            response = requests.get(
                feed_url,
                headers=HEADERS,
                timeout=20
            )

            print(
                f"HTTP status: {response.status_code}"
            )

            if not response.ok:
                print("❌ Source unavailable")
                continue

            feed = feedparser.parse(
                response.content
            )

            source_count = 0

            for entry in feed.entries:

                published_at = parse_date(
                    entry
                )

                if not published_at:
                    continue

                if published_at < cutoff:
                    continue

                article = {
                    "type": "AI_NEWS",
                    "source": source,
                    "title": clean_text(
                        entry.get("title")
                    ),
                    "url": entry.get(
                        "link"
                    ),
                    "publishedAt": (
                        published_at.isoformat()
                    ),
                    "summary": clean_text(
                        entry.get(
                            "summary"
                        )
                    ),
                    "collectedAt": (
                        now.isoformat()
                    ),
                }

                articles.append(article)

                source_count += 1

            print(
                f"✅ Fresh articles: {source_count}"
            )

        except Exception as error:

            print(
                f"❌ Error: {error}"
            )

    return articles


# ============================================================
# JOB SOURCES
# ============================================================

def check_job_sources():

    print()
    print("=" * 60)
    print("CHECKING REAL JOB SOURCES")
    print("=" * 60)

    results = []

    for source, url in JOB_SOURCES.items():

        print()
        print(f"Source: {source}")

        try:

            response = requests.get(
                url,
                headers=HEADERS,
                timeout=20,
                allow_redirects=True
            )

            accessible = response.ok

            print(
                f"HTTP status: {response.status_code}"
            )

            if accessible:
                print("✅ Accessible")
            else:
                print("⚠️ Not accessible")

            results.append({
                "source": source,
                "url": url,
                "status": response.status_code,
                "accessible": accessible,
                "checkedAt": (
                    datetime.now(
                        timezone.utc
                    ).isoformat()
                )
            })

        except Exception as error:

            print(
                f"❌ Error: {error}"
            )

            results.append({
                "source": source,
                "url": url,
                "status": None,
                "accessible": False,
                "error": str(error),
                "checkedAt": (
                    datetime.now(
                        timezone.utc
                    ).isoformat()
                )
            })

    return results


# ============================================================
# MAIN
# ============================================================

def main():

    print("=" * 60)
    print("GRAPHONE FRESH AI DATA PIPELINE")
    print("=" * 60)

    now = datetime.now(
        timezone.utc
    )

    cutoff = now - timedelta(
        hours=24
    )

    news = collect_news()

    jobs = check_job_sources()

    output = {
        "generatedAt": now.isoformat(),

        "freshnessWindow": {
            "hours": 24,
            "from": cutoff.isoformat(),
            "to": now.isoformat()
        },

        "news": {
            "sourcesConfigured": len(
                NEWS_FEEDS
            ),
            "articlesFound": len(
                news
            ),
            "items": news
        },

        "jobs": {
            "sourcesConfigured": len(
                JOB_SOURCES
            ),
            "sourcesChecked": len(
                jobs
            ),
            "items": jobs
        }
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
    print("FRESH DATA PIPELINE COMPLETE")
    print("=" * 60)

    print(
        f"Fresh AI news: {len(news)}"
    )

    print(
        f"Job sources checked: {len(jobs)}/5"
    )

    print(
        f"Output: {OUTPUT_FILE}"
    )


if __name__ == "__main__":
    main()