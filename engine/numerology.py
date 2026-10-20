"""Numerology (Pythagorean + Chaldean) and number meanings."""
from __future__ import annotations

PYTHAGOREAN = {}
for i, ch in enumerate("ABCDEFGHIJKLMNOPQRSTUVWXYZ"):
    PYTHAGOREAN[ch] = (i % 9) + 1

CHALDEAN = {
    "A": 1, "B": 2, "C": 3, "D": 4, "E": 5, "F": 8, "G": 3, "H": 5, "I": 1,
    "J": 1, "K": 2, "L": 3, "M": 4, "N": 5, "O": 7, "P": 8, "Q": 1, "R": 2,
    "S": 3, "T": 4, "U": 6, "V": 6, "W": 6, "X": 5, "Y": 1, "Z": 7,
}

VOWELS = set("AEIOU")

RULER = {1: "Sun", 2: "Moon", 3: "Jupiter", 4: "Rahu", 5: "Mercury",
         6: "Venus", 7: "Ketu", 8: "Saturn", 9: "Mars", 11: "Moon (master)",
         22: "Rahu (master)", 33: "Jupiter (master)"}

MEANINGS = {
    1: ("Leadership, independence, originality, drive.", "नेतृत्व, स्वतंत्रता, आत्मविश्वास।"),
    2: ("Cooperation, sensitivity, diplomacy, partnership.", "सहयोग, संवेदनशीलता, कूटनीति।"),
    3: ("Expression, creativity, joy, communication.", "अभिव्यक्ति, रचनात्मकता, आनंद।"),
    4: ("Discipline, stability, hard work, order.", "अनुशासन, स्थिरता, परिश्रम।"),
    5: ("Freedom, change, adventure, versatility.", "स्वतंत्रता, परिवर्तन, बहुमुखी प्रतिभा।"),
    6: ("Responsibility, love, family, service.", "उत्तरदायित्व, प्रेम, परिवार, सेवा।"),
    7: ("Analysis, spirituality, introspection, wisdom.", "विश्लेषण, आध्यात्म, ज्ञान।"),
    8: ("Ambition, authority, material mastery, karma.", "महत्वाकांक्षा, अधिकार, भौतिक सफलता।"),
    9: ("Compassion, humanitarianism, completion.", "करुणा, मानवतावाद, पूर्णता।"),
    11: ("Master number: intuition, illumination, idealism.", "मास्टर संख्या: अंतर्ज्ञान, प्रेरणा।"),
    22: ("Master number: the master builder, large vision.", "मास्टर संख्या: महान निर्माता।"),
    33: ("Master number: the master teacher, healing love.", "मास्टर संख्या: महान शिक्षक।"),
}


def _reduce(n, keep_master=True):
    while n > 9:
        if keep_master and n in (11, 22, 33):
            return n
        n = sum(int(d) for d in str(n))
    return n


def _letters_sum(name, table):
    total = 0
    for ch in name.upper():
        if ch in table:
            total += table[ch]
    return total


def compute(full_name, day, month, year, current_year=2026):
    life_path = _reduce(_reduce(day) + _reduce(month) + _reduce(year))
    birthday = _reduce(day)
    pyth = _reduce(_letters_sum(full_name, PYTHAGOREAN))
    chald = _reduce(_letters_sum(full_name, CHALDEAN))
    vowels = sum(PYTHAGOREAN.get(c, 0) for c in full_name.upper() if c in VOWELS)
    cons = sum(PYTHAGOREAN.get(c, 0) for c in full_name.upper()
               if c.isalpha() and c not in VOWELS)
    soul = _reduce(vowels)
    personality = _reduce(cons)
    personal_year = _reduce(_reduce(day) + _reduce(month) + _reduce(current_year))

    def pack(n):
        m = MEANINGS.get(n, MEANINGS[n % 9 or 9])
        return {"number": n, "ruler": RULER.get(n, RULER[n % 9 or 9]),
                "meaning_en": m[0], "meaning_hi": m[1]}

    return {
        "life_path": pack(life_path),
        "birthday": pack(birthday),
        "expression_pythagorean": pack(pyth),
        "expression_chaldean": pack(chald),
        "soul_urge": pack(soul),
        "personality": pack(personality),
        "personal_year": pack(personal_year),
    }
