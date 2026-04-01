import os
import requests
import json
import pandas as pd
from time import sleep

BASE_RAW = "https://raw.githubusercontent.com/PokemonTCG/pokemon-tcg-data/master"
CSV_DIR = os.path.join(os.getcwd(), "csv_new")
IMG_ROOT = os.path.join(os.getcwd(), "images")

COLS = [
    "Image_Names", "Card_ID", "Card_Name", "Super_Type", "Types", "Set_Name", "Number", "Rarity",
    "Large_Image_URL", "Small_Image_URL",
    "Normal_low", "Normal_mid", "Normal_high", "Normal_market", "Normal_directLow",
    "Holofoil_low", "Holofoil_mid", "Holofoil_high", "Holofoil_market", "Holofoil_directLow",
    "ReverseHolofoil_low", "ReverseHolofoil_mid", "ReverseHolofoil_high", "ReverseHolofoil_market", "ReverseHolofoil_directLow",
    "FirstEditionHolofoil_low", "FirstEditionHolofoil_mid", "FirstEditionHolofoil_high", "FirstEditionHolofoil_market", "FirstEditionHolofoil_directLow",
    "FirstEditionNormal_low", "FirstEditionNormal_mid", "FirstEditionNormal_high", "FirstEditionNormal_market", "FirstEditionNormal_directLow"
]

def safe_name(name):
    return name.replace(":", "")

def ensure_dirs():
    os.makedirs(CSV_DIR, exist_ok=True)
    os.makedirs(IMG_ROOT, exist_ok=True)

def fetch_json(url):
    r = requests.get(url, timeout=30)
    r.raise_for_status()
    return r.json()

def download_image(url, path):
    try:
        r = requests.get(url, timeout=30)
        r.raise_for_status()
        with open(path, "wb") as f:
            f.write(r.content)
    except Exception:
        pass

def main():
    ensure_dirs()

    sets_url = f"{BASE_RAW}/sets/en.json"
    sets = fetch_json(sets_url)

    # existing csv set names
    existing = set([f for f in os.listdir(CSV_DIR) if f.lower().endswith('.csv')])

    # record newly created CSVs this run
    new_csvs = []

    for s in sets:
        set_name = s.get('name')
        csv_filename = safe_name(set_name) + ".csv"
        if csv_filename in existing:
            continue

        set_id = s.get('id')
        cards_url = f"{BASE_RAW}/cards/en/{set_id}.json"
        try:
            cards = fetch_json(cards_url)
        except Exception:
            # skip sets with no card file
            continue

        rows = []
        img_dir = os.path.join(IMG_ROOT, set_name)
        os.makedirs(img_dir, exist_ok=True)

        for i, card in enumerate(cards):
            img_name = f"{i:03d}.jpg"
            images = card.get('images', {})
            large = images.get('large') or images.get('hires')
            small = images.get('small')
            if large:
                download_image(large, os.path.join(img_dir, img_name))
            elif small:
                download_image(small, os.path.join(img_dir, img_name))

            types = card.get('types')
            if types:
                types = "__".join(types)

            # prices not in repo JSON, keep empty columns to match layout
            prices = [None] * 25

            row = [img_name, card.get('id'), card.get('name'), card.get('supertype'), types, set_name, card.get('number'), card.get('rarity'), large, small] + prices
            rows.append(row)

        df = pd.DataFrame(rows, columns=COLS)
        out_path = os.path.join(CSV_DIR, csv_filename)
        df.to_csv(out_path, index=False)
        print(f"Wrote {out_path} ({len(rows)} cards)")

        new_csvs.append({
            "csv": csv_filename,
            "set_name": set_name,
            "cards": len(rows)
        })

        # be polite to raw.githubusercontent
        sleep(0.5)

    return new_csvs


if __name__ == '__main__':
    created = main()
    # After run: write artifact listing newly created CSVs (if any)
    artifacts_dir = os.path.join(os.getcwd(), "artifacts")
    os.makedirs(artifacts_dir, exist_ok=True)
    artifact_path = os.path.join(artifacts_dir, "new_csvs.json")
    try:
        with open(artifact_path, "w", encoding="utf-8") as af:
            json.dump({"new_csvs": created}, af, ensure_ascii=False, indent=2)
        print(f"Wrote artifact: {artifact_path}")
    except Exception as e:
        print(f"Failed to write artifact: {e}")
