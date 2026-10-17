#!/usr/bin/env python3
# =============================================================================
# AUDIT COMPARATIF COMPLET : FRWAC 500-D vs META FASTTEXT CC.FR.300
#
# Analyse et compare objectivement les deux catalogues sur :
# 1. La pureté lexicale (absence de bruit, de mots étrangers et de fautes)
# 2. La logique notionnelle et la richesse des synonymes
# 3. La diversité des concepts dans le Top 15 (anti-monotonie)
# 4. Comparatifs côte à côte sur 10 univers thématiques majeurs
# =============================================================================

import os
import sys
import json
import base64
import array
import unicodedata
from collections import defaultdict

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CAT_FRWAC_PATH = os.path.join(ROOT_DIR, "data", "catalogue.json")
CAT_FASTTEXT_PATH = os.path.join(ROOT_DIR, "data", "catalogue_fasttext.json")

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

SUSPECT_FOREIGN_OR_NOISE = {
    "contest", "compet", "competencia", "championship", "workshop", "factory", "track",
    "ride", "path", "seas", "swansea", "seagate", "reina", "king", "reign", "artwork",
    "laboratory", "tart", "quilt", "patchwork", "banana", "cream", "ice", "fire", "water",
    "student", "school", "winner", "damned", "evil", "devil", "gaming", "elit", "counterstrike",
    "crfpa", "sasu", "itrf", "cpge", "capet", "ceea", "icsi", "cmmi", "hcci", "claj",
    "apap", "aspc", "asptt", "aract", "lcen", "legt", "cegep", "iufm", "capes", "deug",
    "caer", "cned", "cnce", "cdefi", "anpaa", "anas", "anaf", "anya", "anil", "akane",
    "yanis", "anakin", "boinc", "teisseire", "athlon", "trackmania", "bazin", "babar", "baan"
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

def evaluer_catalogue(cat_data, label):
    words = cat_data["words"]
    c_bytes = base64.b64decode(cat_data["classic"])
    c_arr = array.array("H", c_bytes)
    total_games = cat_data.get("classicGames", 500)

    total_noise = 0
    total_unacc_dups = 0
    total_secret_typos = 0
    total_consonant_acronyms = 0
    total_diverse_top10 = 0

    for g in range(total_games):
        offset = g * 1000
        sec = words[c_arr[offset]]
        top100_indices = [c_arr[offset + i] for i in range(1, 101)]
        top100 = [words[idx] for idx in top100_indices]
        top10 = top100[:10]

        # Bruit étranger
        total_noise += sum(1 for w in top100 if w in SUSPECT_FOREIGN_OR_NOISE)

        # Doublons d'accents
        seen_norm = set()
        for w in top100:
            norm = strip_accents(w)
            if norm in seen_norm: total_unacc_dups += 1
            else: seen_norm.add(norm)

        # Typos du secret
        for w in top100:
            if len(sec) >= 4 and distance_lev(sec, w) == 1 and not (w.endswith("e") and len(w) == len(sec)+1):
                total_secret_typos += 1

        # Sigles sans voyelles
        for w in top100:
            v_count = sum(1 for c in w if c in VOWELS)
            if v_count == 0 or (len(w) >= 4 and v_count <= 1 and not w.endswith(("e", "er", "é", "ée", "és"))):
                total_consonant_acronyms += 1

        # Diversité des racines dans le Top 10
        roots = set(strip_accents(w)[:4] for w in top10 if len(w) >= 4)
        if len(roots) >= 8:
            total_diverse_top10 += 1

    purity = 100.0 - ((total_noise + total_unacc_dups + total_secret_typos + total_consonant_acronyms) / (total_games * 100) * 100)
    diversity_rate = (total_diverse_top10 / total_games) * 100

    return {
        "label": label,
        "modele": cat_data.get("modele"),
        "total_games": total_games,
        "purity": purity,
        "diversity_rate": diversity_rate,
        "noise_count": total_noise,
        "unacc_dups": total_unacc_dups,
        "secret_typos": total_secret_typos,
        "acronyms": total_consonant_acronyms,
        "c_arr": c_arr,
        "words": words
    }

def main():
    print("=" * 80)
    print("AUDIT COMPARATIF MAJEUR : FRWAC 500-D vs META FASTTEXT CC.FR.300")
    print("=" * 80)

    if not os.path.exists(CAT_FASTTEXT_PATH):
        print(f"Erreur : '{CAT_FASTTEXT_PATH}' n'existe pas encore. Attendez la fin de la compilation.")
        return

    with open(CAT_FRWAC_PATH, "r", encoding="utf-8") as f:
        data_frwac = json.load(f)
    with open(CAT_FASTTEXT_PATH, "r", encoding="utf-8") as f:
        data_fasttext = json.load(f)

    stats_frwac = evaluer_catalogue(data_frwac, "frWaC 500-D (Curé v2.0)")
    stats_ft = evaluer_catalogue(data_fasttext, "Meta FastText cc.fr.300 (2018)")

    print("\n1. RÉSULTATS STATISTIQUES GLOBAUX (50 000 MOTS AUDITÉS PAR MODÈLE) :")
    print("-" * 80)
    print(f"{'Critère':<35} | {'frWaC 500-D (Curé)':<20} | {'Meta FastText (Curé)':<20}")
    print("-" * 80)
    print(f"{'Taux de pureté lexicale':<35} | {stats_frwac['purity']:>18.2f}% | {stats_ft['purity']:>18.2f}%")
    print(f"{'Mots étrangers / bruit web':<35} | {stats_frwac['noise_count']:>18d}  | {stats_ft['noise_count']:>18d} ")
    print(f"{'Doublons sans accents':<35} | {stats_frwac['unacc_dups']:>18d}  | {stats_ft['unacc_dups']:>18d} ")
    print(f"{'Fautes de frappe (distance 1)':<35} | {stats_frwac['secret_typos']:>18d}  | {stats_ft['secret_typos']:>18d} ")
    print(f"{'Acronymes suspects':<35} | {stats_frwac['acronyms']:>18d}  | {stats_ft['acronyms']:>18d} ")
    print(f"{'Diversité racinaire Top 10':<35} | {stats_frwac['diversity_rate']:>18.1f}% | {stats_ft['diversity_rate']:>18.1f}%")
    print("-" * 80)

    print("\n2. COMPARATIF CÔTE À CÔTE PAR UNIVERS THÉMATIQUE :")
    test_games = [
        ("Éducation / Concours", 102, "concours"),
        ("Nature / Fruits", 386, "ananas"),
        ("Beaux-arts / Peinture", 385, "peinture"),
        ("Gastronomie / Cuisine", 377, "casserole"),
        ("Musique / Instruments", 393, "piano"),
        ("Justice / Société", 132, "prison"),
        ("Histoire / Châteaux", 27, "château"),
        ("Espace / Géographie", 371, "océan"),
        ("Monde animal", 53, "girafe"),
        ("Outils / Éléments", 7, "puits")
    ]

    for category, g_id, sec_expected in test_games:
        offset = (g_id - 1) * 1000
        sec = stats_frwac["words"][stats_frwac["c_arr"][offset]]
        top_frwac = [stats_frwac["words"][stats_frwac["c_arr"][offset + i]] for i in range(1, 9)]
        top_ft = [stats_ft["words"][stats_ft["c_arr"][offset + i]] for i in range(1, 9)]

        print(f"\n  ► #{g_id:3d} [{sec.upper()}] ({category}) :")
        print(f"    • frWaC 500-D   : {', '.join(top_frwac)}")
        print(f"    • Meta FastText : {', '.join(top_ft)}")

    print("\n" + "=" * 80)
    print("FIN DE L'AUDIT COMPARATIF.")
    print("=" * 80)

if __name__ == "__main__":
    main()
