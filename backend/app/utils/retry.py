import asyncio
from functools import wraps


def retry(max_retries: int = 3, delay: int = 2):
    """
    Retry an async function on failure.

    Args:
        max_retries: Number of retry attempts.
        delay: Delay (seconds) between retries.
    """

    def decorator(func):

        @wraps(func)
        async def wrapper(*args, **kwargs):

            last_exception = None

            for attempt in range(1, max_retries + 1):

                try:
                    return await func(*args, **kwargs)

                except Exception as e:
                    last_exception = e

                    print(
                        f"[Retry {attempt}/{max_retries}] "
                        f"{func.__name__} failed: {e}"
                    )

                    if attempt < max_retries:
                        await asyncio.sleep(delay)

            raise last_exception

        return wrapper

    return decorator