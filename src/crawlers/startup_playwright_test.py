import asyncio
from playwright.async_api import async_playwright


URL = "https://www.startuphub.ai/startups"


async def main():

    async with async_playwright() as p:

        browser = await p.chromium.launch(
            headless=True
        )

        page = await browser.new_page()

        print("Opening:", URL)

        await page.goto(
            URL,
            wait_until="domcontentloaded",
            timeout=60000,
        )

        await page.wait_for_timeout(5000)

        print("Final URL:", page.url)

        title = await page.title()

        print("Title:", title)

        links = await page.locator("a").all()

        print(
            "Total links:",
            len(links)
        )

        print("\nFirst 30 links:")

        count = 0

        for link in links:

            text = (
                await link.inner_text()
            ).strip()

            href = await link.get_attribute(
                "href"
            )

            if text and href:

                print(
                    f"{text[:80]} -> {href}"
                )

                count += 1

            if count >= 30:
                break

        await browser.close()


if __name__ == "__main__":
    asyncio.run(main())