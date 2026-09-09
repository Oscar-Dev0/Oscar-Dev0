from datetime import date
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from update_discord import USER_ID, avatar_url, banner_url, is_due, render_avatar, render_profile, update


class DiscordTests(unittest.TestCase):
    def test_profile_rename_banner_removal_and_escaping(self):
        template = '<svg xmlns="http://www.w3.org/2000/svg">' + ''.join(
            f'<!-- {key}:START --><!-- {key}:END -->'
            for key in ('NAME', 'USERNAME', 'PROFILE_TITLE', 'BANNER')) + '</svg>'
        payload = {'user': {'id': USER_ID, 'username': 'new_user',
                            'global_name': 'Oscar <&> "Dev"', 'accent_color': 0}}
        result = render_profile(template, payload, b'\x89PNG\r\n\x1a\nexample')
        self.assertIn('data:image/png;base64,', result)
        self.assertIn('Oscar &lt;&amp;&gt; &quot;Dev&quot;', result)
        payload['user']['global_name'] = None
        result = render_profile(result, payload, None)
        self.assertNotIn('data:image/png', result)
        self.assertIn('#071120', result)
        self.assertIn('new_user', result)
        import xml.etree.ElementTree as ET
        ET.fromstring(result)

    def test_banner_hash_and_missing_banner(self):
        self.assertIsNone(banner_url({'user': {'banner': None}}))
        hashed = 'a_' + 'a' * 32
        self.assertEqual(banner_url({'user': {'banner': hashed}}),
                         f'https://cdn.discordapp.com/banners/{USER_ID}/{hashed}.png?size=1024')
        with self.assertRaises(ValueError):
            banner_url({'user': {'banner': '../bad'}})

    def test_broken_banner_preserves_card_and_state(self):
        with tempfile.TemporaryDirectory() as tmp:
            card, state = Path(tmp) / 'card.svg', Path(tmp) / 'state.json'
            original = '<!-- AVATAR:START -->OD<!-- AVATAR:END -->'
            card.write_text(original)
            state.write_text('{"last_success":"2026-01-01"}')
            payload = {'user': {'id': USER_ID, 'banner': 'a' * 32},
                       'defaultAvatar': 'https://cdn.discordapp.com/embed/avatars/4.png'}
            with patch('update_discord.download', side_effect=[json.dumps(payload).encode(),
                       b'\x89PNG\r\n\x1a\nexample', OSError('API unavailable')]):
                with self.assertRaises(OSError):
                    update(date(2026, 9, 9), card, state)
            self.assertEqual(card.read_text(), original)
            self.assertEqual(json.loads(state.read_text())['last_success'], '2026-01-01')

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
