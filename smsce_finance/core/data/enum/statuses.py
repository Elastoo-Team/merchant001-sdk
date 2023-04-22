from __future__ import annotations

from enum import IntEnum

from smsce_finance.core.errors.status_not_found import RestAPIStatusNotFound


class RestAPIStatus(IntEnum):
    """RestAPIStatus."""

    OK = 0
    MVMT_ERROR = 1000
    PARAM_PARSE_ERROR = 9010
    ACCESS_DENIED = 9011
    UNKNOWN = 9013
    CHARGE_ERROR = 8001
    ACCOUNT_ERROR = 7001
    MOVENETS_CREATE_ERROR = 6501

    @classmethod
    def get_status(cls, status_code: int) -> RestAPIStatus:
        """Get_status."""
        for name, code in cls.__members__.items():
            if code.value == status_code:
                return cls[name]

        raise RestAPIStatusNotFound("Invalid status code.")
