#!/usr/bin/env python3
# =============================================================================
# AUDIT DE COHÉRENCE SÉMANTIQUE SUR 100 PARTIES DU CATALOGUE
# Analyse les 100 mots les plus proches pour chaque mot secret
# =============================================================================

import os
import sys
import json
import base64
import array
from collections import defaultdict

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CATALOGUE_PATH = os.path.join(ROOT_DIR, "data", "catalogue.json")

def charger_catalogue():
    with open(CATALOGUE_PATH, "r", encoding="utf-8") as f:
        cat = json.load(f)
    words = cat["words"]
    classic_buf = base64.b64decode(cat["classic"])
    classic_arr = array.array("H")
    classic_arr.frombytes(classic_buf)
    return words, classic_arr

def distance_levenshtein(s1, s2):
    if len(s1) < len(s2):
        return distance_levenshtein(s2, s1)
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

def analyser_100_parties():
    words, classic_arr = charger_catalogue()
    nb_games = min(100, len(classic_arr) // 1000)
    print(f"Audit lancé sur {nb_games} parties classiques...")

    resultats = []
    total_typos_suspects = 0
    total_derivations = 0
    total_mots_obscurs = 0

    # Dictionnaire de contrôle basique : longueur, présence de caractères suspects
    for g in range(nb_games):
        offset = g * 1000
        secret = words[classic_arr[offset]]
        
        # Les 100 mots les plus proches (indices 1 à 100, soit Rangs 999 à 900)
        top100_indices = [classic_arr[offset + r] for r in range(1, 101)]
        top100 = [words[idx] for idx in top100_indices]
        
        # Top 10 pour affichage rapide
        top10 = top100[:10]

        # 1. Détections de dérivés morphologiques directs (même radical de 4+ lettres ou distance <= 2)
        derivations_secret = []
        for w in top100:
            if len(secret) >= 4 and (w.startswith(secret[:4]) or secret.startswith(w[:4])):
                if w != secret:
                    derivations_secret.append(w)
            elif distance_levenshtein(secret, w) <= 2 and len(secret) >= 5:
                derivations_secret.append(w)

        # 2. Détection de fautes de frappe / doublons quasi-identiques dans le Top 100
        paires_typos = []
        for i in range(len(top100)):
            w1 = top100[i]
            for j in range(i + 1, min(i + 15, len(top100))):
                w2 = top100[j]
                if abs(len(w1) - len(w2)) <= 1 and distance_levenshtein(w1, w2) == 1:
                    paires_typos.append((w1, w2))

        # 3. Mots potentiellement frustrants (très courts, avec tirets étranges, ou jargon)
        mots_atypiques = [w for w in top100 if len(w) <= 2 or w.count("-") >= 2 or any(c in w for c in "0123456789_")]

        score_frustration = (len(derivations_secret) * 1.5) + (len(paires_typos) * 2) + (len(mots_atypiques) * 2)

        total_derivations += len(derivations_secret)
        total_typos_suspects += len(paires_typos)
        total_mots_obscurs += len(mots_atypiques)

        resultats.append({
            "game_id": g + 1,
            "secret": secret,
            "top10": top10,
            "top100": top100,
            "derivations_count": len(derivations_secret),
            "derivations_sample": derivations_secret[:4],
            "paires_typos": paires_typos[:3],
            "mots_atypiques": mots_atypiques,
            "score_frustration": score_frustration
        })

    # Trier par frustration (les pires et les meilleures)
    resultats_tries = sorted(resultats, key=lambda x: x["score_frustration"], reverse=True)

    print("\n=======================================================")
    print(f"RAPPORT GLOBAL SUR {nb_games} PARTIES AUDITÉES")
    print("=======================================================")
    print(f"• Dérivations morphologiques du mot secret dans le Top 100 : {total_derivations / nb_games:.1f} par partie en moyenne")
    print(f"• Paires de doublons / fautes de frappe détectées : {total_typos_suspects / nb_games:.1f} par partie")
    print(f"• Mots atypiques / bruit web détectés : {total_mots_obscurs / nb_games:.1f} par partie")

    print("\n--- TOP 5 DES PARTIES LES PLUS COHÉRENTES ET AGRÉABLES (PEU DE BRUIT) ---")
    for r in resultats_tries[-5:]:
        print(f"\nPartie #{r['game_id']} : Mot secret = [{r['secret'].upper()}]")
        print(f"  Top 10 : {', '.join(r['top10'])}")
        print(f"  Dérivés : {r['derivations_count']} | Doublons/Typos : {len(r['paires_typos'])}")

    print("\n--- TOP 5 DES PARTIES LES PLUS FRUSTRANTES (BRUIT, DOUBLONS, OU DÉRIVATIONS EXCESSIVES) ---")
    for r in resultats_tries[:5]:
        print(f"\nPartie #{r['game_id']} : Mot secret = [{r['secret'].upper()}] (Score frustration: {r['score_frustration']:.1f})")
        print(f"  Top 10 : {', '.join(r['top10'])}")
        if r['derivations_sample']:
            print(f"  Dérivés directs ({r['derivations_count']}) : {', '.join(r['derivations_sample'])}")
        if r['paires_typos']:
            print(f"  Paires suspectes/typos : {r['paires_typos']}")
        if r['mots_atypiques']:
            print(f"  Mots atypiques : {r['mots_atypiques']}")

if __name__ == "__main__":
    analyser_100_parties()
