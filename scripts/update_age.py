"""Actualiza la edad del perfil usando la fecha local de Costa Rica."""
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
import re
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

BIRTH_DATE = date(2004, 1, 5)
README = Path(__file__).resolve().parents[1] / "README.md"
PATTERN = r"(<!-- AGE:START -->)\d+(<!-- AGE:END -->)"


def costa_rica_today() -> date:
    try:
        local_zone = ZoneInfo("America/Costa_Rica")
    except ZoneInfoNotFoundError:
        # Costa Rica usa UTC-6 sin horario de verano; soporte para Windows.
        local_zone = timezone(timedelta(hours=-6))
    return datetime.now(local_zone).date()


def age_on(today: date) -> int:
    if today < BIRTH_DATE:
        raise ValueError("La fecha no puede ser anterior al nacimiento")
    return today.year - BIRTH_DATE.year - (
        (today.month, today.day) < (BIRTH_DATE.month, BIRTH_DATE.day)
    )


def update_content(content: str, today: date) -> str:
    if len(re.findall(PATTERN, content)) != 1:
        raise ValueError("El README debe tener exactamente un bloque AGE válido")
    return re.sub(PATTERN, lambda m: f"{m[1]}{age_on(today)}{m[2]}", content)


if __name__ == "__main__":
    original = README.read_text(encoding="utf-8")
    updated = update_content(original, costa_rica_today())
    if updated != original:
        README.write_text(updated, encoding="utf-8", newline="\n")
        print("Edad actualizada")
    else:
        print("La edad ya está al día")
