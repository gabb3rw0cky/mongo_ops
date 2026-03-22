from    .auth_token_errors  import  TokenInputError
from    .auth_token_errors  import  InvalidTokenError
from    datetime            import  timedelta
from    datetime            import  datetime, timezone, timedelta
from    typing              import  Dict, Optional
import  secrets
import  base64
import  jwt

DEFAULT_EXPIRATION          =   30
MIN_SECRET_LENGTH           =   32
DEFAULT_ALGORITHM           =   "HS256"
ALLOWED_ALGORITHMS          =   {"HS256", "HS384", "HS512"}

def _generate_app_secret(user_secret: Optional[str] = None) -> str:
    """
    Return a secure application secret.

    If `user_secret` is provided and is sufficiently long, it is returned.
    Otherwise, a new cryptographically secure base64-encoded secret is generated.

    Args:
        user_secret (Optional[str]): Optional user-provided secret.

    Returns:
        str: A secure secret string.

    Raises:
        TokenInputError: If `user_secret` is provided but is not a string.
    """
    if user_secret is None or user_secret == "":
        return base64.urlsafe_b64encode(secrets.token_bytes(32)).decode("utf-8")

    if not isinstance(user_secret, str):
        raise TokenInputError("Secret must be a string.")

    if len(user_secret) < MIN_SECRET_LENGTH:
        raise TokenInputError(
            f"Secret must be at least {MIN_SECRET_LENGTH} characters long."
        )

    return user_secret
     
class AuthToken:
    """
    JWT token management class for authentication.
    
    Provides methods to create, decode, and verify JWT tokens.
    """
    def __init__( 
    	self,
        secret      :   Optional[str]   =   None,
        minutes     :   int             =   DEFAULT_EXPIRATION,
        algorithm   :   str             =   DEFAULT_ALGORITHM,
    ) -> None:
        """
        Initialize the token manager.

        Args:
            secret (Optional[str]): Signing secret. If omitted, a random secret is generated.
            minutes (int): Token expiration time in minutes.
            algorithm (str): JWT signing algorithm.

        Raises:
            TokenInputError: If any configuration value is invalid.
        """
        if not isinstance(algorithm, str):
            raise TokenInputError("Algorithm must be a string.")

        if algorithm not in ALLOWED_ALGORITHMS:
            raise TokenInputError(
                f"Unsupported algorithm '{algorithm}'. "
                f"Allowed values: {sorted(ALLOWED_ALGORITHMS)}"
            )

        if not isinstance(minutes, int):
            raise TokenInputError("Minutes must be an integer.")

        if minutes <= 0:
            raise TokenInputError("Minutes must be greater than 0.")
        
        self.secret 	=	_generate_app_secret(secret)
        self.minutes	=	minutes
        self.algorithm	=	algorithm
    
    def create_token(self, data:Dict) -> str:
        """
        Create a JWT token with user information

        Args:
            data (Dict) : Payload data to include in the token.

        Returns:
            str : A signed JWT token string.

        Raises:
            TokenInput: If user_id or role is invalid.
            UnexpectedTokenError: If an unexpected error occurs.
        """
        try:           
            now         =   datetime.now(timezone.utc) 
            payload		=	{
                **data,
                'exp'	    :	now + timedelta(minutes=self.minutes),
                'iat'	    :	now
            }
            
            return  jwt.encode(payload, self.secret, algorithm=self.algorithm)

        except Exception as exc:
            raise TokenInputError(f"Failed to create token: {exc}") from exc

    def decode_token(self, token:str="") -> Dict:
        """
        Decode and verify a JWT token.

        Args:
            token (str): The JWT token to decode.

        Returns:
            Dict: The payload extracted from the token if valid.

        Raises:
            InvalidTokenError: If token is expired, malformed, or invalid.
            UnexpectedTokenError: If decoding fails unexpectedly.
        """
        try:
            if not isinstance(token, str) or not token.strip():
                raise InvalidTokenError("Token must be a non-empty string.")
            
            payload     =   jwt.decode(
                token, self.secret, algorithms=[self.algorithm],
                # options={"require": ["exp", "iat"]},
            )
            
            if not payload:
                raise InvalidTokenError("Could not decode token.")
            
            return payload

        except InvalidTokenError:
            raise
        except Exception as exc:
            raise InvalidTokenError(exc)
