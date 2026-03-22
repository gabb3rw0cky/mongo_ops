"""
Pydantic models used for validating MongoDB data and WebSocket payloads.
"""

from    pydantic        import  BaseModel, Field
from    typing          import  Dict, Any

class   MongoResponse(BaseModel):
    """Structured response returned by MongoWebSocket actions."""
    action      :   str             =   ""
    is_error    :   bool            =   False
    data        :   Dict[str, Any]  =   Field(default_factory=Dict)