import numpy as np

MODEL_PATH = "frWac_no_postag_no_phrase_500_skip_cut100.bin"

CANDIDATS_POP_MANGA = [
    # Manga & Anime
    "manga", "anime", "naruto", "sasuke", "sakura", "kakashi", "hokage", "ninja", "shinobi",
    "sharingan", "chakra", "akatsuki", "konoha", "sangoku", "goku", "vegeta", "saiyan",
    "namek", "freezer", "luffy", "zoro", "sanji", "chopper", "ichigo", "shinigami",
    "bankai", "alchemist", "ghibli", "miyazaki", "totoro", "mononoké", "akira", "seiya",
    "cosplay", "otaku", "shonen", "seinen", "shojo", "mangaka", "samouraï", "katana",
    # Jeux Vidéo
    "zelda", "hyrule", "triforce", "ganondorf", "mario", "luigi", "bowser", "peach",
    "pikachu", "pokémon", "pokemon", "mewtwo", "sonic", "tetris", "pacman", "lara",
    "croft", "warcraft", "azeroth", "starcraft", "diablo", "skyrim", "playstation",
    "nintendo", "gameboy", "joystick", "manette", "arcade", "boss", "mmorpg", "gamer",
    # Fantasy, Sci-Fi & Pop Culture
    "voldemort", "poudlard", "gryffondor", "serpentard", "moldu", "hagrid", "dumbledore",
    "gandalf", "frodon", "sauron", "anneau", "mordor", "hobbit", "elfe", "nain", "orc",
    "dragon", "donjon", "troll", "gobelin", "vampire", "loup-garou", "zombie", "cyborg",
    "jedi", "sith", "vador", "skywalker", "yoda", " sabre", "matrix", "batman", "joker",
    "spiderman", "superman", "marvel", "x-men", "wolverine", "avatar", "terminator"
]

def explorer_modele():
    print("Chargement du modèle pour le scan Pop Culture & Manga...")
    with open(MODEL_PATH, "rb") as f:
        vocab_size, dim = map(int, f.readline().decode("utf-8").split())
        vectors = np.empty((vocab_size, dim), dtype=np.float32)
        words = []
        word_to_idx = {}
        for i in range(vocab_size):
            wb = bytearray()
            while True:
                ch = f.read(1)
                if ch == b" " or not ch: break
                if ch != b"\n": wb.extend(ch)
            w = wb.decode("utf-8", errors="ignore").lower().strip()
            vectors[i] = np.frombuffer(f.read(dim * 4), dtype=np.float32)
            words.append(w)
            if w not in word_to_idx:
                word_to_idx[w] = i

    norms = np.linalg.norm(vectors, axis=1, keepdims=True)
    norms[norms == 0] = 1.0
    vectors /= norms

    print("\n=== RÉSULTATS DU SCAN POP CULTURE / MANGA / GAMING ===")
    trouves = 0
    for terme in CANDIDATS_POP_MANGA:
        t = terme.strip().lower()
        if t not in word_to_idx:
            print(f"❌ '{t}' : Inconnu du modèle")
            continue
        trouves += 1
        idx = word_to_idx[t]
        sims = vectors @ vectors[idx]
        top_idx = np.argsort(-sims)[1:11]
        voisins = ", ".join([f"{words[i]}({sims[i]*100:.0f}%)" for i in top_idx])
        print(f"✅ [{t.upper()}] (rang fréqu. #{idx}) -> {voisins}")

    print(f"\nBilans : {trouves}/{len(CANDIDATS_POP_MANGA)} termes Pop Culture reconnus avec succès !")

if __name__ == "__main__":
    explorer_modele()