import asyncio

# from .gemini_provider import GeminiProvider
from .groq_provider import GroqProvider


async def main():

    # provider = GeminiProvider()
    provider = GroqProvider()

    schema = {
        "recordType": "STARTUP",
        "entityName": "string",
        "employeeCount": "integer or null"
    }

    text = """
    OpenAI is an artificial intelligence company.
    The company develops AI systems and products.
    """

    print("Sending request to Groq...")

    result = await provider.extract(
        text,
        schema
    )

    print()
    print("========== GROQ RESULT ==========")
    print(result)


if __name__ == "__main__":
    asyncio.run(main())