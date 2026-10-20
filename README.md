# Jyotish Studio

An online (web) astrology application: enter **DOB / TOB / POB** and get a
complete chart — divisional charts D1–D60, Vimshottari dasha, Shadbala,
Ashtakavarga, Yogas & Doshas, the full KP system, Lal Kitab, Nadi (D150) with
progression, transits-ready positions, Jaimini Chara Karakas, Numerology and
Tarot. Bilingual UI (English / हिंदी).

```
astroweb/
  app.py                Flask app + JSON API
  engine/               the astrology engine (pure Python)
    ephemeris.py        positions, ayanamsa, ascendant, Placidus cusps
    divisional.py       D1..D60 vargas
    dasha.py            Vimshottari (Maha/Antar/Pratyantar/…)
    shadbala.py         six-fold strength
    ashtakavarga.py     BAV / SAV + shodhana
    yogas.py            yogas & doshas
    kp.py               KP cusps, sub-lords, significators, ruling planets
    jaimini.py          chara karakas, karakamsa, arudha, chara dasha
    lalkitab.py         pakka ghar, blind/sleeping, remedies
    nadi.py             Nadi Amsa (D150) + progression
    numerology.py       Pythagorean + Chaldean
    tarot.py            78-card deck & spreads
    chart.py            assembles the full chart
  templates/index.html  UI
  static/               css + js (bilingual)
  data/cities.json      ~180 built-in cities (lat/lon/tz)
  data/de440s.bsp       JPL ephemeris (1849–2150)
```

## Run locally

```bash
pip install -r requirements.txt
python app.py            # http://localhost:5000
```

## Deploy (make it "online")

Any Python host works — the app is a standard Flask app.

* **Render / Railway / Fly.io:** start command `gunicorn app:app --bind 0.0.0.0:$PORT`,
  build command `pip install -r requirements.txt`.
* **PythonAnywhere / VPS:** `pip install -r requirements.txt` then run behind
  gunicorn/nginx.
* **Docker:** `FROM python:3.12-slim`, copy the folder, `pip install -r requirements.txt`,
  `CMD gunicorn app:app --bind 0.0.0.0:8000`.

If you deploy *without* `data/de440s.bsp`, the engine downloads it automatically
on first use (needs outbound internet once).

## Accuracy & engine

* **Ephemeris:** NASA JPL **DE440s** via [Skyfield](https://rhodesmill.org/skyfield/)
  — sub-arcsecond, no compiler required. If you have a C toolchain you may switch
  to **Swiss Ephemeris** (`pyswisseph`); the engine interface is unchanged.
  Validated against the 2024 equinox (0.000° error) and Makar Sankranti 2024
  (computed 02:40 IST vs published 02:43 IST).
* **Ayanamsa:** Lahiri / Chitrapaksha, anchored on the official J2000 value
  (23°51'11.6") and advanced with IAU-2006 general precession.
* **Bhavas:** whole-sign houses for Parashari work; **Placidus** cusps for KP.
* **Ashtakavarga** totals are checked against the canonical 48/49/39/54/56/52/39
  = **337** bindus.

### Varga conventions (they differ between traditions)

D1 identity; D2 hora (odd→Leo/Cancer, even→Cancer/Leo); D3 +0/+4/+8; D4 +0/+3/+6/+9;
D5,D6,D8,D11 counted from Aries (odd) / Libra (even); D7 from the sign (odd) / 7th (even);
D9 & D27 continuous from Aries; D10 from the sign (odd) / 9th (even);
D12 from the sign; D16 & D45 movable→Aries, fixed→Leo, dual→Sagittarius;
D20 movable→Aries, fixed→Sagittarius, dual→Leo; D24 odd→Leo, even→Cancer;
D30 trimsamsa (unequal); D40 from Aries (odd) / Libra (even); D60 from the sign.
Adjust `engine/divisional.py` if your tradition differs.

## Honest scope notes

* **Shadbala** covers Sthana, Dig, Kala (Nathonnatha, Paksha, Tribhaga, Varsha,
  Masa, Dina, Hora, Ayana), Cheshta, Naisargika and Drik. Yuddha bala is not applied.
* **Lal Kitab** implements the framework (pakka ghar, exaltation by house,
  Lal Kitab friendships, sleeping/blind charts, debts, general remedies). The full
  108 planet-in-house effect tables vary by edition and are not reproduced.
* **Nadi:** the classical palm-leaf Nadi is a manuscript-lookup system and is *not*
  derivable from a birth chart. This app computes the derivable **Nadi Amsa (D150)**
  and an annual Nadi progression.
* **Transits:** the engine gives accurate transit positions for any date; add a
  transit view by calling `engine.ephemeris` for the target date.
* **Tarot** is a random draw with meanings — entertainment, not prediction.

## Disclaimer

Jyotish, KP, Lal Kitab, Nadi, numerology and tarot are traditional systems.
This software computes and presents them for study and personal interest; it is
not a substitute for professional advice of any kind.
