from __future__ import annotations

import unittest

from espx.client import BattleRoyaleLeaderboardAPI, CertificateAPI
from espx.exceptions import ESPXResponseError
from espx.models import (
    BRLeaderboardPayload,
    CertificateData,
    CertificateSocial,
    LeaderboardRow,
    LeaderboardSocial,
    to_payload,
)


class StubTransport:
    def __init__(self, *, get_json_result=None, post_json_result=None, post_bytes_result=b""):
        self.get_json_result = get_json_result
        self.post_json_result = post_json_result
        self.post_bytes_result = post_bytes_result

    def get_json(self, path: str, *, require_auth: bool = False):
        return self.get_json_result

    def post_json(self, path: str, *, json_body, require_auth: bool = False):
        return self.post_json_result

    def post_bytes(self, path: str, *, json_body, require_auth: bool = False):
        return self.post_bytes_result

    def response_error(self, message: str, *, payload=None):
        return ESPXResponseError(message, payload=payload)


class PayloadTests(unittest.TestCase):
    def test_nested_dataclasses_drop_none_values(self) -> None:
        payload = CertificateData(
            organizer="Org",
            eventname="Cup",
            date="2026-04-04",
            certificateno="123",
            name="Winner",
            rank=1,
            social=CertificateSocial(twitter="@org"),
        )

        self.assertEqual(
            to_payload(payload),
            {
                "organizer": "Org",
                "eventname": "Cup",
                "date": "2026-04-04",
                "certificateno": "123",
                "name": "Winner",
                "rank": 1,
                "social": {"twitter": "@org"},
            },
        )


class CertificateApiTests(unittest.TestCase):
    def test_generate_url_accepts_plain_string_response(self) -> None:
        api = CertificateAPI(StubTransport(post_json_result="https://cdn.example/cert.png"))
        result = api.generate_url(
            CertificateData(
                organizer="Org",
                eventname="Cup",
                date="2026-04-04",
                certificateno="123",
                name="Winner",
                rank=1,
            )
        )
        self.assertEqual(result, "https://cdn.example/cert.png")

    def test_render_image_returns_bytes(self) -> None:
        api = CertificateAPI(StubTransport(post_bytes_result=b"png-data"))
        content = api.render_image(
            CertificateData(
                organizer="Org",
                eventname="Cup",
                date="2026-04-04",
                certificateno="123",
                name="Winner",
                rank=1,
            )
        )
        self.assertEqual(content, b"png-data")


class LeaderboardApiTests(unittest.TestCase):
    def test_list_templates_handles_wrapped_response(self) -> None:
        api = BattleRoyaleLeaderboardAPI(
            StubTransport(
                get_json_result={
                    "templates": [
                        {
                            "id": "minimal_dark",
                            "name": "Minimal - Dark",
                            "max_teams": 12,
                            "games": ["bgmi", "freefire"],
                        }
                    ]
                }
            )
        )

        templates = api.list_templates()
        self.assertEqual(len(templates), 1)
        self.assertEqual(templates[0].id, "minimal_dark")

    def test_generate_url_reads_object_response(self) -> None:
        api = BattleRoyaleLeaderboardAPI(
            StubTransport(post_json_result={"url": "https://cdn.example/board.png"})
        )
        result = api.generate_url(
            BRLeaderboardPayload(
                template="minimal_dark",
                teams=[LeaderboardRow(rank=1, name="Alpha")],
                organizer="Org",
                eventname="Cup",
                social=LeaderboardSocial(),
            )
        )
        self.assertEqual(result, "https://cdn.example/board.png")


if __name__ == "__main__":
    unittest.main()
