from __future__ import annotations

import http
import io
import pathlib
import typing as t
from dataclasses import dataclass, field

import httpx

from merchant001_sdk.client.base import BaseClient, sync_or_async
from merchant001_sdk.core.data.schemas import responses


@dataclass(kw_only=True)
class Client(BaseClient):
    """Client."""

    endpoint: str = field()
    token: str = field()
    token_prefix: str = field(default="Bearer")
    cookies: dict[str, t.Any] = field(default_factory=dict)
    is_async: bool = field(default=False)
    close_on_exit: bool = field(default=False)
    _client: httpx.AsyncClient | None = field(default=None)

    @sync_or_async()
    async def get_merchant_healthcheck(self) -> responses.healthcheck.MerchantHealthcheck | responses.ErrorResult:
        """get_merchant_healthcheck.

        Args:

        Returns:
            responses.healthcheck.MerchantHealthcheck | responses.ErrorResult
        """
        result: responses.RawResult | responses.ErrorResult = await self._request(  # type: ignore
            "POST",
            "v1/healthcheck/merchant/",
            return_raw=True,
            success_status=(http.HTTPStatus.CREATED,),
        )

        if isinstance(result, responses.ErrorResult):
            return result

        body_data = result.get_json() or {}

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
        """get_payment_methods.

        Args:
            raw_dict (bool): raw_dict
            method_names_only (bool): method_names_only
            amount (int | None): amount

        Returns:
            (
                dict[str, dict[str, dict[str, t.Any]]]
                | list[responses.payment_method.PaymentMethodType]
                | responses.ErrorResult
            ):
        """
        params = {}

        if not raw_dict:
            params["makeArray"] = 1

        if method_names_only:
            params["onlyMethod"] = 1

        if amount is not None and amount > 0:
            params["amount"] = amount

        result: responses.RawResult | responses.ErrorResult = await self._request(  # type: ignore
            "GET",
            "v1/payment-method/merchant/available",
            return_raw=True,
            params=params,
            success_status=(http.HTTPStatus.OK,),
        )

        if isinstance(result, responses.ErrorResult):
            return result

        body_data = result.get_json() or {}

        if raw_dict:
            return body_data
        else:
            return [responses.payment_method.PaymentMethodType(**mt) for mt in body_data]  # type: ignore

    @sync_or_async()
    async def create_transaction(
        self,
        pricing: dict[str, dict[str, str | float]],
        provider_type: str | None = None,
        provider_method: str | None = None,
        is_partner_fee: bool = False,
    ) -> responses.transaction.CreatedTransaction | responses.ErrorResult:
        """create_transaction.

        Args:
            pricing (dict[str, dict[str, str | float]]): pricing
            provider_type (str | None): provider_type
            provider_method (str | None): provider_method
            is_partner_fee (bool): is_partner_fee

        Returns:
            responses.transaction.CreatedTransaction | responses.ErrorResult:
        """
        data = {
            "isPartnerFee": is_partner_fee,
            "pricing": pricing,
        }

        if provider_type and provider_method:
            data["selectedProvider"] = {"type": provider_type, "method": provider_method}

        result: responses.RawResult | responses.ErrorResult = await self._request(  # type: ignore
            "POST",
            "v1/transaction/merchant",
            return_raw=True,
            data=data,
            success_status=(http.HTTPStatus.CREATED,),
        )

        if isinstance(result, responses.ErrorResult):
            return result

        body_data = result.get_json() or {}

        return responses.transaction.CreatedTransaction(**body_data)

    @sync_or_async()
    async def get_transaction(
        self,
        transaction_id: str,
    ) -> responses.transaction.GettedTransaction | responses.ErrorResult:
        """get_transaction.

        Args:
            transaction_id (str): transaction_id

        Returns:
            responses.transaction.GettedTransaction | responses.ErrorResult:
        """
        result: responses.RawResult | responses.ErrorResult = await self._request(  # type: ignore
            "GET",
            f"v1/transaction/merchant/{transaction_id}",
            return_raw=True,
            success_status=(http.HTTPStatus.OK,),
        )

        if isinstance(result, responses.ErrorResult):
            return result

        body_data = result.get_json() or {}

        return responses.transaction.GettedTransaction(**body_data)

    @sync_or_async()
    async def get_transaction_requisite(
        self,
        transaction_id: str,
    ) -> responses.transaction.GettedTransactionRequisite | responses.ErrorResult:
        """get_transaction_requisite.

        Args:
            transaction_id (str): transaction_id

        Returns:
            responses.transaction.GettedTransactionRequisite | responses.ErrorResult:
        """

        result: responses.RawResult | responses.ErrorResult = await self._request(  # type: ignore
            "GET",
            f"v1/transaction/merchant/requisite/{transaction_id}",
            return_raw=True,
            success_status=(http.HTTPStatus.OK,),
        )

        if isinstance(result, responses.ErrorResult):
            if result.status_code == 400 and (result.message or "").lower() == "bitconce order is closed":
                result.message = "Order is closed"

            return result

        body_data = result.get_json() or {}

        return responses.transaction.GettedTransactionRequisite(**body_data)

    @sync_or_async()
    async def claim_transaction_paid(
        self,
        transaction_id: str,
    ) -> responses.transaction.Transaction | responses.ErrorResult:
        """claim_transaction_paid.

        Args:
            transaction_id (str): transaction_id

        Returns:
            responses.transaction.Transaction | responses.ErrorResult:
        """

        result: responses.RawResult | responses.ErrorResult = await self._request(  # type: ignore
            "POST",
            f"v1/transaction/merchant/paid/{transaction_id}",
            return_raw=True,
            success_status=(http.HTTPStatus.CREATED,),
        )

        if isinstance(result, responses.ErrorResult):
            return result

        body_data = result.get_json() or {}

        return responses.transaction.Transaction(**body_data)

    @sync_or_async()
    async def claim_transaction_canceled(
        self,
        transaction_id: str,
    ) -> responses.transaction.Transaction | responses.ErrorResult:
        """claim_transaction_canceled.

        Args:
            transaction_id (str): transaction_id

        Returns:
            responses.transaction.Transaction | responses.ErrorResult:
        """

        result: responses.RawResult | responses.ErrorResult = await self._request(  # type: ignore
            "POST",
            f"v1/transaction/merchant/cancel/{transaction_id}",
            return_raw=True,
            success_status=(http.HTTPStatus.CREATED,),
        )

        if isinstance(result, responses.ErrorResult):
            return result

        body_data = result.get_json() or {}

        return responses.transaction.Transaction(**body_data)

    @sync_or_async()
    async def set_transaction_payment_method(
        self,
        transaction_id: str,
        provider_type: str,
        provider_method: str,
    ) -> responses.transaction.CreatedTransaction | responses.ErrorResult:
        """set_transaction_payment_method.

        Args:
            transaction_id (str): transaction_id
            provider_type (str): provider_type
            provider_method (str): provider_method

        Returns:
            responses.transaction.CreatedTransaction | responses.ErrorResult:
        """

        result: responses.RawResult | responses.ErrorResult = await self._request(  # type: ignore
            "POST",
            f"v1/transaction/merchant/provider/{transaction_id}",
            return_raw=True,
            data={"selectedProvider": {"method": provider_method, "type": provider_type}},
            success_status=(http.HTTPStatus.CREATED, http.HTTPStatus.OK),
        )

        if isinstance(result, responses.ErrorResult):
            return result

        body_data = result.get_json() or {}

        return responses.transaction.CreatedTransaction(**body_data)

    @sync_or_async()
    async def get_payment_method_rate(
        self,
        payment_method: str,
    ) -> responses.rate.PaymentMethodRate | responses.ErrorResult:
        """get_payment_method_rate.

        Args:
            payment_method (str): payment_method

        Returns:
            responses.rate.PaymentMethodRate | responses.ErrorResult:
        """

        result: responses.RawResult | responses.ErrorResult = await self._request(  # type: ignore
            "GET",
            f"v1/rate/",
            return_raw=True,
            params={"method": payment_method},
            success_status=(http.HTTPStatus.OK,),
        )

        if isinstance(result, responses.ErrorResult):
            return result

        body_data = result.get_json() or {}

        return responses.rate.PaymentMethodRate(**body_data)

    @sync_or_async()
    async def upload_payment_receipt(
        self,
        transaction_id: str,
        receipt_file: str | pathlib.Path | io.BufferedReader,
        amount: float | None = None,
    ) -> responses.StatusStub | responses.ErrorResult:
        """upload_payment_receipt.

        Args:
            transaction_id (str): transaction_id
            receipt_file (str | pathlib.Path | io.BufferedReader): receipt_file
            amount (float | None): amount

        Returns:
            responses.StatusStub | responses.ErrorResult:
        """
        form_data = {}

        if amount is not None:
            form_data["amount"] = amount

        if isinstance(receipt_file, str):
            receipt_file = pathlib.Path(receipt_file)

        if isinstance(receipt_file, pathlib.Path) and (not receipt_file.exists() or not receipt_file.is_file()):
            raise FileNotFoundError(f"Receipt file by path {receipt_file} not found!")

        elif isinstance(receipt_file, pathlib.Path):
            receipt_file = receipt_file.open(mode="rb")

        files = {"file": receipt_file}

        result: responses.RawResult | responses.ErrorResult = await self._request(  # type: ignore
            "POST",
            f"v1/transaction/merchant/receipt/{transaction_id}",
            return_raw=True,
            form=form_data,
            files=files,
            success_status=(http.HTTPStatus.OK, http.HTTPStatus.CREATED),
        )

        if isinstance(result, responses.ErrorResult):
            return result

        body_data = result.get_json() or {}

        return responses.StatusStub(**body_data)
