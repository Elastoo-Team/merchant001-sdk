from dataclasses import dataclass, field

from merchant001_sdk.core.data.schemas.base import BaseSchema


@dataclass(frozen=True, kw_only=True)
class PaymentMethodRate(BaseSchema):
    """Data of current rate for payment method."""

    method: str = field()
    rate: float = field()

    @property
    def data(self) -> dict[str, str | float]:
        return {"method": self.method, "rate": self.rate}
