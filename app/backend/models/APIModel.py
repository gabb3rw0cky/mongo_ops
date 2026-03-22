from    pydantic    import  BaseModel, ConfigDict

class APIModel(BaseModel):
    """
    Standardized base schema for all API models.

    This class centralizes shared Pydantic configuration to ensure
    consistent validation behavior across request and response models.
    """

    model_config    =   ConfigDict(
        extra                   =   "forbid",
        str_strip_whitespace    =   True,
        validate_assignment     =   True,
    )