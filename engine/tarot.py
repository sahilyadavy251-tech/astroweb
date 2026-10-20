"""Tarot reading: 78-card deck, spreads, upright/reversed meanings."""
from __future__ import annotations

import random

MAJOR = [
    ("The Fool", "मूर्ख", "New beginnings, innocence, leap of faith, spontaneity."),
    ("The Magician", "जादूगर", "Manifestation, skill, willpower, resourcefulness."),
    ("The High Priestess", "पुरोहिता", "Intuition, mystery, inner knowledge, patience."),
    ("The Empress", "साम्राज्ञी", "Fertility, nurture, abundance, creativity."),
    ("The Emperor", "सम्राट", "Authority, structure, stability, fatherly control."),
    ("The Hierophant", "धर्मगुरु", "Tradition, guidance, conformity, teaching."),
    ("The Lovers", "प्रेमी", "Love, union, choice, alignment of values."),
    ("The Chariot", "रथ", "Determination, victory, will, forward drive."),
    ("Strength", "बल", "Courage, patience, inner strength, compassion."),
    ("The Hermit", "सन्यासी", "Introspection, solitude, inner guidance, search."),
    ("Wheel of Fortune", "भाग्य चक्र", "Cycles, destiny, turning point, luck."),
    ("Justice", "न्याय", "Balance, truth, cause and effect, fairness."),
    ("The Hanged Man", "लटकता मनुष्य", "Pause, surrender, new perspective, sacrifice."),
    ("Death", "मृत्यु", "Endings, transformation, transition, letting go."),
    ("Temperance", "संयम", "Balance, moderation, patience, healing."),
    ("The Devil", "शैतान", "Bondage, temptation, materialism, attachment."),
    ("The Tower", "मीनार", "Sudden change, upheaval, revelation, awakening."),
    ("The Star", "तारा", "Hope, faith, inspiration, serenity."),
    ("The Moon", "चन्द्रमा", "Illusion, fear, subconscious, uncertainty."),
    ("The Sun", "सूर्य", "Success, joy, vitality, clarity."),
    ("Judgement", "निर्णय", "Rebirth, reckoning, awakening, inner calling."),
    ("The World", "संसार", "Completion, fulfilment, wholeness, travel."),
]

SUITS = [
    ("Wands", "चोब", "action, energy, creativity, passion"),
    ("Cups", "कप", "emotion, love, relationships, intuition"),
    ("Swords", "तलवार", "thought, conflict, truth, intellect"),
    ("Pentacles", "सिक्के", "material, money, work, body"),
]
RANKS = ["Ace", "Two", "Three", "Four", "Five", "Six", "Seven", "Eight",
         "Nine", "Ten", "Page", "Knight", "Queen", "King"]
RANK_MEAN = {
    "Ace": "a new seed / opportunity", "Two": "balance and choice",
    "Three": "growth and collaboration", "Four": "stability and consolidation",
    "Five": "conflict and challenge", "Six": "harmony and giving",
    "Seven": "assessment and patience", "Eight": "movement and mastery",
    "Nine": "near fulfilment", "Ten": "culmination",
    "Page": "a beginner / a message", "Knight": "a quest / momentum",
    "Queen": "mature inward mastery", "King": "mature outward mastery",
}

SPREADS = {
    "three": [("Past", "अतीत"), ("Present", "वर्तमान"), ("Future", "भविष्य")],
    "career": [("Situation", "स्थिति"), ("Action", "कर्म"), ("Outcome", "परिणाम")],
    "celtic": [("Present", "वर्तमान"), ("Challenge", "चुनौती"), ("Past", "अतीत"),
               ("Future", "भविष्य"), ("Above", "चेतना"), ("Below", "अवचेतन"),
               ("Advice", "सलाह"), ("External", "वाह्य प्रभाव"), ("Hopes/Fears", "आशा/भय"),
               ("Outcome", "परिणाम")],
}


def deck():
    d = [{"card": m[0], "card_hi": m[1], "meaning": m[2], "arcana": "Major"} for m in MAJOR]
    for suit, suit_hi, theme in SUITS:
        for rank in RANKS:
            d.append({
                "card": f"{rank} of {suit}", "card_hi": f"{suit_hi} का {rank}",
                "meaning": f"{RANK_MEAN[rank]} in matters of {theme}.",
                "arcana": "Minor",
            })
    return d


def draw(spread="three", seed=None):
    rng = random.Random(seed)
    cards = deck()
    rng.shuffle(cards)
    positions = SPREADS.get(spread, SPREADS["three"])
    out = []
    for i, (pos_en, pos_hi) in enumerate(positions):
        c = cards[i]
        reversed_ = rng.random() < 0.35
        out.append({
            "position_en": pos_en, "position_hi": pos_hi,
            "card": c["card"], "card_hi": c["card_hi"], "arcana": c["arcana"],
            "reversed": reversed_,
            "meaning_en": ("(reversed) " if reversed_ else "") + c["meaning"],
        })
    return {"spread": spread, "cards": out}
