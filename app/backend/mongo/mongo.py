"""
MongoDB abstraction layer.

Provides async CRUD operations and handles low-level database interactions.
"""

from    pymongo.asynchronous.collection     import  AsyncCollection
from    pymongo.asynchronous.database       import  AsyncDatabase
from    pymongo.errors                      import  PyMongoError
from    pymongo.errors                      import  ServerSelectionTimeoutError
from    .mongo_errors                       import  MongoInputError
from    .mongo_errors                       import  MongoOperationalError
from    collections                         import  defaultdict
from    pymongo                             import  AsyncMongoClient
from    typing                              import  List, Dict, Any, Optional

SAMPLE_SIZE     =   100

async def   _get_collection_schema(
    collection  :   AsyncCollection, 
    sample_size :   int     =   SAMPLE_SIZE
)-> Dict[str, List[str]]:
    """
    Infer a lightweight schema from a sample of documents in a collection.

    The schema maps each field name to the set of Python type names observed
    across the sampled documents.

    Args:
        collection (AsyncCollection): The async MongoDB collection to inspect.
        sample_size (int): Maximum number of documents to sample. Must be >= 1.

    Returns:
        A dictionary where keys are field names and values are sorted lists of
        observed Python type names.

    Raises:
        MongoInputError: If sample_size is invalid.
        MongoOperationalError: If the schema inspection fails.
    """
    if sample_size < 1:
        raise MongoInputError("sample_size must be at least 1.")
    schema: dict[str, set[str]] = defaultdict(set)


    try:
        async for doc in collection.find().limit(sample_size):
            for key, value in doc.items():
                schema[key].add(type(value).__name__)

        return {k: sorted(v) for k, v in schema.items()}
    except Exception as e:
        raise MongoOperationalError("Failed to inspect collection schema.") from e

class   Mongo():
    """An async MongoDB client wrapper."""

    def __init__(self) -> None:
        """Initialize an empty Mongo wrapper."""
        self.uri                :   str | None                  =   None
        self.database_name      :   str | None                  =   None
        self.collection_name    :   str | None                  =   None

        self.client             :   AsyncMongoClient    | None  =   None
        self.database           :   AsyncDatabase       | None  =   None
        self.collection         :   AsyncCollection     | None  =   None

    def _reset_database_state(self) -> None:
        """Clear selected database and collection state."""
        self.database_name      =   None
        self.collection_name    =   None
        self.database           =   None
        self.collection         =   None

    def _reset_all_state(self) -> None:
        """Clear all connection, database, and collection state."""
        self._reset_database_state()
        self.uri                =   None
        self.client             =   None

    async def   close_connection(self) -> bool:
        """
        Close the active MongoDB client connection and reset internal state.

        Returns:
            bool: True if the method completes successfully.

        Raises:
            MongoOperationalError: If closing the client fails.
        """
        try:
            if self.client is not None:
                self.client.close()
            self._reset_all_state()
            return True
        except Exception as e:
            raise MongoOperationalError("Failed to close MongoDB connection.") from e

    async def   check_connection(self) -> bool:
        """
        Check whether the current client is connected and responsive.

        Returns:
            bool: True if the client exists and responds to a ping, otherwise False.
        """
        if self.client is None:
            return False

        try:
            await self.client.admin.command("ping")
            return True
        except PyMongoError:
            return False

    async def   connect(self, uri: str) -> List[str]:
        """
        Asynchronously establish a connection to a MongoDB server.

        Args:
            uri (str): The MongoDB connection URI string 

        Returns:
            List[str]: A list of database names available on the server.

        Note:
            This method must be awaited when called. It stores the URI and initializes
            the AsyncMongoClient instance as instance attributes.
        """
        try:
            trimmed_uri =   uri.strip()
            if not trimmed_uri:
                raise   MongoInputError("No URI provided.")
            
            client          =   AsyncMongoClient(
                trimmed_uri, serverSelectionTimeoutMS=3000
            )
            database_names  =   await client.list_database_names()
            
            self.uri    =   trimmed_uri
            self.client =   client
            self._reset_database_state()
            return database_names
        except ServerSelectionTimeoutError:
            raise MongoInputError("Invalid URI or MongoDB server is unreachable.")
        except  MongoInputError:
            raise
        except  Exception as e:
            raise   MongoOperationalError("Failed to connect to MongoDB.") from e

    async def   reconnect(self) -> List[str]:
        """
        Reconnect using the previously stored URI.

        Returns:
            List[str]: A list of database names if reconnection succeeds

        Raises:
            MongoInputError: If the stored URI is invalid.
            MongoOperationalError: If reconnection fails.
        """
        try:
            if await self.check_connection():
                return await self.client.list_database_names()
            if self.uri:  
                return  await self.connect(self.uri)
            return  []
        except  MongoInputError:
            raise
        except  Exception as e:
            raise   MongoOperationalError("Failed to connect to MongoDB.") from e

    async def   connect_database(self, database: str) -> List[str]:
        """
        Select an existing database.

        Args:
            database (str): Database name.

        Returns:
            List[str]: A list of collection names in the selected database.

        Raises:
            MongoInputError: If the database name is invalid, no client is connected,
                or the database does not exist.
            MongoOperationalError: If the operation fails.
        """
        try:
            trimmed_database        =   database.strip()
            if not trimmed_database:
                raise   MongoInputError("No database name provided.")
            
            if self.client is None:
                raise   MongoInputError("Not connected to MongoDB.")

            databases               =   await self.client.list_database_names()
            if trimmed_database not in databases:
                raise   MongoInputError("Database does not exist")
            
            self.database_name      =   trimmed_database
            self.database           =   self.client[trimmed_database]
            self.collection_name    =   None
            self.collection         =   None
            return await self.database.list_collection_names()
        except  MongoInputError:
            raise
        except  Exception as e:
            raise   MongoOperationalError("Failed to connect to MongoDB.") from e

    async def   connect_collection(self, collection: str) -> Dict[str, Any]:
        """
        Select an existing collection from the current database.

        Args:
            collection (str): Collection name.

        Returns:
            Dict : A dictionary containing:
            - count (int): total document count
            - schema (Dict[str, List[str]]): inferred schema from sampled documents

        Raises:
            MongoInputError: If the collection name is invalid, no client/database
                is selected, or the collection does not exist.
            MongoOperationalError: If the operation fails.
        """
        try:
            trimmed_collection    =   collection.strip()
            if not trimmed_collection:
                raise   MongoInputError("No collection name provided.")
            
            if self.client is None:
                raise   MongoInputError("Not connected to mongo.")
            
            if self.database is None:
                raise   MongoInputError("No database selected.")

            collections           =   await self.database.list_collection_names()
            if trimmed_collection not in collections:
                raise   MongoInputError("Collection does not exist")
            
            self.collection_name  =   trimmed_collection
            self.collection       =   self.database[trimmed_collection]
            count   =   await self.collection.count_documents({})
            schema  =   await _get_collection_schema(self.collection)
            return  {
                'count'     :   count,
                'schema'    :   schema,
            }
        except  MongoInputError:
            raise
        except  Exception as e:
            raise MongoOperationalError("Failed to select collection.") from e

    async def   get_collection_data(self, limit: Optional[int] = None) -> List[Dict]:
        """
        Fetch documents from the currently selected collection.

        Args:
            limit (Optional[int]): Optional maximum number of documents to return. Must be >= 1 if set.

        Returns:
            List[Dict]: A list of documents.

        Raises:
            MongoInputError: If no client, database, or collection is selected,
                or if limit is invalid.
            MongoOperationalError: If the query fails.
        """
        try:
            
            if self.client is None:
                raise   MongoInputError("Not connected to MongoDB.")
            
            if self.database is None:
                raise   MongoInputError("No database selected.")
            
            if self.collection is None:
                raise   MongoInputError("No database collections.")
            
            if limit:
                cursor		=	self.collection.find().limit(limit)
            else:
                cursor		=	self.collection.find()
            
            return  [
                i async for i in cursor
            ]
        except  MongoInputError:
            raise
        except  Exception as e:
            raise MongoOperationalError("Failed to get data.") from e