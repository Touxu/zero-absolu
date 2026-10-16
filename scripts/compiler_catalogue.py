import os
import sys
import json
import base64
import random
import numpy as np

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.dirname(SCRIPT_DIR)
sys.path.insert(0, SCRIPT_DIR)

from generer_500_parties import (
    load_word2vec_bin, build_semantic_ban_mask, build_deduplicated_vocabulary,
    select_500_curated_secrets, strip_accents
)
from generer_parties_pop import POP_CULTURE_SECRETS, POP_WHITELIST_EXTRA

# Cherche automatiquement le modèle .bin dans models/ ou à la racine
MODEL_CANDIDATES = [
    os.path.join(ROOT_DIR, "models", "frWac_no_postag_no_phrase_500_skip_cut100.bin"),
    os.path.join(ROOT_DIR, "frWac_no_postag_no_phrase_500_skip_cut100.bin"),
]
MODEL_PATH = next((p for p in MODEL_CANDIDATES if os.path.exists(p)), MODEL_CANDIDATES[0])
OUTPUT_FILE = os.path.join(ROOT_DIR, "data", "catalogue.json")

NB_CLASSIC_GAMES = 500
NB_POP_GAMES = 91

def compiler_catalogue_unique():
    os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)

    # 1. Chargement du modèle Word2Vec et construction du dictionnaire Classique (55 000 mots)
    raw_words, raw_word_to_idx, raw_vectors = load_word2vec_bin(MODEL_PATH)
    banned_indices = build_semantic_ban_mask(raw_words, raw_word_to_idx, raw_vectors)
    clean_indices, clean_words, word_to_clean_pos = build_deduplicated_vocabulary(
        raw_words, raw_word_to_idx, banned_indices
    )

    classic_count = len(clean_words)
    all_words = list(clean_words)
    all_indices = list(clean_indices)

    # 2. Ajout des termes exclusifs Pop Culture / Manga / Gaming à la fin du vocabulaire
    for w_pop in sorted(POP_WHITELIST_EXTRA):
        if w_pop in raw_word_to_idx and w_pop not in word_to_clean_pos:
            word_to_clean_pos[w_pop] = len(all_words)
            all_words.append(w_pop)
            all_indices.append(raw_word_to_idx[w_pop])

    all_vectors = raw_vectors[np.array(all_indices, dtype=np.int32)]
    classic_vectors = all_vectors[:classic_count]

    print(f"    ✓ Vocabulaire mutualisé : {classic_count:,} mots Classiques + {len(all_words) - classic_count} mots Pop = {len(all_words):,} mots")

    # 3. Sélection et calcul des 500 parties Classiques (Top 1000 exact en uint16)
    classic_secrets = select_500_curated_secrets(
        all_words[:classic_count], classic_vectors, word_to_clean_pos, NB_CLASSIC_GAMES
    )
    print(f"4/6 Compression binaire des {len(classic_secrets)} parties Classiques...")
    classic_top_matrix = np.zeros((len(classic_secrets), 1000), dtype=np.uint16)

    for g_idx, secret in enumerate(classic_secrets):
        secret_pos = word_to_clean_pos[secret]
        target_vec = classic_vectors[secret_pos]
        secret_stem = strip_accents(secret).replace("-", "")

        sims = classic_vectors @ target_vec
        order = np.argsort(-sims)

        top_ids = [secret_pos]
        for pos in order:
            if pos == secret_pos:
                continue
            w_stem = strip_accents(all_words[pos]).replace("-", "")
            if w_stem == secret_stem or (len(secret_stem) >= 5 and w_stem == secret_stem + "e"):
                continue
            top_ids.append(int(pos))
            if len(top_ids) == 1000:
                break

        classic_top_matrix[g_idx] = np.array(top_ids, dtype=np.uint16)

    # 4. Sélection et calcul des 91 parties Pop Culture & Manga (Top 1000 exact en uint16)
    valid_pop_secrets = [s for s in dict.fromkeys(POP_CULTURE_SECRETS) if s in word_to_clean_pos][:NB_POP_GAMES]
    random.seed(42)
    random.shuffle(valid_pop_secrets)

    print(f"5/6 Compression binaire des {len(valid_pop_secrets)} parties Pop Culture & Manga...")
    pop_top_matrix = np.zeros((len(valid_pop_secrets), 1000), dtype=np.uint16)

    for g_idx, secret in enumerate(valid_pop_secrets):
        secret_pos = word_to_clean_pos[secret]
        target_vec = all_vectors[secret_pos]
        secret_stem = strip_accents(secret).replace("-", "")

        sims = all_vectors @ target_vec
        order = np.argsort(-sims)

        top_ids = [secret_pos]
        for pos in order:
            if pos == secret_pos:
                continue
            if strip_accents(all_words[pos]).replace("-", "") == secret_stem:
                continue
            top_ids.append(int(pos))
            if len(top_ids) == 1000:
                break

        pop_top_matrix[g_idx] = np.array(top_ids, dtype=np.uint16)

    # 5. Empreintes thermiques compactes 16-D (int8) pour calculer les mots froids à la volée
    print("6/6 Quantification des empreintes thermiques 16-D et écriture de data/catalogue.json...")
    rng = np.random.RandomState(42)
    proj = rng.randn(all_vectors.shape[1], 16).astype(np.float32)
    proj, _ = np.linalg.qr(proj)
    vecs16 = all_vectors @ proj
    norms16 = np.linalg.norm(vecs16, axis=1, keepdims=True)
    norms16[norms16 == 0] = 1.0
    vecs16 /= norms16
    vecs16_int8 = np.clip(np.round(vecs16 * 127.0), -127, 127).astype(np.int8)

    catalogue_payload = {
        "v": "1.2",
        "classicCount": classic_count,
        "classicGames": len(classic_secrets),
        "popGames": len(valid_pop_secrets),
        "words": all_words,
        "vecs16": base64.b64encode(vecs16_int8.tobytes()).decode("ascii"),
        "classic": base64.b64encode(classic_top_matrix.astype("<u2").tobytes()).decode("ascii"),
        "pop": base64.b64encode(pop_top_matrix.astype("<u2").tobytes()).decode("ascii")
    }

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(catalogue_payload, f, ensure_ascii=False, separators=(",", ":"))

    size_mb = os.path.getsize(OUTPUT_FILE) / (1024 * 1024)
    print(f"✅ Terminé ! Fichier unique '{OUTPUT_FILE}' généré ({size_mb:.2f} Mo au lieu de 530 Mo) !")

if __name__ == "__main__":
    compiler_catalogue_unique()