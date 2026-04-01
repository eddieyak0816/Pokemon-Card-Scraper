from pokemontcgsdk import Card, Set
import requests
import os
import pandas as pd
from time import sleep
from datetime import datetime

SET_NAME = "Perfect Order"

def ensure_dirs():
    os.makedirs("images", exist_ok=True)
    os.makedirs("csv_new", exist_ok=True)
    os.makedirs(os.path.join("images", SET_NAME), exist_ok=True)

def down_img(url, dest_path):
    try:
        r = requests.get(url, timeout=20)
        r.raise_for_status()
        with open(dest_path, "wb") as f:
            f.write(r.content)
    except Exception:
        pass

def main():
    ensure_dirs()

    # Query cards in the set
    q = f'set.name:"{SET_NAME}"'
    cards = Card.where(q=q)

    cols = [
        "Image_Names", "Card_ID", "Card_Name", "Super_Type", "Types", "Set_Name", "Number", "Rarity",
        "Large_Image_URL", "Small_Image_URL",
        "Normal_low", "Normal_mid", "Normal_high", "Normal_market", "Normal_directLow",
        "Holofoil_low", "Holofoil_mid", "Holofoil_high", "Holofoil_market", "Holofoil_directLow",
        "ReverseHolofoil_low", "ReverseHolofoil_mid", "ReverseHolofoil_high", "ReverseHolofoil_market", "ReverseHolofoil_directLow",
        "FirstEditionHolofoil_low", "FirstEditionHolofoil_mid", "FirstEditionHolofoil_high", "FirstEditionHolofoil_market", "FirstEditionHolofoil_directLow",
        "FirstEditionNormal_low", "FirstEditionNormal_mid", "FirstEditionNormal_high", "FirstEditionNormal_market", "FirstEditionNormal_directLow"
    ]

    details = []
    for i, card in enumerate(cards):
        L_img = getattr(card.images, 'large', None)
        S_img = getattr(card.images, 'small', None)

        img_name = f"{i:03d}.jpg"
        if L_img:
            down_img(L_img, os.path.join("images", SET_NAME, img_name))
        elif S_img:
            down_img(S_img, os.path.join("images", SET_NAME, img_name))

        Types = card.types
        if Types is not None:
            Types = "__".join(Types)

        prices = [None]*25
        if card.tcgplayer and card.tcgplayer.prices:
            prices_list = []
            for key in ["normal", "holofoil", "reverseHolofoil", "firstEditionHolofoil", "firstEditionNormal"]:
                obj = getattr(card.tcgplayer.prices, key, None)
                if obj is None:
                    p = [None]*5
                else:
                    p = [getattr(obj, attr, None) for attr in ("low","mid","high","market","directLow")]
                prices_list += p
            prices = prices_list

        row = [img_name, card.id, card.name, card.supertype, Types, card.set.name, card.number, card.rarity, L_img, S_img] + prices
        details.append(row)

    df = pd.DataFrame(details, columns=cols)
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    safe_name = SET_NAME.replace(":", "")
    out_path = os.path.join("csv_new", f"{safe_name}_{ts}.csv")
    df.to_csv(out_path, index=False)
    print(f"Saved CSV: {out_path}")

if __name__ == '__main__':
    main()
