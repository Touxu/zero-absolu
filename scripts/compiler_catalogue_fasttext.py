#!/usr/bin/env python3
# =============================================================================
# COMPILATEUR DE CATALOGUE META FASTTEXT (CC.FR.300)
#
# Génère un catalogue complet de 500 parties classiques avec les vecteurs
# 300-D de Meta FastText (2018), pour comparaison objective avec frWaC.
# =============================================================================

import os
import sys
import json
import base64
import array
import math
import struct
import unicodedata
import time

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.dirname(SCRIPT_DIR)
CATALOGUE_PATH = os.path.join(ROOT_DIR, "data", "catalogue.json")
FASTTEXT_BIN = os.path.join(ROOT_DIR, "models", "fasttext_fr_300.bin")
OUTPUT_PATH = os.path.join(ROOT_DIR, "data", "catalogue_fasttext.json")

VOWELS = set("aeiouyàâäéèêëîïôöùûüÿœæ")

VALID_SHORT_WORDS = {
    "âge", "air", "ail", "ami", "âme", "âne", "arc", "art", "as", "bac", "bal", "bar",
    "bas", "bec", "blé", "bol", "bon", "box", "bu", "bus", "but", "cap", "car", "cas",
    "cep", "chat", "cil", "clé", "col", "coq", "cor", "cou", "cour", "cri", "cru", "crû",
    "cube", "cuir", "dam", "dame", "dé", "don", "dos", "du", "dû", "duc", "dur", "eau",
    "ego", "élu", "épi", "ère", "est", "été", "fac", "fée", "fer", "feu", "fil", "fin",
    "foi", "fou", "fût", "gai", "gaz", "gel", "glu", "gré", "gui", "gué", "if", "île",
    "ile", "ion", "jet", "jeu", "jus", "lac", "lait", "lin", "lit", "loi", "lot", "lys",
    "mai", "mal", "mas", "mat", "mât", "mer", "mets", "mie", "miel", "mois", "mot", "mou",
    "mur", "mûr", "né", "nef", "nez", "nid", "nom", "noix", "nu", "nue", "ode", "oie",
    "œil", "oeil", "or", "os", "oui", "ours", "pain", "paix", "parc", "pas", "peau", "peur",
    "pic", "pied", "pin", "pli", "pneu", "poil", "pois", "pont", "porc", "port", "pot",
    "pou", "pré", "prix", "pub", "puits", "pur", "puy", "quai", "rai", "ras", "rat",
    "raz", "rez", "riz", "roc", "roi", "roue", "ru", "rue", "sac", "sec", "sel", "ski",
    "soi", "soie", "soir", "sol", "son", "sot", "sou", "su", "sud", "suc", "sur", "sûr",
    "taux", "thé", "the", "tir", "toit", "ton", "tort", "tôt", "toux", "tri", "trou", "tube",
    "val", "van", "veau", "vent", "ver", "vie", "vif", "vin", "vis", "voix", "vol", "vu",
    "vue", "vœu", "voeu", "yak", "yen", "zen", "zoo"
}

BLACKLIST_NOISE = {
    "contest", "compet", "competencia", "championship", "competitive", "matches", "prize",
    "wins", "playoff", "prizee", "counter", "workshop", "factory", "track", "ride", "path",
    "seas", "swansea", "seagate", "reina", "king", "reign", "artwork", "laboratory", "tart",
    "quilt", "patchwork", "shop", "retail", "hummingbird", "birdie", "banana", "cream", "ice",
    "fire", "water", "world", "book", "food", "drink", "student", "school", "winner", "damned",
    "evil", "devil", "hell", "diane", "lady", "donzelle", "freeroll", "hold", "stud", "gaming",
    "elit", "counterstrike", "crfpa", "sasu", "itrf", "cpge", "capet", "ceea", "icsi", "cmmi",
    "hcci", "claj", "apap", "aspc", "asptt", "aract", "lcen", "legt", "cegep", "iufm", "capes",
    "deug", "caer", "cned", "cnce", "cdefi", "boinc", "teisseire", "athlon", "trackmania",
    "olympiakos", "contador", "sourcefourge", "anpaa", "anas", "anaf", "anya", "anil", "akane",
    "yanis", "anakin", "bazin", "babar", "baan", "braguette", "bavette", "babin", "baas"
}

def strip_accents(s):
    s = s.replace("œ", "oe").replace("æ", "ae")
    return "".join(c for c in unicodedata.normalize("NFD", s) if unicodedata.category(c) != "Mn")

def distance_lev(s1, s2):
    if len(s1) < len(s2): return distance_lev(s2, s1)
    if len(s2) == 0: return len(s1)
    row = range(len(s2) + 1)
    for i, c1 in enumerate(s1):
        cur = [i + 1]
        for j, c2 in enumerate(s2):
            cur.append(min(row[j+1]+1, cur[j]+1, row[j]+(c1!=c2)))
        row = cur
    return row[-1]

def is_noise_word(w, secret):
    if w == secret: return False
    if w in BLACKLIST_NOISE: return True
    if len(w) <= 3 and w not in VALID_SHORT_WORDS: return True

    v_count = sum(1 for c in w if c in VOWELS)
    if v_count == 0: return True
    if len(w) >= 4 and v_count <= 1 and not w.endswith(("e", "er", "é", "ée", "és")): return True

    max_c = 0; cur_c = 0
    for c in w:
        if c not in VOWELS:
            cur_c += 1
            if cur_c > max_c: max_c = cur_c
        else: cur_c = 0
    if max_c >= 4: return True

    if len(secret) >= 4 and distance_lev(secret, w) == 1:
        if not (w.endswith("e") and len(w) == len(secret) + 1):
            return True

    return False

def curate_top_list(secret, sorted_indices, words, target_count=999):
    clean = []
    secret_norm = strip_accents(secret).replace("-", "")
    seen_stems = {secret_norm}
    seen_roots_top = set()
    deferred = []

    secret_stem = secret_norm[:4] if len(secret_norm) >= 5 else secret_norm

    for idx in sorted_indices:
        w = words[idx]
        if w == secret: continue
        norm = strip_accents(w).replace("-", "")
        if norm == secret_norm: continue
        if is_noise_word(w, secret): continue

        if norm in seen_stems: continue
        seen_stems.add(norm)

        # Flexion directe
        if len(secret) >= 4 and (norm.startswith(secret_stem) or secret_stem.startswith(norm[:4] if len(norm)>=4 else norm)):
            deferred.append(idx)
            continue

        # Diversité Top 18
        w_root = norm[:4] if len(norm) >= 4 else norm
        if len(clean) < 18 and w_root in seen_roots_top:
            deferred.append(idx)
            continue
        if len(clean) < 18:
            seen_roots_top.add(w_root)

        # Élimination des fautes de frappe inter-mots (ex: carosserie si carrosserie est déjà pris)
        if any(abs(len(w) - len(words[c_idx])) <= 1 and distance_lev(w, words[c_idx]) == 1 for c_idx in clean[-15:]):
            continue

        clean.append(idx)
        if len(clean) >= target_count + 150:
            break

    final = clean[:15] + deferred[:5] + clean[15:] + deferred[5:]
    return final[:target_count]

def compiler_catalogue_fasttext():
    print("=" * 75)
    print("COMPILATION DU CATALOGUE META FASTTEXT (CC.FR.300)")
    print("=" * 75)

    with open(CATALOGUE_PATH, "r", encoding="utf-8") as f:
        cat = json.load(f)

    words = cat["words"]
    classic_count = cat.get("classicCount", 55000)
    total_games = cat.get("classicGames", 500)
    c_bytes = base64.b64decode(cat["classic"])
    c_arr = array.array("H", c_bytes)

    # Secrets actuels assainis
    secrets = [words[c_arr[g * 1000]] for g in range(total_games)]
    w2i = {w: i for i, w in enumerate(words)}

    print(f"Chargement des vecteurs FastText 300-D depuis '{FASTTEXT_BIN}'...")
    dim = 300
    vecs = array.array("f")
    with open(FASTTEXT_BIN, "rb") as f:
        header = f.readline().decode("utf-8")
        nb_w, d = map(int, header.split())
        assert d == dim
        vecs.fromfile(f, len(words) * dim)

    print(f"✓ {len(words):,} vecteurs 300-D chargés.")

    # Matrice de Top 1000 FastText
    print(f"\nCalcul des Top 1000 pour les {total_games} parties avec FastText...")
    t0 = time.time()
    new_classic = []

    for g, secret in enumerate(secrets):
        s_idx = w2i[secret]
        s_vec = vecs[s_idx * dim : (s_idx + 1) * dim]

        # Dot product avec les 55 000 mots classiques
        sims = []
        for i in range(classic_count):
            w_vec = vecs[i * dim : (i + 1) * dim]
            dot = sum(a * b for a, b in zip(s_vec, w_vec))
            sims.append((dot, i))
        sims.sort(reverse=True)

        sorted_indices = [idx for _, idx in sims[:2000]]
        curated_top = curate_top_list(secret, sorted_indices, words, target_count=999)

        assert len(curated_top) == 999, f"Partie #{g+1} a {len(curated_top)} mots au lieu de 999"
        game_entry = [s_idx] + curated_top
        new_classic.extend(game_entry)

        if (g + 1) % 50 == 0 or (g + 1) == total_games:
            elapsed = time.time() - t0
            print(f"  [{g+1:3d}/{total_games}] parties calculées ({elapsed:.1f}s)")

    # Assemblage
    new_arr = array.array("H", new_classic)
    fasttext_cat = {
        "v": 2,
        "modele": "Meta FastText cc.fr.300 (2018)",
        "classicCount": classic_count,
        "classicGames": total_games,
        "popGames": cat.get("popGames", 91),
        "words": words,
        "vecs16": cat.get("vecs16"),
        "classic": base64.b64encode(new_arr.tobytes()).decode("ascii"),
        "pop": cat.get("pop")
    }

    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        json.dump(fasttext_cat, f, ensure_ascii=False, separators=(",", ":"))

    out_mb = os.path.getsize(OUTPUT_PATH) / (1024 * 1024)
    print(f"\n✓ Catalogue FastText sauvegardé dans '{OUTPUT_PATH}' ({out_mb:.2f} Mo) !")
    print("=" * 75)

if __name__ == "__main__":
    compiler_catalogue_fasttext()
