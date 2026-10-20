"""Jaimini system: Chara Karakas, Karakamsa, Arudha Padas, Chara Dasha."""
from __future__ import annotations

from . import constants as C
from . import divisional as DV

# Chara karakas are taken from the seven planets only (Rahu/Ketu excluded).
KARAKA_PLANETS = ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn"]


def _sign(lon):
    return int((lon % 360) // 30)


def _deg_in_sign(lon):
    return (lon % 360) % 30.0


def chara_karakas(pos):
    """Rank the eight karakas by descending degree in sign (Rahu reversed)."""
    degs = {p: _deg_in_sign(pos[p]) for p in KARAKA_PLANETS}
    order = sorted(KARAKA_PLANETS, key=lambda p: degs[p], reverse=True)
    out = {}
    for (code, name), p in zip(C.CHARA_KARAKAS, order):
        out[code] = {"planet": p, "degree": round(degs[p], 4), "full_name": name}
    return out


def karakamsa(pos, ak_planet):
    """Sign occupied by the Atmakaraka in the Navamsa (D9)."""
    nav = DV.varga_sign(pos[ak_planet], 9)
    return {"sign_index": nav, "sign_en": C.SIGNS_EN[nav], "sign_hi": C.SIGNS_HI[nav]}


def arudha_padas(asc_sid, pos):
    """Arudha pada (A1..A12) for each bhava."""
    asc_sign = _sign(asc_sid)
    sign_of = {p: _sign(pos[p]) for p in KARAKA_PLANETS}
    out = {}
    for h in range(1, 13):
        hsign = (asc_sign + h - 1) % 12
        lord = C.SIGN_LORDS[hsign]
        ls = sign_of.get(lord)
        if ls is None:
            out[h] = {"sign_index": hsign, "sign_en": C.SIGNS_EN[hsign],
                      "sign_hi": C.SIGNS_HI[hsign], "lord": lord}
            continue
        d = (ls - hsign) % 12
        a = (ls + d) % 12
        if a == hsign or a == (hsign + 6) % 12:
            a = (a + 9) % 12
        out[h] = {"sign_index": a, "sign_en": C.SIGNS_EN[a],
                  "sign_hi": C.SIGNS_HI[a], "lord": lord}
    return out


# ---------------------------------------------------------------------------
# Chara Dasha (Jaimini).  Convention used here:
#   * duration of a rasi = count from the rasi to its lord's rasi, counted
#     directly for odd-footed (savya) rasis {Ar,Ta,Ge,Li,Sc,Sg} and in reverse
#     for even-footed (apsavya) rasis.
#   * the sequence runs from the Lagna rasi, direct if the Lagna rasi is
#     odd-footed, otherwise in reverse.
# ---------------------------------------------------------------------------
SAVYA = {0, 1, 2, 6, 7, 8}


def _rasi_duration(sign, sign_of):
    lord = C.SIGN_LORDS[sign]
    ls = sign_of.get(lord)
    if ls is None:
        return 12
    if sign in SAVYA:
        count = (ls - sign) % 12
    else:
        count = (sign - ls) % 12
    return count if count != 0 else 12


def chara_dasha(asc_sid, pos, years=100):
    asc_sign = _sign(asc_sid)
    sign_of = {p: _sign(pos[p]) for p in KARAKA_PLANETS}
    direct = asc_sign in SAVYA
    seq = [(asc_sign + (i if direct else -i)) % 12 for i in range(12)]
    out = []
    total = 0
    for s in seq:
        dur = _rasi_duration(s, sign_of)
        if total + dur > years:
            dur = years - total
        out.append({"sign_index": s, "sign_en": C.SIGNS_EN[s], "sign_hi": C.SIGNS_HI[s],
                    "years": dur, "start_year": total})
        total += dur
        if total >= years:
            break
    return out
