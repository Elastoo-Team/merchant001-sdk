from __future__ import annotations

import asyncio
import functools
import http
import re
import typing as t
from contextlib import AbstractAsyncContextManager, AbstractContextManager
from dataclasses import dataclass, field
from types import TracebackType

import httpx

from smsce_finance.core.data.enum.statuses import RestAPIStatus
from smsce_finance.core.data.schemas import requests, responses
from smsce_finance.core.data.schemas.base import BaseSchema
from smsce_finance.core.errors.client_closed import FinanceClientClosed
from smsce_finance.core.errors.http_error import ClientResponseHTTPError
from smsce_finance.core.errors.internal_code_error import ClientResponseInternalError


def sync_or_async() -> t.Callable[[t.Callable[[t.Any], t.Any]], t.Any]:
    """Sync_or_async."""

    def decorator(
        func: t.Callable[[t.Any], t.Any],
    ) -> t.Callable[[Client, t.Tuple[t.Any, ...], t.Dict[str, t.Any]], t.Union[t.Any, t.Coroutine[None, None, None]]]:
        @functools.wraps(func)
        def wrapper(
            self: Client, *args: t.Tuple[t.Any, ...], **kwargs: t.Dict[str, t.Any]
        ) -> t.Union[t.Any, t.Coroutine[None, None, None]]:
            if not self._loop or self._loop.is_closed():
                self._loop = asyncio.get_event_loop()

            coro = func(self, *args, **kwargs)

            if self.is_async:
                return coro
            else:
                return self._loop.create_task(coro)

        return wrapper  # type: ignore

    return decorator


@dataclass(kw_only=True)
class Client(BaseSchema, AbstractAsyncContextManager["Client"], AbstractContextManager["Client"]):
    url: str = field()
    token: str = field()
    is_async: bool = field(default=False)
    close_on_exit: bool = field(default=False)
    _client: httpx.AsyncClient | None = field(default=None)
    _loop: asyncio.AbstractEventLoop | None = field(default=None)

    @sync_or_async()
    async def get_account_balance(self) -> dict[str, t.Any]:
        """get_account_balance."""

        return await self._request(  # type: ignore
            http.HTTPMethod.POST,
            "account/get",
            request_validator=None,
            response_validator=responses.GetAccountBalance,
        )

    @sync_or_async()
    async def get_accounts_status(self, user_id: str | None = None) -> list[dict[str, t.Any]]:
        """Get_accounts_status."""

        return await self._request(  # type: ignore
            http.HTTPMethod.POST,
            "account/list",
            data={"user_id": user_id},
            is_list=True,
            request_validator=requests.ListAccounts,
            response_validator=responses.ListAccounts,
        )

    @sync_or_async()
    async def create_payment_url(self) -> dict[str, t.Any]:
        """create_payment_url."""

        return await self._request(  # type: ignore
            http.HTTPMethod.POST,
            "charge/create",
            request_validator=None,
            response_validator=responses.CreateMoneyURL,
        )

    @sync_or_async()  # type: ignore
    async def create_money_movement(
        self,
        user_id: str,
        description: str,
        sum: float,
        type: int,
        code: str | None = None,
    ) -> None:
        """Create_money_move."""

        await self._request(
            http.HTTPMethod.POST,
            "movements/create",
            data={"user_id": user_id, "description": description, "sum": sum, "type": type, "code": code},
            response_validator=None,
            request_validator=requests.CreateMoneyMovement,
        )

    @sync_or_async()  # type: ignore
    async def get_money_movements(
        self,
        date_begin: str,
        date_end: str,
        user_id: str | None = None,
    ) -> list[dict[str, t.Any]]:
        """get_money_movements."""

        return await self._request(  # type: ignore
            http.HTTPMethod.POST,
            "movements/get",
            data={"user_id": user_id, "date_begin": date_begin, "date_end": date_end},
            is_list=True,
            request_validator=requests.GetMoneyMovement,
        )

    async def _request(
        self,
        method: http.HTTPMethod,
        path: str,
        is_list: bool = False,
        request_validator: type[BaseSchema] | None = None,
        response_validator: type[BaseSchema] | None = None,
        data: dict[str, t.Any] | None = None,
    ) -> dict[str, t.Any] | list[dict[str, t.Any]] | None:
        """_request."""

        if not self._client or self._client.is_closed:
            raise FinanceClientClosed("Client is closed.")

        response = await self._client.request(
            method,
            path,
            data=request_validator(**data).data if data and request_validator else None,
        )

        if response.status_code != http.HTTPStatus.OK:
            raise ClientResponseHTTPError(f"Error http status code in request on {path}: {response.status_code}.")

        response_data = response.json()

        if response_data["status"]["errcode"] != RestAPIStatus.OK:
            raise ClientResponseInternalError(
                (
                    f"Error internal status code in request on {path}: {response_data['status']['errcode']} ->"
                    f" \"{response_data['status']['errmsg']}\""
                ),
            )

        results = response_data.get("data")

        if response_validator and results:
            if is_list:
                results = [response_validator(**d).data for d in results]
            else:
                results = response_validator(**response_data["data"]).data

        return results

    def validate_url(self, value: str) -> str:
        """Validate_url.

        Args:
            value (str): url for client

        Returns:
            str: valid url
        """
        regex = re.compile(
            r"^(?:http|ftp)s?://"
            r"(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|"
            r"localhost|"
            r"\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})"
            r"(?::\d+)?"
            r"(?:/?|[/?]\S+)$",
            re.IGNORECASE,
        )

        assert re.match(regex, value) is not None, "Invalid URL"

        return value

    @sync_or_async()
    async def _close(self) -> None:
        """_close."""

        if self._client:
            if not self._client.is_closed:
                await self._client.__aexit__()

            self._client = None

    @sync_or_async()
    async def _open(self) -> None:
        """_open."""

        self._client = httpx.AsyncClient(base_url=self.url, headers=httpx.Headers({"X-Auth-Token": self.token}))

        await self._client.__aenter__()

    def __enter__(
        self,
    ) -> Client:
        self.is_async = False

        if not self._client or self._client.is_closed:
            self._open()

        return super().__enter__()

    def __exit__(
        self,
        __exc_type: t.Optional[type[BaseException]],
        __exc_value: t.Optional[BaseException],
        __traceback: t.Optional[TracebackType],
    ) -> t.Optional[bool]:
        if self.close_on_exit:
            self._close()

        return super().__exit__(__exc_type, __exc_value, __traceback)

    async def __aenter__(
        self,
    ) -> Client:
        self.is_async = True

        if not self._client or self._client.is_closed:
            await self._open()

        return await super().__aenter__()

    async def __aexit__(
        self,
        __exc_type: t.Optional[type[BaseException]],
        __exc_value: t.Optional[BaseException],
        __traceback: t.Optional[TracebackType],
    ) -> t.Optional[bool]:
        if self.close_on_exit:
            await self._close()

        return await super().__aexit__(__exc_type, __exc_value, __traceback)
