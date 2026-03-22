# Overview of Mongo.py

## `await connect(uri: str) -> list[str]`
uri (str): The MongoDB connection URI string 
Connects to MongoDB and returns database names.

## `await reconnect() -> list[str]`
Reconnects using the stored URI if needed.

## `await connect_database(database: str) -> list[str]`
database (str): Database name.
Selects a database and returns its collections.

## `await connect_collection(collection: str, schema_sample_size: int = 100) -> dict[str, Any]`
collection (str): Collection name.
Selects a collection and returns:
- `count`: total number of documents
- `schema`: lightweight inferred schema

## `await get_collection_data(limit: int | None = None) -> list[dict[str, Any]]`
limit (Optional[int]): Optional maximum number of documents to return. Must be >= 1 if set.
Returns documents from the selected collection.

## `await check_connection() -> bool`
Pings MongoDB and returns whether the connection is alive.

## `await close_connection() -> bool`
Closes the client and resets internal state.

## `get_collection_schema(collection, sample_size=100) -> dict[str, list[str]]`
Infers a lightweight schema from a sample of documents.

# Exceptions
- `MongoError`
- `MongoInputError`
- `MongoOperationalError`

# Overview of MongoWebSocket.py

Async MongoDB action handler designed for WebSocket-style APIs.

This package wraps a `Mongo` backend and exposes a small action-based interface for:

- connecting to MongoDB
- listing databases
- selecting a database
- selecting a collection
- fetching collection data
- closing the connection

It also converts MongoDB-specific values like `ObjectId` and `datetime` into JSON-serializable values.

## Features

- Async API
- Structured responses using Pydantic
- Recursive serialization of MongoDB documents
- Safer error handling
- Logging support
- GitHub-ready package layout