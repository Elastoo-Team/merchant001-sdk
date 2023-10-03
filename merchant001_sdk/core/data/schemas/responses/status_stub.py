import typing as t
from dataclasses import dataclass, field

from merchant001_sdk.core.data.schemas.base import BaseSchema


@dataclass(frozen=True, kw_only=True)
class StatusStub(BaseSchema):
    """Status stub."""

    status: bool = field()

    @property
    def data(self) -> dict[str, t.Any]:
        """data.

        Args:

        Returns:
            dict[str, t.Any]:
        """
        return {"status": self.status}
