import http
import json
import typing as t
from dataclasses import dataclass, field

from merchant001_sdk.core.data.schemas.base import BaseSchema


@dataclass(frozen=True, kw_only=True)
class RawResult(BaseSchema):
    """Raw json result."""

    status_code: http.HTTPStatus = field()
    body: t.Any | None = field(default=None)
    content_type: str | None = field(default=None)

    def get_json(self) -> dict[str, t.Any]:
        return json.loads(self.body)

    @property
    def data(self) -> dict[str, t.Any]:
        return {"status_code": self.status_code, "body": self.body, "content_type": self.content_type}
