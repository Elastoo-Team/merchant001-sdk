import http
import typing as t
from dataclasses import dataclass, field

from merchant001_sdk.core.data.schemas.base import BaseSchema


@dataclass(kw_only=True)
class ErrorResult(BaseSchema):
    """Error response for queries."""

    status_code: http.HTTPStatus = field()
    message: str | None = field(default=None)
    error: str | None = field(default=None)

    @property
    def data(self) -> dict[str, t.Any]:
        """data.

        Args:

        Returns:
            dict[str, t.Any]:
        """
        return {"status_code": self.status_code, "error": self.error, "message": self.message}
