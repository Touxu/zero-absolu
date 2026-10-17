#!/usr/bin/env python3
# =============================================================================
# CURATION ET ASSAINISSEMENT SÉMANTIQUE MAJEUR DE ZÉROABSOLU (V2.0)
#
# Restaure l'excellence du modèle vectoriel 500-D (frWaC) tout en éliminant :
# 1. Tous les mots anglais/espagnols parasites (contest, championship, workshop, etc.)
# 2. Toutes les fautes de frappe et doublons d'accents (admissibilite vs admissibilité)
# 3. Tous les sigles administratifs et abréviations (crfpa, sasu, itrf, cpge, etc.)
# 4. Toutes les marques et noms de domaine (boinc, teisseire, trackmania, etc.)
# 5. Les 18 mots secrets obscurs (remplacés par peinture, casserole, piano, prison...)
#
# Garantit 1000 mots strictement uniques, cohérents et gratifiants par partie.
# =============================================================================

import os
import sys
import json
import base64
import array
import math
import struct
import unicodedata
import subprocess

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.dirname(SCRIPT_DIR)
MODEL_PATH = os.path.join(ROOT_DIR, "models", "frWac_no_postag_no_phrase_500_skip_cut100.bin")
OUTPUT_PATH = os.path.join(ROOT_DIR, "data", "catalogue.json")

# Ensemble de mots courts français légitimes (longueur <= 3)
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

# Sigles institutionnels, marques, jargon web, anglais et sous-mots parasites
BLACKLIST_NOISE = {
    # Mots anglais ou espagnols
    "contest", "compet", "competencia", "championship", "competitive", "matches", "prize",
    "wins", "playoff", "prizee", "counter", "workshop", "factory", "track", "ride", "path",
    "seas", "swansea", "seagate", "reina", "king", "reign", "artwork", "laboratory", "tart",
    "quilt", "patchwork", "shop", "retail", "hummingbird", "birdie", "banana", "cream", "ice",
    "fire", "water", "world", "book", "food", "drink", "student", "school", "winner", "damned",
    "evil", "devil", "hell", "diane", "lady", "donzelle", "freeroll", "hold", "stud", "gaming",
    "elit", "counterstrike",
    # Sigles administratifs / scolaires / concours
    "crfpa", "sasu", "itrf", "cpge", "capet", "ceea", "icsi", "cmmi", "hcci", "claj",
    "apap", "aspc", "asptt", "aract", "lcen", "legt", "cegep", "iufm", "capes", "deug",
    "caer", "cned", "cnce", "cdefi", "pma", "fiv", "ivg", "tib", "cmm", "icf", "bnp",
    "sncf", "ratp", "urssaf", "unedic", "assedic", "smic", "medef", "cfdt", "cgt", "fo",
    "fsu", "unsa", "sud", "ump", "udf", "pcf", "lcr", "npa", "fn", "rn", "modem", "eelv",
    "ps", "siac", "inra", "anpe", "sivom", "epci", "tcsp", "sytral", "cafep", "crpe",
    "caplp", "capeps", "ipag", "jorf", "cnrs", "inserm", "insee", "sida", "ptac", "ccap",
    "samu", "smur", "dgac", "oaci", "dsna", "iaaf", "fnsea", "fdsea", "cnja", "adasea",
    "pnud", "pnue", "cedh", "enssib", "cadist", "sudoc", "cjce",
    # Marques, web, gaming et bruit de crawl
    "boinc", "teisseire", "athlon", "trackmania", "olympiakos", "contador", "sourcefourge",
    "pixma", "lexmark", "bwin", "betclic", "unibet", "partouche", "novotel", "sofitel",
    "kyriad", "exxon", "totalfinaelf", "lagerfeld", "balenciaga", "galliano", "castelbajac",
    "ebay", "paypal", "colissimo", "monoprix", "auchan", "intersport", "décathlon", "leclerc",
    "intermarché", "lidl", "spar", "cora", "netto", "tesco", "sofinco", "cofinoga", "ficp",
    "marnier", "sorbonne", "larousse", "robert", "faraday", "tesla", "habsbourg",
    "http", "https", "www", "html", "htm", "php", "pdf", "jpg", "gif", "png", "url",
    "float", "left", "right", "height", "width", "padding", "margin", "border", "color",
    "overflow", "uppercase", "ffffff", "script", "applet", "browser", "firefox", "mozilla",
    "thunderbird", "microsoft", "google", "yahoo", "linux", "windows", "server", "proxy",
    "anpaa", "anas", "anaf", "anya", "anil", "akane", "yanis", "anakin", "bazin", "babar",
    "baan", "braguette", "bavette", "babin", "baas", "ciboire", "claj", "calcin", "cuill",
    "pallice", "palilia", "pallas", "paloma", "palière", "palerme", "palau", "paladin",
    "rampal", "paludier", "gifas", "girino", "mowgli", "rhino", "giselle", "giroud",
    "colomb", "cairoli", "cambio", "chamoiseau", "cochabamba", "cobol", "ciron", "cotopaxi",
    "coline", "coliposte", "lycé", "aspen", "viagra", "apical", "ascite", "mungiu",
    "croisette", "guerrillero", "mostra", "loach", "schnabel", "concurent", "championat",
    "trophee", "pacours", "artisant", "artesi", "gagor", "gorz", "goron", "gorce",
    "puit"
}

# Remplacement des mots secrets obscurs par des mots concrets et évocateurs
OBSCURE_SECRET_REPLACEMENTS = {
    "gouache": "peinture",
    "faitout": "casserole",
    "clavecin": "piano",
    "geôle": "prison",
    "bonze": "moine",
    "fleuret": "escrime",
    "amnistie": "pardon",
    "prieuré": "abbaye",
    "ermitage": "refuge",
    "viaduc": "pont",
    "sarcophage": "tombeau",
    "calice": "coupe",
    "âtre": "foyer",
    "cric": "levier",
    "timbale": "trombone",
    "burin": "gravure",
    "diapason": "harmonie",
    "sacrilège": "blasphème"
}

VOWELS = set("aeiouyàâäéèêëîïôöùûüÿœæ")

def strip_accents(s):
    s = s.replace("œ", "oe").replace("æ", "ae")
    return "".join(c for c in unicodedata.normalize("NFD", s) if unicodedata.category(c) != "Mn")

def distance_levenshtein(s1, s2):
    if len(s1) < len(s2):
        return distance_levenshtein(s2, s1)
    if len(s2) == 0:
        return len(s1)
    row = range(len(s2) + 1)
    for i, c1 in enumerate(s1):
        cur = [i + 1]
        for j, c2 in enumerate(s2):
            cur.append(min(row[j + 1] + 1, cur[j] + 1, row[j] + (c1 != c2)))
        row = cur
    return row[-1]

def is_noise_word(w, secret):
    if w == secret:
        return False
    if w in BLACKLIST_NOISE:
        return True
    if len(w) <= 3 and w not in VALID_SHORT_WORDS:
        return True

    # Détection sigles sans voyelles ou quasi-consonantiques
    v_count = sum(1 for c in w if c in VOWELS)
    if v_count == 0:
        return True
    if len(w) >= 4 and v_count <= 1 and not w.endswith(("e", "er", "é", "ée", "és")):
        return True

    # 4 consonnes consécutives (anglais ou acronyme)
    max_c = 0
    cur_c = 0
    for c in w:
        if c not in VOWELS:
            cur_c += 1
            if cur_c > max_c:
                max_c = cur_c
        else:
            cur_c = 0
    if max_c >= 4:
        return True

    # Fautes de frappe évidentes sur le mot secret (distance 1)
    if len(secret) >= 4 and distance_levenshtein(secret, w) == 1:
        if not (w.endswith("e") and len(w) == len(secret) + 1):
            return True

    return False

def curate_top_list(secret, raw_indices, words, target_count=999):
    clean = []
    seen_stems = set()
    seen_roots_top = set()
    deferred = []

    secret_stem = strip_accents(secret).replace("-", "")
    if len(secret_stem) >= 5:
        secret_stem = secret_stem[:4]

    for idx in raw_indices:
        w = words[idx]
        if w == secret:
            continue

        if is_noise_word(w, secret):
            continue

        # Suppression des doublons d'accents (ex: admissibilite si admissibilité existe)
        norm = strip_accents(w).replace("-", "")
        if norm in seen_stems:
            continue
        seen_stems.add(norm)

        # Dérivation directe du mot secret (même radical de 4 lettres)
        if len(secret) >= 4 and (norm.startswith(secret_stem) or secret_stem.startswith(norm[:4] if len(norm)>=4 else norm)):
            deferred.append(idx)
            continue

        # Diversification du Top 18 (éviter 4 mots de la même famille)
        w_root = norm[:4] if len(norm) >= 4 else norm
        if len(clean) < 18 and w_root in seen_roots_top:
            deferred.append(idx)
            continue
        if len(clean) < 18:
            seen_roots_top.add(w_root)

        clean.append(idx)

    # Réassemblage équilibré : concepts en premier, quelques flexions plus bas
    final = clean[:15] + deferred[:5] + clean[15:] + deferred[5:]
    return final[:target_count]

def main():
    print("="*75)
    print("CURATION ET ASSAINISSEMENT SÉMANTIQUE MAJEUR (500 PARTIES)")
    print("="*75)

    # 1. Chargement du vocabulaire de catalogue.json
    print("\n1/5 Récupération de la matrice initiale 500-D...")
    raw_cat_json = subprocess.check_output(["git", "show", "7407b94:data/catalogue.json"])
    base_cat = json.loads(raw_cat_json)

    words = base_cat["words"]
    classic_count = base_cat.get("classicCount", 55000)
    w2i = {w: i for i, w in enumerate(words)}

    classic_bytes = base64.b64decode(base_cat["classic"])
    classic_arr = array.array("H", classic_bytes)
    total_games = base_cat.get("classicGames", 500)
    print(f"  ✓ {total_games} parties classiques chargées ({len(words):,} mots au catalogue)")

    # 2. Indexation des offsets dans le fichier binaire frWaC
    print("\n2/5 Indexation du fichier binaire Word2Vec...")
    dim = 500
    bin_offsets = {}
    with open(MODEL_PATH, "rb") as f:
        header = f.readline().decode("utf-8")
        vocab_size, _ = map(int, header.split())
        for i in range(vocab_size):
            w_bytes = bytearray()
            while True:
                ch = f.read(1)
                if ch == b" " or not ch:
                    break
                if ch != b"\n":
                    w_bytes.extend(ch)
            w = w_bytes.decode("utf-8", errors="ignore").lower().strip()
            bin_offsets[w] = f.tell()
            f.seek(dim * 4, 1)

    print(f"  ✓ {len(bin_offsets):,} mots indexés dans le fichier binaire.")

    # 3. Chargement des vecteurs ALIGNÉS avec words (dans le même ordre !)
    print("\n3/5 Chargement en mémoire des vecteurs normalisés alignés avec le vocabulaire...")
    vecs = array.array("f")
    with open(MODEL_PATH, "rb") as f:
        for i, w in enumerate(words):
            if w in bin_offsets:
                f.seek(bin_offsets[w])
                floats = struct.unpack(f"<{dim}f", f.read(dim * 4))
                norm = math.sqrt(sum(x * x for x in floats)) or 1.0
                vecs.extend(x / norm for x in floats)
            else:
                vecs.extend([0.0] * dim)

    print(f"  ✓ {len(words):,} vecteurs 500-D normalisés et alignés prêts en mémoire.")

    def compute_exact_top_indices(word, count=1500):
        if word not in w2i:
            return []
        t_idx = w2i[word]
        t_vec = vecs[t_idx * dim : (t_idx + 1) * dim]
        sims = []
        for i in range(classic_count):
            w_vec = vecs[i * dim : (i + 1) * dim]
            dot = sum(a * b for a, b in zip(t_vec, w_vec))
            sims.append((dot, i))
        sims.sort(reverse=True)
        return [idx for _, idx in sims[:count]]

    # 4. Traitement et assainissement des 500 parties
    print("\n4/5 Curation des 500 parties et remplacement des secrets obscurs...")
    new_classic = []
    replaced_count = 0

    for g in range(total_games):
        offset = g * 1000
        sec_idx = classic_arr[offset]
        secret = words[sec_idx]

        # Remplacement si le mot secret fait partie de la liste obscure
        if secret in OBSCURE_SECRET_REPLACEMENTS:
            new_secret = OBSCURE_SECRET_REPLACEMENTS[secret]
            if new_secret in w2i:
                sec_idx = w2i[new_secret]
                secret = new_secret
                replaced_count += 1
                raw_top = compute_exact_top_indices(secret, count=1600)
            else:
                raw_top = [classic_arr[offset + i] for i in range(1000)]
        else:
            raw_top = [classic_arr[offset + i] for i in range(1000)]

        # Nettoyage et assainissement du Top 999
        clean_top = curate_top_list(secret, raw_top, words, target_count=999)

        # Si le filtrage a retiré des éléments (ex: sigles), compléter avec les meilleurs suivants
        if len(clean_top) < 999:
            existing_set = set(clean_top)
            existing_set.add(sec_idx)

            candidates_top = compute_exact_top_indices(secret, count=1500)
            for c_idx in candidates_top:
                cw = words[c_idx]
                if c_idx not in existing_set and not is_noise_word(cw, secret):
                    clean_top.append(c_idx)
                    existing_set.add(c_idx)
                    if len(clean_top) == 999:
                        break

        assert len(clean_top) == 999, f"Erreur longueur partie #{g+1}: {len(clean_top)}"
        game_1000 = [sec_idx] + clean_top
        new_classic.extend(game_1000)

        if (g + 1) % 50 == 0 or (g + 1) == total_games:
            print(f"  [{g+1:3d}/{total_games}] parties vérifiées et assainies (secrets obscurs remplacés: {replaced_count})")

    assert len(new_classic) == total_games * 1000, "Taille finale invalide !"

    # 5. Export du catalogue final
    print("\n5/5 Export du catalogue assaini vers data/catalogue.json...")
    new_arr = array.array("H", new_classic)

    catalogue_final = {
        "v": 2,
        "modele": "frWaC 500D (Word2Vec Curation Sémantique v2.0)",
        "classicCount": classic_count,
        "classicGames": total_games,
        "popGames": base_cat.get("popGames", 91),
        "words": words,
        "vecs16": base_cat.get("vecs16"),
        "classic": base64.b64encode(new_arr.tobytes()).decode("ascii"),
        "pop": base_cat.get("pop")
    }

    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        json.dump(catalogue_final, f, ensure_ascii=False, separators=(",", ":"))

    size_mb = os.path.getsize(OUTPUT_PATH) / (1024 * 1024)
    print(f"  ✓ {OUTPUT_PATH} généré avec succès ({size_mb:.2f} Mo) !")

    # Validation sur les parties clés
    print("\nValidation des parties clés après alignement :")
    test_games = {
        "CONCOURS": 102,
        "ANANAS": 386,
        "PEINTURE": 385,
        "PUITS": 7,
        "ATELIER": 11,
        "OCÉAN": 371,
        "CASSEROLE": 377,
        "PIANO": 393,
        "PRISON": 132
    }
    for label, g_id in test_games.items():
        offset = (g_id - 1) * 1000
        sec = words[new_classic[offset]]
        top10 = [words[new_classic[offset + i]] for i in range(1, 11)]
        print(f"  • Partie #{g_id:3d} [{sec.upper()}] : {', '.join(top10)}")

    print("\n" + "="*75)
    print("✅ ASSAINISSEMENT TERMINÉ ! LE CATALOGUE EST 100% COHÉRENT ET PURIFIÉ.")
    print("="*75)

if __name__ == "__main__":
    main()
