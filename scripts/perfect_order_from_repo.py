import os
import requests
import pandas as pd
from datetime import datetime

BASE_RAW = "https://raw.githubusercontent.com/PokemonTCG/pokemon-tcg-data/master"
SET_ID = "me3"
SET_NAME = "Perfect Order"
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

def fetch_cards():
    url = f"{BASE_RAW}/cards/en/{SET_ID}.json"
    r = requests.get(url, timeout=30)
    r.raise_for_status()
    return r.json()

def write_csv(cards):
    os.makedirs(CSV_DIR, exist_ok=True)
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
        row = [img_name, card.get('id'), card.get('name'), card.get('supertype'), types, SET_NAME, card.get('number'), card.get('rarity'), large, small] + prices
        rows.append(row)

    df = pd.DataFrame(rows, columns=COLS)
    base_name = SET_NAME
    out_name = f"{base_name}.csv"
    out_path = os.path.join(CSV_DIR, out_name)
    if os.path.exists(out_path):
        ts = datetime.now().strftime('%Y%m%d_%H%M%S')
        out_name = f"{base_name}_{ts}.csv"
        out_path = os.path.join(CSV_DIR, out_name)
    df.to_csv(out_path, index=False)
    return out_path

def main():
    cards = fetch_cards()
    path = write_csv(cards)
    print(f"Wrote {path} with {len(cards)} cards (image URLs only).")

if __name__ == '__main__':
    main()
