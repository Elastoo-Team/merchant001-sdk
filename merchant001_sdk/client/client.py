from __future__ import annotations

import asyncio
import functools
import http
import typing as t
from contextlib import AbstractAsyncContextManager, AbstractContextManager
from dataclasses import dataclass, field
from types import TracebackType

import httpx

from merchant001_sdk.core.data.schemas.base import BaseSchema
from merchant001_sdk.core.errors.client_closed import SDKClientClosed
from merchant001_sdk.core.errors.http_error import ClientResponseHTTPError


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
    endpoint: str = field()
    user_id: str = field()
    user_groups: str = field()
    cookies: dict[str, t.Any] = field(default_factory=dict)
    is_async: bool = field(default=False)
    close_on_exit: bool = field(default=False)
    _client: httpx.AsyncClient | None = field(default=None)
    _loop: asyncio.AbstractEventLoop | None = field(default=None)

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
            raise SDKClientClosed("Client is closed.")

        response = await self._client.request(
            method,
            path,
            data=request_validator(**data).data if data and request_validator else None,
            cookies=self.cookies,
        )

        if response.status_code != http.HTTPStatus.OK:
            raise ClientResponseHTTPError(f"Error http status code in request on {path}: {response.status_code}.")

        response_data = response.json()

        results = response_data.get("data")

        if response_validator and results:
            if is_list:
                results = [response_validator(**d).data for d in results]
            else:
                results = response_validator(**response_data["data"]).data

        return results

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

        self._client = httpx.AsyncClient(
            base_url=self.endpoint,
            headers=httpx.Headers({"X-UserId": self.user_id, "X-Groups": self.user_groups}),
        )

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
