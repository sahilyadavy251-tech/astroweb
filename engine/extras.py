"""Extra jyotish modules: Gun Milan (matching), Ishta Devta, Hora,
Golden Time Period and Bhava Chalit.

Ported to the same conventions used by the rest of the engine.
"""
from datetime import datetime, timedelta

from . import constants as C
from . import ephemeris as E

PLANETS = ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn", "Rahu", "Ketu"]
RULER = ["Mars", "Venus", "Mercury", "Moon", "Sun", "Mercury",
         "Venus", "Mars", "Jupiter", "Saturn", "Saturn", "Jupiter"]
NAK_SIZE = 360.0 / 27.0

# ------------------------------------------------------------------ #
#  Gun Milan (Ashtakoot) -- 36 point compatibility
# ------------------------------------------------------------------ #
GM_VARNA = [3, 2, 1, 4, 3, 2, 1, 4, 3, 2, 1, 4]
GM_VARNA_NAME = {4: "Brahmin", 3: "Kshatriya", 2: "Vaishya", 1: "Shudra"}
GM_VASHYA = ["C", "C", "M", "J", "V", "M", "M", "K", "C", "J", "M", "J"]
GM_VASHYA_PTS = {"CC": 2, "CJ": 1, "CK": 1, "CM": 1, "CV": 1, "JJ": 2, "JK": 1,
                 "JM": 0.5, "JV": 1, "KK": 2, "KM": 1, "KV": 1, "MM": 2, "MV": 1, "VV": 2}
GM_VASHYA_NAME = {"C": "Chatushpada", "M": "Manava", "J": "Jalachara",
                  "V": "Vanachara", "K": "Keeta"}
GM_GANA = ["D", "M", "R", "M", "D", "M", "D", "D", "R", "R", "M", "M", "D", "R",
           "D", "R", "D", "R", "R", "M", "M", "D", "R", "R", "M", "M", "D"]
GM_GANA_NAME = {"D": "Deva", "M": "Manushya", "R": "Rakshasa"}
GM_YONI = ["Horse", "Elephant", "Sheep", "Serpent", "Serpent", "Dog", "Cat", "Sheep",
           "Cat", "Rat", "Rat", "Cow", "Buffalo", "Tiger", "Buffalo", "Tiger", "Deer",
           "Deer", "Dog", "Monkey", "Mongoose", "Monkey", "Lion", "Horse", "Lion",
           "Cow", "Elephant"]
GM_YONI_ENEMY = {"Horse": "Buffalo", "Buffalo": "Horse", "Elephant": "Lion",
                 "Lion": "Elephant", "Sheep": "Monkey", "Monkey": "Sheep",
                 "Serpent": "Mongoose", "Mongoose": "Serpent", "Dog": "Deer",
                 "Deer": "Dog", "Cat": "Rat", "Rat": "Cat", "Cow": "Tiger",
                 "Tiger": "Cow"}
GM_NADI = ["A", "M", "Y", "Y", "M", "A", "A", "M", "Y", "Y", "M", "A", "A", "M",
           "Y", "Y", "M", "A", "A", "M", "Y", "Y", "M", "A", "A", "M", "Y"]
GM_NADI_NAME = {"A": "Adi", "M": "Madhya", "Y": "Antya"}
GM_NAT_FRIEND = {"Sun": ["Moon", "Mars", "Jupiter"], "Moon": ["Sun", "Mercury"],
                 "Mars": ["Sun", "Moon", "Jupiter"], "Mercury": ["Sun", "Venus"],
                 "Jupiter": ["Sun", "Moon", "Mars"], "Venus": ["Mercury", "Saturn"],
                 "Saturn": ["Mercury", "Venus"]}
GM_NAT_ENEMY = {"Sun": ["Venus", "Saturn"], "Moon": [], "Mars": ["Mercury"],
                "Mercury": ["Moon"], "Jupiter": ["Mercury", "Venus"],
                "Venus": ["Sun", "Moon"], "Saturn": ["Sun", "Moon", "Mars"]}


def _nak_index(lon):
    return int(lon // NAK_SIZE) % 27


def _gm_tara_one(from_n, to_n):
    n = (to_n - from_n) % 27
    t = n % 9
    return 0.0 if t in (1, 3, 5, 7) else 1.5


def _gm_rel(a, b):
    if a == b:
        return "f"
    if b in GM_NAT_FRIEND.get(a, []):
        return "f"
    if b in GM_NAT_ENEMY.get(a, []):
        return "e"
    return "n"


def _gm_maitri(a, b):
    if a == b:
        return 5
    ra, rb = _gm_rel(a, b), _gm_rel(b, a)
    if ra == "f" and rb == "f":
        return 5
    if (ra == "f" and rb == "n") or (ra == "n" and rb == "f"):
        return 4
    if ra == "n" and rb == "n":
        return 3
    if (ra == "f" and rb == "e") or (ra == "e" and rb == "f"):
        return 1
    if (ra == "n" and rb == "e") or (ra == "e" and rb == "n"):
        return 0.5
    return 0


def _gm_yoni(a, b):
    if a == b:
        return 4
    if GM_YONI_ENEMY.get(a) == b:
        return 0
    return 2


def _gm_bhakoot(sa, sb):
    d = ((sb - sa) % 12) + 1
    return 0 if d in (2, 5, 6, 8, 9, 12) else 7


def _manglik(chart):
    h = chart["planets"]["Mars"]["house"]
    return {"manglik": h in (1, 2, 4, 7, 8, 12), "house": h}


def gun_milan(chart_a, chart_b):
    """Ashtakoot Guna Milan between two charts (0-36)."""
    ma, mb = chart_a["planets"]["Moon"], chart_b["planets"]["Moon"]
    na, nb = _nak_index(ma["longitude"]), _nak_index(mb["longitude"])
    sa, sb = ma["sign_index"], mb["sign_index"]
    va, vb = GM_VARNA[sa], GM_VARNA[sb]
    ga, gb = GM_GANA[na], GM_GANA[nb]
    ya, yb = GM_YONI[na], GM_YONI[nb]
    nadia, nadib = GM_NADI[na], GM_NADI[nb]
    la, lb = RULER[sa], RULER[sb]

    rows = []
    rows.append({"k": "Varna", "max": 1, "pts": 1 if va >= vb else 0,
                 "note": "%s / %s" % (GM_VARNA_NAME[va], GM_VARNA_NAME[vb])})
    vsa, vsb = GM_VASHYA[sa], GM_VASHYA[sb]
    rows.append({"k": "Vashya", "max": 2,
                 "pts": GM_VASHYA_PTS.get("".join(sorted([vsa, vsb])), 2),
                 "note": "%s / %s" % (GM_VASHYA_NAME[vsa], GM_VASHYA_NAME[vsb])})
    rows.append({"k": "Tara", "max": 3, "pts": _gm_tara_one(na, nb) + _gm_tara_one(nb, na),
                 "note": "Nakshatra count, both ways"})
    rows.append({"k": "Yoni", "max": 4, "pts": _gm_yoni(ya, yb), "note": "%s / %s" % (ya, yb)})
    rows.append({"k": "Graha Maitri", "max": 5, "pts": _gm_maitri(la, lb),
                 "note": "%s / %s" % (la, lb)})
    if ga == gb:
        gp = 6
    elif {ga, gb} == {"D", "M"}:
        gp = 5
    elif {ga, gb} == {"M", "R"}:
        gp = 1
    else:
        gp = 0
    rows.append({"k": "Gana", "max": 6, "pts": gp,
                 "note": "%s / %s" % (GM_GANA_NAME[ga], GM_GANA_NAME[gb])})
    rows.append({"k": "Bhakoot", "max": 7, "pts": _gm_bhakoot(sa, sb),
                 "note": "%s / %s" % (C.SIGNS_EN[sa], C.SIGNS_EN[sb])})
    rows.append({"k": "Nadi", "max": 8, "pts": 0 if nadia == nadib else 8,
                 "note": "%s / %s" % (GM_NADI_NAME[nadia], GM_NADI_NAME[nadib])})

    total = sum(r["pts"] for r in rows)
    pct = round(total / 36.0 * 100)
    if total >= 28:
        verdict_en, verdict_hi = "Excellent match", "उत्तम मिलान"
    elif total >= 21:
        verdict_en, verdict_hi = "Good match", "अच्छा मिलान"
    elif total >= 18:
        verdict_en, verdict_hi = "Average match", "साधारण मिलान"
    else:
        verdict_en, verdict_hi = "Below average — needs care", "कमज़ोर मिलान — सावधानी"
    doshas = []
    if _gm_bhakoot(sa, sb) == 0:
        doshas.append("Bhakoot dosha")
    if nadia == nadib:
        doshas.append("Nadi dosha")
    ma_, mb_ = _manglik(chart_a), _manglik(chart_b)
    if ma_["manglik"] or mb_["manglik"]:
        doshas.append("Mangal dosha present")
    return {"rows": rows, "total": round(total, 1), "max": 36, "pct": pct,
            "verdict_en": verdict_en, "verdict_hi": verdict_hi,
            "doshas": doshas,
            "moon_a": {"nakshatra": ma["nakshatra"], "nakshatra_hi": ma["nakshatra_hi"],
                       "sign": ma["sign"], "sign_hi": ma["sign_hi"]},
            "moon_b": {"nakshatra": mb["nakshatra"], "nakshatra_hi": mb["nakshatra_hi"],
                       "sign": mb["sign"], "sign_hi": mb["sign_hi"]},
            "manglik_a": ma_, "manglik_b": mb_}


# ------------------------------------------------------------------ #
#  Ishta Devta  (from Karakamsa -- Jaimini)
# ------------------------------------------------------------------ #
ISHTA_PLANET = {
    "Sun": {"deity_en": "Bhagwan Shiv / Bhagwan Ram", "deity_hi": "भगवान शिव / भगवान राम",
            "mantra": "Om Namah Shivaya / 'Ram' naam", "day_en": "Sunday", "day_hi": "रविवार",
            "avatar": "Ram"},
    "Moon": {"deity_en": "Maa Gauri (Parvati) / Shri Krishna", "deity_hi": "माँ गौरी (पार्वती) / श्री कृष्ण",
             "mantra": "Om Gauryai Namah / Om Namo Bhagavate Vasudevaya", "day_en": "Monday",
             "day_hi": "सोमवार", "avatar": "Krishna"},
    "Mars": {"deity_en": "Bhagwan Hanuman / Kartikeya (Skanda)", "deity_hi": "भगवान हनुमान / कार्तिकेय",
             "mantra": "Hanuman Chalisa / Om Sharavanabhavaya Namah", "day_en": "Tuesday",
             "day_hi": "मंगलवार", "avatar": "Narasimha"},
    "Mercury": {"deity_en": "Bhagwan Vishnu (or Maa Saraswati)", "deity_hi": "भगवान विष्णु (या माँ सरस्वती)",
                "mantra": "Vishnu Sahasranama / Om Namo Narayanaya", "day_en": "Wednesday",
                "day_hi": "बुधवार", "avatar": "Buddha"},
    "Jupiter": {"deity_en": "Bhagwan Vishnu / Dattatreya (Guru)", "deity_hi": "भगवान विष्णु / दत्तात्रेय",
                "mantra": "Om Dram Dattatreyaya Namah / Om Namo Bhagavate Vasudevaya",
                "day_en": "Thursday", "day_hi": "गुरुवार", "avatar": "Vamana"},
    "Venus": {"deity_en": "Maa Lakshmi", "deity_hi": "माँ लक्ष्मी",
              "mantra": "Om Shreem Mahalakshmyai Namah", "day_en": "Friday",
              "day_hi": "शुक्रवार", "avatar": "Parashurama"},
    "Saturn": {"deity_en": "Bhagwan Shiv / Narayana (or Hanuman)", "deity_hi": "भगवान शिव / नारायण (या हनुमान)",
               "mantra": "Om Namah Shivaya / Om Namo Narayanaya", "day_en": "Saturday",
               "day_hi": "शनिवार", "avatar": "Kurma"},
    "Rahu": {"deity_en": "Maa Durga", "deity_hi": "माँ दुर्गा", "mantra": "Om Dum Durgayai Namah",
             "day_en": "Saturday", "day_hi": "शनिवार", "avatar": "Varaha"},
    "Ketu": {"deity_en": "Bhagwan Ganesh", "deity_hi": "भगवान गणेश",
             "mantra": "Om Gam Ganapataye Namah", "day_en": "Tuesday",
             "day_hi": "मंगलवार", "avatar": "Matsya"},
}


def _varga(chart, num):
    v = chart["vargas"].get(str(num))
    return v if v is not None else chart["vargas"].get(num)


def ishta_devta(chart):
    """Ishta Devta from the 12th house of the Karakamsa (D9 of Atmakaraka)."""
    ak = chart["jaimini"]["chara_karakas"].get("AK")
    if not ak:
        return None
    akp = ak["planet"]
    d9 = _varga(chart, 9) or {}
    kamsha = d9.get(akp)
    if kamsha is None:
        return None
    twelfth = (kamsha + 11) % 12
    occ = None
    for p in PLANETS:
        if d9.get(p) == twelfth:
            occ = p
            break
    planet = occ or RULER[twelfth]
    info = ISHTA_PLANET.get(planet, {})
    # also the 5th-house-lord method (classical jyotish)
    fifth_lord = chart["houses"][5]["lord"]
    return {"atmakaraka": akp, "karakamsa": kamsha,
            "karakamsa_sign": C.SIGNS_EN[kamsha], "karakamsa_sign_hi": C.SIGNS_HI[kamsha],
            "twelfth_sign": twelfth, "twelfth_sign_en": C.SIGNS_EN[twelfth],
            "twelfth_sign_hi": C.SIGNS_HI[twelfth],
            "occupant": occ, "planet": planet,
            "planet_hi": C.PLANET_HI.get(planet, planet),
            "fifth_lord": fifth_lord, "fifth_lord_hi": C.PLANET_HI.get(fifth_lord, fifth_lord),
            "info": info,
            "table": [dict(planet=p, planet_hi=C.PLANET_HI.get(p, p), **ISHTA_PLANET[p])
                      for p in PLANETS]}


# ------------------------------------------------------------------ #
#  Hora (planetary hours)
# ------------------------------------------------------------------ #
HORA_DAYLORDS = ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn"]
HORA_ORDER = ["Sun", "Venus", "Mercury", "Moon", "Saturn", "Jupiter", "Mars"]
HORA_GOOD = {"Sun": "Authority, government work, power", "Moon": "Travel, water, emotions, home",
             "Mars": "Courage, land, surgery, competition", "Mercury": "Business, trade, learning, writing",
             "Jupiter": "Marriage, money, dharma, education", "Venus": "Love, art, luxury, vehicles",
             "Saturn": "Labour, service, oil/iron, delays"}


def hora(year, month, day, lat, lon, tz_offset, hour=None, minute=None):
    """The 24 planetary hours (horas) of the given local day."""
    birth = None
    if hour is not None:
        birth = datetime(year, month, day) + timedelta(hours=hour - tz_offset, minutes=(minute or 0))
    d = datetime(year, month, day)
    sr, ss = E.sun_times(d.year, d.month, d.day, lat, lon, tz_offset)
    # a birth before sunrise belongs to the *previous* day's hora cycle
    if birth is not None and sr and birth < sr:
        d = d - timedelta(days=1)
        sr, ss = E.sun_times(d.year, d.month, d.day, lat, lon, tz_offset)
    nd = d + timedelta(days=1)
    sr2, _ = E.sun_times(nd.year, nd.month, nd.day, lat, lon, tz_offset)
    if not (sr and ss and sr2):
        return {"horas": [], "day_lord": None}
    js_day = (d.weekday() + 1) % 7   # 0 = Sunday
    day_lord = HORA_DAYLORDS[js_day]
    base = HORA_ORDER.index(day_lord)
    day_ms = (ss - sr).total_seconds() * 1000.0
    night_ms = (sr2 - ss).total_seconds() * 1000.0
    d_h, n_h = day_ms / 12.0, night_ms / 12.0
    horas = []
    for i in range(24):
        if i < 12:
            start = sr + timedelta(milliseconds=i * d_h)
            end = sr + timedelta(milliseconds=(i + 1) * d_h)
            part, in_part = "day", i + 1
        else:
            start = ss + timedelta(milliseconds=(i - 12) * n_h)
            end = ss + timedelta(milliseconds=(i - 11) * n_h)
            part, in_part = "night", i - 11
        lord = HORA_ORDER[((base + i) % 7 + 7) % 7]
        is_now = bool(birth and start <= birth < end)
        horas.append({"n": i + 1, "lord": lord, "lord_hi": C.PLANET_HI.get(lord, lord),
                      "start": start.strftime("%Y-%m-%dT%H:%M:%S"),
                      "end": end.strftime("%Y-%m-%dT%H:%M:%S"),
                      "part": part, "in_part": in_part, "good": HORA_GOOD.get(lord, ""),
                      "at_birth": is_now})
    return {"horas": horas, "day_lord": day_lord, "day_lord_hi": C.PLANET_HI.get(day_lord, day_lord),
            "weekday": js_day,
            "sunrise": sr.strftime("%Y-%m-%dT%H:%M:%S"),
            "sunset": ss.strftime("%Y-%m-%dT%H:%M:%S"),
            "next_sunrise": sr2.strftime("%Y-%m-%dT%H:%M:%S"),
            "day_hora_min": round(d_h / 60000.0, 2), "night_hora_min": round(n_h / 60000.0, 2)}


# ------------------------------------------------------------------ #
#  Golden Time Period
# ------------------------------------------------------------------ #
GOLD_HOUSES = [1, 2, 4, 9, 11]
GOLD_NUM = {"Sun": 7, "Moon": 3, "Mars": 10, "Mercury": 6, "Jupiter": 9,
            "Venus": 5, "Saturn": 1, "Rahu": 0, "Ketu": 0}


def golden_period(chart):
    asc = chart["ascendant"]["sign_index"]
    x = y = 0
    rows = []
    for h in GOLD_HOUSES:
        sign = (asc + h - 1) % 12
        ps = [p for p in PLANETS if chart["planets"][p]["house"] == h]
        nums = [GOLD_NUM.get(p, 0) for p in ps]
        rashi_num = sign + 1
        x += rashi_num
        y += sum(nums)
        rows.append({"house": h, "sign_en": C.SIGNS_EN[sign], "sign_hi": C.SIGNS_HI[sign],
                     "rashi_num": rashi_num,
                     "planets": ps, "planets_hi": [C.PLANET_HI.get(p, p) for p in ps],
                     "nums": nums})
    total = x + y
    r = total % 12
    res_house = 2 if r <= 1 else r + 1
    res_sign = (asc + res_house - 1) % 12
    res_lord = RULER[res_sign]
    res_planets = [p for p in PLANETS if chart["planets"][p]["house"] == res_house]
    golden = list(dict.fromkeys(res_planets + [res_lord]))
    return {"rows": rows, "x": x, "y": y, "total": total, "r": r,
            "result_house": res_house, "result_sign_en": C.SIGNS_EN[res_sign],
            "result_sign_hi": C.SIGNS_HI[res_sign], "result_lord": res_lord,
            "result_lord_hi": C.PLANET_HI.get(res_lord, res_lord),
            "result_planets": res_planets,
            "result_planets_hi": [C.PLANET_HI.get(p, p) for p in res_planets],
            "golden": golden, "golden_hi": [C.PLANET_HI.get(p, p) for p in golden]}


# ------------------------------------------------------------------ #
#  Bhava Chalit (cuspal chart)
# ------------------------------------------------------------------ #
def chalit(chart):
    """House of each planet by the Placidus cusp ranges (bhava chalit)."""
    cusps = chart["cusps"]
    c = {}
    for i in range(1, 13):
        v = cusps[i]
        c[i] = v["longitude"] if isinstance(v, dict) else float(v)
    asc = chart["ascendant"]["sign_index"]

    def house_of(lon):
        for i in range(1, 13):
            nxt = 1 if i == 12 else i + 1
            if (lon - c[i]) % 360.0 < (c[nxt] - c[i]) % 360.0:
                return i
        return 1

    planets = {}
    for p in PLANETS:
        lon = chart["planets"][p]["longitude"]
        h = house_of(lon)
        rh = ((chart["planets"][p]["sign_index"] - asc) % 12) + 1
        planets[p] = {"house": h, "rashi_house": rh, "shifted": h != rh,
                      "name_hi": C.PLANET_HI.get(p, p)}
    return {"cusps": {str(i): round(c[i], 4) for i in range(1, 13)}, "planets": planets}
