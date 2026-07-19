import asyncio
from functools import wraps

from app.core.logger import logger


NON_RETRYABLE_ERRORS = (
    "429",
    "RESOURCE_EXHAUSTED",
    "quota",
    "quota exceeded",
    "invalid api key",
    "unauthorized",
    "authentication",
    "permission denied",
    "bad request",
    "400",
    "401",
    "403",
    "404",
)


def retry(max_retries: int = 3, delay: int = 2):
    """
    Retry an async function only for transient failures.

    Args:
        max_retries: Maximum retry attempts.
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

                    error = str(e).lower()

                    logger.warning(
                        f"[Retry {attempt}/{max_retries}] "
                        f"{func.__name__} failed: {e}"
                    )

                    # Don't retry permanent errors
                    if any(keyword.lower() in error for keyword in NON_RETRYABLE_ERRORS):

                        logger.error(
                            "Non-retryable error detected. "
                            "Skipping retries."
                        )

                        raise e

                    if attempt < max_retries:

                        logger.info(
                            f"Retrying in {delay} second(s)..."
                        )

                        await asyncio.sleep(delay)

            logger.error(
                f"{func.__name__} failed after "
                f"{max_retries} attempts."
            )

            raise last_exception

        return wrapper

    return decorator