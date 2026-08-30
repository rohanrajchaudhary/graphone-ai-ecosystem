import asyncio
import random
from functools import wraps


RETRYABLE_STATUS_CODES = {
    429,
    500,
    502,
    503,
    504,
}


def get_status_code(error):
    text = str(error)

    for code in RETRYABLE_STATUS_CODES:
        if str(code) in text:
            return code

    return None


def async_retry(
    max_attempts=3,
    base_delay=1.0,
    max_delay=30.0,
    max_retries=None,
):
    """
    Async retry decorator.

    Supports both:
        max_attempts=3
    and:
        max_retries=3

    max_retries is kept for backward compatibility
    with existing crawlers.
    """

    # If caller uses max_retries, convert it to total attempts.
    if max_retries is not None:
        max_attempts = max_retries + 1

    def decorator(func):

        @wraps(func)
        async def wrapper(*args, **kwargs):

            last_error = None

            for attempt in range(
                1,
                max_attempts + 1
            ):

                try:
                    return await func(
                        *args,
                        **kwargs
                    )

                except Exception as error:

                    last_error = error

                    status_code = get_status_code(
                        error
                    )

                    error_text = str(
                        error
                    ).lower()

                    retryable = (
                        status_code
                        in RETRYABLE_STATUS_CODES
                        or
                        "timeout" in error_text
                        or
                        "temporarily unavailable"
                        in error_text
                    )

                    # Don't retry non-retryable errors.
                    if not retryable:
                        raise

                    # No attempts remaining.
                    if attempt == max_attempts:
                        break

                    delay = min(
                        max_delay,
                        base_delay * (
                            2 ** (attempt - 1)
                        )
                    )

                    jitter = random.uniform(
                        0,
                        delay * 0.25
                    )

                    total_delay = (
                        delay + jitter
                    )

                    print(
                        f"Retry {attempt + 1}/"
                        f"{max_attempts} "
                        f"after "
                        f"{total_delay:.2f}s"
                    )

                    await asyncio.sleep(
                        total_delay
                    )

            raise last_error

        return wrapper

    return decorator