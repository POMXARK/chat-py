from pydantic import Field

from utils.ddd import ValueObject

__all__ = ["ProductID"]


class ProductID(ValueObject):
    __root__: int = Field(..., ge=111111111)
