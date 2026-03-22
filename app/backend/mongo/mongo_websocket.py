"""
WebSocket action handler for MongoDB operations.

Maps incoming WebSocket actions to MongoDB functions.
"""

from    __future__      import  annotations
from    .mongo_errors   import  MongoInputError
from    .models         import  MongoResponse
from    .mongo          import  Mongo
from    bson            import  ObjectId
from	datetime        import  datetime
from    typing          import  Dict, Any

INITIALIZE      =   'INITIALIZE'
GET_DATABASE    =   'GET_DATABASE'
GET_COLLECTION  =   'GET_COLLECTION'
GET_DATA        =   'GET_DATA'
CLOSE           =   'CLOSE'
MAX_LIMIT       =   1000

def _format_value(value: Any) -> Any:
    """
    Convert values into JSON-serializable Python types.

    Supported conversions:
    - ObjectId  ->  str
    - datetime  ->  ISO 8601 string
    - bytes     ->  UTF-8 string if possible, otherwise base64 string
    - dict      ->  recursively formatted dict
    - list      ->  recursively formatted list

    Args:
        value (Any) : Python object.

    Returns:
        Any: A JSON-serializable representation when possible.
    """
    
    if isinstance(value, ObjectId):
        return str(value)
    
    if isinstance(value, datetime):
        return value.isoformat()
    
    if isinstance(value, bytes):
        return value.decode()
    
    if isinstance(value, dict):
        return	_format_object(value)
    
    if isinstance(value, list):
        return	[_format_value(v) for v in value]
    
    return	value

def _format_object(item: Dict[str, Any]) -> Dict[str, Any]:
    """
    Recursively format a MongoDB document into a JSON-safe dictionary.

    Args:
        item  (Dict): The source dictionary.

    Returns:
        Dict: A recursively formatted dictionary.
    """
    return {key: _format_value(value) for key, value in item.items()}

class   MongoWebSocket():
    """Async MongoDB action handler intended for WebSocket integrations."""

    def __init__(self)                                          ->  None:
        """Initialize the handler."""
        self.mongo      =   Mongo()
        self._actions   =   {
            INITIALIZE      :   self.initialize,
            GET_DATABASE    :   self.get_database,
            GET_COLLECTION  :   self.get_collection,
            GET_DATA        :   self.get_data,
            CLOSE           :   self.close,
        }

    def _success(self, action: str, data: Dict[str, Any]={})    ->  MongoResponse:
        """
        Build a success response.

        Args:
            action (str): Action to respond to.
            data (Dict): Data produced by action.

        Returns:
            MongoResponse: MongoResponse populated with action and data.
        
        """
        return MongoResponse(action=action, is_error=False, data=data or {})

    def _error(self, action: str, message: str)                 ->  MongoResponse:
        """
        Build a error response.

        Args:
            action (str): Action to respond to.
            message (str): Error message.

        Returns:
            MongoResponse: MongoResponse populated with action and error message.
        
        """
        return MongoResponse(
            action=action,
            is_error=True,
            data={"error_message": message},
        )

    async def   initialize(self, payload: Dict[str, Any])       ->  MongoResponse:
        """
        Initialize a Mongo connection.

        Args:
            payload (Dict): Incoming action payload. 
                Expected payload: {"mongo_uri": "<mongodb-uri>"}

        Returns:
            MongoResponse: Successful MongoResponse populated with database.
        """
        action  =   INITIALIZE
        try:
            uri =   payload.get("mongo_uri")
            if not uri or not isinstance(uri, str):
                raise MongoInputError("A valid 'mongo_uri' is required.")
            
            database_names  =   await self.mongo.connect(uri)
            
            return  self._success(action, {"database_names": database_names})
        except  MongoInputError as e:
            return self._error(action, str(e))
        except  Exception as e:
            return self._error(action, str(e))

    async def   get_database(self, payload: Dict[str, Any])     ->  MongoResponse:
        """
        Select a database and list collections.

        Args:
            payload (Dict): Incoming action payload. 
                Expected payload: {"database": "<database-name>"}

        Returns:
            MongoResponse: Successful MongoResponse populated with collection names.
        """
        action          =   GET_DATABASE
        try:
            database    =   payload.get("database")
            if not database or not isinstance(database, str):
                raise MongoInputError("A valid 'database' is required.")
            
            collection_names    =   await self.mongo.connect_database(database)
            
            return  self._success(action, {"collection_names": collection_names})
        except  MongoInputError as e:
            return self._error(action, str(e))
        except  Exception as e:
            return self._error(action, str(e))

    async def   get_collection(self, payload: Dict[str, Any])   ->  MongoResponse:
        """
        Select a collection.

        Args: 
            payload: Incoming action payload. 
                Expected payload: {"collection": "<collection-name>"}

        Returns:
            MongoResponse: Successful MongoResponse populated with collection metadata.
        """
        action          =   GET_COLLECTION
        try:
            collection  =   payload.get("collection")
            if not collection or not isinstance(collection, str):
                raise MongoInputError("A valid 'collection' is required.")

            raw_data    =   await self.mongo.connect_collection(collection)
            serialized  =   _format_value(raw_data)
            return  self._success(action, {"data": serialized})
        except  MongoInputError as e:
            return self._error(action, str(e))
        except  Exception as e:
            return self._error(action, str(e))
        
    async def   get_data(self, payload: Dict[str, Any])         ->  MongoResponse:
        """
        Fetch documents from the current collection.

        Args:
            payload: Incoming action payload. 
                Expected payload: {"limit": 100}  # optional

        Returns:
            MongoResponse: Successful MongoResponse populated with serialized documents.
        """
        action              =   GET_DATA
        try:
            limit           =   payload.get("limit")
            if limit is not None:
                if not isinstance(limit, int):
                    raise MongoInputError("'limit' must be an integer.")
                if limit < 1:
                    raise MongoInputError("'limit' must be greater than 0.")
                limit       =   min(limit, MAX_LIMIT)

            data            =   await self.mongo.get_collection_data(limit)
            formatted_data  =   [_format_object(doc) for doc in data]
            return self._success(action, {"data": formatted_data})
        except  MongoInputError as e:
            return self._error(action, str(e))
        except  Exception as e:
            return self._error(action, str(e))

    async def   close(self)                                     ->  MongoResponse:
        """
        Close the Mongo connection.

        Returns:
            MongoResponse: MongoResponse indicating whether the connection was closed.
        """
        action      =   CLOSE
        try:
            result  =   await self.mongo.close_connection()

            if result:
                return self._success(action, {})

            return self._error(action, "Error trying to close connection.")
        except  Exception as e:
            return self._error(action, str(e))

    async def   run_action(self, payload: Dict[str, Any])       ->  MongoResponse:
        """
        Dispatch an incoming action payload to the appropriate handler.

        Args:
            payload: Action payload. Expected payload format:
    {
        "action": "INITIALIZE" | "GET_DATABASE" | "GET_COLLECTION" | "GET_DATA" | "CLOSE",
        ...
    }

        Returns:
            MongoResponse: MongoResponse from the corresponding action handler.
        """
        action      =   payload.get("action", "")
        handler     =   self._actions.get(action)

        if handler is None:
            return self._error("ERROR", "Invalid action")

        return await handler(payload)
