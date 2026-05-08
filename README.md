# ESPX Python Client

Typed Python wrapper for the ESPX server.

## What it covers

- Certificate template discovery and generation
- Battle royale leaderboard template discovery and generation
- Custom exceptions for auth, validation, transport, and server errors
- Typed dataclasses for payloads and responses

## Install

```bash
pip install -e ./python
```

## Quick example

```python
from espx import ESPXClient
from espx.models import CertificateData

client = ESPXClient(
    base_url="https://api.espx.tech",
    access_token="your-access-token",
)

certificate_url = client.certificates.generate_url(
    CertificateData(
        organizer="LiFe Esports",
        eventname="SUMMER CUP",
        date="04/04/2026",
        certificateno="123456789",
        name="Hydra sfx Esports",
        rank=1,
    ),
    template_id="premium_blackyellow",
)

print(certificate_url)
```

## Design notes

The current server returns a few shapes inconsistently:

- `POST /certificate/generate` returns a plain string URL or `null`
- `POST /leaderboard/br/generate` returns `{ "url": ... }`
- `GET /leaderboard/br/templates` returns `{ "templates": [...] }` or a bare list when filters are used

This client normalizes those responses into predictable Python values.
