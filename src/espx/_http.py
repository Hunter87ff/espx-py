from __future__ import annotations

import asyncio
import json
from dataclasses import dataclass
from typing import Any
from urllib.parse import urljoin

import aiohttp

from .exceptions import (
    ESPXAuthenticationError,
    ESPXConfigurationError,
    ESPXHTTPError,
    ESPXResponseError,
    ESPXServerError,
    ESPXTemplateNotFoundError,
    ESPXTransportError,
    ESPXValidationError,
)
from .models import to_payload


@dataclass(slots=True)
class HttpTransport:
    base_url: str
    access_token: str | None = None
    timeout: float = 30.0
    user_agent: str = "espx-python/0.1.0"
    _session: aiohttp.ClientSession | None = None

    def __post_init__(self) -> None:
        if not self.base_url:
            raise ESPXConfigurationError("base_url is required.")
        normalized = self.base_url.rstrip("/") + "/"
        object.__setattr__(self, "base_url", normalized)

    async def _get_session(self) -> aiohttp.ClientSession:
        session = self._session
        if session is None or session.closed:
            session = aiohttp.ClientSession(
                timeout=aiohttp.ClientTimeout(total=self.timeout)
            )
            object.__setattr__(self, "_session", session)
        return session

    async def close(self) -> None:
        session = self._session
        if session is not None and not session.closed:
            await session.close()

    async def get_json(self, path: str, *, require_auth: bool = False) -> Any:
        body = await self._request("GET", path, require_auth=require_auth)
        return self._decode_json(body)

    async def post_json(
        self,
        path: str,
        *,
        json_body: Any,
        require_auth: bool = False,
    ) -> Any:
        body = await self._request(
            "POST",
            path,
            json_body=json_body,
            require_auth=require_auth,
        )
        return self._decode_json(body)

    async def post_bytes(
        self,
        path: str,
        *,
        json_body: Any,
        require_auth: bool = False,
    ) -> bytes:
        return await self._request(
            "POST",
            path,
            json_body=json_body,
            require_auth=require_auth,
        )

    def response_error(
        self,
        message: str,
        *,
        payload: object | None = None,
    ) -> ESPXResponseError:
        return ESPXResponseError(message, payload=payload)

    async def _request(
        self,
        method: str,
        path: str,
        *,
        json_body: Any | None = None,
        require_auth: bool = False,
    ) -> bytes:
        headers = {"User-Agent": self.user_agent}
        body: bytes | None = None

        if require_auth:
            if not self.access_token:
                raise ESPXConfigurationError(
                    "This endpoint requires access_token, but none was configured."
                )
            headers["Authorization"] = self.access_token

        if json_body is not None:
            headers["Content-Type"] = "application/json"
            body = json.dumps(to_payload(json_body)).encode("utf-8")

        url = urljoin(self.base_url, path.lstrip("/"))
        session = await self._get_session()

        try:
            async with session.request(method, url, data=body, headers=headers) as response:
                payload = await response.read()
                if response.status >= 400:
                    raise self._map_http_error(response.status, payload)
                return payload
        except aiohttp.ClientError as exc:
            raise ESPXTransportError(str(exc)) from exc
        except asyncio.TimeoutError as exc:
            raise ESPXTransportError("The request timed out.") from exc
        except OSError as exc:
            raise ESPXTransportError(str(exc)) from exc

    def _decode_json(self, body: bytes) -> Any:
        try:
            return json.loads(body.decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError) as exc:
            raise ESPXResponseError(
                "The server response was not valid JSON.",
                payload=body,
            ) from exc

    def _map_http_error(self, status_code: int, body: bytes) -> ESPXHTTPError:
        payload: Any = None
        message = "Request failed"

        if body:
            try:
                payload = json.loads(body.decode("utf-8"))
            except (UnicodeDecodeError, json.JSONDecodeError):
                payload = body.decode("utf-8", errors="replace")

        if isinstance(payload, dict):
            raw_message = payload.get("message") or payload.get("error")
            if raw_message:
                message = str(raw_message)
        elif isinstance(payload, str) and payload.strip():
            message = payload.strip()

        lower_message = message.lower()

        if status_code == 401:
            return ESPXAuthenticationError(status_code, message, payload=payload)
        if status_code == 404 and "template" in lower_message:
            return ESPXTemplateNotFoundError(status_code, message, payload=payload)
        if status_code == 400 and (
            "template not found" in lower_message or "template" in lower_message
        ):
            return ESPXTemplateNotFoundError(status_code, message, payload=payload)
        if status_code == 400:
            return ESPXValidationError(status_code, message, payload=payload)
        if status_code >= 500:
            return ESPXServerError(status_code, message, payload=payload)
        return ESPXHTTPError(status_code, message, payload=payload)
