"""Ephemeris layer.

Primary engine: NASA JPL ephemeris (DE440s) through Skyfield -- pure Python,
sub-arcsecond accuracy, no compiler needed.

If the optional ``pyswisseph`` package is importable AND the environment
variable ``ASTRO_USE_SWISSEPH=1`` is set, the Swiss Ephemeris is used instead
(identical output interface).  See README.
"""
from __future__ import annotations

import math
import os
from functools import lru_cache

from skyfield.api import load
from skyfield.framelib import ecliptic_frame

from . import constants as C

# ---------------------------------------------------------------------------
# Ephemeris files
# ---------------------------------------------------------------------------
_HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(_HERE, "data")
_EPH_CANDIDATES = ["de440s.bsp", "de421.bsp", "de440.bsp"]
_JPL_URL = "https://ssd.jpl.nasa.gov/ftp/eph/planets/bsp/de440s.bsp"


@lru_cache(maxsize=1)
def _load():
    ts = load.timescale()
    # 1) use a .bsp already on disk -- the data dir first, then the working dir
    for name in _EPH_CANDIDATES:
        for d in (DATA_DIR, os.getcwd()):
            p = os.path.join(d, name)
            if os.path.exists(p):
                return ts, load(p)
    # 2) download it into the data dir, then open it
    os.makedirs(DATA_DIR, exist_ok=True)
    dest = os.path.join(DATA_DIR, "de440s.bsp")
    try:
        load.download(_JPL_URL, dest)
    except Exception:
        pass
    if os.path.exists(dest):
        return ts, load(dest)
    # 3) last resort: let Skyfield fetch and open it itself
    return ts, load("de440s.bsp")


# planets we compute (geocentric).  Rahu/Ketu are derived from the lunar node.
# de440s carries the outer planets only as barycenters.
_BODY_KEYS = {
    "Sun": "Sun", "Moon": "Moon", "Mercury": "Mercury", "Venus": "Venus",
    "Mars": "Mars Barycenter", "Jupiter": "Jupiter Barycenter",
    "Saturn": "Saturn Barycenter", "Uranus": "Uranus Barycenter",
    "Neptune": "Neptune Barycenter", "Pluto": "Pluto Barycenter",
}


def _earth():
    _, eph = _load()
    return eph["Earth"]


def _body(name):
    _, eph = _load()
    return eph[_BODY_KEYS[name]]


# ---------------------------------------------------------------------------
# Angle helpers
# ---------------------------------------------------------------------------
def norm360(x: float) -> float:
    return x % 360.0


def mean_obliquity(jd_tt: float) -> float:
    """Mean obliquity of the ecliptic in degrees (Meeus 22.2)."""
    T = (jd_tt - 2451545.0) / 36525.0
    secs = (21.448 - 46.8150 * T - 0.00059 * T * T + 0.001813 * T ** 3)
    return 23.0 + (26.0 + secs / 60.0) / 60.0


def lahiri_ayanamsa(jd_tt: float) -> float:
    """Lahiri / Chitrapaksha ayanamsa in degrees.

    Anchored on the official Lahiri value at J2000.0 (23d51'11.6") and
    advanced with the IAU-2006 general precession in longitude.
    """
    T = (jd_tt - 2451545.0) / 36525.0
    p_A = (5028.796195 * T + 1.1054348 * T ** 2 + 0.00007964 * T ** 3
           - 0.000023857 * T ** 4 - 0.0000000383 * T ** 5)  # arcsec
    return 23.853222 + p_A / 3600.0


# ---------------------------------------------------------------------------
# Positions
# ---------------------------------------------------------------------------
def _geocentric_lon(body_name: str, t):
    app = _earth().at(t).observe(_body(body_name)).apparent()
    _lat, lon, _dist = app.frame_latlon(ecliptic_frame)
    return norm360(lon.degrees)


def _ecl_xyz(body_name: str, t):
    app = _earth().at(t).observe(_body(body_name)).apparent()
    p = app.frame_xyz(ecliptic_frame)
    return p.au  # numpy array [x, y, z] in AU, ecliptic of date


def mean_node(jd_tt: float) -> float:
    """Mean lunar node (Rahu) longitude, tropical, degrees (Meeus 47.7).

    Vedic astrology uses the *mean* node for Rahu/Ketu (the true/osculating
    node can differ by up to ~1.5 degrees and flips the house when Ketu sits
    on a sign boundary).
    """
    T = (jd_tt - 2451545.0) / 36525.0
    omega = (125.0445479 - 1934.1362891 * T + 0.0020754 * T * T
             + T ** 3 / 467441.0 - T ** 4 / 60616000.0)
    return norm360(omega)


def true_node(t) -> float:
    """True (osculating) lunar node longitude, ecliptic of date, degrees."""
    import numpy as np
    dt = 0.01  # days
    ts, _ = _load()
    t2 = ts.tt_jd(t.tt + dt)
    r1 = np.array(_ecl_xyz("Moon", t))
    r2 = np.array(_ecl_xyz("Moon", t2))
    v = (r2 - r1) / dt
    h = np.cross(r1, v)               # orbital angular momentum
    z = np.array([0.0, 0.0, 1.0])     # ecliptic pole of date
    n = np.cross(z, h)                # ascending node direction
    lon = math.degrees(math.atan2(n[1], n[0]))
    return norm360(lon)


def build_time(year, month, day, hour, minute, second=0.0):
    """Build a Skyfield Time from a UTC calendar date."""
    ts, _ = _load()
    return ts.utc(year, month, day, hour, minute, second)


def compute_positions(t):
    """Return tropical ecliptic longitudes (of date) for all planets.

    ``t`` is a Skyfield Time.  Returns dict name -> degrees.
    """
    out = {}
    for name in _BODY_KEYS:
        out[name] = _geocentric_lon(name, t)
    out["Rahu"] = mean_node(t.tt)          # mean node (standard for Vedic)
    out["Ketu"] = norm360(out["Rahu"] + 180.0)
    return out


# ---------------------------------------------------------------------------
# Ascendant / houses
# ---------------------------------------------------------------------------
def _ra_to_lon(ra_deg: float, eps_deg: float) -> float:
    ra = math.radians(ra_deg)
    eps = math.radians(eps_deg)
    return norm360(math.degrees(math.atan2(math.sin(ra), math.cos(ra) * math.cos(eps))))


def _decl_of_ra(ra_deg: float, eps_deg: float) -> float:
    ra = math.radians(ra_deg)
    eps = math.radians(eps_deg)
    return math.degrees(math.atan(math.tan(eps) * math.sin(ra)))


def ascendant(ramc_deg: float, eps_deg: float, lat_deg: float) -> float:
    ramc = math.radians(ramc_deg)
    eps = math.radians(eps_deg)
    phi = math.radians(lat_deg)
    lam = math.atan2(math.cos(ramc),
                     -(math.sin(ramc) * math.cos(eps) + math.tan(phi) * math.sin(eps)))
    return norm360(math.degrees(lam))


def midheaven(ramc_deg: float, eps_deg: float) -> float:
    return _ra_to_lon(ramc_deg, eps_deg)


def placidus_cusps(ramc_deg: float, eps_deg: float, lat_deg: float) -> dict:
    """Placidus house cusps (tropical), keys 1..12."""
    phi = math.radians(lat_deg)

    def sa(ra):  # semi-diurnal arc (deg)
        d = math.radians(_decl_of_ra(ra, eps_deg))
        x = -math.tan(phi) * math.tan(d)
        x = max(-1.0, min(1.0, x))
        return math.degrees(math.acos(x))

    def na(ra):  # semi-nocturnal arc (deg)
        return 180.0 - sa(ra)

    cusps = {}
    cusps[10] = midheaven(ramc_deg, eps_deg)
    cusps[1] = ascendant(ramc_deg, eps_deg, lat_deg)
    cusps[4] = norm360(cusps[10] + 180)
    cusps[7] = norm360(cusps[1] + 180)

    # cusp 11 and 12 (east, above horizon): fractions of own semi-diurnal arc
    for cusp, frac in ((11, 1.0 / 3.0), (12, 2.0 / 3.0)):
        ra = ramc_deg + 30.0 * (1 if cusp == 11 else 2)
        for _ in range(100):
            ra_new = ramc_deg + frac * sa(ra)
            if abs(ra_new - ra) < 1e-10:
                ra = ra_new
                break
            ra = ra_new
        cusps[cusp] = _ra_to_lon(ra, eps_deg)

    # cusp 2 and 3 (east, below horizon): fractions of own semi-nocturnal arc
    for cusp, frac in ((2, 2.0 / 3.0), (3, 1.0 / 3.0)):
        ra = ramc_deg + 120.0
        for _ in range(100):
            ra_new = ramc_deg + 180.0 - frac * na(ra)
            if abs(ra_new - ra) < 1e-10:
                ra = ra_new
                break
            ra = ra_new
        cusps[cusp] = _ra_to_lon(ra, eps_deg)

    # opposite cusps
    cusps[5] = norm360(cusps[11] + 180)
    cusps[6] = norm360(cusps[12] + 180)
    cusps[8] = norm360(cusps[2] + 180)
    cusps[9] = norm360(cusps[3] + 180)
    return cusps


# ---------------------------------------------------------------------------
# Nakshatra / pada helpers
# ---------------------------------------------------------------------------
def nakshatra_of(lon: float) -> dict:
    span = 360.0 / 27.0
    idx = int(lon // span) % 27
    within = lon - idx * span
    pada = int(within // (span / 4)) + 1
    return {
        "index": idx,
        "name_en": C.NAKSHATRAS_EN[idx],
        "name_hi": C.NAKSHATRAS_HI[idx],
        "lord": C.NAKSHATRA_LORDS[idx],
        "pada": pada,
    }


def sign_of(lon: float) -> dict:
    idx = int(lon // 30) % 12
    return {
        "index": idx,
        "name_en": C.SIGNS_EN[idx],
        "name_hi": C.SIGNS_HI[idx],
        "deg_in_sign": lon - idx * 30.0,
        "lord": C.SIGN_LORDS[idx],
    }


# ---------------------------------------------------------------------------
# Extra helpers (sunrise/sunset, latitudes, sign-entry search)
# ---------------------------------------------------------------------------
def _place(lat, lon):
    from skyfield.api import wgs84
    _, eph = _load()
    return eph["Earth"] + wgs84.latlon(lat, lon)


def geocentric_ecl(body_name: str, t):
    """Return (longitude, latitude) in the ecliptic of date, degrees."""
    app = _earth().at(t).observe(_body(body_name)).apparent()
    lat, lon, _dist = app.frame_latlon(ecliptic_frame)
    return norm360(lon.degrees), lat.degrees


def sun_times(year, month, day, lat, lon, tz_offset_hours=0.0):
    """Return (sunrise, sunset) as Skyfield Times for the local civil day."""
    from skyfield import almanac
    from skyfield.api import wgs84
    ts, eph = _load()
    topos = wgs84.latlon(lat, lon)
    # search window: local midnight +/- 1 day in UTC
    t0 = ts.utc(year, month, day, -tz_offset_hours)
    t1 = ts.utc(year, month, day + 1, -tz_offset_hours)
    f = almanac.sunrise_sunset(eph, topos)
    times, events = almanac.find_discrete(t0, t1, f)
    sr = ss = None
    for tm, ev in zip(times, events):
        if ev == 1 and sr is None:
            sr = tm
        elif ev == 0 and sr is not None:
            ss = tm
            break
    if sr is None:
        for tm, ev in zip(times, events):
            if ev == 1:
                sr = tm
            elif ev == 0:
                ss = tm
    return sr, ss


def sun_sidereal_lon(t):
    lon = _geocentric_lon("Sun", t)
    return norm360(lon - lahiri_ayanamsa(t.tt))


_MEAN_SUN_RATE = 0.98564736  # degrees per day


def find_sun_sign_entry(target_sign: int, t_before, ts=None):
    """Most recent time (<= t_before) when sidereal Sun entered ``target_sign``.

    ``target_sign`` 0..11 (0 = Aries).  Returns a Skyfield Time.

    Uses a Newton-style estimate from the Sun's mean motion -- only a handful
    of ephemeris evaluations instead of a long day-by-day scan.
    """
    if ts is None:
        ts, _ = _load()
    target = target_sign * 30.0

    def diff(t):
        return (sun_sidereal_lon(t) - target) % 360.0  # 0 at the entry, grows after

    # first estimate: days since the entry (Sun covers ~0.9856 deg/day)
    t = ts.tt_jd(t_before.tt - diff(t_before) / _MEAN_SUN_RATE)
    # refine -- the Sun's true rate varies a little through the year
    for _ in range(4):
        e = diff(t)
        if e > 180.0:      # we landed *before* the entry -> move forward
            e -= 360.0
        t = ts.tt_jd(t.tt - e / _MEAN_SUN_RATE)
    return t
