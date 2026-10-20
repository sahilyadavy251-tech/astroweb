"""Divisional charts (Vargas) D1 .. D60.

Varga rules follow the Parashara / Jagannatha-Hora conventions.  Where
traditions genuinely differ (D5, D8, D11, D60) the rule used here is stated
in the docstring of ``VARGA_INFO``.
"""
from __future__ import annotations

import math

VARGA_LIST = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 16, 20, 24, 27, 30, 40, 45, 60]

VARGA_INFO = {
    1:  ("Rasi", "राशि", "Body, overall life"),
    2:  ("Hora", "होरा", "Wealth (odd->Leo, even->Cancer first)"),
    3:  ("Drekkana", "द्रेक्काण", "Siblings, co-borns"),
    4:  ("Chaturthamsa", "चतुर्थांश", "Property, fortune"),
    5:  ("Panchamsa", "पंचमांश", "Fame, authority (odd Aries / even Libra)"),
    6:  ("Shashthamsa", "षष्ठांश", "Health (odd Aries / even Libra)"),
    7:  ("Saptamsa", "सप्तमांश", "Children, progeny"),
    8:  ("Ashtamsa", "अष्टमांश", "Longevity, troubles (odd Aries / even Libra)"),
    9:  ("Navamsa", "नवमांश", "Marriage, dharma, strength"),
    10: ("Dasamsa", "दशमांश", "Career, profession"),
    11: ("Rudramsa", "रुद्रांश", "Gains (odd Aries / even Libra)"),
    12: ("Dwadasamsa", "द्वादशांश", "Parents"),
    16: ("Shodasamsa", "षोडशांश", "Vehicles, comforts"),
    20: ("Vimsamsa", "विंशांश", "Spiritual life, upasana"),
    24: ("Siddhamsa", "चतुर्विंशांश", "Education, learning"),
    27: ("Bhamsa", "सप्तविंशांश", "Strengths, vitality"),
    30: ("Trimsamsa", "त्रिंशांश", "Evils, misfortune"),
    40: ("Khavedamsa", "खवेदांश", "Maternal legacy"),
    45: ("Akshavedamsa", "अक्षवेदांश", "Paternal legacy"),
    60: ("Shashtiamsa", "षष्ट्यंश", "Karma, overall effect (from sign itself)"),
}


def _odd(sign: int) -> bool:
    return sign % 2 == 0  # Aries(0) is an odd rasi


def _movable(sign: int) -> bool:
    return sign % 3 == 0


def _fixed(sign: int) -> bool:
    return sign % 3 == 1


def varga_sign(lon: float, n: int) -> int:
    """Return the sign index (0..11) of ``lon`` (sidereal, 0-360) in varga Dn."""
    lon = lon % 360.0
    sign = int(lon // 30)
    lis = lon - sign * 30.0
    odd = _odd(sign)

    if n == 1:
        return sign
    if n == 2:
        # odd: 1st half Leo, 2nd Cancer ; even: reversed
        half = 0 if lis < 15 else 1
        if odd:
            return 4 if half == 0 else 3
        return 3 if half == 0 else 4
    if n == 3:
        return (sign + int(lis // 10.0) * 4) % 12
    if n == 4:
        return (sign + int(lis // 7.5) * 3) % 12
    if n == 5:
        base = 0 if odd else 6
        return (base + int(lis // 6.0)) % 12
    if n == 6:
        base = 0 if odd else 6
        return (base + int(lis // 5.0)) % 12
    if n == 7:
        base = sign if odd else (sign + 6) % 12
        return (base + int(lis // (30.0 / 7))) % 12
    if n == 8:
        base = 0 if odd else 6
        return (base + int(lis // 3.75)) % 12
    if n == 9:
        return int(lon // (10.0 / 3.0)) % 12
    if n == 10:
        base = sign if odd else (sign + 8) % 12
        return (base + int(lis // 3.0)) % 12
    if n == 11:
        base = 0 if odd else 6
        return (base + int(lis // (30.0 / 11))) % 12
    if n == 12:
        return (sign + int(lis // 2.5)) % 12
    if n == 16:
        base = 0 if _movable(sign) else (4 if _fixed(sign) else 8)
        return (base + int(lis // 1.875)) % 12
    if n == 20:
        base = 0 if _movable(sign) else (8 if _fixed(sign) else 4)
        return (base + int(lis // 1.5)) % 12
    if n == 24:
        base = 4 if odd else 3
        return (base + int(lis // 1.25)) % 12
    if n == 27:
        return int(lon // (30.0 / 27)) % 12
    if n == 30:
        return _trimsamsa(sign, lis, odd)
    if n == 40:
        base = 0 if odd else 6
        return (base + int(lis // 0.75)) % 12
    if n == 45:
        base = 0 if _movable(sign) else (4 if _fixed(sign) else 8)
        return (base + int(lis // (30.0 / 45))) % 12
    if n == 60:
        return (sign + int(lis // 0.5)) % 12
    raise ValueError("unsupported varga D%d" % n)


def _trimsamsa(sign: int, lis: float, odd: bool) -> int:
    # odd rasi order (Aries, Aquarius, Sagittarius, Gemini, Libra)
    # even rasi order (Taurus, Virgo, Pisces, Capricorn, Scorpio)
    if odd:
        bounds = [(0, 5, 0), (5, 10, 10), (10, 18, 8), (18, 25, 2), (25, 30, 6)]
    else:
        bounds = [(0, 5, 1), (5, 12, 5), (12, 20, 11), (20, 25, 9), (25, 30, 7)]
    for lo, hi, sgn in bounds:
        if lis < hi or hi == 30:
            return sgn
    return bounds[-1][2]


def build_vargas(positions_sid: dict, asc_sid: float, vargas=VARGA_LIST) -> dict:
    """Return {varga_number: {planet: sign_index}} plus ascendant."""
    out = {}
    for n in vargas:
        row = {}
        for p, lon in positions_sid.items():
            row[p] = varga_sign(lon, n)
        row["Ascendant"] = varga_sign(asc_sid, n)
        out[n] = row
    return out
