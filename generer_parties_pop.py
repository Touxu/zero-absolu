import os
import json
import random
import unicodedata
import numpy as np
from generer_500_parties import (
    MODEL_PATH, load_word2vec_bin, strip_accents, has_french_accent,
    get_singular_candidate, is_valid_french_word
)

OUTPUT_POP_DIR = "parties_pop"

# Exactement 91 Mots Secrets Pop Culture, Manga, Gaming, Fantasy & Sci-Fi (aligné sur total: 91 de app.js)
POP_CULTURE_SECRETS = [
    # Manga & Animation Japonaise (40)
    "manga", "anime", "naruto", "sasuke", "sakura", "kakashi", "hokage", "ninja",
    "shinobi", "sharingan", "chakra", "akatsuki", "konoha", "orochimaru", "itachi",
    "tsunade", "sangoku", "goku", "vegeta", "gohan", "trunks", "bulma", "saiyan",
    "luffy", "ichigo", "rukia", "shinigami", "ghibli", "miyazaki", "totoro",
    "chihiro", "mononoké", "akira", "seiya", "cosplay", "otaku", "shonen",
    "seinen", "shojo", "mangaka", "samouraï", "katana",
    # Jeux Vidéo & Consoles (24)
    "zelda", "hyrule", "triforce", "mario", "bowser", "peach", "wario", "pikachu",
    "pokémon", "mewtwo", "sonic", "tetris", "croft", "warcraft", "azeroth",
    "starcraft", "diablo", "playstation", "nintendo", "gamecube", "gameboy",
    "joystick", "manette", "mmorpg", "gamer",
    # Harry Potter, Seigneur des Anneaux, Star Wars, Comics & Sci-Fi (27)
    "voldemort", "poudlard", "gryffondor", "serpentard", "moldu", "hagrid",
    "dumbledore", "quidditch", "gandalf", "frodon", "aragorn", "gollum", "sauron",
    "mordor", "hobbit", "elfe", "dragon", "donjon", "troll", "gobelin", "vampire",
    "loup-garou", "zombie", "cyborg", "jedi", "sith", "vador", "skywalker", "yoda",
    "matrix", "batman", "spiderman", "superman", "marvel", "x-men", "wolverine",
    "terminator"
]

POP_WHITELIST_EXTRA = set(POP_CULTURE_SECRETS) | {
    "uzumaki", "jiraya", "kyuubi", "uchiwa", "uchiha", "neji", "hatake", "obito",
    "yondaime", "anbu", "kazekage", "chuunin", "juunin", "sannin", "suna",
    "mangekyou", "taijutsu", "ninjutsu", "genjutsu", "dojutsu", "byakugan",
    "jutsu", "suiton", "fuuton", "katon", "raiton", "hidan", "kakuzu", "tobi",
    "kisame", "sangohan", "végéta", "sangoten", "broly", "saiyen", "dragonball",
    "dbz", "bleach", "kurosaki", "hitsugaya", "shikai", "bankai", "zampakuto",
    "zanpakuto", "shuriken", "kunai", "kunaï", "fullmetal", "alchemist", "elric",
    "nausicaä", "laputa", "takahata", "toriyama", "kenshin", "shiryu", "nami",
    "shanks", "ganon", "majora", "ocarina", "goron", "minish", "yoshi", "donkey",
    "kong", "metroid", "samus", "pikmin", "pokédex", "pokéball", "evoli", "kanto",
    "sega", "dreamcast", "megadrive", "wii", "wiimote", "nunchuck", "xbox", "psp",
    "psone", "tekken", "bomberman", "lara", "tomb", "raider", "blizzard", "wow",
    "outreterre", "kalimdor", "lordaeron", "tauren", "arthas", "orcs", "orc",
    "warhammer", "counter-strike", "half-life", "crysis", "bioshock", "gameplay",
    "multijoueur", "mangemort", "horcruxe", "détraqueur", "weasley", "malefoy",
    "mcgonagall", "poufsouffle", "serdaigle", "choixpeau", "hermione", "harry",
    "albus", "gimli", "legolas", "boromir", "elrond", "saroumane", "bilbon",
    "bilbo", "tolkien", "gondor", "isengard", "fondcombe", "balrog", "naheulbeuk",
    "dracula", "buffy", "anakin", "palpatine", "padawan", "coruscant", "tatooine",
    "chewbacca", "jabba", "padmé", "darth", "vader", "catwoman", "punisher",
    "gotham", "smallville", "luthor", "venom", "hulk", "daredevil", "magneto",
    "spider-man", "robocop", "predator", "alien"
}

def generate_pop_games():
    os.makedirs(OUTPUT_POP_DIR, exist_ok=True)
    raw_words, raw_word_to_idx, raw_vectors = load_word2vec_bin(MODEL_PATH)

    print("2/3 Construction du dictionnaire enrichi Pop Culture, Manga & Gaming...")
    candidates = []
    seen_exact = set()
    internal_accent_lookup = {}

    for idx, w in enumerate(raw_words):
        if w in seen_exact:
            continue
        if w not in POP_WHITELIST_EXTRA and not is_valid_french_word(w):
            continue
        seen_exact.add(w)
        candidates.append((idx, w))

        if has_french_accent(w) and not w.endswith(("é", "ée", "és", "ées")):
            unacc = strip_accents(w)
            if unacc not in internal_accent_lookup:
                internal_accent_lookup[unacc] = (w, idx)

        if len(candidates) >= 110000:
            break

    all_valid_set = {w for _, w in candidates}
    clean_indices = []
    clean_words = []
    word_to_clean_pos = {}

    for orig_idx, w in candidates:
        if w not in POP_WHITELIST_EXTRA:
            if not has_french_accent(w) and w in internal_accent_lookup:
                _, acc_idx = internal_accent_lookup[w]
                if acc_idx < orig_idx:
                    continue
            sing = get_singular_candidate(w)
            if sing and (sing in word_to_clean_pos or sing in all_valid_set):
                continue

        word_to_clean_pos[w] = len(clean_words)
        clean_words.append(w)
        clean_indices.append(orig_idx)
        if len(clean_words) >= 55000:
            break

    clean_vectors = raw_vectors[np.array(clean_indices, dtype=np.int32)]

    valid_secrets = [s for s in dict.fromkeys(POP_CULTURE_SECRETS) if s in word_to_clean_pos][:91]
    random.seed(42)
    random.shuffle(valid_secrets)

    print(f"3/3 Génération de {len(valid_secrets)} parties Pop Culture dans '{OUTPUT_POP_DIR}/'...")
    for game_id, secret in enumerate(valid_secrets, start=1):
        secret_pos = word_to_clean_pos[secret]
        target_vec = clean_vectors[secret_pos]
        secret_stem = strip_accents(secret).replace("-", "")

        sims = clean_vectors @ target_vec
        order = np.argsort(-sims)

        words_dict = {}
        rank_counter = 1000

        for pos in order:
            w = clean_words[pos]
            if w == secret:
                words_dict[w] = [100.0, 1000]
                continue
            if strip_accents(w).replace("-", "") == secret_stem:
                continue

            if rank_counter > 1:
                rank_counter -= 1
                words_dict[w] = [round(float(sims[pos]) * 100, 2), rank_counter]
            else:
                words_dict[w] = round(float(sims[pos]) * 100, 1)

        filepath = os.path.join(OUTPUT_POP_DIR, f"partie_{game_id}.json")
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump({"id": game_id, "mode": "pop", "words": words_dict}, f, ensure_ascii=False, separators=(",", ":"))

    print(f"✅ Terminé ! {len(valid_secrets)} parties Pop Culture & Manga générées dans '{OUTPUT_POP_DIR}/' !")

if __name__ == "__main__":
    generate_pop_games()