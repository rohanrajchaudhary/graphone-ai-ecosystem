import asyncio

from .retry import async_retry


attempts = 0


@async_retry(
    max_attempts=3,
    base_delay=0.5
)
async def unstable_function():

    global attempts

    attempts += 1

    print(
        f"Function attempt: {attempts}"
    )

    if attempts < 3:
        raise RuntimeError(
            "429 rate limit"
        )

    return "SUCCESS"


async def main():

    result = await unstable_function()

    print()
    print("Final result:", result)


if __name__ == "__main__":
    asyncio.run(main())