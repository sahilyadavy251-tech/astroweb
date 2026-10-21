"""Assemble a complete chart from birth data."""
from __future__ import annotations

import math
from datetime import datetime, timedelta, timezone

from . import (constants as C, ephemeris as E, divisional as DV, dasha as DS,
               shadbala as SB, ashtakavarga as AK, yogas as YG, kp as KP,
               jaimini as JM, lalkitab as LK, nadi as ND, numerology as NU,
               tarot as TR)

SEVEN = ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn"]
NINE = SEVEN + ["Rahu", "Ketu"]


def _decl(lon, lat, eps):
    lam = math.radians(lon)
    bet = math.radians(lat)
    e = math.radians(eps)
    return math.degrees(math.asin(math.sin(bet) * math.cos(e) +
                                  math.cos(bet) * math.sin(e) * math.sin(lam)))


def _panchanga(sun, moon, weekday):
    diff = (moon - sun) % 360
    tithi_idx = int(diff / 12)
    paksha = "Shukla (waxing)" if tithi_idx < 15 else "Krishna (waning)"
    tno = tithi_idx % 15 + 1
    tname = C.TITHI_NAMES_EN[tno - 1]
    yoga_idx = int(((sun + moon) % 360) / (360 / 27))
    karana_idx = int(diff / 6)
    knames = ["Kimstughna"] + C.KARANA_NAMES * 8 + ["Shakuni", "Chatushpada", "Naga"]
    karana = knames[karana_idx % len(knames)]
    return {
        "tithi_number": tno,
        "tithi": tname,
        "tithi_hi": C.TITHI_NAMES_HI[tno - 1],
        "paksha": paksha,
        "yoga": C.YOGA_NAMES[yoga_idx % 27],
        "karana": karana,
        "vara": C.VAARA_EN[weekday],
        "vara_hi": C.VAARA_HI[weekday],
        "vara_lord": C.VAARA_LORDS[weekday],
    }


def build_chart(name, year, month, day, hour, minute, second,
                tz_offset, lat, lon, place="", now=None):
    local_dt = datetime(year, month, day, hour, minute, second)
    utc_dt = local_dt - timedelta(hours=tz_offset)
    t = E.build_time(utc_dt.year, utc_dt.month, utc_dt.day,
                     utc_dt.hour, utc_dt.minute, utc_dt.second)

    ayan = E.lahiri_ayanamsa(t.tt)
    eps = E.mean_obliquity(t.tt)
    full = E.compute_positions_full(t)          # lon+lat in ONE ephemeris pass
    tropical = {p: full[p][0] for p in full}
    sidereal = {p: (tropical[p] - ayan) % 360 for p in tropical}

    # angles
    lst_deg = (t.gmst * 15.0 + lon) % 360
    asc_trop = E.ascendant(lst_deg, eps, lat)
    mc_trop = E.midheaven(lst_deg, eps)
    asc = (asc_trop - ayan) % 360
    mc = (mc_trop - ayan) % 360
    cusps_trop = E.placidus_cusps(lst_deg, eps, lat)
    cusps = {i: (cusps_trop[i] - ayan) % 360 for i in range(1, 13)}

    # latitudes, declinations, speeds, retrograde
    planet_lat, decl, speed, retro = {}, {}, {}, {}
    ts, _ = E._load()
    for p in NINE:
        if p in ("Rahu", "Ketu"):
            planet_lat[p] = 0.0
            speed[p] = -0.0529  # nodes are retrograde
            retro[p] = True
        else:
            planet_lat[p] = full[p][1]
            if p in ("Mars", "Mercury", "Jupiter", "Venus", "Saturn"):
                l1 = E._geocentric_lon(p, ts.tt_jd(t.tt - 0.5))
                d = (((tropical[p] - l1 + 180) % 360) - 180) * 2.0
                speed[p] = d
                retro[p] = d < 0
            else:                       # Sun & Moon never go retrograde
                speed[p] = 0.9856 if p == "Sun" else 13.176
                retro[p] = False
        decl[p] = _decl(sidereal[p], planet_lat[p], eps)

    # weekday (local)
    weekday = (local_dt.weekday() + 1) % 7  # Sunday=0
    dina_lord = C.VAARA_LORDS[weekday]

    # sunrise/sunset
    sr_dt, ss_dt = E.sun_times(year, month, day, lat, lon, tz_offset)

    # varsha / masa lords
    mesha = E.find_sun_sign_entry(0, t)
    varsha_lord = C.VAARA_LORDS[(mesha.utc_datetime().weekday() + 1) % 7]
    cur_sign = int(sidereal["Sun"] // 30)
    mstart = E.find_sun_sign_entry(cur_sign, t)
    masa_lord = C.VAARA_LORDS[(mstart.utc_datetime().weekday() + 1) % 7]
    hora_lord = SB._hora_lord(local_dt, sr_dt, dina_lord)

    ctx = dict(local_hour=hour + minute / 60.0, birth_local=local_dt,
               sunrise=sr_dt, sunset=ss_dt, varsha_lord=varsha_lord,
               masa_lord=masa_lord, dina_lord=dina_lord, hora_lord=hora_lord,
               decl=decl, speed=speed)

    # planets detail
    planets = {}
    for p in NINE:
        nk = E.nakshatra_of(sidereal[p])
        sg = E.sign_of(sidereal[p])
        house = int((sg["index"] - int(asc // 30)) % 12) + 1
        planets[p] = {
            "name": p, "name_hi": C.PLANETS_HI[p], "abbr": C.PLANETS_ABBR[p],
            "longitude": round(sidereal[p], 4),
            "sign_index": sg["index"], "sign": sg["name_en"], "sign_hi": sg["name_hi"],
            "deg_in_sign": round(sg["deg_in_sign"], 4),
            "house": house,
            "nakshatra": nk["name_en"], "nakshatra_hi": nk["name_hi"],
            "nakshatra_lord": nk["lord"], "pada": nk["pada"],
            "retrograde": bool(retro[p]),
            "speed": round(speed[p], 4),
        }

    # houses (whole sign) and cusp-based
    asc_sign = int(asc // 30)
    houses = {}
    for h in range(1, 13):
        hsign = (asc_sign + h - 1) % 12
        occupants = [p for p in NINE if int(sidereal[p] // 30) == hsign]
        houses[h] = {
            "sign_index": hsign, "sign": C.SIGNS_EN[hsign], "sign_hi": C.SIGNS_HI[hsign],
            "lord": C.SIGN_LORDS[hsign],
            "planets": occupants,
            "cusp": round(cusps[h], 4),
            "cusp_sign": C.SIGNS_EN[int(cusps[h] // 30)],
        }

    result = {
        "meta": {
            "name": name, "place": place, "lat": lat, "lon": lon,
            "tz_offset": tz_offset,
            "local_datetime": local_dt.isoformat(),
            "utc_datetime": utc_dt.isoformat(),
            "ayanamsa": round(ayan, 5),
            "ayanamsa_name": "Lahiri (Chitrapaksha)",
            "weekday": C.VAARA_EN[weekday], "weekday_hi": C.VAARA_HI[weekday],
            "sunrise": sr_dt.isoformat() if sr_dt is not None else None,
            "sunset": ss_dt.isoformat() if ss_dt is not None else None,
        },
        "ascendant": {
            "longitude": round(asc, 4), "sign_index": asc_sign,
            "sign": C.SIGNS_EN[asc_sign], "sign_hi": C.SIGNS_HI[asc_sign],
            "deg_in_sign": round(asc - asc_sign * 30, 4),
            "nakshatra": E.nakshatra_of(asc)["name_en"],
            "nakshatra_hi": E.nakshatra_of(asc)["name_hi"],
            "nakshatra_lord": E.nakshatra_of(asc)["lord"],
        },
        "midheaven": {"longitude": round(mc, 4), "sign": C.SIGNS_EN[int(mc // 30)]},
        "planets": planets,
        "houses": houses,
        "cusps": {i: round(cusps[i], 4) for i in range(1, 13)},
        "panchanga": _panchanga(sidereal["Sun"], sidereal["Moon"], weekday),
    }

    # divisional charts
    result["vargas"] = DV.build_vargas(sidereal, asc)
    result["varga_info"] = {str(k): {"name_en": v[0], "name_hi": v[1], "meaning": v[2]}
                            for k, v in DV.VARGA_INFO.items()}

    # dasha
    ref = now or datetime(2026, 10, 20, 12, 0, 0)
    tree = DS.vimshottari(sidereal["Moon"], local_dt, max_depth=3)
    result["dasha"] = tree
    result["current_dasha"] = DS.current_chain(tree, ref)

    # shadbala
    result["shadbala"] = SB.compute(sidereal, asc, ctx)

    # ashtakavarga
    result["ashtakavarga"] = AK.compute(sidereal, asc)

    # yogas & doshas
    yogas = YG.detect(sidereal, asc)
    result["yogas"] = [y for y in yogas if y["kind"] == "yoga"]
    result["doshas"] = [y for y in yogas if y["kind"] == "dosha"]

    # KP
    result["kp"] = {
        "cusps": KP.cusps_analysis(cusps),
        "planets": {p: KP.analyse_planet(sidereal[p]) for p in NINE},
        "significators": KP.significators(sidereal, cusps),
        "ruling_planets": KP.ruling_planets(asc, sidereal, dina_lord),
    }

    # Jaimini
    ck = JM.chara_karakas(sidereal)
    ak_planet = ck["AK"]["planet"]
    result["jaimini"] = {
        "chara_karakas": ck,
        "karakamsa": JM.karakamsa(sidereal, ak_planet),
        "arudha_padas": JM.arudha_padas(asc, sidereal),
        "chara_dasha": JM.chara_dasha(asc, sidereal, years=90),
    }

    # Lal Kitab
    result["lalkitab"] = LK.compute(sidereal, asc)

    # Nadi
    result["nadi"] = {
        "amsa": ND.compute(sidereal, asc),
        "progression": ND.progression(sidereal, asc, year, (now or datetime(2026, 10, 20)).year),
    }

    # Numerology (needs name)
    result["numerology"] = NU.compute(name or "", day, month, year,
                                      (now or datetime(2026, 10, 20)).year)

    # ---- extras: Ishta Devta, Golden period, Hora, Bhava Chalit ----
    from . import extras as X
    result["ishta_devta"] = X.ishta_devta(result)
    result["golden"] = X.golden_period(result)
    result["hora"] = X.hora(year, month, day, lat, lon, tz_offset, hour, minute)
    result["chalit"] = X.chalit(result)

    return result


def transit_chart(natal_asc_sign, natal_moon_sign, year, month, day,
                  hour, minute, tz_offset, lat, lon):
    """Transit (gochara) positions for a target moment, with houses from the
    natal Lagna and from the natal Moon (whole sign)."""
    from datetime import datetime as _dt
    local_dt = _dt(year, month, day, hour, minute, 0)
    utc_dt = local_dt - timedelta(hours=tz_offset)
    t = E.build_time(utc_dt.year, utc_dt.month, utc_dt.day,
                     utc_dt.hour, utc_dt.minute, utc_dt.second)
    ayan = E.lahiri_ayanamsa(t.tt)
    trop = E.compute_positions(t)
    sid = {p: (trop[p] - ayan) % 360 for p in trop}
    out = {}
    for p in NINE:
        sg = E.sign_of(sid[p])
        nk = E.nakshatra_of(sid[p])
        out[p] = {
            "name": p, "name_hi": C.PLANETS_HI[p],
            "sign_index": sg["index"], "sign": sg["name_en"], "sign_hi": sg["name_hi"],
            "deg_in_sign": round(sg["deg_in_sign"], 3),
            "nakshatra": nk["name_en"], "nakshatra_hi": nk["name_hi"],
            "house_from_lagna": ((sg["index"] - natal_asc_sign) % 12) + 1,
            "house_from_moon": ((sg["index"] - natal_moon_sign) % 12) + 1,
        }
    return {"date": local_dt.isoformat(), "ayanamsa": round(ayan, 5), "planets": out}
