"""Shadbala -- the six-fold planetary strength (in virupas / shashtiamsas).

1 rupa = 60 virupas.  Implemented components:
  Sthana (positional), Dig (directional), Kala (temporal),
  Cheshta (motional), Naisargika (natural), Drik (aspectual).

Temporal sub-parts: Nathonnatha, Paksha, Tribhaga, Varsha, Masa, Dina, Hora,
Ayana.  (Yuddha bala is not applied.)
"""
from __future__ import annotations

import math
from datetime import datetime

from . import constants as C
from . import divisional as DV

SEVEN = ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn"]

# deep debilitation points (degrees)
DEB_POINT = {"Sun": 190, "Moon": 213, "Mars": 118, "Mercury": 345,
             "Jupiter": 275, "Venus": 177, "Saturn": 20}

# naisargika bala (virupas)
NAISARGIKA = {"Sun": 60.0, "Moon": 51.43, "Venus": 42.86, "Jupiter": 34.29,
              "Mercury": 25.71, "Mars": 17.14, "Saturn": 8.57}

# approximate maximum *geocentric* direct speed (deg/day), used as the
# upper anchor of cheshta bala (retrograde -> 60, fastest direct -> 0)
MAX_SPEED = {"Mars": 0.80, "Mercury": 2.21, "Jupiter": 0.24,
             "Venus": 1.35, "Saturn": 0.13}

SAPTA_VARGAS = [1, 2, 3, 7, 9, 12, 30]  # D1,D2,D3,D7,D9,D12,D30

HORA_SEQ = ["Sun", "Venus", "Mercury", "Moon", "Saturn", "Jupiter", "Mars"]


def _norm(x):
    return x % 360.0


def _angdist(a, b):
    d = abs((a - b) % 360.0)
    return min(d, 360.0 - d)


def _sign(lon):
    return int(_norm(lon) // 30)


def _lis(lon):
    return _norm(lon) % 30.0


# ---------------------------------------------------------------------------
# relationships
# ---------------------------------------------------------------------------
def _natural(a, b):
    f = C.FRIENDSHIP.get(a, {})
    if b in f.get("friends", []):
        return "friend"
    if b in f.get("enemies", []):
        return "enemy"
    return "neutral"


def _temporal(a, b, pos):
    ha = ((_sign(pos[b]) - _sign(pos[a])) % 12) + 1
    return "friend" if ha in (2, 3, 4, 10, 11, 12) else "enemy"


def _compound(a, b, pos):
    nat, tmp = _natural(a, b), _temporal(a, b, pos)
    if nat == "friend":
        return "great_friend" if tmp == "friend" else "neutral"
    if nat == "enemy":
        return "neutral" if tmp == "friend" else "great_enemy"
    return "friend" if tmp == "friend" else "enemy"


_REL_VALUE = {"great_friend": 22.5, "friend": 15.0, "neutral": 7.5,
              "enemy": 3.75, "great_enemy": 1.875}


def _varga_rel_value(planet, lon, varga, pos):
    sign = DV.varga_sign(lon, varga)
    if planet in C.OWN_SIGNS and sign in C.OWN_SIGNS[planet]:
        if varga == 1:
            mt = C.MOOLATRIKONA.get(planet)
            if mt and sign == mt[0] and mt[1] <= _lis(lon) <= mt[2]:
                return 45.0
        return 30.0
    lord = C.SIGN_LORDS[sign]
    if lord == planet:
        return 30.0
    if lord in ("Rahu", "Ketu"):
        return 7.5
    return _REL_VALUE[_compound(planet, lord, pos)]


# ---------------------------------------------------------------------------
# sthana bala
# ---------------------------------------------------------------------------
def _uchcha_bala(planet, lon):
    return _angdist(lon, DEB_POINT[planet]) / 3.0


def _saptavargaja_bala(planet, lon, pos):
    return sum(_varga_rel_value(planet, lon, v, pos) for v in SAPTA_VARGAS)


def _ojhayugma_bala(planet, lon):
    odd = _sign(lon) % 2 == 0
    nav = DV.varga_sign(lon, 9)
    odd_nav = nav % 2 == 0
    if planet in ("Sun", "Mars", "Jupiter"):
        return (15.0 if odd else 0) + (15.0 if odd_nav else 0)
    if planet in ("Moon", "Venus"):
        return (15.0 if not odd else 0) + (15.0 if not odd_nav else 0)
    return 30.0  # Mercury, Saturn (neuter)


def _kendra_bala(planet, lon, asc):
    h = ((_sign(lon) - _sign(asc)) % 12) + 1
    if h in (1, 4, 7, 10):
        return 60.0
    if h in (2, 5, 8, 11):
        return 30.0
    return 15.0


def _drekkana_bala(planet, lon):
    d = int(_lis(lon) // 10.0)
    if planet in ("Sun", "Mars", "Jupiter") and d == 0:
        return 15.0
    if planet in ("Moon", "Venus") and d == 1:
        return 15.0
    if planet in ("Mercury", "Saturn") and d == 2:
        return 15.0
    return 0.0


def sthana_bala(planet, lon, asc, pos):
    parts = {
        "uchcha": _uchcha_bala(planet, lon),
        "saptavargaja": _saptavargaja_bala(planet, lon, pos),
        "ojhayugma": _ojhayugma_bala(planet, lon),
        "kendra": _kendra_bala(planet, lon, asc),
        "drekkana": _drekkana_bala(planet, lon),
    }
    parts["total"] = sum(parts.values())
    return parts


# ---------------------------------------------------------------------------
# dig bala
# ---------------------------------------------------------------------------
_DIG_WEAK = {
    "Jupiter": 7, "Mercury": 7, "Sun": 4, "Mars": 4, "Saturn": 1,
    "Moon": 10, "Venus": 10,
}


def dig_bala(planet, lon, asc):
    weak_house = _DIG_WEAK[planet]
    weak_lon = _norm(asc + (weak_house - 1) * 90.0)
    return _angdist(lon, weak_lon) / 3.0


# ---------------------------------------------------------------------------
# kala bala
# ---------------------------------------------------------------------------
def _nathonnatha(planet, local_hour):
    hours_from_noon = abs(((local_hour - 12 + 12) % 24) - 12)
    nath = 60.0 * (1.0 - hours_from_noon / 12.0)
    if planet in ("Sun", "Jupiter", "Venus"):
        return nath
    if planet in ("Moon", "Mars", "Saturn"):
        return 60.0 - nath
    return 60.0


def _paksha_bala(planet, sun_lon, moon_lon):
    e = (moon_lon - sun_lon) % 360.0
    waxing = e < 180.0
    e = e if e <= 180.0 else 360.0 - e
    ben = e / 3.0
    mal = 60.0 - ben
    if planet == "Moon":
        return ben if waxing else mal
    if planet in ("Jupiter", "Venus", "Mercury"):
        return ben
    return mal


def _tribhaga_bala(planet, birth_local, sunrise, sunset):
    if sunrise and sunset:
        if sunrise <= birth_local < sunset:
            part = int((birth_local - sunrise).total_seconds() /
                       (sunset - sunrise).total_seconds() * 3)
            lords = ["Mercury", "Sun", "Saturn"]
        else:
            # night: from sunset to next sunrise
            nxt = sunset
            end = sunrise if sunrise > sunset else None
            # approximate night as 12h if we don't have next sunrise
            if end is None:
                end = sunset.replace(hour=23, minute=59)
            part = int((birth_local - sunset).total_seconds() /
                       max(1, (end - sunset).total_seconds()) * 3)
            lords = ["Moon", "Venus", "Mars"]
        part = max(0, min(2, part))
        return 60.0 if lords[part] == planet else 0.0
    # fallback: treat 06:00-18:00 as day
    h = birth_local.hour + birth_local.minute / 60.0
    if 6 <= h < 18:
        part = int((h - 6) / 4)
        lords = ["Mercury", "Sun", "Saturn"]
    else:
        hh = h if h >= 18 else h + 24
        part = int((hh - 18) / 4) % 3
        lords = ["Moon", "Venus", "Mars"]
    return 60.0 if lords[max(0, min(2, part))] == planet else 0.0


def _ayana_bala(planet, decl):
    north_strong = planet in ("Sun", "Mars", "Jupiter", "Venus", "Mercury")
    val = (24.0 + decl) / 48.0 * 60.0 if north_strong else (24.0 - decl) / 48.0 * 60.0
    return max(0.0, min(60.0, val))


def kala_bala(ctx, planet, sun_lon, moon_lon):
    parts = {}
    parts["nathonnatha"] = _nathonnatha(planet, ctx["local_hour"])
    parts["paksha"] = _paksha_bala(planet, sun_lon, moon_lon)
    parts["tribhaga"] = _tribhaga_bala(planet, ctx["birth_local"], ctx.get("sunrise"), ctx.get("sunset"))
    parts["varsha"] = 15.0 if ctx.get("varsha_lord") == planet else 0.0
    parts["masa"] = 30.0 if ctx.get("masa_lord") == planet else 0.0
    parts["dina"] = 45.0 if ctx.get("dina_lord") == planet else 0.0
    parts["hora"] = 60.0 if ctx.get("hora_lord") == planet else 0.0
    parts["ayana"] = _ayana_bala(planet, ctx["decl"].get(planet, 0.0))
    parts["total"] = sum(parts.values())
    return parts


def _hora_lord(birth_local, sunrise, dina_lord):
    idx = HORA_SEQ.index(dina_lord)
    if sunrise:
        hrs = (birth_local - sunrise).total_seconds() / 3600.0
        n = int(hrs // 1) if hrs >= 0 else int((hrs // 1) - 1)
    else:
        h = birth_local.hour + birth_local.minute / 60.0
        n = int((h - 6) // 1)
    return HORA_SEQ[(idx + n) % 7]


# ---------------------------------------------------------------------------
# cheshta bala
# ---------------------------------------------------------------------------
def cheshta_bala(planet, speed, ayana, paksha):
    if planet == "Sun":
        return ayana
    if planet == "Moon":
        return paksha
    if planet not in MAX_SPEED:
        return 0.0
    v = speed
    if v < 0:
        return 60.0
    vmax = MAX_SPEED[planet]
    return max(0.0, min(60.0, 60.0 * (1.0 - v / vmax)))


# ---------------------------------------------------------------------------
# drik bala
# ---------------------------------------------------------------------------
def _drishti(d):
    """Parashari sputa-drishti (0..60) for angular distance d (0..360)."""
    d = d % 360.0
    if d < 30 or d >= 330:
        return 0.0
    if d < 60:
        return (d - 30) / 2.0
    if d < 90:
        return (d - 60) + 15.0
    if d < 120:
        return 45.0 - (d - 90) / 2.0
    if d < 150:
        return 30.0 - (d - 120) / 2.0
    if d < 180:
        return 15.0 + (d - 150) * 1.5
    if d < 210:
        return 60.0 - (d - 180) / 2.0
    if d < 240:
        return 45.0 - (d - 210) / 2.0
    if d < 270:
        return 30.0 + (d - 240) / 2.0
    if d < 300:
        return 45.0 - (d - 270)
    if d < 330:
        return 15.0 - (d - 300) / 2.0
    return 0.0


def drik_bala(planet, pos):
    total = 0.0
    for other in SEVEN:
        if other == planet:
            continue
        d = (pos[planet] - pos[other]) % 360.0
        v = _drishti(d)
        hh = int(round((d % 360) / 30.0)) % 12 + 1
        if (other == "Saturn" and hh in (3, 10)) or \
           (other == "Mars" and hh in (4, 8)) or \
           (other == "Jupiter" and hh in (5, 9)) or hh == 7:
            v = 60.0
        benefic = other in ("Jupiter", "Venus", "Mercury") or \
            (other == "Moon" and ((pos["Moon"] - pos["Sun"]) % 360) < 180)
        total += v if benefic else -v
    return total / 4.0


# ---------------------------------------------------------------------------
# assemble
# ---------------------------------------------------------------------------
def compute(pos, asc, ctx):
    """Return {planet: {component: value, 'total_virupa':..., 'rupa':...}}."""
    sun_lon, moon_lon = pos["Sun"], pos["Moon"]
    required = {"Sun": 5.0, "Moon": 6.0, "Mars": 5.0, "Mercury": 7.0,
                "Jupiter": 6.5, "Venus": 5.5, "Saturn": 5.0}
    out = {}
    for p in SEVEN:
        lon = pos[p]
        st = sthana_bala(p, lon, asc, pos)
        dg = dig_bala(p, lon, asc)
        kb = kala_bala(ctx, p, sun_lon, moon_lon)
        ay = kb["ayana"]
        ch = cheshta_bala(p, ctx["speed"].get(p, 0.0), ay, kb["paksha"])
        na = NAISARGIKA[p]
        dr = drik_bala(p, pos)
        total = st["total"] + dg + kb["total"] + ch + na + dr
        out[p] = {
            "sthana": {k: round(v, 2) for k, v in st.items()},
            "dig": round(dg, 2),
            "kala": {k: round(v, 2) for k, v in kb.items()},
            "cheshta": round(ch, 2),
            "naisargika": round(na, 2),
            "drik": round(dr, 2),
            "total_virupa": round(total, 2),
            "rupa": round(total / 60.0, 3),
            "required_rupa": required[p],
            "sufficient": round(total / 60.0, 3) >= required[p],
        }
    return out
