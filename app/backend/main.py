from    security                import  *
from    mongo                   import  *
from    models                  import  *
from    contextlib              import  asynccontextmanager
from    fastapi                 import  FastAPI, Request
from    fastapi                 import  WebSocket, WebSocketDisconnect
from    fastapi                 import  HTTPException, status
from    fastapi.middleware.cors import  CORSMiddleware
from    slowapi.errors          import  RateLimitExceeded
from    typing                  import  Dict, Optional
from    dotenv                  import  load_dotenv
from    uuid                    import  uuid4
import  uvicorn
import  logging
import  os

load_dotenv()

logging.basicConfig(
    level   =   logging.INFO,
    format  =   "%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)

logger = logging.getLogger(__name__)
def get_required_env(name: str) -> str:
    """Return a required environment variable or raise a startup error.

    Args:
        name: Environment variable name.

    Returns:
        The environment variable value.

    Raises:
        RuntimeError: If the variable is missing or empty.
    """
    value = os.getenv(name, "").strip()
    if not value:
        raise RuntimeError(f"Missing required environment variable: {name}")
    return value

def get_allowed_origins() -> list[str]:
    """
    Parse ALLOWED_ORIGINS into a list of origins.

    Returns:
        A list of configured origins.

    Raises:
        RuntimeError: If ALLOWED_ORIGINS is missing or empty.
    """
    raw_value = get_required_env("ALLOWED_ORIGINS")
    origins = [origin.strip() for origin in raw_value.split(",") if origin.strip()]
    if not origins:
        raise RuntimeError("ALLOWED_ORIGINS must contain at least one origin.")
    return origins

ENCRYPTION_KEY      =   get_required_env("ENCRYPTION_KEY")
JWT_SECRET_KEY      =   get_required_env("JWT_SECRET_KEY")
ALLOWED_ORIGINS     =   get_allowed_origins()
cipher              =   Cipher(ENCRYPTION_KEY)
jwt_tokenizer       =   AuthToken(secret=JWT_SECRET_KEY)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan handler."""
    logger.info("Application starting")
    yield
    logger.info("Application shutting down")

app     =   FastAPI(
    title       =   "Mongo Websocket Service",
    version     =   "1.0.0",
    description =   "Encrypted request API with JWT auth and Mongo WebSocket support.",
    lifespan    =   lifespan,
)

app.state.limiter   =   limiter
app.add_exception_handler(RateLimitExceeded, rate_limit_exceeded_handler)

app.add_middleware(
    CORSMiddleware,
    allow_origins       =   ALLOWED_ORIGINS,
    allow_credentials   =   True,
    allow_methods       =   ["GET", "POST", "OPTIONS"],
    allow_headers       =   ["Authorization", "Content-Type"],
)

# ============================================================================
# HTTP Endpoint Helper Functions
# ============================================================================

def build_success_response(message:str, data:Optional[Dict]=None) -> CommonResponse:
    """
    Build a standardized success response.

    Args:
        message (str): Human-readable success message.
        data (Optional[str]): Optional response payload.

    Returns:
        CommonResponse: Standardized API response wrapper.
    """
    return CommonResponse(
        message     =   message,
        is_error    =   False,
        data        =   data or {},
    )

def build_http_error(status_code: int, detail: str) -> HTTPException:
    """
    Create a standardized HTTPException.

    Args:
        status_code (str): HTTP status code.
        detail (str): Error detail message.

    Returns:
        HTTPException: HTTPException instance.
    """
    return HTTPException(status_code=status_code, detail=detail)

def build_encrypted_error_payload(message: str) -> str:
    """
    Build a standardized encrypted WebSocket error payload.

    Args:
        message (str): Error message to return to the client.

    Returns:
        str: Encrypted string payload.
    """
    return cipher.encrypt_payload(
        {
            "message": "An error occureed",
            "is_error": True,
            "data": {
                "error_message":message
            },
        }
    )

def create_session_token() -> str:
    """
    Create a JWT-backed session token.

    Returns:
        str: Encoded session token.
    """
    session_id = str(uuid4())
    return jwt_tokenizer.create_token({"session_id": session_id})

# ============================================================================
# Public Endpoints (No Authentication Required)
# ============================================================================

@app.get("/auth", response_model=EncryptedMessage)
@limiter.limit("60/minute")
async def auth_session(request: Request) -> EncryptedMessage:
    """
    Create an anonymous session token for WebSocket authentication.

    Returns:
        CommonResponse with a session token.

    Raises:
        HTTPException: If token generation fails.
    """
    try:
        token = create_session_token()        
        return EncryptedMessage(
            encrypted=cipher.encrypt_payload({'token':token})
        )
    except TokenInputError:
        logger.exception("Invalid Credentials")
        raise build_http_error(
            status.HTTP_500_INTERNAL_SERVER_ERROR,
            "Authentication service error.",
        )
    except AuthTokenError:
        logger.exception("Token generation failed")
        raise build_http_error(
            status.HTTP_500_INTERNAL_SERVER_ERROR,
            "Authentication service error.",
        )

    except EncryptionError:
        logger.warning("Login failed due to invalid encrypted payload")
        raise build_http_error(
            status.HTTP_400_BAD_REQUEST,
            "Invalid encrypted data.",
        )
    except HTTPException:
        raise
    except Exception:
        logger.exception("Unexpected error during login")
        raise build_http_error(
            status.HTTP_400_BAD_REQUEST,
            "Invalid request.",
        )
 
@app.get("/health", tags=["System"])
@limiter.limit("60/minute")
async def health_check(request: Request) -> dict[str, str]:
    """Service health check endpoint.

    Returns:
        A simple status payload.
    """
    return {"status": "ok"}

# ============================================================================
# WebSocket Endpoint Helper Functions
# ============================================================================

def decode_websocket_session_token(token: str = '') -> str:
    """
    Validate and decode the WebSocket session token.

    Args:
        token (str): JWT token from query params.

    Returns:
        str: session_id extracted from the token.

    Raises:
        InvalidTokenError: If token is invalid.
        HTTPException: If session_id is missing.
    """
    if not token:
        raise build_http_error(status.HTTP_401_UNAUTHORIZED, "Missing token.")

    payload     =   jwt_tokenizer.decode_token(token)
    session_id  =   payload.get("session_id")

    if not isinstance(session_id, str) or not session_id.strip():
        raise build_http_error(status.HTTP_401_UNAUTHORIZED, "Invalid session token.")

    return session_id

async def process_websocket_message(session_id:str, mongo: MongoWebSocket, received_data: str) -> str:
    """
    Decrypt, validate, process, and re-encrypt a single WebSocket message.

    The token in the payload must contain the same session_id that was used
    during the WebSocket handshake.

    Args:
        session_id (str): Session identifier established on WebSocket connection.
        mongo (MongoWebSocket): MongoWebSocket action handler.
        received_data (str): Encrypted incoming client message.

    Returns:
        str: Encrypted response payload.
    """
    try:
        payload             =   cipher.decrypt_payload(received_data)
        token               =   jwt_tokenizer.decode_token(payload.get('token', ''))
        
        token_session_id    =   token.get('session_id', '')
        if token_session_id != session_id:
            logger.warning("Invalid Token")
            return build_encrypted_error_payload(f"Invalid Token")

        result              =   await mongo.run_action(payload)
        return cipher.encrypt_payload(result.model_dump())

    except InvalidTokenError as e:
        logger.warning(f"Invalid Token. {e}")
        return build_encrypted_error_payload(f"Invalid Token. {e}")

    except InvalidEncryptedData as e:
        logger.warning("WebSocket received invalid encrypted payload")
        return build_encrypted_error_payload(f"Invalid encrypted payload. {e}")

    except DecryptionError as e:
        logger.warning("WebSocket payload decryption failed")
        return build_encrypted_error_payload(f"Could not decrypt data. {e}")

    except EncryptionError as e:
        logger.exception("WebSocket response encryption failed")
        return build_encrypted_error_payload(f"Could not process response. {e}")

    except EVP_BytesToKeyError as e:
        logger.exception("Low-level encryption key derivation error")
        return build_encrypted_error_payload("Encryption error.")

    except Exception as e:
        logger.exception("Unexpected error while processing WebSocket message")
        return build_encrypted_error_payload("Could not process data.")



# ============================================================================
# WebSocket Endpoints Helper Functions
# ============================================================================   
@app.websocket('/ws/mongo')
async   def mongo_websocket(websocket: WebSocket) -> WebSocket:
    """
    WebSocket endpoint for encrypted Mongo actions.

    Workflow:
    1. Client connects with `?token=<session_token>`
    2. Server validates session token
    3. Client sends encrypted text payloads
    4. Server decrypts payload, validates embedded token, executes action
    5. Server encrypts and returns the response

    Notes:
        - Errors are handled within the loop and returned as encrypted payloads.
        - Sensitive internal details are not exposed to clients.
    """
    session_id  =   None
    mongo       =   None
    
    try:
        session_token   =   websocket.query_params.get("token")
        session_id      =   decode_websocket_session_token(session_token)
    except InvalidTokenError:
        logger.warning("WebSocket connection rejected: invalid token")
        await websocket.close(code=1008)
        return
    except HTTPException as exc:
        logger.warning("WebSocket connection rejected: %s", exc.detail)
        await websocket.close(code=1008)
        return
    except Exception:
        logger.exception("Unexpected error during WebSocket authentication")
        await websocket.close(code=1011)
        return
    
    await websocket.accept()
    mongo       =   MongoWebSocket()

    logger.info(f"WebSocket client connected to {session_id}")
    try:
        while True:
            request     =   await websocket.receive_text()
            response    =   await process_websocket_message(session_id, mongo, request)
            await   websocket.send_text(response)

    except WebSocketDisconnect:
        logger.info(f"WebSocket client disconnected form {session_id}")
    except Exception:
        logger.exception("Unexpected websocket error")
        try:
            await websocket.close(code=1011)
        except Exception:
            logger.debug("WebSocket close failed", exc_info=True)



if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
