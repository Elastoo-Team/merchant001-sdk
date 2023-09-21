from dataclasses import dataclass, field

from merchant001_sdk.core.data.schemas.base import BaseSchema


@dataclass(frozen=True, kw_only=True)
class MerchantHealthcheck(BaseSchema):
    success: bool = field()

    @property
    def data(self) -> dict[str, bool]:
        return {
            "success": self.success,
        }
