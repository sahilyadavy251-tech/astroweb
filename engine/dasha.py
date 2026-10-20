"""Vimshottari Dasha system (Maha / Antar / Pratyantar / Sookshma / Prana)."""
from __future__ import annotations

from datetime import datetime, timedelta

from . import constants as C

YEAR_DAYS = C.YEAR_DAYS  # 365.2425

LEVEL_NAMES = ["Mahadasha", "Antardasha", "Pratyantardasha", "Sookshma", "Prana"]
LEVEL_NAMES_HI = ["महादशा", "अन्तर्दशा", "प्रत्यन्तर्दशा", "सूक्ष्मदशा", "प्राणदशा"]


def _add_years(dt: datetime, years: float) -> datetime:
    return dt + timedelta(days=years * YEAR_DAYS)


def _sequence_from(lord: str):
    i = C.VIMSHOTTARI_ORDER.index(lord)
    return [C.VIMSHOTTARI_ORDER[(i + k) % 9] for k in range(9)]


def _sub_periods(start: datetime, total_years: float, lord: str, depth: int,
                 max_depth: int, out: list):
    """Recursively build sub-periods.  Appends nodes at each level."""
    seq = _sequence_from(lord)
    t = start
    for sub_lord in seq:
        dur = total_years * C.VIMSHOTTARI_YEARS[sub_lord] / 120.0
        end = _add_years(t, dur)
        node = {
            "lord": sub_lord,
            "start": t.isoformat(),
            "end": end.isoformat(),
            "years": round(dur, 6),
        }
        if depth < max_depth:
            node["sub"] = []
            _sub_periods(t, dur, sub_lord, depth + 1, max_depth, node["sub"])
        out.append(node)
        t = end


def vimshottari(moon_lon: float, birth: datetime, max_depth: int = 3):
    """Build the Vimshottari dasha tree.

    ``max_depth`` 1 = only Mahadashas, 2 = + Antardashas, 3 = + Pratyantardashas,
    up to 5 levels.
    """
    span = 360.0 / 27.0
    nak = int((moon_lon % 360) / span) % 27
    frac = ((moon_lon % 360) - nak * span) / span
    lord = C.NAKSHATRA_LORDS[nak]
    balance = (1.0 - frac) * C.VIMSHOTTARI_YEARS[lord]

    mahadashas = []
    t = birth
    seq = _sequence_from(lord)
    first = True
    for md_lord in seq:
        if first:
            dur = balance
            first = False
        else:
            dur = float(C.VIMSHOTTARI_YEARS[md_lord])
        end = _add_years(t, dur)
        node = {
            "lord": md_lord,
            "start": t.isoformat(),
            "end": end.isoformat(),
            "years": round(dur, 6),
        }
        if max_depth > 1:
            node["sub"] = []
            _sub_periods(t, dur, md_lord, 2, max_depth, node["sub"])
        mahadashas.append(node)
        t = end

    # one full 120-year cycle is built; extend once more for completeness
    return {
        "moon_nakshatra": C.NAKSHATRAS_EN[nak],
        "moon_nakshatra_hi": C.NAKSHATRAS_HI[nak],
        "starting_lord": lord,
        "balance_years_at_birth": round(balance, 6),
        "mahadashas": mahadashas,
    }


def current_chain(tree: dict, when: datetime) -> list:
    """Return the running Maha/Antar/... chain at ``when`` (ISO dicts)."""
    chain = []
    nodes = tree["mahadashas"]
    while nodes:
        found = None
        for n in nodes:
            if datetime.fromisoformat(n["start"]) <= when < datetime.fromisoformat(n["end"]):
                found = n
                break
        if not found:
            break
        chain.append({"level": LEVEL_NAMES[len(chain)] if len(chain) < 5 else "Prana",
                      "lord": found["lord"],
                      "start": found["start"], "end": found["end"]})
        nodes = found.get("sub", [])
    return chain
