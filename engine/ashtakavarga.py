"""Ashtakavarga -- Bhinna (BAV), Sarva (SAV), and the two shodhanas."""
from __future__ import annotations

from . import constants as C

SEVEN = ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn"]
CONTRIBUTORS = ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn", "Ascendant"]

# known totals (for validation)
EXPECTED_TOTAL = {"Sun": 48, "Moon": 49, "Mars": 39, "Mercury": 54,
                  "Jupiter": 56, "Venus": 52, "Saturn": 39}

TRIKONA = [(0, 4, 8), (1, 5, 9), (2, 6, 10), (3, 7, 11)]
# sign pairs sharing a lord (Sun and Moon have single signs)
EKADHIPATYA_PAIRS = [(0, 7), (1, 6), (2, 5), (8, 11), (9, 10)]


def _sign(lon):
    return int((lon % 360) // 30)


def bav(planet: str, sign_of: dict) -> list:
    arr = [0] * 12
    table = C.ASHTAKAVARGA[planet]
    for contrib in CONTRIBUTORS:
        csign = sign_of[contrib]
        for h in table[contrib]:
            arr[(csign + h - 1) % 12] += 1
    return arr


def trikona_shodhana(arr: list) -> list:
    a = arr[:]
    for tri in TRIKONA:
        m = min(a[i] for i in tri)
        if m > 0:
            for i in tri:
                a[i] -= m
    return a


def ekadhipatya_shodhana(arr: list, sign_of: dict) -> list:
    a = arr[:]
    occ_signs = set()
    for p in SEVEN:
        occ_signs.add(sign_of[p])
    for s1, s2 in EKADHIPATYA_PAIRS:
        o1, o2 = s1 in occ_signs, s2 in occ_signs
        if o1 and o2:
            continue
        if not o1 and not o2:
            m = min(a[s1], a[s2])
            a[s1] = a[s2] = m
        elif o1 and not o2:
            if a[s2] > a[s1]:
                a[s2] = a[s1]
        else:
            if a[s1] > a[s2]:
                a[s1] = a[s2]
    return a


def compute(pos_sid: dict, asc_sid: float) -> dict:
    sign_of = {p: _sign(pos_sid[p]) for p in SEVEN}
    sign_of["Ascendant"] = _sign(asc_sid)
    result = {}
    sav = [0] * 12
    for p in SEVEN:
        base = bav(p, sign_of)
        tri = trikona_shodhana(base)
        red = ekadhipatya_shodhana(tri, sign_of)
        result[p] = {
            "bav": base,
            "total": sum(base),
            "expected_total": EXPECTED_TOTAL[p],
            "after_trikona": tri,
            "after_shodhana": red,
        }
        for i in range(12):
            sav[i] += base[i]
    result["SAV"] = {"bav": sav, "total": sum(sav)}
    return result
