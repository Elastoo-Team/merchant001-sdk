from dataclasses import dataclass, field

from merchant001_sdk.core.data.schemas.base import BaseSchema


@dataclass(frozen=True, kw_only=True)
class PaymentMethod(BaseSchema):
    type: str = field()
    name: str = field()
    method: str = field()
    imageUrl: str = field()

    @property
    def data(self) -> dict[str, str | str | None]:
        return {"type": self.type, "name": self.name, "method": self.method, "imageUrl": self.imageUrl}


@dataclass(frozen=True, kw_only=True)
class PaymentMethodType(BaseSchema):
    type: str = field()
    methods: list[PaymentMethod | str] = field(default_factory=list)

    @property
    def data(self) -> dict[str, str | list[dict[str, str | str | None]]]:
        return {"type": self.type, "methods": [m.data if isinstance(m, PaymentMethod) else m for m in self.methods]}  # type: ignore
