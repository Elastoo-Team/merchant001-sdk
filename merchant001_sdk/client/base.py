from __future__ import annotations

import asyncio
import functools
import http
import typing as t
from contextlib import AbstractAsyncContextManager, AbstractContextManager
from types import TracebackType

import httpx

from merchant001_sdk.core.data.schemas import responses
from merchant001_sdk.core.data.schemas.base import BaseSchema
from merchant001_sdk.core.errors.client_closed import SDKClientClosed
from merchant001_sdk.core.errors.http_error import ClientResponseHTTPError


def sync_or_async() -> t.Callable[[t.Any], t.Any]:
    """sync_or_async.

    Args:

    Returns:
        t.Callable[[t.Any], t.Any]:
    """

    def decorator(
        func: t.Any,
    ) -> t.Callable[
        [BaseClient, t.Tuple[t.Any, ...], t.Dict[str, t.Any]],
        t.Union[t.Any, t.Coroutine[None, None, None]],
    ]:
        """decorator.

        Args:
            func (t.Any): func

        Returns:
            t.Callable[[BaseClient, t.Tuple[t.Any, ...], t.Dict[str, t.Any]], t.Union[t.Any, t.Coroutine[None, None, None]]]:
        """

        @functools.wraps(func)
        def wrapper(
            self: BaseClient, *args: t.Tuple[t.Any, ...], **kwargs: t.Dict[str, t.Any]
        ) -> t.Union[t.Any, t.Coroutine[None, None, None]]:
            """wrapper.

            Args:
                self (BaseClient): self
                args (t.Tuple[t.Any, ...]): args
                kwargs (t.Dict[str, t.Any]): kwargs

            Returns:
                t.Union[t.Any, t.Coroutine[None, None, None]]:
            """

            coro = func(self, *args, **kwargs)

            if self.is_async:
                return coro
            else:
                return asyncio.run(coro)

        return wrapper  # type: ignore

    return decorator


class BaseClient(BaseSchema, AbstractAsyncContextManager["BaseClient"], AbstractContextManager["BaseClient"]):
    """BaseClient."""

    endpoint: str
    token: str
    token_prefix: str
    cookies: dict[str, t.Any]
    is_async: bool
    close_on_exit: bool
    _client: httpx.AsyncClient | None

    async def _request(
        self,
        method: str,
        path: str,
        is_list: bool = False,
        return_raw: bool = False,
        request_validator: type[BaseSchema] | None = None,
        response_validator: type[BaseSchema] | None = None,
        data: dict[str, t.Any] | None = None,
        success_status: tuple[http.HTTPStatus, ...] = (http.HTTPStatus.OK,),
        params: dict[str, t.Any] | None = None,
    ) -> BaseSchema | list[BaseSchema] | None:
        """_request.

        Args:
            method (str): method
            path (str): path
            is_list (bool): is_list
            return_raw (bool): return_raw
            request_validator (type[BaseSchema] | None): request_validator
            response_validator (type[BaseSchema] | None): response_validator
            data (dict[str, t.Any] | None): data
            success_status (tuple[http.HTTPStatus, ...]): success_status
            params (dict[str, t.Any] | None): params

        Returns:
            BaseSchema | list[BaseSchema] | None:
        """

        if not self._client or self._client.is_closed:
            raise SDKClientClosed("Client is closed.")

        response = await self._client.request(
            method,
            path,
            json=request_validator(**data).data if data and request_validator else data if data else None,
            cookies=self.cookies,
            params=params,
        )

        if return_raw and response.status_code in success_status:
            return responses.RawResult(
                status_code=response.status_code,
                body=response.text,
                content_type=response.headers.get("Content-Type"),
            )
        elif return_raw and response.status_code not in success_status:
            body_data = response.json()

            return responses.ErrorResult(
                status_code=response.status_code,
                message=body_data.get("message"),
                error=body_data.get("error"),
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
        """_close.

        Args:

        Returns:
            None:
        """

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
    ) -> BaseClient:
        """__enter__."""

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
        """__exit__."""

        if self.close_on_exit:
            self._close()

        return super().__exit__(__exc_type, __exc_value, __traceback)

    async def __aenter__(
        self,
    ) -> BaseClient:
        """__aenter__."""

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
        """__aexit__."""

        if self.close_on_exit:
            await self._close()

        return await super().__aexit__(__exc_type, __exc_value, __traceback)
