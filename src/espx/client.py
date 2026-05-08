from __future__ import annotations

from dataclasses import dataclass
from urllib.parse import urlencode

from ._http import HttpTransport
from .models import (
    CertificateData,
    CertificateTemplate,
    GeneratedAsset,
    LeaderboardTemplate,
    BRLeaderboardPayload,
)


@dataclass(slots=True)
class CertificateAPI:
    _transport: HttpTransport

    async def list_templates(self) -> list[CertificateTemplate]:
        data = await self._transport.get_json("/certificate/templates")
        if not isinstance(data, list):
            raise self._transport.response_error(
                "Expected a list of certificate templates.",
                payload=data,
            )
        return [CertificateTemplate.from_dict(item) for item in data]

    async def get_template(self, template_id: str) -> CertificateTemplate:
        data = await self._transport.get_json(
            f"/certificate/templates?{urlencode({'id': template_id})}"
        )
        if not isinstance(data, dict):
            raise self._transport.response_error(
                "Expected a certificate template object.",
                payload=data,
            )
        return CertificateTemplate.from_dict(data)

    async def generate(
        self,
        payload: CertificateData,
        *,
        template_id: str = "premium_blackyellow",
        raw: bool = False,
    ) -> GeneratedAsset:
        query = urlencode({"template": template_id, "raw": int(raw)})
        if raw:
            content = await self._transport.post_bytes(
                f"/certificate/generate?{query}",
                json_body=payload,
                require_auth=True,
            )
            return GeneratedAsset(content=content, content_type="image/png")

        data = await self._transport.post_json(
            f"/certificate/generate?{query}",
            json_body=payload,
            require_auth=True,
        )
        if data is not None and not isinstance(data, str):
            raise self._transport.response_error(
                "Expected the certificate endpoint to return a URL string or null.",
                payload=data,
            )
        return GeneratedAsset(url=data)

    async def generate_url(
        self,
        payload: CertificateData,
        *,
        template_id: str = "premium_blackyellow",
    ) -> str | None:
        asset = await self.generate(payload, template_id=template_id, raw=False)
        return asset.url

    async def render_image(
        self,
        payload: CertificateData,
        *,
        template_id: str = "premium_blackyellow",
    ) -> bytes:
        asset = await self.generate(payload, template_id=template_id, raw=True)
        return asset.require_content()


@dataclass(slots=True)
class BattleRoyaleLeaderboardAPI:
    _transport: HttpTransport

    async def list_templates(
        self,
        *,
        game: str | None = None,
        teams: int | None = None,
    ) -> list[LeaderboardTemplate]:
        params: dict[str, str | int] = {}
        if game is not None:
            params["game"] = game
        if teams is not None:
            params["teams"] = teams

        path = "/leaderboard/br/templates"
        if params:
            path = f"{path}?{urlencode(params)}"

        data = await self._transport.get_json(path, require_auth=True)
        raw_templates = data.get("templates", data) if isinstance(data, dict) else data
        if not isinstance(raw_templates, list):
            raise self._transport.response_error(
                "Expected a list of leaderboard templates.",
                payload=data,
            )
        return [LeaderboardTemplate.from_dict(item) for item in raw_templates]

    async def generate(
        self,
        payload: BRLeaderboardPayload,
        *,
        raw: bool = False,
        send_image: bool = False,
    ) -> GeneratedAsset:
        params = {"raw": int(raw)}
        if send_image:
            params["sendimg"] = 1
        query = urlencode(params)

        if raw or send_image:
            content = await self._transport.post_bytes(
                f"/leaderboard/br/generate?{query}",
                json_body=payload,
                require_auth=True,
            )
            return GeneratedAsset(content=content, content_type="image/png")

        data = await self._transport.post_json(
            f"/leaderboard/br/generate?{query}",
            json_body=payload,
            require_auth=True,
        )
        if not isinstance(data, dict):
            raise self._transport.response_error(
                "Expected the leaderboard endpoint to return an object.",
                payload=data,
            )
        url = data.get("url")
        if url is not None and not isinstance(url, str):
            raise self._transport.response_error(
                "Expected the leaderboard URL to be a string or null.",
                payload=data,
            )
        return GeneratedAsset(url=url)

    async def generate_url(self, payload: BRLeaderboardPayload) -> str | None:
        asset = await self.generate(payload)
        return asset.url

    async def render_image(self, payload: BRLeaderboardPayload) -> bytes:
        asset = await self.generate(payload, raw=True)
        return asset.require_content()


@dataclass(slots=True)
class LeaderboardAPI:
    br: BattleRoyaleLeaderboardAPI


class ESPXClient:
    def __init__(
        self,
        *,
        base_url: str,
        access_token: str | None = None,
        timeout: float = 30.0,
        user_agent: str = "espx-python/0.1.0",
    ) -> None:
        self._transport = HttpTransport(
            base_url=base_url,
            access_token=access_token,
            timeout=timeout,
            user_agent=user_agent,
        )
        self.certificates = CertificateAPI(self._transport)
        self.leaderboards = LeaderboardAPI(
            br=BattleRoyaleLeaderboardAPI(self._transport)
        )

    async def close(self) -> None:
        await self._transport.close()

    def __enter__(self) -> ESPXClient:
        raise TypeError("ESPXClient is async-only. Use 'async with ESPXClient(...)'.")

    def __exit__(self, exc_type, exc, tb) -> None:
        return None

    async def __aenter__(self) -> ESPXClient:
        return self

    async def __aexit__(self, exc_type, exc, tb) -> None:
        await self.close()
