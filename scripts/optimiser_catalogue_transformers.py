#!/usr/bin/env python3
# =============================================================================
# OPTIMISATEUR DU CATALOGUE TRANSFORMERS DE ZÉROABSOLU
# Purge les anomalies de sous-mots, les regroupements de racines monotones
# et le bruit web pour obtenir un Top 1000 riche, varié et gratifiant.
# Garantit strictement 1000 éléments par partie (aucun décalage d'offset).
# =============================================================================

import os
import json
import base64
import array
import re
from collections import defaultdict

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CATALOGUE_PATH = os.path.join(ROOT_DIR, "data", "catalogue.json")

# Ensemble de mots courts français légitimes (longueur <= 3)
MOTS_COURTS_VALIDES = {
    "eau", "feu", "air", "mer", "sol", "fer", "or", "vin", "jus", "sel", "riz", "gaz",
    "sac", "bus", "ski", "roi", "loi", "art", "but", "ami", "vis", "fil", "pin", "dos",
    "pas", "vie", "fin", "lit", "vue", "bar", "cap", "vol", "duc", "tas", "île", "ile",
    "mur", "col", "bol", "cou", "pot", "arc", "box", "pub", "gel", "rat", "pie", "mât",
    "riz", "thé", "the", "zoo", "blé", "ble", "ail", "pan", "soc", "ski", "pic", "lac",
    "nez", "yeux", "œil", "oeil", "âme", "dieu", "ange", "sang", "dent", "peau", "bras",
    "main", "pied", "chat", "loup", "ours", "veau", "porc", "bœuf", "boeuf", "poul",
    "fête", "nuit", "jour", "midi", "soir", "aube", "vert", "bleu", "rose", "brun", "gris",
    "noir", "gras", "doux", "pur", "sûr", "sur", "vrai", "joli", "beau", "bon", "gros"
}

# Mots anglais fréquents à écarter du haut du classement
MOTS_ANGLAIS_A_ECARTER = {
    "hummingbird", "birdie", "hell", "devil", "evil", "damned", "shop", "retail",
    "banana", "cream", "ice", "fire", "water", "world", "book", "food", "drink"
}

def est_mot_valide_pour_top(w):
    if not re.match(r"^[a-zàâäéèêëîïôöùûüç\-']+$", w):
        return False
    if len(w) <= 3 and w not in MOTS_COURTS_VALIDES:
        return False
    if w.endswith(("o", "i", "u")) and len(w) == 4 and w not in MOTS_COURTS_VALIDES:
        return False
    if w in MOTS_ANGLAIS_A_ECARTER:
        return False
    return True

def extraire_racine(w):
    w_clean = re.sub(r"[éèêë]", "e", w)
    w_clean = re.sub(r"[àâä]", "a", w_clean)
    w_clean = re.sub(r"[îï]", "i", w_clean)
    w_clean = re.sub(r"[ôö]", "o", w_clean)
    w_clean = re.sub(r"[ûü]", "u", w_clean)
    if len(w_clean) >= 6:
        return w_clean[:5]
    if len(w_clean) >= 4:
        return w_clean[:4]
    return w_clean

def filtrer_et_diversifier_top(secret_idx, secret, top_indices, words, max_keep=999):
    secret_root = extraire_racine(secret)
    
    clean_unique = []
    seen_roots_top = set()
    deferred = []

    for idx in top_indices:
        w = words[idx]
        if w == secret or idx == secret_idx:
            continue

        if not est_mot_valide_pour_top(w):
            continue

        # Problème "cric" -> "cri" / "crie"
        if len(secret) <= 5 and len(w) <= 4 and (w in secret or secret in w):
            if w in ("cri", "crie", "crier", "cria", "crisser", "cap", "capa", "capo"):
                deferred.append(idx)
                continue

        w_root = extraire_racine(w)

        # Flexion directe du mot secret (ex: fossilisation pour fossile)
        if len(secret) >= 4 and (w.startswith(secret_root) or secret.startswith(w_root)):
            deferred.append(idx)
            continue

        # Dé-doublonnage des familles dans le Top 20 (ex: banane, banana, bananier)
        if len(clean_unique) < 25:
            if w_root in seen_roots_top:
                deferred.append(idx)
                continue
            seen_roots_top.add(w_root)

        clean_unique.append(idx)

    # Réassemblage
    final_ranked = clean_unique[:20] + deferred[:15] + clean_unique[20:] + deferred[15:]
    
    # GARANTIE STRICTE : Exactement max_keep (999) éléments
    if len(final_ranked) < max_keep:
        existing_set = set(final_ranked)
        existing_set.add(secret_idx)
        for idx in top_indices:
            if idx not in existing_set:
                final_ranked.append(idx)
                existing_set.add(idx)
                if len(final_ranked) == max_keep:
                    break

    return final_ranked[:max_keep]

def optimiser_catalogue():
    print(f"Chargement de {CATALOGUE_PATH}...")
    with open(CATALOGUE_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)

    words = data["words"]
    c_bytes = base64.b64decode(data["classic"])
    c_arr = array.array("H", c_bytes)
    total_games = len(c_arr) // 1000

    print(f"Optimisation sémantique de {total_games} parties...")

    new_classic = []
    modifs = 0

    for g in range(total_games):
        secret_idx = c_arr[g * 1000]
        secret = words[secret_idx]
        top_indices = [c_arr[g * 1000 + i] for i in range(1, 1000)]

        curated_top = filtrer_et_diversifier_top(secret_idx, secret, top_indices, words, max_keep=999)
        assert len(curated_top) == 999, f"Erreur longueur partie #{g+1}: {len(curated_top)}"

        if curated_top[:10] != top_indices[:10]:
            modifs += 1

        new_classic.append(secret_idx)
        new_classic.extend(curated_top)

    assert len(new_classic) == total_games * 1000, "Longueur totale incorrecte !"
    print(f"Parties optimisées avec amélioration de diversité : {modifs}/{total_games}")

    new_arr = array.array("H", new_classic)
    data["classic"] = base64.b64encode(new_arr.tobytes()).decode("ascii")

    with open(CATALOGUE_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False)

    print(f"✅ {CATALOGUE_PATH} réécrit et optimisé avec succès (exactement {len(new_classic)} entrées) !")

if __name__ == "__main__":
    optimiser_catalogue()
