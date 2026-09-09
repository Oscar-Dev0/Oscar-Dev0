from datetime import date
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from update_discord import USER_ID, avatar_url, is_due, render_avatar, update


class DiscordTests(unittest.TestCase):
    def test_ten_days_across_month_and_year(self):
        for last, before, due in [("2026-09-25", date(2026, 10, 4), date(2026, 10, 5)),
                                  ("2026-12-25", date(2027, 1, 3), date(2027, 1, 4))]:
            self.assertFalse(is_due({"last_success": last}, before))
            self.assertTrue(is_due({"last_success": last}, due))
        self.assertTrue(is_due({}, date(2026, 9, 9)))

    def test_default_avatar_and_wrong_user(self):
        payload = {"user": {"id": USER_ID}, "avatar": None,
                   "defaultAvatar": "https://cdn.discordapp.com/embed/avatars/4.png"}
        self.assertEqual(avatar_url(payload), payload["defaultAvatar"])
        payload["user"]["id"] = "wrong"
        with self.assertRaises(ValueError):
            avatar_url(payload)

    def test_reject_non_discord_url(self):
        with self.assertRaises(ValueError):
            avatar_url({"user": {"id": USER_ID}, "defaultAvatar": "https://example.com/x.png"})

    def test_invalid_image_leaves_files_unchanged(self):
        with tempfile.TemporaryDirectory() as tmp:
            card, state = Path(tmp) / "card.svg", Path(tmp) / "state.json"
            card.write_text("<!-- AVATAR:START -->OD<!-- AVATAR:END -->")
            old = card.read_bytes()
            payload = json.dumps({"user": {"id": USER_ID},
                                  "defaultAvatar": "https://cdn.discordapp.com/embed/avatars/4.png"}).encode()
            with patch("update_discord.download", side_effect=[payload, b"error page"]):
                with self.assertRaises(ValueError):
                    update(date(2026, 9, 9), card, state)
            self.assertEqual(card.read_bytes(), old)
            self.assertFalse(state.exists())

    def test_skip_does_not_call_api(self):
        with tempfile.TemporaryDirectory() as tmp:
            state = Path(tmp) / "state.json"
            state.write_text('{"last_success":"2026-09-09"}')
            with patch("update_discord.download") as fetch:
                self.assertFalse(update(date(2026, 9, 18), Path(tmp) / "card.svg", state))
                fetch.assert_not_called()

    def test_embed_preserves_surrounding_design(self):
        card = '<svg><!-- AVATAR:START -->OD<!-- AVATAR:END --></svg>'
        result = render_avatar(card, b"\x89PNG\r\n\x1a\nexample")
        self.assertTrue(result.startswith('<svg><!-- AVATAR:START -->'))
        self.assertTrue(result.endswith('<!-- AVATAR:END --></svg>'))
        self.assertIn('data:image/png;base64,', result)


if __name__ == "__main__":
    unittest.main()
