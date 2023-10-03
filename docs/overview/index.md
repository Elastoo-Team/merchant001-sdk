# Use

## Client

### Sync

```python3
from merchant001_sdk import Client


with Client(token=...) as client:
    # comming soon...

```

### Async

```python3
from merchant001_sdk import Client


async def main(token: str) -> None:
    async with Client(token=token) as client:
        # comming soon...

```

## Methods

In this section I use async-only, but you can use sync/async (as in previous 2-level section).

### Merchant Healthcheck

```python3
from merchant001_sdk import Client


async def main(token: str) -> None:
    async with Client(token=token, endpoint="https://api.merchant001.io/") as client:
        result = await client.get_merchant_healthcheck()

    print(result)
```

On Success:

```python3
MerchantHealthcheck(success=True)
```

On Error (invalid token for example):

```python3
ErrorResult(status_code=401, message='Unavailable api token', error='Unauthorized')
```

### Payment Methods List

Params:

- raw_dict (boolean) - eq. to makeArray, default is false.
- method_names_only (boolean) - eq. to onlyMethod, default is false.
- amount (int; > 0) - eq. to amount, default is null (optional).

```python3
from merchant001_sdk import Client


async def main(token: str) -> None:
    async with Client(token=token, endpoint="https://api.merchant001.io/") as client:
        result = await client.get_payment_methods(raw_dict=True, method_names_only=False)

    print(result)
```

On Success:

```python3
[PaymentMethodType(type='GATE [RUB/USDT] CARD', methods=[{'type': 'GATE [RUB/USDT] CARD', 'method': 'tinkoff', 'imageUrl': None, 'name': 'Тинькофф'}, {'type': 'GATE [RUB/USDT] CARD', 'method': 'sberbank', 'imageUrl': None, 'name': 'Сбербанк'}])]  # raw_dict=False
```

```python3
[PaymentMethodType(type='GATE [RUB/USDT] CARD', methods=['tinkoff', 'sberbank'])]  # raw_dict=False, method_names_only=True
```

```python3
{'GATE [RUB/USDT] CARD': {'tinkoff': {'type': 'GATE [RUB/USDT] CARD', 'method': 'tinkoff', 'imageUrl': None, 'name': 'Тинькофф'}, 'sberbank': {'type': 'GATE [RUB/USDT] CARD', 'method': 'sberbank', 'imageUrl': None, 'name': 'Сбербанк'}}}  # raw_dict=True
```

On Error (invalid token for example):

```python3
ErrorResult(status_code=401, message='Unavailable api token', error='Unauthorized')
```

### Create Transaction

Params:

- pricing (mapping[str, mapping[str, str | float]]) - eq. to pricing.
- provider_type (str) - eq. to selectedProvider.type.
- provider_method (str) - eq. to selectedProvider.method.
- is_partner_fee (boolean) - eq. to amount, default is null (optional).

```python3
from merchant001_sdk import Client


async def main(token: str) -> None:
    async with Client(token=token, endpoint="https://api.merchant001.io/") as client:
        result = await client.create_transaction(
            pricing={"local": {"amount": 1, "currency": "RUB"}},
            provider_type="GATE [RUB/USDT] CARD",
            provider_method="SBERBANK",
            is_partner_fee=False,
        )

    print(result)
```

### Get Transaction

Params:

- transaction_id (str)

```python3
from merchant001_sdk import Client


async def main(token: str, transaction_id: str) -> None:
    async with Client(token=token, endpoint="https://api.merchant001.io/") as client:
        result = await client.get_transaction(transaction_id=transaction_id)

    print(result)
```

### Get Transaction Requisite

Params:

- transaction_id (str)

```python3
from merchant001_sdk import Client


async def main(token: str, transaction_id: str) -> None:
    async with Client(token=token, endpoint="https://api.merchant001.io/") as client:
        result = await client.get_transaction_requisite(transaction_id=transaction_id)

    print(result)
```

### Claim Transaction as PAID

Params:

- transaction_id (str)

```python3
from merchant001_sdk import Client


async def main(token: str, transaction_id: str) -> None:
    async with Client(token=token, endpoint="https://api.merchant001.io/") as client:
        result = await client.claim_transaction_paid(transaction_id=transaction_id)

    print(result)
```

### Claim Transaction as CANCELED

Params:

- transaction_id (str)

```python3
from merchant001_sdk import Client


async def main(token: str, transaction_id: str) -> None:
    async with Client(token=token, endpoint="https://api.merchant001.io/") as client:
        result = await client.claim_transaction_canceled(transaction_id=transaction_id)

    print(result)
```

### Set Transaction payment method

Params:

- transaction_id (str)
- provider_type (str)
- provider_method (str)

```python3
from merchant001_sdk import Client


async def main(
    token: str, transaction_id: str, provider_type: str, provider_method: str
) -> None:
    async with Client(token=token, endpoint="https://api.merchant001.io/") as client:
        result = await client.set_transaction_payment_method(
            transaction_id=transaction_id,
            provider_type=provider_type,
            provider_method=provider_method,
        )

    print(result)
```

### Get Payment Method Rate

Params:

- payment_method (str)

```python3
from merchant001_sdk import Client


async def main(token: str, transaction_id: str, payment_method: str) -> None:
    async with Client(token=token, endpoint="https://api.merchant001.io/") as client:
        result = await client.get_payment_method_rate(payment_method=payment_method)

    print(result)
```

On Success:

```python3
PaymentMethodRate(method='sberbank', rate=103.38)
```

### Upload payment receipt

Params:

- transaction_id (str)
- receipt_file (str) - filepath or opened file with mode "rb".
- amount (float; optional) - if you need to specify the amount.

```python3
from merchant001_sdk import Client


async def main(token: str, transaction_id: str, filepath: str) -> None:
    async with Client(token=token, endpoint="https://api.merchant001.io/") as client:
        result = await client.get_payment_method_rate(
            transaction_id=transaction_id, receipt_file=filepath
        )

    print(result)
```

On Success:

```python3
StatusStub(status=True)
```
