import asyncio

from .groq_provider import GroqProvider
from .fallback_chain import FallbackChain


class FailingProvider:

    async def extract(self, text, schema):
        raise RuntimeError("Simulated Gemini failure")


async def main():

    failing_gemini = FailingProvider()
    groq = GroqProvider()

    chain = FallbackChain([
        failing_gemini,
        groq
    ])

    schema = {
        "recordType": "STARTUP",
        "entityName": "string",
        "employeeCount": "integer or null"
    }

    text = """
    OpenAI is an artificial intelligence company.
    It develops artificial intelligence systems and products.
    """

    print("=" * 50)
    print("GRAPHONE LLM FALLBACK TEST")
    print("=" * 50)

    result = await chain.extract(
        text,
        schema
    )

    print()
    print("=" * 50)
    print("FINAL RESULT")
    print("=" * 50)

    print(result)


if __name__ == "__main__":
    asyncio.run(main())