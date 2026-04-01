import os
import requests
import pandas as pd
from time import sleep

BASE_RAW = "https://raw.githubusercontent.com/PokemonTCG/pokemon-tcg-data/master"
CSV_DIR = os.path.join(os.getcwd(), "csv_new")

COLS = [
    "Image_Names", "Card_ID", "Card_Name", "Super_Type", "Types", "Set_Name", "Number", "Rarity",
    "Large_Image_URL", "Small_Image_URL",
    "Normal_low", "Normal_mid", "Normal_high", "Normal_market", "Normal_directLow",
    "Holofoil_low", "Holofoil_mid", "Holofoil_high", "Holofoil_market", "Holofoil_directLow",
    "ReverseHolofoil_low", "ReverseHolofoil_mid", "ReverseHolofoil_high", "ReverseHolofoil_market", "ReverseHolofoil_directLow",
    "FirstEditionHolofoil_low", "FirstEditionHolofoil_mid", "FirstEditionHolofoil_high", "FirstEditionHolofoil_market", "FirstEditionHolofoil_directLow",
    "FirstEditionNormal_low", "FirstEditionNormal_mid", "FirstEditionNormal_high", "FirstEditionNormal_market", "FirstEditionNormal_directLow"
]

def ensure_dirs():
    os.makedirs(CSV_DIR, exist_ok=True)

def fetch_json(url):
    r = requests.get(url, timeout=30)
    r.raise_for_status()
    return r.json()

def safe_name(name):
    return name.replace(":", "")

def main():
    ensure_dirs()
    sets_url = f"{BASE_RAW}/sets/en.json"
    sets = fetch_json(sets_url)

    existing = set([f for f in os.listdir(CSV_DIR) if f.lower().endswith('.csv')])

    for s in sets:
        set_name = s.get('name')
        csv_filename = safe_name(set_name) + ".csv"
        if csv_filename in existing:
            # skip sets that already have CSVs
            continue

        set_id = s.get('id')
        cards_url = f"{BASE_RAW}/cards/en/{set_id}.json"
        try:
            cards = fetch_json(cards_url)
        except Exception:
            continue

        rows = []
        for i, card in enumerate(cards):
            img_name = f"{i:03d}.jpg"
            images = card.get('images', {})
            large = images.get('large') or images.get('hires')
            small = images.get('small')
            types = card.get('types')
            if types:
                types = "__".join(types)
            prices = [None] * 25
            row = [img_name, card.get('id'), card.get('name'), card.get('supertype'), types, set_name, card.get('number'), card.get('rarity'), large, small] + prices
            rows.append(row)

        df = pd.DataFrame(rows, columns=COLS)
        out_path = os.path.join(CSV_DIR, csv_filename)
        df.to_csv(out_path, index=False)
        print(f"Wrote {out_path} ({len(rows)} cards)")

        sleep(0.2)

if __name__ == '__main__':
    main()
