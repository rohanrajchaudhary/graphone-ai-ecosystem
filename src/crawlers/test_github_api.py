import asyncio
import aiohttp


async def main():

    url = "https://api.github.com/search/repositories"

    params = {
        "q": "llama 3",
        "per_page": 5,
    }

    headers = {
        "Accept": "application/vnd.github+json",
        "User-Agent": "GraphOne-AI-Pipeline/1.0",
    }

    async with aiohttp.ClientSession() as session:

        async with session.get(
            url,
            params=params,
            headers=headers,
        ) as response:

            print("Status:", response.status)

            data = await response.json()

            print("Total results:", data.get("total_count"))

            for repo in data.get("items", []):

                print(
                    repo["full_name"],
                    "| Stars:",
                    repo["stargazers_count"],
                )


if __name__ == "__main__":
    asyncio.run(main())