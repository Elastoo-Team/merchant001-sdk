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
    async def get_merchant_healthcheck(self) -> responses.healthcheck.MerchantHealthcheck | responses.ErrorResult:
        """get_merchant_healthcheck."""

        result: responses.RawResult = await self._request(  # type: ignore
            http.HTTPMethod.POST,
            "v1/healthcheck/merchant/",
            return_raw=True,
        )

        body_data = result.get_json() or {}

        if result.status_code != http.HTTPStatus.CREATED:
            return responses.ErrorResult(
                status_code=result.status_code,
                message=body_data.get("message"),
                error=body_data.get("error"),
            )

        return responses.healthcheck.MerchantHealthcheck(success=body_data.get("success"))

    @sync_or_async()
    async def get_payment_methods(
        self,
        raw_dict: bool = False,
        method_names_only: bool = False,
        amount: int | None = None,
    ) -> (
        dict[str, dict[str, dict[str, t.Any]]]
        | list[responses.payment_method.PaymentMethodType]
        | responses.ErrorResult
    ):
        """get_payment_methods."""

        params = {}

        if not raw_dict:
            params["makeArray"] = 1

        if method_names_only:
            params["onlyMethod"] = 1

        if amount is not None and amount > 0:
            params["amount"] = amount

        result: responses.RawResult = await self._request(  # type: ignore
            http.HTTPMethod.GET,
            "v1/payment-method/merchant/available",
            return_raw=True,
            params=params,
        )

        body_data = result.get_json() or {}

        if result.status_code != http.HTTPStatus.OK:
            return responses.ErrorResult(
                status_code=result.status_code,
                message=body_data.get("message"),
                error=body_data.get("error"),
            )

        if raw_dict:
            return body_data
        else:
            return [responses.payment_method.PaymentMethodType(**mt) for mt in body_data]  # type: ignore

    @sync_or_async()
    async def create_transaction(
        self,
        pricing: dict[str, dict[str, str | float]],
        provider_type: str,
        provider_method: str,
        is_partner_fee: bool = False,
    ) -> responses.transaction.CreatedTransaction | responses.ErrorResult:
        """create_transaction."""

        data = {
            "isPartnerFee": is_partner_fee,
            "pricing": pricing,
            "selectedProvider": {"type": provider_type, "method": provider_method},
        }

        result: responses.RawResult = await self._request(  # type: ignore
            http.HTTPMethod.POST,
            "v1/transaction/merchant",
            return_raw=True,
            data=data,
        )

        body_data = result.get_json() or {}

        if result.status_code != http.HTTPStatus.OK:
            return responses.ErrorResult(
                status_code=result.status_code,
                message=body_data.get("message"),
                error=body_data.get("error"),
            )

        return responses.transaction.CreatedTransaction(**body_data)

    @sync_or_async()
    async def get_transaction(
        self,
        transaction_id: str,
    ) -> responses.transaction.GettedTransaction | responses.ErrorResult:
        """get_transaction."""

        result: responses.RawResult = await self._request(  # type: ignore
            http.HTTPMethod.GET,
            f"v1/transaction/merchant/{transaction_id}",
            return_raw=True,
        )

        body_data = result.get_json() or {}

        if result.status_code != http.HTTPStatus.OK:
            return responses.ErrorResult(
                status_code=result.status_code,
                message=body_data.get("message"),
                error=body_data.get("error"),
            )

        return responses.transaction.GettedTransaction(**body_data)

    @sync_or_async()
    async def get_transaction_requisite(
        self,
        transaction_id: str,
    ) -> responses.transaction.GettedTransactionRequisite | responses.ErrorResult:
        """get_transaction_requisite."""

        result: responses.RawResult = await self._request(  # type: ignore
            http.HTTPMethod.GET,
            f"v1/transaction/merchant/requisite/{transaction_id}",
            return_raw=True,
        )

        body_data = result.get_json() or {}

        if result.status_code != http.HTTPStatus.OK:
            return responses.ErrorResult(
                status_code=result.status_code,
                message=body_data.get("message"),
                error=body_data.get("error"),
            )

        return responses.transaction.GettedTransactionRequisite(**body_data)

    @sync_or_async()
    async def claim_transaction_paid(
        self,
        transaction_id: str,
    ) -> responses.transaction.Transaction | responses.ErrorResult:
        """claim_transaction_paid."""

        result: responses.RawResult = await self._request(  # type: ignore
            http.HTTPMethod.POST,
            f"v1/transaction/merchant/paid/{transaction_id}",
            return_raw=True,
        )

        body_data = result.get_json() or {}

        if result.status_code != http.HTTPStatus.OK:
            return responses.ErrorResult(
                status_code=result.status_code,
                message=body_data.get("message"),
                error=body_data.get("error"),
            )

        return responses.transaction.Transaction(**body_data)

    @sync_or_async()
    async def claim_transaction_canceled(
        self,
        transaction_id: str,
    ) -> responses.transaction.Transaction | responses.ErrorResult:
        """claim_transaction_canceled."""

        result: responses.RawResult = await self._request(  # type: ignore
            http.HTTPMethod.POST,
            f"v1/transaction/merchant/cancel/{transaction_id}",
            return_raw=True,
        )

        body_data = result.get_json() or {}

        if result.status_code != http.HTTPStatus.OK:
            return responses.ErrorResult(
                status_code=result.status_code,
                message=body_data.get("message"),
                error=body_data.get("error"),
            )

        return responses.transaction.Transaction(**body_data)

    @sync_or_async()
    async def set_transaction_payment_method(
        self,
        transaction_id: str,
        provider_type: str,
        provider_method: str,
    ) -> responses.transaction.CreatedTransaction | responses.ErrorResult:
        """claim_transaction_canceled."""

        result: responses.RawResult = await self._request(  # type: ignore
            http.HTTPMethod.POST,
            f"v1/transaction/merchant/provider/{transaction_id}",
            return_raw=True,
            data={"selectedProvider": {"method": provider_method, "type": provider_type}},
        )

        body_data = result.get_json() or {}

        if result.status_code != http.HTTPStatus.OK:
            return responses.ErrorResult(
                status_code=result.status_code,
                message=body_data.get("message"),
                error=body_data.get("error"),
            )

        return responses.transaction.CreatedTransaction(**body_data)

    @sync_or_async()
    async def get_payment_method_rate(
        self,
        payment_method: str,
    ) -> responses.rate.PayemntMethodRate | responses.ErrorResult:
        """claim_transaction_canceled."""

        result: responses.RawResult = await self._request(  # type: ignore
            http.HTTPMethod.GET,
            f"v1/rate/",
            return_raw=True,
            params={"method": payment_method},
        )

        body_data = result.get_json() or {}

        if result.status_code != http.HTTPStatus.OK:
            return responses.ErrorResult(
                status_code=result.status_code,
                message=body_data.get("message"),
                error=body_data.get("error"),
            )

        return responses.rate.PayemntMethodRate(**body_data)

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
        params: dict[str, t.Any] | None = None,
    ) -> BaseSchema | list[BaseSchema] | None:
        """_request."""

        if not self._client or self._client.is_closed:
            raise SDKClientClosed("Client is closed.")

        response = await self._client.request(
            method,
            path,
            data=request_validator(**data).data if data and request_validator else data if data else None,
            cookies=self.cookies,
            params=params,
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
