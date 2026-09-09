"""Descarga el avatar público cada diez días y lo integra en el SVG local."""
import base64
import argparse
from html import escape
from datetime import date
import json
from pathlib import Path
import re
import urllib.request
from urllib.parse import urlparse

from update_age import costa_rica_today

ROOT = Path(__file__).resolve().parents[1]
CARD = ROOT / "assets/svg/discord-profile.svg"
STATE = ROOT / "assets/discord-avatar.json"
USER_ID = "518251720128856084"
API = f"https://www.vibebot.gg/api/tools/avatar-lookup?id={USER_ID}"
AVATAR_BLOCK = r"<!-- AVATAR:START -->.*?<!-- AVATAR:END -->"


def is_due(state: dict, today: date) -> bool:
    last = state.get("last_success")
    return not last or (today - date.fromisoformat(last)).days >= 10


def download(url: str, limit: int) -> bytes:
    request = urllib.request.Request(url, headers={"User-Agent": "Oscar-Dev0-profile/1.0"})
    with urllib.request.urlopen(request, timeout=30) as response:
        data = response.read(limit + 1)
    if len(data) > limit:
        raise ValueError("La respuesta supera el tamaño permitido")
    return data


def avatar_url(payload: dict) -> str:
    if payload["user"]["id"] != USER_ID:
        raise ValueError("La API devolvió otro usuario")
    url = (payload.get("avatar") or {}).get("png", {}).get("256")
    url = url or payload["defaultAvatar"]
    parsed = urlparse(url)
    if parsed.scheme != "https" or parsed.netloc != "cdn.discordapp.com":
        raise ValueError("El avatar debe proceder del CDN de Discord")
    if not parsed.path.startswith((f"/avatars/{USER_ID}/", "/embed/avatars/")):
        raise ValueError("Ruta de avatar inesperada")
    return url


def render_avatar(card: str, png: bytes) -> str:
    if not png.startswith(b"\x89PNG\r\n\x1a\n"):
        raise ValueError("La descarga no es una imagen PNG")
    if len(re.findall(AVATAR_BLOCK, card, flags=re.S)) != 1:
        raise ValueError("Se requiere exactamente un bloque AVATAR")
    encoded = base64.b64encode(png).decode("ascii")
    block = ('<!-- AVATAR:START -->\n'
             '  <image x="33" y="77" width="100" height="100" '
             'clip-path="url(#avatar-clip)" preserveAspectRatio="xMidYMid slice" '
             f'href="data:image/png;base64,{encoded}"/>\n'
             '  <!-- AVATAR:END -->')
    return re.sub(AVATAR_BLOCK, lambda _: block, card, flags=re.S)


def replace_block(card: str, name: str, content: str) -> str:
    pattern = rf"<!-- {name}:START -->.*?<!-- {name}:END -->"
    if len(re.findall(pattern, card, flags=re.S)) != 1:
        raise ValueError(f"Se requiere exactamente un bloque {name}")
    return re.sub(pattern, lambda _: f"<!-- {name}:START -->{content}<!-- {name}:END -->", card, flags=re.S)


def banner_url(payload: dict) -> str | None:
    banner = payload['user'].get('banner')
    if not banner:
        return None
    if not isinstance(banner, str) or not re.fullmatch(r'(?:a_)?[a-f0-9]{32}', banner):
        raise ValueError('Hash de banner inválido')
    return f'https://cdn.discordapp.com/banners/{USER_ID}/{banner}.png?size=1024'


def render_profile(card: str, payload: dict, banner: bytes | None) -> str:
    user = payload['user']
    if user['id'] != USER_ID:
        raise ValueError('Usuario incorrecto')
    username = user['username']
    name = user.get('global_name') or username
    if not isinstance(name, str) or not isinstance(username, str):
        raise ValueError('Nombre de usuario inválido')
    discriminator = user.get('discriminator', '0')
    handle = username + (f'#{discriminator}' if discriminator not in ('0', None, '') else '')
    def label(text, y, size, color, bold=False):
        # Tamaño adaptable y límite de longitud visual para nombres extensos.
        size = min(size, 550 / max(len(text), 1) / .65)
        return (f'<text x="30" y="{y}" fill="{color}" font-size="{size:.1f}" '
                f'font-weight="{"bold" if bold else "normal"}">{escape(text)}</text>')
    card = replace_block(card, 'NAME', label(name, 222, 34, '#f5f3ff', True))
    card = replace_block(card, 'USERNAME', label(handle, 250, 17, '#c4b5fd'))
    card = replace_block(card, 'PROFILE_TITLE', escape(f'{name} en Discord · {handle}'))
    backdrop = ''
    accent = user.get('accent_color')
    if isinstance(accent, int) and not isinstance(accent, bool) and 0 <= accent <= 0xFFFFFF:
        backdrop = f'<rect width="640" height="145" fill="#{accent:06x}" opacity=".45"/>'
    if banner is not None:
        if not banner.startswith(b'\x89PNG\r\n\x1a\n'):
            raise ValueError('El banner no es PNG')
        encoded = base64.b64encode(banner).decode('ascii')
        backdrop = (f'<image width="640" height="145" preserveAspectRatio="xMidYMid slice" '
                    f'href="data:image/png;base64,{encoded}"/>'
                    '<rect width="640" height="145" fill="#100d27" opacity=".3"/>')
    return replace_block(card, 'BANNER', backdrop)


def update(today: date, card_path: Path = CARD, state_path: Path = STATE, force: bool = False) -> bool:
    state = json.loads(state_path.read_text(encoding="utf-8")) if state_path.exists() else {}
    if not force and not is_due(state, today):
        print("Avatar al día: todavía no han transcurrido 10 días")
        return False
    payload = json.loads(download(API, 100_000))
    url = avatar_url(payload)
    png = download(url, 2_000_000)
    original = card_path.read_text(encoding="utf-8")
    updated = render_avatar(original, png)
    banner_link = banner_url(payload)
    banner = download(banner_link, 5_000_000) if banner_link else None
    updated = render_profile(updated, payload, banner)
    # No se escribe nada hasta validar ambas respuestas y preparar el SVG.
    if updated != original:
        card_path.write_text(updated, encoding="utf-8", newline="\n")
    state_path.write_text(json.dumps({"last_success": today.isoformat(),
                                     "user_id": USER_ID, "avatar_url": url,
                                     "banner_url": banner_link,
                                     "username": payload['user']['username'],
                                     "global_name": payload['user'].get('global_name')},
                                    indent=2) + "\n", encoding="utf-8")
    print("Avatar consultado y tarjeta actualizada")
    return True


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--force', action='store_true', help='Actualizar sin esperar diez días')
    update(costa_rica_today(), force=parser.parse_args().force)
