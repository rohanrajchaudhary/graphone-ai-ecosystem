import asyncio


class FallbackChain:

    def __init__(self, providers):
        self.providers = providers

    async def extract(self, text, schema):

        last_error = None

        for provider in self.providers:

            provider_name = provider.__class__.__name__

            print(f"\nTrying: {provider_name}")

            try:
                result = await provider.extract(
                    text,
                    schema
                )

                if result is not None:
                    print(
                        f"SUCCESS: {provider_name}"
                    )
                    return result

            except Exception as e:

                last_error = e

                print(
                    f"FAILED: {provider_name}"
                )
                print(
                    f"Reason: {e}"
                )

                # Quickly move to next provider
                await asyncio.sleep(0.2)

        raise RuntimeError(
            f"All LLM providers failed. "
            f"Last error: {last_error}"
        )