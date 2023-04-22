import typing

from cliar import Cliar

from smsce_finance.__about__ import __version__
from smsce_finance.cli.groups import AccountGroup


class App(Cliar):
    """App entrypoint."""

    account = AccountGroup

    def __init__(self, *args: typing.Any, **kwargs: typing.Any) -> None:
        super().__init__(*args, **kwargs)

    def version(self) -> None:
        """Show version."""
        print(__version__)
