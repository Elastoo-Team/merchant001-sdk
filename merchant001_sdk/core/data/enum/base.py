from enum import Enum

__all__ = ["BaseEnum"]


class BaseEnum(str, Enum):
    """Base class for enums."""

    def __str__(self) -> str:
        """Return string representation."""
        return self.name

    def __repr__(self) -> str:
        """Return string representation."""
        return self.name
