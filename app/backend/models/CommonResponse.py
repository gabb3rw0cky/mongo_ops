from    .APIModel   import  APIModel
from    pydantic    import  Field
from    typing      import  Dict, Any

class   CommonResponse(APIModel):
    """
    Standardized API response wrapper.

    Attributes:
        message     (str)   :   Human-readable response message.
        is_error    (bool)  :   Indicates whether the response represents an error.
        data        (Dict)  :   Optional structured payload returned by the API.
    """
    message     :   str         =   ''
    is_error    :   bool        =   False
    data        :   Dict        =   Field(default_factory=Dict)