import glob
import json
from collections import Counter

def generer_rapport():
    # Récupère tous les fichiers partie_1.json à partie_500.json dans l'ordre
    fichiers = sorted(
        glob.glob("parties/partie_*.json"),
        key=lambda x: int(x.split("_")[1].split(".")[0])
    )

    if not fichiers:
        print("Aucun fichier trouvé dans le dossier 'parties/'.")
        return

    print(f"Analyse de {len(fichiers)} parties en cours...")

    tous_les_secrets = []
    frequence_top50 = Counter()
    mots_tirets_top100 = Counter()
    mots_courts_top100 = Counter()
    lignes_detail = []

    for idx, filepath in enumerate(fichiers):
        gid = filepath.split("_")[1].split(".")[0]
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)["words"]

        # Extraction du Top 100 trié du rang 1000 (secret) au rang 900
        top100 = sorted(
            [(w, v[0], v[1]) for w, v in data.items() if isinstance(v, list) and v[1] >= 900],
            key=lambda x: -x[2]
        )
        if not top100:
            continue

        secret = top100[0][0]
        tous_les_secrets.append(f"{gid}:{secret}")

        # Statistiques globales sur les 500 parties pour repérer les mots parasites
        for w, temp, rank in top100[1:]:
            if rank >= 950:  # Top 50
                frequence_top50[w] += 1
            if "-" in w:
                mots_tirets_top100[w] += 1
            if len(w) <= 3:
                mots_courts_top100[w] += 1

        # Détail complet sur les 80 premières parties
        if idx < 80:
            top15_liste = [f"{w}({t:.0f})" for w, t, r in top100[1:16]]
            top15_texte = ", ".join(top15_liste)

            suspects = [w for w, t, r in top100[1:] if "-" in w or len(w) <= 3]
            suspects_texte = " | Suspects: " + ", ".join(suspects[:8]) if suspects else ""

            lignes_detail.append(f"P{gid} [{secret.upper()}] : {top15_texte}{suspects_texte}")

    # Écriture du rapport dans rapport_audit.txt
    with open("rapport_audit.txt", "w", encoding="utf-8") as out:
        out.write("=== 1. LISTE DES 500 MOTS SECRETS TIRÉS AU SORT ===\n")
        out.write(", ".join(tous_les_secrets) + "\n\n")

        out.write("=== 2. MOTS PARASITES (APPARAISSANT LE PLUS SOUVENT DANS LES TOP 50) ===\n")
        parasites = [f"{w} ({c}x)" for w, c in frequence_top50.most_common(60)]
        out.write(", ".join(parasites) + "\n\n")

        out.write("=== 3. MOTS COMPOSÉS AVEC TIRET DANS LES TOP 100 ===\n")
        tirets = [f"{w} ({c}x)" for w, c in mots_tirets_top100.most_common(50)]
        out.write(", ".join(tirets) + "\n\n")

        out.write("=== 4. MOTS TRÈS COURTS (2-3 LETTRES) DANS LES TOP 100 ===\n")
        courts = [f"{w} ({c}x)" for w, c in mots_courts_top100.most_common(50)]
        out.write(", ".join(courts) + "\n\n")

        out.write("=== 5. DÉTAIL DU TOP 15 DES 80 PREMIÈRES PARTIES ===\n")
        out.write("\n".join(lignes_detail) + "\n")

    print("✅ Terminé ! Le fichier 'rapport_audit.txt' a été créé.")

if __name__ == "__main__":
    generer_rapport()
