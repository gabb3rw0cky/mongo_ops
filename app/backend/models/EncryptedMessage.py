from    .APIModel   import  APIModel
from    pydantic    import  Field
class EncryptedMessage(APIModel):
    """
    Request and Response body for endpoints that accept encrypted payloads 
    and encrypt response returned by API.

    Attributes:
        encrypted   (str)   :   Encrypted string payload.
    """
    encrypted   :   str         =   Field(min_length=1)