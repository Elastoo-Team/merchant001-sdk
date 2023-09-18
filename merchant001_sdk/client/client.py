from __future__ import annotations

import asyncio
import functools
import http
import typing as t
from contextlib import AbstractAsyncContextManager, AbstractContextManager
from dataclasses import dataclass, field
from types import TracebackType

import httpx

from merchant001_sdk.core.data.schemas import responses
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
            coro = func(self, *args, **kwargs)

            if self.is_async:
                return coro
            else:
                return asyncio.run(coro)

        return wrapper  # type: ignore

    return decorator


@dataclass(kw_only=True)
class Client(BaseSchema, AbstractAsyncContextManager["Client"], AbstractContextManager["Client"]):
    endpoint: str = field()
    token: str = field()
    token_prefix: str = field(default="Bearer")
    cookies: dict[str, t.Any] = field(default_factory=dict)
    is_async: bool = field(default=False)
    close_on_exit: bool = field(default=False)
    _client: httpx.AsyncClient | None = field(default=None)

    @sync_or_async()
    async def get_merchant_healthcheck(self) -> responses.MerchantHealthcheck | responses.ErrorResult:
        """get_merchant_healthcheck."""

        result: responses.RawResult = await self._request(  # type: ignore
            http.HTTPMethod.POST,
            "v1/healthcheck/merchant/",
            request_validator=None,
            response_validator=None,
            return_raw=True,
        )

        body_data = result.get_json() or {}

        if result.status_code != http.HTTPStatus.CREATED:
            return responses.ErrorResult(
                status_code=result.status_code,
                message=body_data.get("message"),
                error=body_data.get("error"),
            )

        return responses.MerchantHealthcheck(success=body_data.get("success"))

    async def _request(
        self,
        method: http.HTTPMethod,
        path: str,
        is_list: bool = False,
        return_raw: bool = False,
        request_validator: type[BaseSchema] | None = None,
        response_validator: type[BaseSchema] | None = None,
        data: dict[str, t.Any] | None = None,
        success_status: tuple[http.HTTPStatus, ...] = (http.HTTPStatus.OK,),
    ) -> BaseSchema | list[BaseSchema] | None:
        """_request."""

        if not self._client or self._client.is_closed:
            raise SDKClientClosed("Client is closed.")

        response = await self._client.request(
            method,
            path,
            data=request_validator(**data).data if data and request_validator else None,
            cookies=self.cookies,
        )

        if return_raw:
            return responses.RawResult(
                status_code=response.status_code,
                body=response.text,
                content_type=response.headers.get("Content-Type"),
            )

        if response.status_code not in success_status:
            raise ClientResponseHTTPError(f"Error http status code in request on {path}: {response.status_code}.")

        results = response.json()

        if response_validator and results:
            if is_list:
                results = [response_validator(**d) for d in results]
            else:
                results = response_validator(**results)

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
            headers={"Authorization": f"{self.token_prefix} {self.token}"},
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
