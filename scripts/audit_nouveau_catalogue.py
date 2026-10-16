#!/usr/bin/env python3
import json
import base64
import array
from collections import defaultdict

def auditer_catalogue():
    with open('data/catalogue.json', 'r', encoding='utf-8') as f:
        data = json.load(f)

    words = data['words']
    c_bytes = base64.b64decode(data['classic'])
    c_arr = array.array('H', c_bytes)
    total_games = len(c_arr) // 1000

    print(f"Audit lancé sur {total_games} parties du nouveau catalogue...")
    print(f"Modèle déclaré : {data.get('modele')}")

    problemes = defaultdict(list)
    scores_frustration = []

    for g in range(total_games):
        secret = words[c_arr[g * 1000]]
        top100_indices = [c_arr[g * 1000 + i] for i in range(1, 101)]
        top100_words = [words[idx] for idx in top100_indices]
        top10 = top100_words[:10]

        # 1. Problème d'homonymie / sous-mots / confusion morphologique grossière
        # Ex: "cric" -> "cri", "crier" (le modèle a confondu le cric avec le verbe crier)
        subword_artifacts = []
        for w in top10:
            if len(w) <= 4 and len(secret) <= 5 and (w in secret or secret in w) and w != secret:
                # Vérifier si c'est vraiment lié sémantiquement
                subword_artifacts.append(w)

        # 2. Répétition de la même racine dans le Top 10 (ex: 5 mots en paléo-)
        prefixes = defaultdict(list)
        for w in top10:
            if len(w) >= 5:
                prefixes[w[:5]].append(w)
            elif len(w) >= 4:
                prefixes[w[:4]].append(w)
        
        monotonous_roots = [words_list for p, words_list in prefixes.items() if len(words_list) >= 3]

        # 3. Mots courts ou bruit de tokenisation (ex: "kara", "paléo", "probl")
        truncated_tokens = [w for w in top100_words if len(w) <= 4 and w.endswith(('o', 'i', 'u', 'a')) and w not in ('moto', 'auto', 'vélo', 'kilo', 'zéro', 'solo', 'duo', 'trio', 'eau', 'peau', 'bleu', 'vrai', 'joli', 'ami', 'chat', 'bras', 'bois', 'voix', 'prix', 'nuit', 'vent', 'dent', 'pain', 'main', 'pied', 'mer', 'fer', 'or', 'vin', 'jus', 'sel', 'riz', 'gaz', 'sac', 'bus', 'ski', 'roi', 'dieu', 'âme', 'loi', 'art', 'but', 'air', 'feu', 'sol')]

        # 4. Formes fléchies du mot secret dans le Top 10 (ex: "banquet" et "banqueter" pour "pique-nique")
        inflection_count = 0
        secret_stem = secret[:4] if len(secret) >= 5 else secret
        for w in top10:
            if w.startswith(secret_stem) or secret.startswith(w[:4] if len(w)>=4 else w):
                inflection_count += 1

        frustration_score = len(subword_artifacts) * 4 + len(monotonous_roots) * 3 + len(truncated_tokens[:10]) * 2 + inflection_count * 2
        scores_frustration.append((frustration_score, g + 1, secret, top10, subword_artifacts, monotonous_roots, truncated_tokens[:5]))

    # Tri par niveau de frustration
    scores_frustration.sort(key=lambda x: x[0], reverse=True)

    print("\n" + "="*70)
    print("ANALYSE DES POTENTIELS PROBLÈMES DÉTECTÉS")
    print("="*70)

    print(f"\n--- TOP 10 DES PARTIES LES PLUS PROBLÉMATIQUES ---")
    for score, num, secret, top10, subwords, roots, truncs in scores_frustration[:10]:
        print(f"\nPartie #{num} : Mot secret = [{secret.upper()}] (Score problème: {score})")
        print(f"  Top 10 actuel : {', '.join(top10)}")
        if subwords:
            print(f"  ⚠️ Confusions de sous-mots : {subwords}")
        if roots:
            print(f"  ⚠️ Racines monotones dans le top 10 : {roots}")
        if truncs:
            print(f"  ⚠️ Mots courts/tronqués suspects : {truncs}")

    print(f"\n--- TOP 5 DES PARTIES EXCELLENTES ET TRÈS COHÉRENTES ---")
    scores_frustration.sort(key=lambda x: x[0])
    for score, num, secret, top10, subwords, roots, truncs in scores_frustration[:5]:
        print(f"\nPartie #{num} : Mot secret = [{secret.upper()}]")
        print(f"  Top 10 actuel : {', '.join(top10)}")

if __name__ == '__main__':
    auditer_catalogue()
