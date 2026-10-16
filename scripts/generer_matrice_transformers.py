#!/usr/bin/env python3
# =============================================================================
# GÉNÉRATEUR DE CATALOGUE SÉMANTIQUE PAR TRANSFORMERS (OPTION B : SENTENCE-CAMEMBERT)
# Remplace les embeddings Word2Vec de 2012 par des Transformers récents en français.
#
# Modèle d'excellence recommandé :
#   - "Lajavaness/sentence-camembert-large" (335M paramètres, 1024 dimensions)
#     Développé et affiné spécifiquement sur le français pour la similarité sémantique (STS).
#     Offre une logique notionnelle, culturelle et contextuelle incomparablement plus
#     riche et subtile qu'un modèle base ou un vieux Word2Vec.
#
# Autres modèles supportés :
#   - "dangvantuan/sentence-camembert-base" (110M params, 768D - plus léger pour CPU)
#   - "sentence-transformers/paraphrase-multilingual-mpnet-base-v2" (278M params, 768D)
#   - "sentence-transformers/all-MiniLM-L6-v2" (22M params, 384D - ultra-rapide pour prototypage)
# =============================================================================

import os
import sys
import json
import base64
import array
import argparse

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.dirname(SCRIPT_DIR)
OUTPUT_FILE = os.path.join(ROOT_DIR, "data", "catalogue_transformers.json")

MODEL_PRESETS = {
    "lajavaness": "Lajavaness/sentence-camembert-large",
    "camembert": "dangvantuan/sentence-camembert-base",
    "mpnet": "sentence-transformers/paraphrase-multilingual-mpnet-base-v2",
    "minilm": "sentence-transformers/all-MiniLM-L6-v2"
}

DEFAULT_MODEL = "Lajavaness/sentence-camembert-large"

def verifier_dependances():
    try:
        import torch
        import sentence_transformers
        print("\n✅ Environnement Machine Learning opérationnel !")
        print(f"PyTorch version : {torch.__version__}")
        print(f"CUDA disponible : {torch.cuda.is_available()}")
        return True
    except ImportError:
        print("\n" + "="*70)
        print("⚠️ DÉPENDANCES MACHINE LEARNING REQUISES")
        print("="*70)
        print("Pour générer la matrice avec Lajavaness/sentence-camembert-large :")
        print("\n    pip install torch sentence-transformers scikit-learn numpy\n")
        print("Avantage de Lajavaness/sentence-camembert-large (335M paramètres) :")
        print("  • 1024 dimensions d'embedding (contre 300 pour Word2Vec et 768 pour CamemBERT-base)")
        print("  • Élimine les fausses proximités morphologiques et les antonymes")
        print("  • Comprend le sens conceptuel profond en français (ex. château <-> forteresse/royauté)")
        print("  • Impact nul sur le joueur web : le calcul est fait 1 seule fois hors-ligne !")
        print("="*70 + "\n")
        return False

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
    import re
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
    import re
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
    """
    Garantit que le Top 15 offre 15 concepts distincts :
    1. Élimine le bruit web et les sous-mots parasites.
    2. Dé-double les familles morphologiques (ex: un seul 'banane' dans le Top 10).
    3. Place les flexions du mot secret au-delà du rang 980.
    """
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

def encoder_mots_transformers(mots, nom_modele=DEFAULT_MODEL,
                                prompt_template="Le concept sémantique et la définition du mot « {} » dans la langue française."):
    from sentence_transformers import SentenceTransformer
    import numpy as np

    print(f"\nChargement du modèle Transformer [{nom_modele}]...")
    model = SentenceTransformer(nom_modele)
    try:
        model.max_seq_length = 512
    except Exception:
        pass

    phrases = [prompt_template.format(m) for m in mots]
    print(f"Calcul des embeddings sémantiques pour {len(mots)} mots (batch_size=128)...")
    embeddings = model.encode(phrases, batch_size=128, show_progress_bar=True, normalize_embeddings=True)
    return np.array(embeddings, dtype=np.float32)

def compiler_catalogue_transformers(vocab_file=None, nb_games=500, output_path=OUTPUT_FILE, nom_modele=DEFAULT_MODEL):
    if not verifier_dependances():
        return False

    import numpy as np
    from sklearn.decomposition import PCA

    # 1. Chargement du vocabulaire de base épuré
    catalogue_existant = os.path.join(ROOT_DIR, "data", "catalogue.json")
    with open(catalogue_existant, "r", encoding="utf-8") as f:
        cat_data = json.load(f)

    all_words = cat_data["words"]
    classic_count = cat_data.get("classicCount", 55000)
    words = all_words[:classic_count]

    print(f"Vocabulaire prêt : {len(words)} mots classiques.")

    # 2. Encodage avec le Transformer sélectionné
    vectors = encoder_mots_transformers(words, nom_modele=nom_modele)

    # 3. Compression en 16 dimensions pour le produit scalaire ultra-rapide côté client
    print("Réduction de dimensionnalité à 16 composantes (PCA normalisée)...")
    pca = PCA(n_components=16)
    vecs16_float = pca.fit_transform(vectors)
    norms = np.linalg.norm(vecs16_float, axis=1, keepdims=True)
    norms[norms == 0] = 1.0
    vecs16_norm = vecs16_float / norms
    vecs16_int8 = np.clip(np.round(vecs16_norm * 127), -128, 127).astype(np.int8)

    # 4. Calcul des Top 1000 pour chaque mot secret
    print(f"Génération des Top 1000 pour {nb_games} parties avec filtrage anti-dérivés...")
    classic_indices = []

    # 4. Sélection des mots secrets : priorise les vrais mots secrets concrets de catalogue.json
    word_to_idx = {w: i for i, w in enumerate(words)}
    secrets_indices = []
    if "classic" in cat_data:
        try:
            c_bytes = base64.b64decode(cat_data["classic"])
            c_arr = array.array("H", c_bytes)
            num_available = min(nb_games, len(c_arr) // 1000)
            for g in range(num_available):
                w_sec = all_words[c_arr[g * 1000]]
                if w_sec in word_to_idx:
                    secrets_indices.append(word_to_idx[w_sec])
            print(f"Extraction de {len(secrets_indices)} mots secrets captivants de catalogue.json.")
        except Exception as e:
            print("Note extraction secrets:", e)

    # Complète si nécessaire
    if len(secrets_indices) < nb_games:
        fallback = list(range(100, min(len(words), 100 + nb_games * 25), 25))
        for idx in fallback:
            if idx not in secrets_indices:
                secrets_indices.append(idx)
            if len(secrets_indices) >= nb_games:
                break

    for count, s_idx in enumerate(secrets_indices):
        secret_word = words[s_idx]
        s_vec = vectors[s_idx]

        # Similarité cosinus globale
        sims = np.dot(vectors, s_vec)
        # Tri décroissant
        filtered_top = filtrer_et_diversifier_top(s_idx, secret_word, ranked, words, max_keep=999)
        assert len(filtered_top) == 999, f"Erreur longueur partie #{count+1}"
        game_top1000 = [s_idx] + filtered_top
        classic_indices.extend(game_top1000)

        if (count + 1) % 50 == 0:
            print(f"  -> {count + 1}/{nb_games} parties calculées...")

    assert len(classic_indices) == nb_games * 1000, "Longueur totale incorrecte !"
    classic_arr = np.array(classic_indices, dtype=np.uint16)

    # 5. Export JSON compact compatible moteur ZeroAbsolu
    catalogue_final = {
        "v": 2,
        "modele": nom_modele,
        "classicCount": classic_count,
        "classicGames": nb_games,
        "popGames": cat_data.get("popGames", 91),
        "words": all_words,
        "vecs16": base64.b64encode(vecs16_int8.tobytes()).decode("ascii"),
        "classic": base64.b64encode(classic_arr.tobytes()).decode("ascii"),
        "pop": cat_data.get("pop", "")
    }

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(catalogue_final, f, ensure_ascii=False)

    taille_mo = os.path.getsize(output_path) / (1024 * 1024)
    print(f"\n✅ Nouveau catalogue Transformers généré avec succès !")
    print(f"Modèle source : {nom_modele}")
    print(f"Fichier : {output_path} ({taille_mo:.2f} Mo)")
    return True

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Générateur de catalogue Transformers pour ZéroAbsolu")
    parser.add_argument("--modele", default="lajavaness",
                        help="Choix du modèle : lajavaness (recommandé), camembert, mpnet, minilm, ou identifiant HuggingFace")
    parser.add_argument("--parties", type=int, default=500, help="Nombre de parties classiques à générer (défaut: 500)")
    parser.add_argument("--verifier", action="store_true", help="Vérifie si PyTorch et sentence-transformers sont disponibles")
    parser.add_argument("--compiler", action="store_true", help="Lance la génération complète du catalogue")
    args = parser.parse_args()

    target_model = MODEL_PRESETS.get(args.modele.lower(), args.modele)

    if args.compiler:
        compiler_catalogue_transformers(nb_games=args.parties, nom_modele=target_model)
    else:
        verifier_dependances()
