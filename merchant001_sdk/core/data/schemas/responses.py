import http
import json
import typing as t
from dataclasses import dataclass, field

from merchant001_sdk.core.data.schemas.base import BaseSchema


@dataclass(frozen=True, kw_only=True)
class RawResult(BaseSchema):
    status_code: http.HTTPStatus = field()
    body: t.Any | None = field(default=None)
    content_type: str | None = field(default=None)

    def get_json(self) -> dict[str, t.Any]:
        return json.loads(self.body)

    @property
    def data(self) -> dict[str, t.Any]:
        return {"status_code": self.status_code, "body": self.body, "content_type": self.content_type}


@dataclass(frozen=True, kw_only=True)
class ErrorResult(BaseSchema):
    status_code: http.HTTPStatus = field()
    message: str | None = field(default=None)
    error: str | None = field(default=None)

    @property
    def data(self) -> dict[str, t.Any]:
        return {"status_code": self.status_code, "error": self.error, "message": self.message}


@dataclass(frozen=True, kw_only=True)
class MerchantHealthcheck(BaseSchema):
    success: bool = field()

    @property
    def data(self) -> dict[str, bool]:
        return {
            "success": self.success,
        }
