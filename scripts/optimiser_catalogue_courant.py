#!/usr/bin/env python3
# =============================================================================
# OPTIMISATION & CURATION DU CATALOGUE ACTUEL (AMÉLIORATION IMMÉDIATE)
# Réorganise les Top 1000 pour placer les concepts et synonymes devant les
# simples déclinaisons morphologiques et fautes de frappe.
# =============================================================================

import os
import json
import base64
import array

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CATALOGUE_PATH = os.path.join(ROOT_DIR, "data", "catalogue.json")

def distance_lev(s1, s2):
    if len(s1) < len(s2):
        return distance_lev(s2, s1)
    if len(s2) == 0:
        return len(s1)
    previous_row = range(len(s2) + 1)
    for i, c1 in enumerate(s1):
        current_row = [i + 1]
        for j, c2 in enumerate(s2):
            insertions = previous_row[j + 1] + 1
            deletions = current_row[j] + 1
            substitutions = previous_row[j] + (c1 != c2)
            current_row.append(min(insertions, deletions, substitutions))
        previous_row = current_row
    return previous_row[-1]

def optimiser_top_mots(secret, indices, words):
    secret_stem = secret[:4] if len(secret) >= 5 else secret
    
    concepts = []
    derivations = []

    for idx in indices:
        w = words[idx]
        if w == secret:
            continue
        # Détection même racine ou faute d'orthographe évidente (distance 1 avec le secret)
        is_same_root = (len(w) >= 4 and (w.startswith(secret_stem) or secret.startswith(w[:4])))
        is_typo = (len(secret) >= 5 and distance_lev(secret, w) == 1)

        if is_same_root or is_typo:
            derivations.append(idx)
        else:
            concepts.append(idx)

    # Place au moins 10 vrais concepts en tête avant d'insérer les premières flexions
    # Cela garantit que le Top 10 est riche, varié et gratifiant pour le joueur
    reordered = concepts[:12] + derivations[:4] + concepts[12:30] + derivations[4:] + concepts[30:]
    return reordered[:len(indices)]

def optimiser_catalogue():
    print("Lecture de data/catalogue.json...")
    with open(CATALOGUE_PATH, "r", encoding="utf-8") as f:
        cat = json.load(f)

    words = cat["words"]
    classic_buf = base64.b64decode(cat["classic"])
    arr = array.array("H")
    arr.frombytes(classic_buf)

    nb_games = len(arr) // 1000
    print(f"Optimisation de {nb_games} parties classiques...")

    new_arr = array.array("H")
    reordered_count = 0

    for g in range(nb_games):
        offset = g * 1000
        secret_idx = arr[offset]
        secret = words[secret_idx]

        sub_indices = [arr[offset + r] for r in range(1, 1000)]
        old_top1 = words[sub_indices[0]]

        clean_sub = optimiser_top_mots(secret, sub_indices, words)
        new_top1 = words[clean_sub[0]]

        if old_top1 != new_top1:
            reordered_count += 1

        new_arr.append(secret_idx)
        new_arr.extend(clean_sub)

    cat["classic"] = base64.b64encode(new_arr.tobytes()).decode("ascii")

    with open(CATALOGUE_PATH, "w", encoding="utf-8") as f:
        json.dump(cat, f, ensure_ascii=False)

    print(f"✅ {reordered_count} parties sur {nb_games} optimisées (Top 1 nettoyé de ses déclinaisons monotones) !")

if __name__ == "__main__":
    optimiser_catalogue()
