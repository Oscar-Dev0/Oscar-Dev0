"""Descarga el avatar público cada diez días y lo integra en el SVG local."""
import base64
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


def update(today: date, card_path: Path = CARD, state_path: Path = STATE) -> bool:
    state = json.loads(state_path.read_text(encoding="utf-8")) if state_path.exists() else {}
    if not is_due(state, today):
        print("Avatar al día: todavía no han transcurrido 10 días")
        return False
    payload = json.loads(download(API, 100_000))
    url = avatar_url(payload)
    png = download(url, 2_000_000)
    original = card_path.read_text(encoding="utf-8")
    updated = render_avatar(original, png)
    # No se escribe nada hasta validar ambas respuestas y preparar el SVG.
    if updated != original:
        card_path.write_text(updated, encoding="utf-8", newline="\n")
    state_path.write_text(json.dumps({"last_success": today.isoformat(),
                                     "user_id": USER_ID, "avatar_url": url},
                                    indent=2) + "\n", encoding="utf-8")
    print("Avatar consultado y tarjeta actualizada")
    return True


if __name__ == "__main__":
    update(costa_rica_today())
