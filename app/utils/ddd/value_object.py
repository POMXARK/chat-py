from pydantic import BaseModel

__all__ = ["Nothing", "ValueObject"]


class ValueObject(BaseModel):
    class Config:
        frozen = True


class Nothing(ValueObject):
    ...
