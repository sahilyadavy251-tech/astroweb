"""Yogas and Doshas detection (Parashari)."""
from __future__ import annotations

from . import constants as C

SEVEN = ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn"]
ALL9 = SEVEN + ["Rahu", "Ketu"]

KENDRA = [1, 4, 7, 10]
TRIKONA = [1, 5, 9]
DUSTHANA = [6, 8, 12]


def _sign(lon):
    return int((lon % 360) // 30)


class ChartCtx:
    def __init__(self, pos, asc):
        self.pos = pos
        self.asc = asc
        self.asc_sign = _sign(asc)
        self.sign = {p: _sign(lon) for p, lon in pos.items()}

    def house(self, p):
        return ((self.sign[p] - self.asc_sign) % 12) + 1

    def house_of_sign(self, s):
        return ((s - self.asc_sign) % 12) + 1

    def lord(self, h):
        return C.SIGN_LORDS[(self.asc_sign + h - 1) % 12]

    def in_house(self, h):
        return [p for p in ALL9 if self.house(p) == h]

    def conj(self, a, b):
        return self.sign[a] == self.sign[b]

    def aspects(self, a, b):
        """true if a aspects b (7th) or shares sign."""
        d = (self.sign[b] - self.sign[a]) % 12 + 1
        return d == 7 or self.conj(a, b)

    def relative_from(self, p, q):
        """house of q counted from p (1..12)."""
        return ((self.sign[q] - self.sign[p]) % 12) + 1


def _y(name_en, name_hi, desc_en, desc_hi, planets, kind="yoga"):
    return {"name_en": name_en, "name_hi": name_hi,
            "description_en": desc_en, "description_hi": desc_hi,
            "planets": planets, "kind": kind}


def _own_or_exalt(p, lon):
    s = _sign(lon)
    if p in C.OWN_SIGNS and s in C.OWN_SIGNS[p]:
        return True
    ex = C.EXALTATION.get(p)
    if ex and s == ex[0]:
        return True
    return False


def detect(pos, asc):
    ctx = ChartCtx(pos, asc)
    out = []

    # ---- Pancha Mahapurusha yogas ----
    for p, yname, yhi in [("Mars", "Ruchaka", "रुचक"), ("Mercury", "Bhadra", "भद्र"),
                          ("Jupiter", "Hamsa", "हंस"), ("Venus", "Malavya", "मालव्य"),
                          ("Saturn", "Sasa", "शश")]:
        if _own_or_exalt(p, pos[p]) and ctx.house(p) in KENDRA:
            out.append(_y(f"{yname} Yoga ({p})", f"{yhi} योग",
                          f"{p} is in its own/exaltation sign and in a kendra (house {ctx.house(p)}).",
                          f"{p} स्वराशि/उच्च में तथा केन्द्र ({ctx.house(p)}) में है।", [p]))

    # ---- Gajakesari ----
    if ctx.relative_from("Moon", "Jupiter") in KENDRA:
        out.append(_y("Gajakesari Yoga", "गजकेसरी योग",
                      "Jupiter is in a kendra (1/4/7/10) from the Moon.",
                      "गुरु चन्द्र से केन्द्र में है।", ["Jupiter", "Moon"]))

    # ---- Budhaditya ----
    if ctx.conj("Sun", "Mercury"):
        out.append(_y("Budhaditya Yoga", "बुधादित्य योग",
                      "Sun and Mercury are conjunct in the same sign.",
                      "सूर्य और बुध एक ही राशि में हैं।", ["Sun", "Mercury"]))

    # ---- Chandra-Mangala ----
    if ctx.conj("Moon", "Mars"):
        out.append(_y("Chandra-Mangala Yoga", "चन्द्र-मंगल योग",
                      "Moon and Mars are conjunct.", "चन्द्र और मंगल युत हैं।", ["Moon", "Mars"]))

    # ---- Sunapha / Anapha / Durudhara (from Moon) ----
    second = ctx.in_house(((ctx.house("Moon")) % 12) + 1)
    twelfth_h = ((ctx.house("Moon") - 2) % 12) + 1
    twelfth = ctx.in_house(twelfth_h)
    second = [p for p in second if p != "Moon"]
    twelfth = [p for p in twelfth if p != "Moon"]
    if second and not twelfth:
        out.append(_y("Sunapha Yoga", "सुनफा योग", "Planets in the 2nd from the Moon.",
                      "चन्द्र से द्वितीय में ग्रह।", second))
    elif twelfth and not second:
        out.append(_y("Anapha Yoga", "अनफा योग", "Planets in the 12th from the Moon.",
                      "चन्द्र से द्वादश में ग्रह।", twelfth))
    elif second and twelfth:
        out.append(_y("Durudhara Yoga", "दुरुधरा योग", "Planets in both 2nd and 12th from the Moon.",
                      "चन्द्र से द्वितीय और द्वादश दोनों में ग्रह।", second + twelfth))

    # ---- Kemadruma ----
    if not second and not twelfth:
        out.append(_y("Kemadruma Yoga", "केमद्रुम योग",
                      "No planets in the 2nd/12th from the Moon (isolation of the Moon).",
                      "चन्द्र से 2/12 में कोई ग्रह नहीं।", ["Moon"], kind="dosha"))

    # ---- Vesi / Vasi / Ubhayachari (from Sun) ----
    s2 = [p for p in ctx.in_house(((ctx.house("Sun")) % 12) + 1) if p not in ("Sun",)]
    s12 = [p for p in ctx.in_house(((ctx.house("Sun") - 2) % 12) + 1) if p != "Sun"]
    if s2 and not s12:
        out.append(_y("Vesi Yoga", "वेशि योग", "Planets in the 2nd from the Sun.", "सूर्य से द्वितीय में ग्रह।", s2))
    elif s12 and not s2:
        out.append(_y("Vasi Yoga", "वासि योग", "Planets in the 12th from the Sun.", "सूर्य से द्वादश में ग्रह।", s12))
    elif s2 and s12:
        out.append(_y("Ubhayachari Yoga", "उभयचरि योग", "Planets on both sides of the Sun.", "सूर्य के दोनों ओर ग्रह।", s2 + s12))

    # ---- Amala ----
    tenth = ctx.in_house(10)
    tenth = [p for p in tenth if p in ("Jupiter", "Venus", "Mercury")]
    if tenth:
        out.append(_y("Amala Yoga", "अमल योग", "A benefic in the 10th house.",
                      "दशम भाव में शुभ ग्रह।", tenth))

    # ---- Adhi yoga ----
    adhi = [p for p in ("Jupiter", "Venus", "Mercury")
            if ctx.relative_from("Moon", p) in (6, 7, 8)]
    if len(adhi) >= 2:
        out.append(_y("Adhi Yoga", "आधि योग", "Benefics in the 6th/7th/8th from the Moon.",
                      "चन्द्र से 6/7/8 में शुभ ग्रह।", adhi))

    # ---- Shakata ----
    if ctx.relative_from("Jupiter", "Moon") in (6, 8, 12):
        out.append(_y("Shakata Yoga", "शकट योग", "Moon in 6/8/12 from Jupiter.",
                      "चन्द्र गुरु से 6/8/12 में।", ["Moon", "Jupiter"], kind="dosha"))

    # ---- Saraswati ----
    good_houses = {1, 2, 4, 5, 7, 9, 10}
    if all(ctx.house(p) in good_houses for p in ("Mercury", "Venus", "Jupiter")) and \
       _own_or_exalt("Jupiter", pos["Jupiter"]):
        out.append(_y("Saraswati Yoga", "सरस्वती योग",
                      "Mercury, Venus, Jupiter in kendra/2/5/9 and Jupiter in own/friendly sign.",
                      "बुध, शुक्र, गुरु केन्द्र/2/5/9 में तथा गुरु स्व/मित्र राशि में।",
                      ["Mercury", "Venus", "Jupiter"]))

    # ---- Parivartana (exchange) ----
    for h1 in range(1, 13):
        l1 = ctx.lord(h1)
        if l1 not in ALL9:
            continue
        h2 = ctx.house(l1)
        if h2 == h1:
            continue
        l2 = ctx.lord(h2)
        if l2 in ALL9 and ctx.house(l2) == h1 and h1 < h2:
            kind = "dosha" if (h1 in DUSTHANA or h2 in DUSTHANA) else "yoga"
            out.append(_y(f"Parivartana Yoga ({h1}-{h2})", f"परिवर्तन योग ({h1}-{h2})",
                          f"Exchange between house {h1} and house {h2} (lords {l1} and {l2}).",
                          f"भाव {h1} और {h2} के स्वामियों का परिवर्तन।", [l1, l2], kind=kind))

    # ---- Vipreet Raja Yoga ----
    vip = []
    for h in DUSTHANA:
        lord = ctx.lord(h)
        if lord in ALL9 and ctx.house(lord) in DUSTHANA:
            vip.append(lord)
    if vip:
        out.append(_y("Vipreet Raja Yoga", "विपरीत राज योग",
                      "Lord(s) of 6/8/12 placed in 6/8/12 (reversal gives rise).",
                      "6/8/12 के स्वामी 6/8/12 में (विपरीत राज योग)।", vip))

    # ---- Raja yoga (kendra-trikona) ----
    kendra_lords = {ctx.lord(h) for h in KENDRA}
    trikona_lords = {ctx.lord(h) for h in TRIKONA}
    pairs = []
    for a in kendra_lords:
        for b in trikona_lords:
            if a in ALL9 and b in ALL9 and a != b and (ctx.conj(a, b) or ctx.aspects(a, b)):
                pairs.append((a, b))
    if pairs:
        pl = sorted({x for pr in pairs for x in pr})
        out.append(_y("Raja Yoga (Kendra-Trikona)", "राज योग (केन्द्र-त्रिकोण)",
                      "A kendra lord is conjunct/aspects a trikona lord.",
                      "केन्द्र भावेश और त्रिकोण भावेश का संबंध।", pl))

    # ---- Dhana yoga ----
    dh = []
    for a in (ctx.lord(2), ctx.lord(11)):
        for b in (ctx.lord(1), ctx.lord(5), ctx.lord(9), ctx.lord(2), ctx.lord(11)):
            if a in ALL9 and b in ALL9 and a != b and (ctx.conj(a, b) or ctx.aspects(a, b)):
                dh += [a, b]
    if dh:
        out.append(_y("Dhana Yoga", "धन योग", "Lords of wealth (2/11) linked with 1/5/9 lords.",
                      "धन भावेश (2/11) का लग्नेश/त्रिकोणेश से संबंध।", sorted(set(dh))))

    # ---- Neecha Bhanga ----
    for p in SEVEN:
        s = _sign(pos[p])
        if p in C.DEBILITATION and s == C.DEBILITATION[p]:
            lord = C.SIGN_LORDS[s]
            bang = (lord in ALL9 and ctx.house(lord) in KENDRA) or \
                   (C.EXALTATION.get(lord) and _sign(pos.get(lord, -1)) == C.EXALTATION[lord][0])
            if bang:
                out.append(_y(f"Neecha Bhanga ({p})", f"नीच भंग ({p})",
                              f"{p}'s debilitation is cancelled (dispositor well placed).",
                              f"{p} की नीचता भंग (राशीश बलवान)।", [p]))

    # ================= DOSHAS =================
    # Mangal / Kuja dosha
    mangal_houses = {1, 2, 4, 7, 8, 12}
    mangal = []
    if ctx.house("Mars") in mangal_houses:
        mangal.append("Lagna")
    if ctx.relative_from("Moon", "Mars") in mangal_houses:
        mangal.append("Moon")
    if ctx.relative_from("Venus", "Mars") in mangal_houses:
        mangal.append("Venus")
    if mangal:
        out.append(_y("Mangal Dosha (Kuja)", "मंगल दोष (कुज)",
                      "Mars in 1/2/4/7/8/12 from " + ", ".join(mangal) + ".",
                      "मंगल " + ", ".join(mangal) + " से 1/2/4/7/8/12 में।",
                      ["Mars"], kind="dosha"))

    # Kaal Sarp
    ra, ke = pos["Rahu"], pos["Ketu"]
    span = (ke - ra) % 360

    def between(lon):
        return ((lon - ra) % 360) < span

    if all(between(pos[p]) for p in SEVEN):
        out.append(_y("Kaal Sarp Dosha", "काल सर्प दोष",
                      "All seven planets lie within the Rahu-Ketu axis.",
                      "सभी सात ग्रह राहु-केतु अक्ष के बीच हैं।", SEVEN, kind="dosha"))

    # Grahan
    if ctx.conj("Sun", "Rahu") or ctx.conj("Sun", "Ketu"):
        out.append(_y("Grahan Dosha (Sun)", "ग्रहण दोष (सूर्य)",
                      "Sun is conjunct Rahu or Ketu.", "सूर्य राहु/केतु के साथ।", ["Sun"], kind="dosha"))
    if ctx.conj("Moon", "Rahu") or ctx.conj("Moon", "Ketu"):
        out.append(_y("Grahan Dosha (Moon)", "ग्रहण दोष (चन्द्र)",
                      "Moon is conjunct Rahu or Ketu.", "चन्द्र राहु/केतु के साथ।", ["Moon"], kind="dosha"))

    # Guru Chandal
    if ctx.conj("Jupiter", "Rahu") or ctx.conj("Jupiter", "Ketu"):
        out.append(_y("Guru Chandal Dosha", "गुरु चांडाल दोष",
                      "Jupiter is conjunct Rahu/Ketu.", "गुरु राहु/केतु के साथ।",
                      ["Jupiter"], kind="dosha"))

    # Angarak
    if ctx.conj("Mars", "Rahu") or ctx.conj("Mars", "Ketu"):
        out.append(_y("Angarak Dosha", "अंगारक दोष", "Mars is conjunct Rahu/Ketu.",
                      "मंगल राहु/केतु के साथ।", ["Mars"], kind="dosha"))

    # Shrapit
    if ctx.conj("Saturn", "Rahu"):
        out.append(_y("Shrapit Dosha", "श्रापित दोष", "Saturn conjunct Rahu.",
                      "शनि राहु के साथ।", ["Saturn", "Rahu"], kind="dosha"))

    return out
