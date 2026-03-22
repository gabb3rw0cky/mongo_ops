from    fastapi.responses   import  JSONResponse
from    slowapi.errors      import  RateLimitExceeded
from    slowapi.util        import  get_remote_address
from    slowapi             import  Limiter
from    fastapi             import  Request
import  hashlib

API_KEY_HEADER      =   "X-API-Key"

def _hash_api_key(api_key: str) -> str:
    """
    Derive a stable, non-reversible identifier from an API key.

    This avoids exposing raw API keys in memory structures, logs,
    monitoring systems, or backend rate-limit storage.

    Args:
        api_key (str): Raw API key from the request header.

    Returns:
        str: A SHA-256 hex digest representing the API key.
    """
    return hashlib.sha256(api_key.encode("utf-8")).hexdigest()


def get_rate_limit_identifier(request: Request) -> str:
    """
    Return the identifier used for rate limiting the current request.

    Identification strategy:
    - If the request includes an `X-API-Key` header, use a hashed API-key-based identifier.
    - Otherwise, fall back to the client's remote IP address.

    Args:
        request (Request): Incoming FastAPI request.

    Returns:
        str: A string identifier suitable for use as a rate-limit key.
    """
    api_key = request.headers.get(API_KEY_HEADER)
    if api_key:
        return f"api:{_hash_api_key(api_key)}"

    client_ip = get_remote_address(request)
    return f"ip:{client_ip}"


limiter = Limiter(key_func=get_rate_limit_identifier)


def rate_limit_exceeded_handler(
    request: Request,
    exc: RateLimitExceeded,
) -> JSONResponse:
    """
    Handle rate-limit violations with a consistent JSON error response.

    Args:
        request (Request): Incoming FastAPI request.
        exc (RateLimitExceeded): Raised rate-limit exception.

    Returns:
        JSONResponse with HTTP 429 status.
    """
    return JSONResponse(
        status_code=429,
        content={
            "detail": "Rate limit exceeded",
            "retry_after": str(exc.detail),
        },
    )