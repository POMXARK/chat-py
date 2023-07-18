from uuid import UUID

from pydantic import root_validator

from utils.ddd import ValueObject

__all__ = ["MediaFile"]


class MediaFile(ValueObject):
    id: UUID
    source: str
    preview: str
    host: str | None

    @root_validator(pre=False)
    def add_host(cls, values):
        if values.get("host"):
            values["source"] = f"{values['host']}{values['source']}"
            values["preview"] = f"{values['host']}{values['preview']}"
            values["host"] = None
        return values

    def __eq__(self, other):
        if isinstance(other, UUID):
            return (self.source.split("/")[2]) == str(other)
        return super.__eq__(self, other)
