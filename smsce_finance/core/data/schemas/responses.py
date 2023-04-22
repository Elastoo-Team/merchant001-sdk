from dataclasses import dataclass, field

from smsce_finance.core.data.schemas.base import BaseSchema


@dataclass(frozen=True, kw_only=True)
class GetAccountBalance(BaseSchema):
    balance: float = field()

    @property
    def data(self) -> dict[str, float]:
        return {
            "balance": self.balance,
        }


@dataclass(frozen=True, kw_only=True)
class ListAccounts(BaseSchema):
    id: int = field()
    user_id: str = field()
    balance: float = field()

    @property
    def data(self) -> dict[str, float | str | int]:
        return {
            "id": self.id,
            "balance": self.balance,
            "user_id": self.user_id,
        }


@dataclass(frozen=True, kw_only=True)
class CreateMoneyURL(BaseSchema):
    URL: str = field()

    @property
    def data(self) -> dict[str, str]:
        return {
            "URL": self.URL,
        }
