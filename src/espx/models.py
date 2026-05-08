from __future__ import annotations

from dataclasses import dataclass, field, fields, is_dataclass
from typing import Any, Literal, TYPE_CHECKING
from .exceptions import ESPXResponseError

if TYPE_CHECKING:
    from .client import ESPXClient

CertificateTemplateId = Literal["premium_blackyellow"]
LeaderboardTemplateId = Literal[
    "primary1_bluewhite",
    "primary1_prime1",
    "primary1_redwhite",
    "minimal_solid",
    "minimal_dark",
    "minimal_light",
    "cyber_neon",
    "columns_bg1",
    "columns_dark",
    "columns_light",
    "horizontal_league1",
    "horizontal_blackyellow",
]
GameName = Literal["bgmi", "pubg", "freefire"]

KNOWN_CERTIFICATE_TEMPLATE_IDS: tuple[CertificateTemplateId, ...] = (
    "premium_blackyellow",
)
KNOWN_LEADERBOARD_TEMPLATE_IDS: tuple[LeaderboardTemplateId, ...] = (
    "primary1_bluewhite",
    "primary1_prime1",
    "primary1_redwhite",
    "minimal_solid",
    "minimal_dark",
    "minimal_light",
    "cyber_neon",
    "columns_bg1",
    "columns_dark",
    "columns_light",
    "horizontal_league1",
    "horizontal_blackyellow",
)


def _coerce_dict(data: Any, *, context: str) -> dict[str, Any]:
    if not isinstance(data, dict):
        raise ESPXResponseError(f"Expected {context} to be a JSON object.", payload=data)
    return data


def to_payload(value: Any) -> Any:
    if is_dataclass(value):
        payload: dict[str, Any] = {}
        for item in fields(value):
            raw_value = getattr(value, item.name)
            if raw_value is None:
                continue
            payload[item.name] = to_payload(raw_value)
        return payload
    if isinstance(value, list):
        return [to_payload(item) for item in value]
    if isinstance(value, tuple):
        return [to_payload(item) for item in value]
    return value


@dataclass(slots=True)
class CertificateSocial:
    twitter: str | None = None
    instagram: str | None = None
    facebook: str | None = None
    youtube: str | None = None


@dataclass(slots=True)
class CertificateData:
    organizer: str
    eventname: str
    date: str
    certificateno: str
    name: str
    rank: int
    orglogo: str | None = None
    signature: str | None = None
    social: CertificateSocial | None = None


@dataclass(slots=True)
class CertificateTemplate:
    id: str
    name: str
    premium: bool

    @classmethod
    def from_dict(cls, data: Any) -> CertificateTemplate:
        obj = _coerce_dict(data, context="certificate template")
        return cls(
            id=str(obj["id"]),
            name=str(obj["name"]),
            premium=bool(obj["premium"]),
        )
    

    @classmethod
    async def get_templates(cls, client: ESPXClient) -> list[CertificateTemplate]:
        response = await client._transport.get_json("/v1/certificates/templates")
        if not isinstance(response, list):
            raise ESPXResponseError(
                "Expected certificate templates response to be a list.",
                payload=response,
            )
        return [cls.from_dict(item) for item in response]


@dataclass(slots=True)
class LeaderboardRow:
    rank: str | int | None = None
    name: str | int | None = None
    matches: str | int | None = None
    wins: str | int | None = None
    pos_pts: str | int | None = None
    kill_pts: str | int | None = None
    total_pts: str | int | None = None
    logo: str | None = None
    image: str | None = None
    icon: str | None = None


@dataclass(slots=True)
class LeaderboardSocial:
    twitter: str | None = None
    instagram: str | None = None
    facebook: str | None = None
    youtube: str | None = None


@dataclass(slots=True)
class BRLeaderboardPayload:
    template: str
    teams: list[LeaderboardRow]
    organizer: str
    eventname: str
    social: LeaderboardSocial = field(default_factory=LeaderboardSocial)


@dataclass(slots=True)
class LeaderboardTemplate:
    id: str
    name: str
    max_teams: int
    games: list[str]
    logo: str | None = None
    support_team_logo: bool | None = None

    @classmethod
    def from_dict(cls, data: Any) -> LeaderboardTemplate:
        obj = _coerce_dict(data, context="leaderboard template")
        games = obj.get("games", [])
        if not isinstance(games, list):
            raise ESPXResponseError(
                "Expected leaderboard template games to be a list.",
                payload=data,
            )
        return cls(
            id=str(obj["id"]),
            name=str(obj["name"]),
            max_teams=int(obj["max_teams"]),
            games=[str(item) for item in games],
            logo=str(obj["logo"]) if obj.get("logo") is not None else None,
            support_team_logo=(
                bool(obj["support_team_logo"])
                if obj.get("support_team_logo") is not None
                else None
            ),
        )
    

    @classmethod
    async def get_templates(cls, client: ESPXClient) -> list[LeaderboardTemplate]:
        response = await client._transport.get_json("/v1/leaderboards/templates")
        if not isinstance(response, list):
            raise ESPXResponseError(
                "Expected leaderboard templates response to be a list.",
                payload=response,
            )
        return [cls.from_dict(item) for item in response]


@dataclass(slots=True)
class GeneratedAsset:
    url: str | None = None
    content: bytes | None = None
    content_type: str | None = None

    def require_url(self) -> str:
        if self.url is None:
            raise ESPXResponseError("Expected a generated asset URL but received none.")
        return self.url

    def require_content(self) -> bytes:
        if self.content is None:
            raise ESPXResponseError("Expected generated image bytes but received none.")
        return self.content
