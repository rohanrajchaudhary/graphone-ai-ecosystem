import asyncio

from src.crawlers.base_crawler import BaseCrawler


async def main():

    urls = [
        "https://example.com",
        "https://example.org",
        "https://example.net",
    ]

    crawler = BaseCrawler(concurrency=3)

    results = await crawler.crawl(urls)

    for result in results:

        print("\n--------------------")
        print("URL:", result["source_url"])
        print("Status:", result["status_code"])
        print("Title:", result["title"])
        print("Error:", result["error"])


if __name__ == "__main__":
    asyncio.run(main())