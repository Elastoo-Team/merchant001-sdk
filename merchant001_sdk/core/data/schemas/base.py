import types
import typing as t
from dataclasses import Field


class BaseSchema:
    """BaseSchema."""

    __dataclass_fields__: dict[str, Field[t.Any]]

    def _validate_field_type(self, field: Field[t.Any], value: t.Any) -> None:
        """_validate_field_type."""
        if field.type in [types.UnionType, t.Union, t.Tuple[t.Type, ...], t.Type] and not isinstance(value, field.type):
            raise ValueError(
                f'Invalid field "{field.name}" must be of type {field.type.__name__}, got {value.__class__.__name__}.',
            )

    def __setattr__(self, prop: str, val: t.Any) -> None:
        """__setattr__"""
        self._validate_field_type(self.__dataclass_fields__[prop], val)

        if validator := getattr(self, f"validate_{prop}", None):
            object.__setattr__(self, prop, validator(val) or val)
        else:
            super().__setattr__(prop, val)

    @property
    def data(self) -> dict[str, t.Any]:
        raise NotImplementedError()
