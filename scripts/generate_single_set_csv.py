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
    "HP", "Abilities", "Attacks_JSON", "Attack_Names", "Attack_Damages", "Attack_Texts",
    "Weaknesses", "Resistances", "Retreat_Cost", "Evolves_From", "Artist", "FlavorText",
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


def generate_for_set(set_name_target="Perfect Order"):
    ensure_dirs()

    sets_url = f"{BASE_RAW}/sets/en.json"
    sets = fetch_json(sets_url)

    # find set id by name
    set_id = None
    matched_name = None
    for s in sets:
        if s.get('name') == set_name_target:
            set_id = s.get('id')
            matched_name = s.get('name')
            break

    if not set_id:
        # try case-insensitive
        for s in sets:
            if s.get('name', '').lower() == set_name_target.lower():
                set_id = s.get('id')
                matched_name = s.get('name')
                break

    if not set_id:
        print(f"Set '{set_name_target}' not found in sets/en.json")
        return None

    cards_url = f"{BASE_RAW}/cards/en/{set_id}.json"
    try:
        cards = fetch_json(cards_url)
    except Exception as e:
        print(f"Failed to fetch cards for set {set_id}: {e}")
        return None

    rows = []
    img_dir = os.path.join(IMG_ROOT, matched_name)
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

        # metadata
        hp = card.get('hp')
        abilities = card.get('abilities')
        abilities_json = json.dumps(abilities, ensure_ascii=False) if abilities else None
        attacks = card.get('attacks')
        attacks_json = json.dumps(attacks, ensure_ascii=False) if attacks else None
        if attacks:
            attack_names = "|".join([a.get('name', '') for a in attacks])
            attack_damages = "|".join([a.get('damage', '') or '' for a in attacks])
            attack_texts = "|".join([(' '.join(a.get('text', [])) if isinstance(a.get('text'), list) else (a.get('text') or '')) for a in attacks])
        else:
            attack_names = None
            attack_damages = None
            attack_texts = None

        weaknesses = card.get('weaknesses')
        if weaknesses:
            weaknesses = "|".join([f"{w.get('type')}:{w.get('value')}" for w in weaknesses])

        resistances = card.get('resistances')
        if resistances:
            resistances = "|".join([f"{r.get('type')}:{r.get('value')}" for r in resistances])

        retreat = card.get('retreatCost')
        if retreat:
            retreat = "__".join(retreat)

        evolves_from = card.get('evolvesFrom')
        artist = card.get('artist')
        flavor = card.get('flavorText')

        # prices not in repo JSON, keep empty columns to match layout
        prices = [None] * 25

        row = [
            img_name, card.get('id'), card.get('name'), card.get('supertype'), types, matched_name, card.get('number'), card.get('rarity'), large, small,
            hp, abilities_json, attacks_json, attack_names, attack_damages, attack_texts,
            weaknesses, resistances, retreat, evolves_from, artist, flavor
        ] + prices

        rows.append(row)

    df = pd.DataFrame(rows, columns=COLS)
    out_path = os.path.join(CSV_DIR, safe_name(matched_name) + ".csv")
    df.to_csv(out_path, index=False, encoding='utf-8')
    print(f"Wrote {out_path} ({len(rows)} cards)")

    # be polite
    sleep(0.5)
    return out_path


if __name__ == '__main__':
    ensure_dirs()
    generated = generate_for_set('Perfect Order')
    if generated:
        artifacts_dir = os.path.join(os.getcwd(), "artifacts")
        os.makedirs(artifacts_dir, exist_ok=True)
        artifact_path = os.path.join(artifacts_dir, "new_csvs.json")
        try:
            with open(artifact_path, "w", encoding="utf-8") as af:
                json.dump({"new_csvs": [{"csv": os.path.basename(generated), "set_name": "Perfect Order", "cards": "?"}]}, af, ensure_ascii=False, indent=2)
            print(f"Wrote artifact: {artifact_path}")
        except Exception as e:
            print(f"Failed to write artifact: {e}")
