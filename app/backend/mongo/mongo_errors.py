"""
Custom exception hierarchy for MongoDB-related operations.
"""

class   MongoError(Exception):
    """MongoDB exceptions"""
    def __init__(self, *args):
        super().__init__(*args)

class   MongoInputError(MongoError):
    """Raised when input parameters are invalid or missing."""
    def __init__(self, *args):
        super().__init__(*args)

class   MongoOperationalError(MongoError):
    """Raised when an unexpected error occurs during MongoDB operations."""
    def __init__(self, *args):
        super().__init__(*args)