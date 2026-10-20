"""Lal Kitab system.

House-based (rasi = house number) reading: pakka ghar (permanent houses),
Lal Kitab friendships, exaltation/debilitation by house, sleeping planets,
blind/half-blind charts, dharmi planets, and general remedies (upay).
"""
from __future__ import annotations

NINE = ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn", "Rahu", "Ketu"]

PAKKA_GHAR = {
    "Sun": [1], "Moon": [4], "Mars": [3, 8], "Mercury": [7],
    "Jupiter": [2, 5, 9, 11], "Venus": [7], "Saturn": [8, 10],
    "Rahu": [12], "Ketu": [6],
}

LAL_EXALT = {"Sun": 1, "Moon": 2, "Mars": 10, "Mercury": 6, "Jupiter": 4,
             "Venus": 12, "Saturn": 7, "Rahu": 3, "Ketu": 9}
LAL_DEBIL = {"Sun": 7, "Moon": 8, "Mars": 4, "Mercury": 12, "Jupiter": 10,
             "Venus": 6, "Saturn": 1, "Rahu": 9, "Ketu": 3}

FRIENDS = {
    "Sun": ["Jupiter", "Mars", "Moon"], "Moon": ["Sun", "Mercury"],
    "Mars": ["Sun", "Moon", "Jupiter"], "Mercury": ["Sun", "Venus", "Rahu"],
    "Jupiter": ["Sun", "Moon", "Mars"], "Venus": ["Saturn", "Mercury", "Ketu"],
    "Saturn": ["Mercury", "Venus", "Rahu"], "Rahu": ["Mercury", "Ketu", "Saturn"],
    "Ketu": ["Venus", "Rahu"],
}
ENEMIES = {
    "Sun": ["Venus", "Saturn", "Rahu", "Ketu"], "Moon": ["Rahu", "Ketu"],
    "Mars": ["Mercury", "Ketu"], "Mercury": ["Moon"],
    "Jupiter": ["Venus", "Mercury"], "Venus": ["Sun", "Moon", "Rahu"],
    "Saturn": ["Sun", "Moon", "Mars"], "Rahu": ["Sun", "Venus", "Mars"],
    "Ketu": ["Moon", "Mars"],
}

REMEDIES = {
    "Sun": ["Offer water to the rising Sun daily.", "Donate wheat, jaggery or copper on Sundays.",
            "Serve your father / elders; respect them."],
    "Moon": ["Offer milk or rice on Mondays; keep a silver item with you.",
             "Serve your mother; keep the mind calm and clean."],
    "Mars": ["Donate red lentils (masoor) or jaggery on Tuesdays.",
             "Avoid anger; help siblings and the needy."],
    "Mercury": ["Donate green gram (moong) on Wednesdays; feed green fodder to a cow.",
                "Respect sisters and students; keep speech truthful."],
    "Jupiter": ["Donate turmeric, chana dal or yellow cloth on Thursdays.",
                "Serve teachers and elders; plant a peepal/banyan tree."],
    "Venus": ["Donate white items (rice, milk, silver) on Fridays.",
              "Respect women; keep commitments in relationships."],
    "Saturn": ["Serve the poor, elderly and labourers; donate black sesame or mustard oil on Saturdays.",
               "Feed crows / stray dogs; be punctual and disciplined."],
    "Rahu": ["Donate black gram or blue cloth; keep an iron item.",
             "Avoid intoxicants; do not deceive others."],
    "Ketu": ["Donate blankets or mixed grains; feed stray dogs.",
             "Keep a dog at home if advised; avoid unnecessary disputes."],
}


def _sign(lon):
    return int((lon % 360) // 30)


def _house(asc_sign, sign):
    return ((sign - asc_sign) % 12) + 1


def compute(pos, asc):
    asc_sign = _sign(asc)
    house = {p: _house(asc_sign, _sign(pos[p])) for p in NINE}
    planets_in = {h: [] for h in range(1, 13)}
    for p in NINE:
        planets_in[house[p]].append(p)

    per_planet = {}
    for p in NINE:
        h = house[p]
        at_home = h in PAKKA_GHAR[p]
        # Lal Kitab aspect: 7th (full), 4th & 10th (full), 3/5/9/11 (half)
        aspected = {((h - 1 + k) % 12) + 1 for k in (3, 6, 9)}  # 4th,7th,10th
        sees = [q for q in NINE if q != p and house[q] in aspected]
        sleeping = (not at_home) and (not sees)
        per_planet[p] = {
            "house": h,
            "pakka_ghar": PAKKA_GHAR[p],
            "at_home": at_home,
            "exalted": h == LAL_EXALT[p],
            "debilitated": h == LAL_DEBIL[p],
            "friends_here": [q for q in planets_in[h] if q in FRIENDS[p]],
            "enemies_here": [q for q in planets_in[h] if q in ENEMIES[p]],
            "sleeping": sleeping,
            "sees": sees,
        }

    # blind / half-blind
    blind = False
    tenth = planets_in[10]
    enemy_pairs = 0
    for i in range(len(tenth)):
        for j in range(i + 1, len(tenth)):
            a, b = tenth[i], tenth[j]
            if b in ENEMIES.get(a, []) or a in ENEMIES.get(b, []):
                enemy_pairs += 1
            if tenth[i] in LAL_DEBIL and house[tenth[i]] == LAL_DEBIL[tenth[i]]:
                enemy_pairs += 1
    if enemy_pairs > 0:
        blind = True
    half_blind = (house["Sun"] == 4 and house["Saturn"] == 7)

    # dharmi planets
    dharmi = []
    if house["Saturn"] == 11 or (house["Jupiter"] == house["Saturn"]):
        dharmi.append("Saturn")
    if house["Rahu"] == 4 or house["Rahu"] == house["Moon"]:
        dharmi.append("Rahu")
    if house["Ketu"] == 4 or house["Ketu"] == house["Moon"]:
        dharmi.append("Ketu")

    # debts (rin) -- commonly cited checks
    debts = []
    if house["Rahu"] == 9 or (house["Sun"] == house["Rahu"]) or (house["Sun"] == house["Ketu"]):
        debts.append("Pitri Rin (ancestral debt)")
    if house["Saturn"] == 2 or house["Moon"] == house["Saturn"]:
        debts.append("Rin of the Moon/Saturn (family/emotional debt)")
    if house["Venus"] == 6 or house["Venus"] == house["Rahu"]:
        debts.append("Rin related to Venus (relationships/comforts)")

    return {
        "chart": {p: house[p] for p in NINE},
        "planets_in_house": {h: planets_in[h] for h in range(1, 13)},
        "planets": per_planet,
        "blind_chart": blind,
        "half_blind_chart": half_blind,
        "dharmi_planets": dharmi,
        "debts": debts,
        "remedies": REMEDIES,
        "note": ("Lal Kitab reads rasi = house number. Pakka ghar, exaltation and "
                 "aspect rules follow the classical Lal Kitab; editions vary."),
    }
