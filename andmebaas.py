import json
import os

# --- KONSTANDID (Muutumatud väärtused) ---

# CSV faili veergude nimed ja nende järjekord
ALL_COLUMNS = ["Timestamp", "Kuupäev", "Summa", "Tulu/kulu", "Kategooria", "Kaupmees", "Kirjeldus"]

# Kategooriad sissetulekute jaoks (kasutatakse sisestamisvormil)
TULU_KATEGOORIAD = ["Palk", "Investeeringud", "Lisatöö", "Toetused", "Muu tulu"]

# --- ANDMEBAAS (Kaupmehed ja kulukategooriad) ---

# Vaikimisi andmebaas. 
# "categories": nimekiri võimalikest kulukategooriatest.
# "merchants": sõnastik, mis seob kaupmehe nime vaikimisi kategooriaga.
DEFAULT_DB = {
    "categories": [
        "Söök ja jook",
        "Meelelahutus",
        "Kommunaalid",
        "Laenud",
        "Transport",
        "Kodu",
        "Investeerimised",
        "Muu",
        "Laps",
        "Tervis",
        "Riided",
        "Iluteenused"
    ],
    "merchants": {
        "Rimi": "Söök ja jook",
        "Selver": "Söök ja jook",
        "Maxima": "Söök ja jook",
        "COOP": "Söök ja jook",
        "Bolt": "Söök ja jook",
        "Wolt": "Söök ja jook",
        "Apollo": "Meelelahutus",
        "Spotify": "Meelelahutus",
        "Netflix": "Meelelahutus",
        "Elektrum": "Kommunaalid",
        "Tartu Veevärk": "Kommunaalid",
        "Alexela": "Transport",
        "Circle K": "Transport",
        "IKEA": "Kodu",
        "Swedbank": "Laenud",
        "LHV": "Laenud", 
        "SEB": "Laenud", 
        "III sammas": "Investeerimised",
        "Lapse riided": "Laps",
        "Riided": "Riided",
        "Mikroinvesteerimine": "Investeerimised",
        "Luminor": "Laenud"
    }
}

def load_db():
    """
    Tagastab andmebaasi sõnastiku.
    """
    return DEFAULT_DB
