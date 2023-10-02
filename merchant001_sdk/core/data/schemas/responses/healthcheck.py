from dataclasses import dataclass, field

from merchant001_sdk.core.data.schemas.base import BaseSchema


@dataclass(frozen=True, kw_only=True)
class MerchantHealthcheck(BaseSchema):
    """Response data of test request to verify the validity of the token"""

    success: bool = field()

    @property
    def data(self) -> dict[str, bool]:
        """data.

        Args:

        Returns:
            dict[str, bool]:
        """
        return {
            "success": self.success,
        }
