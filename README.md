# Merchant001 SDK

# Install

## Client-only

### For PIP

```bash
pip3 install merchant001_sdk
```

### For PDM

```bash
pdm add merchant001_sdk
```

## With CLI

### For PIP

```bash
pip3 install merchant001_sdk[cli]
```

### For PDM

```bash
pdm add merchant001_sdk[cli]
```

# Use

## Client

### Sync

```python3
from merchant001_sdk.client import Client


with Client(token=...) as client:
    # comming soon...

```

### Async

```python3
from merchant001_sdk.client import Client


async def main(token: str) -> None:
    async with Client(token=token) as client:
        # comming soon...

```

## Methods

In this section I use async-only, but you can use sync/async (as in previous 2-level section).

### Merchant Healthcheck

```python3
from merchant001_sdk.client import Client


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
