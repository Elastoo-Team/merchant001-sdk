import typing as t
from dataclasses import dataclass, field

from merchant001_sdk.core.data.schemas.base import BaseSchema


@dataclass(frozen=True, kw_only=True)
class TransactionPricing(BaseSchema):
    amount: float = field()
    currency: str = field()

    @property
    def data(self) -> dict[str, str | float]:
        return {
            "amount": self.amount,
            "currency": self.currency,
        }


@dataclass(frozen=True, kw_only=True)
class TransactionSelectedProvider(BaseSchema):
    type: str | None = field(default=None)
    method: str | None = field(default=None)

    @property
    def data(self) -> dict[str, str | None]:
        return {
            "type": self.type,
            "method": self.method,
        }


@dataclass(frozen=True, kw_only=True)
class CreatedTransaction(BaseSchema):
    id: str = field()
    userId: str = field()

    status: str = field()
    direction: str = field()

    pricing: dict[str, TransactionPricing] = field()
    selectedProvider: TransactionSelectedProvider = field()

    fee: float | None = field(default=None)
    currentPaymentFee: float | None = field(default=None)

    outcomeAddress: str | None = field(default=None)

    redirectUrl: str | None = field(default=None)
    cancelUrl: str | None = field(default=None)

    isPartnerFee: bool = field(default=False)

    @property
    def data(self) -> dict[str, str | float | None | bool | dict[str, t.Any]]:
        return {
            "id": self.id,
            "userId": self.userId,
            "status": self.status,
            "pricing": {k: v.data for k, v in self.pricing.items()},
            "selectedProvider": self.selectedProvider.data,
            "fee": self.fee,
            "currentPaymentFee": self.currentPaymentFee,
            "outcomeAddress": self.outcomeAddress,
            "redirectUrl": self.redirectUrl,
            "cancelUrl": self.cancelUrl,
            "isPartnerFee": self.isPartnerFee,
        }


@dataclass(frozen=True, kw_only=True)
class Transaction(BaseSchema):
    userId: str = field()
    providerId: str = field()

    status: str = field()

    pricing: dict[str, TransactionPricing] = field()
    selectedProvider: TransactionSelectedProvider = field()

    redirectUrl: str | None = field(default=None)
    cancelUrl: str | None = field(default=None)

    isPartnerFee: bool = field(default=False)

    @property
    def data(self) -> dict[str, str | float | None | bool | dict[str, t.Any]]:
        return {
            "userId": self.userId,
            "status": self.status,
            "pricing": {k: v.data for k, v in self.pricing.items()},
            "selectedProvider": self.selectedProvider.data,
            "redirectUrl": self.redirectUrl,
            "cancelUrl": self.cancelUrl,
            "isPartnerFee": self.isPartnerFee,
        }


@dataclass(frozen=True, kw_only=True)
class GettedTransaction(BaseSchema):
    status: str = field()
    transaction: Transaction = field()

    @property
    def data(self) -> dict[str, str | dict[str, t.Any]]:
        return {"status": self.status, "transaction": self.transaction.data}


@dataclass(frozen=True, kw_only=True)
class Requisite(BaseSchema):
    accountNumber: str = field()
    accountName: str = field()
    method: str = field()
    type: str = field()
    imageUrl: str = field()
    id: str = field()

    @property
    def data(self) -> dict[str, str | dict[str, t.Any]]:
        return {
            "accountNumber": self.accountNumber,
            "accountName": self.accountName,
            "method": self.method,
            "type": self.type,
            "imageUrl": self.imageUrl,
            "id": self.id,
        }


@dataclass(frozen=True, kw_only=True)
class GettedTransactionRequisite(BaseSchema):
    requisite: Requisite = field()
    transaction: Transaction = field()

    @property
    def data(self) -> dict[str, str | dict[str, t.Any]]:
        return {"requisite": self.requisite.data, "transaction": self.transaction.data}
