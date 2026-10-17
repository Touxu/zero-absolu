#!/usr/bin/env python3
# =============================================================================
# EXTRACTEUR FASTTEXT (META CC.FR.300 -> 55 059 MOTS)
#
# Lit cc.fr.300.vec.gz (ou stdin) et extrait UNIQUEMENT les vecteurs des
# 55 059 mots du jeu ZéroAbsolu pour produire models/fasttext_fr_300.bin (~66 Mo).
# =============================================================================

import os
import sys
import json
import math
import struct
import gzip
import time

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.dirname(SCRIPT_DIR)
CATALOGUE_PATH = os.path.join(ROOT_DIR, "data", "catalogue.json")
GZ_PATH = os.path.join(ROOT_DIR, "models", "cc.fr.300.vec.gz")
OUTPUT_BIN_PATH = os.path.join(ROOT_DIR, "models", "fasttext_fr_300.bin")

def main():
    print("=" * 70)
    print("EXTRACTION META FASTTEXT (CC.FR.300 -> 55 059 MOTS)")
    print("=" * 70)

    with open(CATALOGUE_PATH, "r", encoding="utf-8") as f:
        cat = json.load(f)

    words = cat["words"]
    dim = 300
    target_set = set(words)
    w2i = {w: i for i, w in enumerate(words)}
    print(f"Cible : {len(words):,} mots du dictionnaire ZéroAbsolu.")

    vecs_array = [None] * len(words)
    found_count = 0
    t0 = time.time()
    lines_read = 0

    if os.path.exists(GZ_PATH):
        print(f"Lecture directe de '{GZ_PATH}' via gzip...")
        in_stream = gzip.open(GZ_PATH, "rt", encoding="utf-8", errors="ignore")
    else:
        print("Lecture depuis stdin...")
        in_stream = sys.stdin

    header_line = in_stream.readline()
    if header_line:
        print(f"En-tête FastText : {header_line.strip()}")

    for line in in_stream:
        lines_read += 1
        space_pos = line.find(" ")
        if space_pos <= 0:
            continue

        raw_word = line[:space_pos].lower().strip()

        if raw_word in target_set:
            idx = w2i[raw_word]
            if vecs_array[idx] is None:
                parts = line[space_pos + 1:].strip().split(" ")
                if len(parts) == dim:
                    floats = [float(x) for x in parts]
                    norm = math.sqrt(sum(x * x for x in floats)) or 1.0
                    normed = [x / norm for x in floats]
                    vecs_array[idx] = struct.pack(f"<{dim}f", *normed)
                    found_count += 1

        if lines_read % 100000 == 0 or found_count == len(words):
            now = time.time()
            rate = lines_read / (now - t0 + 0.001)
            print(f"  [{lines_read:7,d} mots lus] Mots trouvés : {found_count:,}/{len(words):,} ({found_count/len(words)*100:.1f}%) | {rate:,.0f} lignes/sec")
            sys.stdout.flush()

        if found_count == len(words):
            print("  ✓ 100% des mots du dictionnaire trouvés !")
            break

    in_stream.close()

    total_time = time.time() - t0
    print(f"\nExtraction terminée en {total_time:.1f}s.")
    print(f"Résultat : {found_count:,}/{len(words):,} mots extraits ({found_count/len(words)*100:.2f}% de couverture).")

    # Écriture du fichier binaire 55k x 300
    zero_vec = struct.pack(f"<{dim}f", *([0.0] * dim))
    missing_words = []
    with open(OUTPUT_BIN_PATH, "wb") as f_out:
        f_out.write(f"{len(words)} {dim}\n".encode("utf-8"))
        for i, packed in enumerate(vecs_array):
            if packed is not None:
                f_out.write(packed)
            else:
                f_out.write(zero_vec)
                missing_words.append(words[i])

    out_size_mb = os.path.getsize(OUTPUT_BIN_PATH) / (1024 * 1024)
    print(f"✓ Fichier binaire généré : {OUTPUT_BIN_PATH} ({out_size_mb:.2f} Mo)")
    if missing_words:
        print(f"  Note : {len(missing_words)} mots non trouvés dans FastText (ex: {missing_words[:5]})")
    print("=" * 70)

if __name__ == "__main__":
    main()
