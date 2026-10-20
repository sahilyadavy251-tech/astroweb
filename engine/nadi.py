"""Nadi system: Nadi Amsa (D150) and an annual Nadi progression.

The traditional palm-leaf Nadi (Nadi Jothidam) is a manuscript-lookup system
and is not derivable from a birth chart by computation alone.  What *is*
computable -- and what this module provides -- is the Nadi Amsa (D150, the
finest classical varga, 0.2 degrees per division) for each planet and the
Lagna, together with an annual Nadi progression (one division per year).
"""
from __future__ import annotations

from . import constants as C

NADI_DIV = 0.2  # degrees per Nadi division (30 / 150)
NINE = ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn", "Rahu", "Ketu"]


def nadi_amsa(lon):
    lon = lon % 360.0
    idx = int(lon / NADI_DIV) % 1800        # 0..1799 across the zodiac
    sign = idx % 12
    # position within the sign's 150 divisions
    within_sign = int((lon % 30.0) / NADI_DIV) + 1  # 1..150
    return {
        "nadi_index": idx,
        "sign_index": sign,
        "sign_en": C.SIGNS_EN[sign],
        "sign_hi": C.SIGNS_HI[sign],
        "nadi_within_sign": within_sign,
        "longitude": round(lon, 4),
    }


def compute(pos, asc):
    out = {p: nadi_amsa(pos[p]) for p in NINE}
    out["Ascendant"] = nadi_amsa(asc)
    return out


def progression(pos, asc, birth_year, target_year):
    """Annual Nadi progression: one Nadi division (0.2 deg) per year."""
    years = target_year - birth_year
    shift = years * NADI_DIV
    out = {}
    for p in NINE:
        out[p] = nadi_amsa(pos[p] + shift)
    out["Ascendant"] = nadi_amsa(asc + shift)
    out["years_elapsed"] = years
    return out
