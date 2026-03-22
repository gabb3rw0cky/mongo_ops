# Models
Models are implemented using **Pydantic** and are used for:
- Validating incoming WebSocket payloads
- Enforcing consistent data structures
- Providing type safety across layers

## Main Models
The purpose of these modules are to provide validated standardized request and response objects for endpoints.

### APIModel

The purpose of this module is to provide a standardized base schema for all API models centralizing shared Pydantic configuration to ensure consistent validation behavior across request and response models.

**Attributes**
- None
  
**Key Components**
- **Pydantic BaseModel**: Provides schema validation, type enforcement, and serialization.
- **ConfigDict**: Enforces a standard set of rules.
- **extra**: Forbids extra data during model initialization.
- **str_strip_whitespace**: Strips leading and trailing whitespaces. 
- **validate_assignment**: Validation on assignment (including changes)

### CommonResponse

The purpose of this module is to provide a standardized API response wrapper for http endpoints. This module extends from APIModel.

**Attributes**
- **message: str**: Human-readable response message.
- **is_error: bool**: Indicates whether the response represents an error.
- **data: Dict**: Optional structured payload returned by the API.

**Key Components**
- **APIModel**: Provides schema validation, type enforcement, and serialization.
- **typing.Dict / Any**: Allows flexible structured payloads while keeping a typed interface.
- **Field(default_factory=Dict)**: Ensures `data` is initialized safely with a default dictionary-like value for each instance.

### EncryptedMessage

The purpose of this module is to provide a Request and Response body for endpoints that accept encrypted payloads and return encrypt responses.

**Attributes**
- **encrypted: str**: An encrypted string.

**Key Components**
- **APIModel**: Provides schema validation, type enforcement, and serialization.
- **Field(min_length=1)**: Ensures string has at least one character.

## Mongo Models
Mongo models define the structure of data returned by database operations.

### MongoResponse

**Purpose**
The purpose of this module is to create a single, reusable response contract for MongoDB/WebSocket, validating MongoDB data and WebSocket payloads.

**Attributes**
- **action: str**: Identifies which Mongo/WebSocket action produced the response.
- **is_error: bool**: Signals whether the response represents an error condition.
- **data: Dict**: Holds the response payload, allowing arbitrary structured content.

**Key Components**
- **Pydantic BaseModel**: Provides schema validation, type enforcement, and serialization.
- **typing.Dict / Any**: Allows flexible structured payloads while keeping a typed interface.
- **Field(default_factory=Dict)**: Ensures `data` is initialized safely with a default dictionary-like value for each instance.
