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
    async with Client(token=...) as client:
        # comming soon...

```
