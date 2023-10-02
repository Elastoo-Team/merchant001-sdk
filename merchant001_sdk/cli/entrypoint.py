import typing

from cliar import Cliar

from merchant001_sdk.__about__ import __version__


class App(Cliar):
    """App entrypoint."""

    def __init__(self, *args: typing.Any, **kwargs: typing.Any) -> None:
        """__init__.

        Args:
            args (typing.Any): args
            kwargs (typing.Any): kwargs

        Returns:
            None:
        """
        super().__init__(*args, **kwargs)

    def version(self) -> None:
        """Show version."""
        print(__version__)
