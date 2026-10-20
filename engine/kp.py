"""KP (Krishnamurti Paddhati) system.

Placidus cusps, sign/star/sub/sub-sub lords of cusps and planets, the
four-fold house significators, and the Ruling Planets.
"""
from __future__ import annotations

from . import constants as C

SEVEN = ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn"]
NINE = SEVEN + ["Rahu", "Ketu"]
NAK_SPAN = 360.0 / 27.0


def _seq_from(lord):
    i = C.VIMSHOTTARI_ORDER.index(lord)
    return [C.VIMSHOTTARI_ORDER[(i + k) % 9] for k in range(9)]


def sign_lord(lon):
    return C.SIGN_LORDS[int((lon % 360) // 30)]


def star_lord(lon):
    nak = int((lon % 360) / NAK_SPAN) % 27
    return C.NAKSHATRA_LORDS[nak], nak


def sub_lords(lon):
    """Return dict with sign/star/sub/sub-sub lords and the nakshatra index."""
    lon = lon % 360
    nak = int(lon / NAK_SPAN) % 27
    sl = C.NAKSHATRA_LORDS[nak]
    start = nak * NAK_SPAN
    offset = lon - start
    sub = subsub = None
    t = 0.0
    for s in _seq_from(sl):
        w = NAK_SPAN * C.VIMSHOTTARI_YEARS[s] / 120.0
        if offset < t + w:
            sub = s
            o2 = offset - t
            t2 = 0.0
            for ss in _seq_from(sub):
                w2 = w * C.VIMSHOTTARI_YEARS[ss] / 120.0
                if o2 < t2 + w2:
                    subsub = ss
                    break
                t2 += w2
            break
        t += w
    return {
        "sign_lord": C.SIGN_LORDS[int(lon // 30)],
        "star_lord": sl,
        "sub_lord": sub,
        "sub_sub_lord": subsub,
        "nakshatra_index": nak,
        "nakshatra_en": C.NAKSHATRAS_EN[nak],
        "nakshatra_hi": C.NAKSHATRAS_HI[nak],
    }


def analyse_planet(lon):
    d = sub_lords(lon)
    d["sign_index"] = int((lon % 360) // 30)
    return d


def cusps_analysis(cusps):
    out = {}
    for i in range(1, 13):
        out[i] = analyse_planet(cusps[i])
    return out


def house_sign(cusps, h):
    return int((cusps[h] % 360) // 30)


def significators(pos, cusps, include_nodes=True):
    """Four-fold significators for each house (KP)."""
    planets = NINE if include_nodes else SEVEN
    pl_sign = {p: int((pos[p] % 360) // 30) for p in planets}
    pl_star = {p: star_lord(pos[p])[0] for p in planets}

    result = {}
    for h in range(1, 13):
        hsign = house_sign(cusps, h)
        owner = C.SIGN_LORDS[hsign]
        occupants = [p for p in planets if pl_sign[p] == hsign]
        # (a) planets in the stars of the occupants
        a = []
        for occ in occupants:
            occ_star = pl_star[occ]
            a += [p for p in planets if p != occ and pl_star[p] == occ_star]
        # (c) planets in the star of the owner
        c = [p for p in planets if pl_star[p] == owner]
        sig = {
            "house": h,
            "sign": C.SIGNS_EN[hsign],
            "sign_hi": C.SIGNS_HI[hsign],
            "owner": owner,
            "occupants": occupants,
            "star_of_occupants": sorted(set(a)),
            "star_of_owner": sorted(set(c)),
            "significators": sorted(set(occupants) | set(a) | set(c) | {owner}),
        }
        result[h] = sig
    return result


def ruling_planets(asc, pos, weekday_lord):
    la_sign = sign_lord(asc)
    la_star, _ = star_lord(asc)
    mo_sign = sign_lord(pos["Moon"])
    mo_star, _ = star_lord(pos["Moon"])
    rp = []
    for x in [weekday_lord, la_sign, la_star, mo_sign, mo_star]:
        if x and x not in rp:
            rp.append(x)
    return {
        "day_lord": weekday_lord,
        "lagna_sign_lord": la_sign,
        "lagna_star_lord": la_star,
        "moon_sign_lord": mo_sign,
        "moon_star_lord": mo_star,
        "ruling_planets": rp,
    }
