"""Download the JPL ephemeris into data/ (run at build time; optional).

If this is skipped or fails, the app downloads it automatically on first use.
"""
import os

from skyfield.api import load

URL = "https://ssd.jpl.nasa.gov/ftp/eph/planets/bsp/de440s.bsp"
DEST = os.path.join("data", "de440s.bsp")


def main():
    os.makedirs("data", exist_ok=True)
    if os.path.exists(DEST):
        print("Ephemeris already present:", DEST)
        return
    print("Downloading ephemeris ->", DEST)
    load.download(URL, DEST)
    print("Done:", os.path.getsize(DEST), "bytes")


if __name__ == "__main__":
    main()
