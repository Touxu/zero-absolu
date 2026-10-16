#!/usr/bin/env python3
"""
Amélioration de la sélection des mots secrets dans catalogue.json.
Remplace les mots trop obscurs/spécialisés (ex: gouache, faitout, calice, clavecin...)
par des mots français courants et universellement connus.
"""
import os
import json
import base64
import struct
import array

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CATALOGUE_PATH = os.path.join(ROOT_DIR, "data", "catalogue.json")

def main():
    print("Chargement de catalogue.json...")
    with open(CATALOGUE_PATH, "r", encoding="utf-8") as f:
        cat = json.load(f)

    words = cat["words"]
    word_to_idx = {w: i for i, w in enumerate(words)}

    c_buf = base64.b64decode(cat["classic"])
    c_arr = list(struct.unpack(f"<{len(c_buf)//2}H", c_buf))

    num_games = cat["classicGames"]
    print(f"Nombre de parties classiques : {num_games}")

    # Dictionnaire des remplacements ciblés pour les mots secrets trop obscurs
    # Si le mot de remplacement est présent dans la manche, on permute simplement leurs positions.
    # Sinon, on prend le mot le plus courant et compréhensible du top 10.
    REPLACEMENTS = {
        "gouache": "peinture",
        "faitout": "marmite",
        "clavecin": "piano",
        "geôle": "prison",
        "bonze": "moine",
        "fleuret": "escrime",
        "amnistie": "pardon",
        "prieuré": "abbaye",
        "ermitage": "refuge",
        "viaduc": "pont",
        "sarcophage": "tombeau",
        "calice": "carafe",
        "âtre": "foyer",
        "cric": "levier",
        "timbale": "trombone",
        "burin": "usinage",
        "diapason": "tonalité",
        "sacrilège": "profanation"
    }

    swapped = 0
    for g in range(num_games):
        offset = g * 1000
        sec_idx = c_arr[offset]
        sec_word = words[sec_idx]

        if sec_word in REPLACEMENTS:
            target_word = REPLACEMENTS[sec_word]
            # Chercher dans les 50 mots les plus proches
            game_indices = c_arr[offset : offset + 50]
            found_pos = None

            # 1. Vérifier si target_word est déjà dans le top 50
            if target_word in word_to_idx:
                target_idx = word_to_idx[target_word]
                if target_idx in game_indices:
                    found_pos = game_indices.index(target_idx)

            # 2. Si pas trouvé exactement, chercher le premier mot français commun dans le top 10
            if found_pos is None:
                for pos in range(1, 10):
                    cand = words[game_indices[pos]]
                    if len(cand) >= 4 and cand.isalpha() and cand not in REPLACEMENTS:
                        found_pos = pos
                        target_word = cand
                        break

            if found_pos is not None:
                new_sec_idx = c_arr[offset + found_pos]
                # Permuter
                c_arr[offset] = new_sec_idx
                c_arr[offset + found_pos] = sec_idx
                swapped += 1
                print(f"  Partie #{g+1} : \"{sec_word}\" remplacé par \"{words[new_sec_idx]}\" (qui était #{found_pos+1})")

    if swapped > 0:
        new_bytes = array.array("H", c_arr).tobytes()
        cat["classic"] = base64.b64encode(new_bytes).decode("ascii")
        with open(CATALOGUE_PATH, "w", encoding="utf-8") as f:
            json.dump(cat, f, separators=(",", ":"))
        print(f"✅ {swapped} mots secrets obscurs remplacés par des mots courants avec succès dans {CATALOGUE_PATH} !")
    else:
        print("Aucun remplacement nécessaire.")

if __name__ == "__main__":
    main()
