import typing as t
from dataclasses import dataclass, field

from smsce_finance.core.data.schemas.base import BaseSchema


@dataclass(frozen=True, kw_only=True)
class ListAccounts(BaseSchema):
    user_id: int | None = field(default=None)

    @property
    def data(self) -> dict[str, int | None]:
        query = {}

        if self.user_id:
            query["user_id"] = self.user_id

        return query


@dataclass(frozen=True, kw_only=True)
class CreateMoneyMovement(BaseSchema):
    user_id: str = field()
    description: str = field()
    sum: float = field()
    type: int = field()
    code: str | None = field(default=None)

    @property
    def data(self) -> dict[str, t.Any]:
        query = {
            "user_id": self.user_id,
            "description": self.description,
            "sum": self.sum,
            "type": self.type,
        }

        if self.code:
            query["code"] = self.code

        return query


@dataclass(frozen=True, kw_only=True)
class GetMoneyMovement(BaseSchema):
    date_begin: str = field()
    date_end: str = field()
    user_id: str | None = field(default=None)

    @property
    def data(self) -> dict[str, t.Any]:
        query = {
            "paginator": {
                "date_end": self.date_end,
                "date_begin": self.date_begin,
            },
        }

        if self.user_id:
            query["user_id"] = self.user_id  # type: ignore

        return query
