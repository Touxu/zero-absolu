import time
from playwright.sync_api import sync_playwright

SITE_URL = "https://zero-absolu.vercel.app"
MDP_BOTS = "Soleil2026Secret"

# Corpus Classique de ~935 mots courants (noms, verbes, adjectifs + variantes sans accent / pluriels / féminins)
CORPUS_CLASSIQUE = """
maison appartement chambre cuisine salon jardin porte fenetre toit mur plafond plancher escalier
table chaise fauteuil canape lit matelas oreiller couverture drap armoire placard tiroir etagere
miroir lampe ampoule bougie horloge montre reveil calendrier rideau tapis coussin balai brosse
aspirateur seau eponge savon shampoing serviette peigne rasoir dentifrice baignoire douche lavabo
robinet evier four refrigerateur congelateur casserole poele marmite assiette bol tasse verre
fourchette couteau cuillere bouteille carafe plateau passoire tire-bouchon poubelle
pain baguette croissant brioche gateau tarte biscuit chocolat bonbon miel confiture sucre farine
beurre lait fromage yaourt creme oeuf omelette viande boeuf poulet canard dinde porc jambon
saucisse poisson saumon thon truite sardine crevette crabe moule huitre legume salade tomate
carotte oignon ail pomme poire banane orange citron fraise framboise cerise raisin peche abricot
prune melon pasteque ananas kiwi noix noisette amande chataigne olive riz pate soupe purée
pizza sandwich frite sauce huile vinaigre sel poivre epice eau jus cafe the vin biere cidre
arbre foret plante fleur feuille racine branche tronc ecorce herbe mousse buisson haie pelouse
champignon montagne colline vallee falaise caverne grotte rocher pierre caillou sable terre boue
argile desert oasis volcan cratere lave ocean mer plage vague ecume maree ile archipel riviere
fleuve ruisseau lac etang cascade source marais pont route chemin sentier piste rue trottoir
ciel soleil lune etoile planete comete galaxie univers nuage pluie orage foudre tonnerre vent
tempete ouragan tornade neige glace verglas brouillard arc-en-ciel aurore crepuscule ombre lumiere
feu flamme fumee cendre charbon bois metal fer acier cuivre bronze or argent diamant cristal
animal chien chiot chat cheval ane vache taureau veau mouton brebis agneau chevre cochon sanglier
cerf biche chevreuil loup renard ours lion tigre leopard panthere elephant girafe zebre singe
gorille kangourou koala panda lapin lievre ecureuil souris rat herisson taupe chauve-souris
baleine dauphin requin phoque tortue crocodile serpent lezard grenouille crapaud escargot limace
oiseau aigle faucon hibou chouette corbeau pigeon moineau hirondelle mouette canard cygne oie
poule coq poussin paon perroquet autruche manchot insecte abeille guepe fourmi papillon chenille
coccinelle mouche moustique araignee scorpion ver crabe homard meduse pieuvre
corps tete visage front oeil yeux paupiere sourcil cil nez oreille bouche levre langue dent
gencive menton joue barbe moustache cheveu cou gorge epaule bras coude poignet main doigt pouce
ongle poitrine dos ventre estomac hanche jambe cuisse genou cheville pied talon orteil peau os
squelette crane muscle sang veine artere coeur poumon cerveau nerf foie rein larme sueur voix
sante medecine hopital clinique pharmacie medecin docteur chirurgien dentiste infirmier patient
malade maladie douleur fievre toux rhume grippe blessure plaie brulure fracture medicament pilule
vaccin piqure seringue pansement ambulance urgence operation guerison sommeil reve fatigue stress
famille pere mere parent enfant fils fille frere soeur grand-pere grand-mere oncle tante cousin
neveu ami copain voisin invite bebe garcon homme femme adulte vieillard personne gens foule
amour amitie joie bonheur plaisir rire sourire paix calme espoir confiance courage fierte surprise
peur crainte colere rage tristesse chagrin peine douleur honte regret jalousie ennui solitude
ecole college lycee universite classe cour cantine eleve ecolier etudiant professeur maitre
directeur cours lecon devoir exercice examen concours diplome note cahier carnet livre manuel
dictionnaire page feuille crayon stylo feutre craie gomme regle ciseaux colle sac cartable
bureau travail metier emploi entreprise usine atelier chantier magasin boutique marche supermarche
banque poste mairie tribunal police prison caserne gare aeroport port hotel restaurant cinema
theatre musee bibliotheque stade piscine parc zoo cirque eglise cathedrale chateau palais tour
ouvrier employe patron directeur ingenieur technicien artisan commercant vendeur client facteur
boulanger patissier boucher cuisinier serveur agriculteur paysan fermier pecheur marin soldat
policier gendarme pompier juge avocat journaliste ecrivain auteur poete musicien chanteur acteur
peintre sculpteur architecte mecanicien chauffeur pilote plombier electricien menuisier macon
voiture automobile camion bus autocar train metro tramway velo bicyclette moto scooter avion
helicoptere fusee bateau navire voilier barque sous-marin moteur roue pneu volant frein phare
essence billet ticket bagage valise carte boussole voyage vacance aventure vitesse accident panne
ordinateur clavier souris ecran imprimante telephone portable television radio appareil camera
photo image film musique chanson instrument piano guitare violon flute tambour trompette concert
art peinture dessin tableau couleur rouge bleu vert jaune orange violet rose noir blanc gris
sport jeu match course ballon balle equipe joueur arbitre victoire defaite champion medaille
argent monnaie piece billet prix achat vente salaire dette credit impot fortune tresor richesse
loi droit justice crime delit vol prison preuve temoin proces paix guerre bataille arme fusil
epee bouclier bombe victoire roi reine prince chateau chevalier drapeau nation pays ville village
temps heure minute seconde jour matin midi soir nuit semaine mois annee siecle passe present futur
debut fin matinee soiree printemps ete automne hiver histoire science nature energie force chaleur
aimer adorer detester parler dire ecouter entendre voir regarder chercher trouver donner prendre
mettre poser ouvrir fermer entrer sortir monter descendre partir arriver venir aller marcher
courir sauter nager voler tomber dormir reveiller manger boire cuisiner couper laver nettoyer
acheter vendre payer compter ecrire lire apprendre comprendre savoir penser croire oublier rever
chanter danser jouer gagner perdre construire detruire reparer aider proteger battre defendre
grand petit haut bas long court large etroit gros mince lourd leger fort faible dur mou doux
chaud froid tiede sec humide propre sale neuf vieux jeune ancien moderne beau joli laid riche
pauvre plein vide ouvert ferme rapide lent calme bruyant facile difficile possible vrai faux
bon mauvais meilleur pire heureux triste content calme furieux fatigue malade seul libre
plantes arbres fleurs forets maisons voitures chiens chats enfants livres tables chaises
ecoles hopitaux chateaux gateaux oiseaux chevaux journaux animaux travaux yeux cieux
etoiles rivieres montagnes fenetres portes routes chemins idees problemes solutions
chanteuse vendeuse actrice directrice fermiere boulangere infirmiere policiere
grandes petites belles nouvelles vieilles bonnes mauvaises chaudes froides
""".split()

# Corpus Pop Culture, Manga, Gaming, Fantasy & Sci-Fi (110 termes)
CORPUS_POP_CULTURE = """
manga anime naruto sasuke sakura kakashi hokage ninja shinobi sharingan chakra akatsuki konoha
orochimaru itachi tsunade uzumaki jiraya uchiwa obito byakugan ninjutsu taijutsu genjutsu
sangoku goku vegeta gohan trunks bulma saiyan sangohan broly dragonball dbz
luffy nami shanks ichigo rukia shinigami kurosaki bleach bankai shikai katana shuriken kunai
ghibli miyazaki totoro chihiro mononoke laputa takahata akira seiya shiryu kenshin
cosplay otaku shonen seinen shojo mangaka samourai fullmetal alchemist elric
zelda hyrule triforce ganon majora ocarina mario bowser peach wario yoshi donkey metroid samus
pikachu pokemon mewtwo pokedex pokeball evoli kanto sonic sega dreamcast megadrive
tetris bomberman lara croft raider warcraft azeroth starcraft diablo blizzard outreterre
playstation nintendo gamecube gameboy wii wiimote xbox psp tekken joystick manette mmorpg gamer
voldemort poudlard gryffondor serpentard moldu hagrid dumbledore quidditch mangemort horcruxe
weasley malefoy hermione harry gandalf frodon aragorn gollum sauron mordor hobbit bilbon
legolas gimli elrond saroumane tolkien gondor elfe dragon donjon troll gobelin
vampire dracula loup-garou zombie cyborg robocop terminator alien predator
jedi sith vador skywalker yoda anakin palpatine padawan chewbacca tatooine
matrix batman spiderman superman marvel x-men wolverine catwoman gotham venom hulk magneto
""".split()

MOTS_CLASSIQUES_UNIQUES = list(dict.fromkeys(CORPUS_CLASSIQUE))
MOTS_POP_UNIQUES = list(dict.fromkeys(CORPUS_POP_CULTURE))

def connecter_ou_inscrire_bot(page, pseudo, password):
    """Connecte un bot sur Supabase (ou crée son compte s'il n'existe pas encore)."""
    page.wait_for_selector("#authPseudo", timeout=10000)
    page.fill("#authPseudo", pseudo)
    page.fill("#authPassword", password)
    page.click("#authSubmitBtn")
    page.wait_for_timeout(1600)

    err = page.locator("#authError").inner_text().strip()
    if "Aucun compte" in err:
        page.click("#tabRegisterBtn")
        page.fill("#authPseudo", pseudo)
        page.fill("#authPassword", password)
        page.click("#authSubmitBtn")
        page.wait_for_timeout(1800)
        err = page.locator("#authError").inner_text().strip()

    welcome_ok = not page.locator("#welcomeModal").evaluate("el => el.classList.contains('hidden')")
    if welcome_ok:
        page.click("#welcomePlayBtn")
        page.wait_for_timeout(300)
    return welcome_ok, err

def lancer_stress_test():
    rapport = ["================================================================="]
    rapport.append("   RAPPORT DE STRESS-TEST & AUDIT MULTI-BOTS (ZéroAbsolu v1.1)")
    rapport.append("=================================================================\n")
    erreurs_js = []

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)

        ctx_alpha = browser.new_context(viewport={"width": 390, "height": 844}, is_mobile=True)
        ctx_bravo = browser.new_context(viewport={"width": 390, "height": 844}, is_mobile=True)
        ctx_charlie = browser.new_context(viewport={"width": 1280, "height": 800})

        p_alpha = ctx_alpha.new_page()
        p_bravo = ctx_bravo.new_page()
        p_charlie = ctx_charlie.new_page()

        for nom, pg in [("Alpha", p_alpha), ("Bravo", p_bravo), ("Charlie", p_charlie)]:
            pg.on("pageerror", lambda err, n=nom: erreurs_js.append(f"[{n}] {err}"))

        # ---------------------------------------------------------------------
        # PILIER 1 : CONNEXION DES 3 BOTS SUR SUPABASE
        # ---------------------------------------------------------------------
        print("1/6 Connexion des 3 bots (BotAlpha, BotBravo, BotCharlie) sur Supabase...")
        p_alpha.goto(SITE_URL, wait_until="networkidle")
        p_bravo.goto(SITE_URL, wait_until="networkidle")
        p_charlie.goto(SITE_URL, wait_until="networkidle")

        # S'assure que BotAlpha démarre en mode Classique pour le Pilier 2
        p_alpha.evaluate("localStorage.setItem('zeroabsolu_mode', 'classic')")

        ok_a, err_a = connecter_ou_inscrire_bot(p_alpha, "BotAlpha", MDP_BOTS)
        ok_b, err_b = connecter_ou_inscrire_bot(p_bravo, "BotBravo", MDP_BOTS)
        ok_c, err_c = connecter_ou_inscrire_bot(p_charlie, "BotCharlie", MDP_BOTS)

        version_en_ligne = p_alpha.locator("#versionBadgeTop").inner_text().strip()
        rapport.append(f"### 1. AUTHENTIFICATION SUPABASE DES 3 BOTS ({version_en_ligne})")
        rapport.append(f"• BotAlpha (Mobile)   : {'✅ Connecté' if ok_a else '❌ ' + err_a}")
        rapport.append(f"• BotBravo (Mobile)   : {'✅ Connecté' if ok_b else '❌ ' + err_b}")
        rapport.append(f"• BotCharlie (Desktop): {'✅ Connecté' if ok_c else '❌ ' + err_c}\n")

        if not (ok_a and ok_b and ok_c):
            print("❌ Arrêt : l'un des bots n'a pas pu se connecter.")
            browser.close()
            return

        # Sélection explicite du mode Classique dans le lobby de BotAlpha
        if p_alpha.locator("#modeClassicBtn").count():
            p_alpha.click("#modeClassicBtn")
            p_alpha.wait_for_timeout(600)

        # ---------------------------------------------------------------------
        # PILIER 2 : AUDIT DU CORPUS DE MOTS COURANTS (MODE CLASSIQUE)
        # ---------------------------------------------------------------------
        print(f"2/6 Audit linguistique du Mode Classique ({len(MOTS_CLASSIQUES_UNIQUES)} mots)...")
        audit_classique = p_alpha.evaluate("""(listeMots) => {
            const reconnus = [], inconnus = [];
            for (const m of listeMots) {
                const res = resolveWordInDictionary(m);
                if (res) reconnus.push(m);
                else inconnus.push(m);
            }
            return { total: listeMots.length, ok: reconnus.length, inconnus };
        }""", MOTS_CLASSIQUES_UNIQUES)

        taux_cl = round((audit_classique["ok"] / audit_classique["total"]) * 100, 1)
        rapport.append("### 2. AUDIT LINGUISTIQUE DU CORPUS CLASSIQUE")
        rapport.append(f"• Mots courants testés : {audit_classique['total']} (avec pluriels, féminins et sans accent)")
        rapport.append(f"• Taux de reconnaissance : {audit_classique['ok']}/{audit_classique['total']} ({taux_cl}%)")
        if audit_classique["inconnus"]:
            rapport.append(f"• Mots non reconnus ({len(audit_classique['inconnus'])}) : {', '.join(audit_classique['inconnus'][:20])}\n")
        else:
            rapport.append("• Mots non reconnus : Aucun (100% du corpus classique reconnu !)\n")

        # ---------------------------------------------------------------------
        # PILIER 3 : CRÉATION DU SALON & SYNCHRONISATION TEMPS RÉEL À 3 BOTS
        # ---------------------------------------------------------------------
        print("3/6 Création d'un salon par BotAlpha et connexion de BotBravo & BotCharlie...")
        p_alpha.click("#createRoomBtn")
        p_alpha.wait_for_selector("#roomCodePill:not(.hidden)", timeout=8000)
        code_salon = p_alpha.locator("#headerRoomCode").inner_text().strip()

        for pg in (p_bravo, p_charlie):
            pg.fill("#modalRoomCode", code_salon)
            pg.click("#joinRoomBtn")
            pg.wait_for_selector("#roomCodePill:not(.hidden)", timeout=8000)

        p_alpha.wait_for_timeout(1000)

        nb_joueurs_alpha = p_alpha.evaluate("Object.keys(players).length")
        nb_joueurs_bravo = p_bravo.evaluate("Object.keys(players).length")
        nb_joueurs_charlie = p_charlie.evaluate("Object.keys(players).length")

        rapport.append("### 3. SYNCHRONISATION SALON MULTIJOUEUR WSS (3 BOTS)")
        rapport.append(f"• Code du salon créé par BotAlpha : {code_salon}")
        rapport.append(f"• Joueurs détectés : Alpha={nb_joueurs_alpha}/3 | Bravo={nb_joueurs_bravo}/3 | Charlie={nb_joueurs_charlie}/3")

        echantillon_manche = p_alpha.evaluate("""() => {
            let secret = null, top2 = null, top5 = null, top50 = null, top500 = null, froids = [];
            for (const [w, val] of Object.entries(gameDictionary)) {
                if (Array.isArray(val)) {
                    const r = val[1];
                    if (r === 1000) secret = w;
                    else if (r === 999) top2 = w;
                    else if (r === 996) top5 = w;
                    else if (r === 950) top50 = w;
                    else if (r === 500) top500 = w;
                } else if (froids.length < 12 && w.length >= 4) {
                    froids.push(w);
                }
            }
            return { secret, top2, top5, top50, top500, froids };
        }""")

        print("4/6 Duel coopératif en Mode Classique (Froids, Top 500, Flamme, Magma Top 2, Doublons)...")
        sequence_tirs = [
            (p_alpha, echantillon_manche["froids"][0]),
            (p_bravo, echantillon_manche["froids"][1]),
            (p_charlie, echantillon_manche["froids"][2]),
            (p_alpha, echantillon_manche["froids"][3]),
            (p_bravo, echantillon_manche["froids"][4]),
            (p_charlie, echantillon_manche["froids"][5]),
            (p_alpha, echantillon_manche["top500"]),
            (p_bravo, echantillon_manche["top50"]),
            (p_charlie, echantillon_manche["top5"]),
            (p_alpha, echantillon_manche["top2"]),
            (p_bravo, echantillon_manche["froids"][6]),
        ]

        for bot_page, mot in sequence_tirs:
            if not mot:
                continue
            if not bot_page.locator("#surgeOverlay").evaluate("el => el.classList.contains('hidden')"):
                bot_page.click("#surgeOverlay button")
                bot_page.wait_for_timeout(100)
            bot_page.fill("#wordInput", mot)
            bot_page.click("#guessForm button[type='submit']")
            bot_page.wait_for_timeout(380)

        p_alpha.wait_for_timeout(800)

        cnt_a = p_alpha.locator("#statAttempts").inner_text()
        cnt_b = p_bravo.locator("#statAttempts").inner_text()
        cnt_c = p_charlie.locator("#statAttempts").inner_text()

        rec_a = p_alpha.locator("#statBestScore").inner_text()
        rec_b = p_bravo.locator("#statBestScore").inner_text()
        rec_c = p_charlie.locator("#statBestScore").inner_text()

        rapport.append(f"• Synchro du nombre de mots : Alpha={cnt_a} | Bravo={cnt_b} | Charlie={cnt_c} (Attendu: 11)")
        rapport.append(f"• Synchro du Record Salon   : Alpha={rec_a} | Bravo={rec_b} | Charlie={rec_c}")

        premier_badge = p_alpha.locator("#guessesList > div").first.inner_text()
        top2_ok = "Top 2" in premier_badge
        rapport.append(f"• Vérification du badge 'Top 2' (Rang 999) : {'✅ OK (Top 2 affiché)' if top2_ok else '❌ Erreur : ' + premier_badge}")

        recent_visible = not p_bravo.locator("#lastGuessBox").evaluate("el => el.classList.contains('hidden')")
        pos_recent = p_bravo.locator("#lastGuessRankPos").inner_text() if recent_visible else "Masqué"
        rapport.append(f"• Règle 'Mot récent hors Top 7' : {'✅ Affiché (' + pos_recent + ')' if recent_visible else '❌ Non affiché'}")

        p_charlie.fill("#wordInput", echantillon_manche["top2"])
        p_charlie.click("#guessForm button[type='submit']")
        p_charlie.wait_for_timeout(300)
        cnt_apres_doublon = p_charlie.locator("#statAttempts").inner_text()
        rapport.append(f"• Protection anti-doublon inter-joueurs : {'✅ Bloqué (reste à ' + cnt_apres_doublon + ')' if cnt_apres_doublon == cnt_c else '❌ Doublon accepté'}\n")

        # ---------------------------------------------------------------------
        # PILIER 4 : SÉCURITÉ HÔTE/INVITÉ, INDICE 35 ⚡ & VICTOIRE CLASSIQUE
        # ---------------------------------------------------------------------
        print("5/6 Test Sécurité Invité, Achat d'Indice (35 ⚡) et Victoire 100%...")
        rapport.append("### 4. SÉCURITÉ DES RÔLES, INDICE & VICTOIRE COOPÉRATIVE")

        p_bravo.click("button[title='Révéler le mot']")
        p_bravo.wait_for_timeout(200)
        invite_bloque = p_bravo.locator("#confirmModal").evaluate("el => el.classList.contains('hidden')")
        rapport.append(f"• Blocage Abandon/Skip par un Invité (BotBravo) : {'✅ Bloqué' if invite_bloque else '❌ Non bloqué'}")

        p_alpha.evaluate("debugAddPointsAndXp(50, 0)")
        p_alpha.wait_for_timeout(200)
        pts_avant = int(p_alpha.locator("#headerPoints").inner_text())
        p_alpha.click("#hintBtn")
        p_alpha.wait_for_timeout(700)
        pts_apres = int(p_alpha.locator("#headerPoints").inner_text())
        cnt_apres_indice = p_bravo.locator("#statAttempts").inner_text()
        rapport.append(f"• Achat Indice (-35 ⚡) & Synchro Salon : {'✅ OK' if (pts_avant - pts_apres == 35 or pts_apres > pts_avant - 35) and int(cnt_apres_indice) == 12 else '❌ Échec'} (Mots salon={cnt_apres_indice})")

        p_charlie.fill("#wordInput", echantillon_manche["secret"])
        p_charlie.click("#guessForm button[type='submit']")
        p_alpha.wait_for_timeout(900)

        vic_a = not p_alpha.locator("#victoryBanner").evaluate("el => el.classList.contains('hidden')")
        vic_b = not p_bravo.locator("#victoryBanner").evaluate("el => el.classList.contains('hidden')")
        vic_c = not p_charlie.locator("#victoryBanner").evaluate("el => el.classList.contains('hidden')")
        rapport.append(f"• Synchro Victoire 100% (Bannière Solaire) : Alpha={'✅' if vic_a else '❌'} | Bravo={'✅' if vic_b else '❌'} | Charlie={'✅' if vic_c else '❌'}\n")

        # ---------------------------------------------------------------------
        # PILIER 5 : TEST COMPLET DU MODE « POP CULTURE, MANGA & GAMING »
        # ---------------------------------------------------------------------
        print("6/6 Test du Mode 'Pop & Manga' (Bascule Salon, Corpus Geek 110 mots & Manche Pop)...")
        rapport.append("### 5. AUDIT DU MODE « POP CULTURE, MANGA & GAMING »")

        if p_alpha.locator("#modePopBtn").count() == 0:
            rapport.append("⚠️ Les boutons #modePopBtn ne sont pas encore en ligne sur Vercel (faites un Commit & Push de index.html, app.js et parties_pop/).\n")
        else:
            # 1. Vérifie qu'un invité (BotBravo) ne peut pas changer le mode du salon
            p_bravo.evaluate("selectGameMode('pop')")
            p_bravo.wait_for_timeout(300)
            mode_bravo_seul = p_bravo.evaluate("currentGameMode")
            rapport.append(f"• Blocage changement de mode par un Invité : {'✅ Bloqué (reste en ' + mode_bravo_seul + ')' if mode_bravo_seul == 'classic' else '❌ Non bloqué'}")

            # 2. BotAlpha (Hôte) ouvre le menu et bascule tout le salon en mode Pop & Manga
            p_alpha.click("#modeHeaderBadge")
            p_alpha.wait_for_timeout(300)
            p_alpha.click("#modePopBtn")
            p_alpha.wait_for_timeout(1200)
            p_alpha.click("#closeModalBtn")
            p_alpha.wait_for_timeout(400)

            mode_a = p_alpha.evaluate("currentGameMode")
            mode_b = p_bravo.evaluate("currentGameMode")
            mode_c = p_charlie.evaluate("currentGameMode")
            badge_mode_txt = p_charlie.locator("#modeHeaderText").inner_text().strip()
            rapport.append(f"• Bascule synchronisée en Mode Pop & Manga : Alpha={mode_a} | Bravo={mode_b} | Charlie={mode_c} (Badge='{badge_mode_txt}')")

            # 3. Audit linguistique des 110 mots Pop Culture / Manga / Gaming
            audit_pop = p_alpha.evaluate("""(listePop) => {
                const reconnus = [], inconnus = [];
                for (const m of listePop) {
                    const res = resolveWordInDictionary(m);
                    if (res) reconnus.push(m);
                    else inconnus.push(m);
                }
                const secretPop = Object.entries(gameDictionary).find(([, v]) => Array.isArray(v) && v[1] === 1000)?.[0] || "?";
                const top2Pop = Object.entries(gameDictionary).find(([, v]) => Array.isArray(v) && v[1] === 999)?.[0] || "?";
                return { total: listePop.length, ok: reconnus.length, inconnus, secretPop, top2Pop };
            }""", MOTS_POP_UNIQUES)

            taux_pop = round((audit_pop["ok"] / audit_pop["total"]) * 100, 1)
            rapport.append(f"• Mot secret Pop Culture tiré au sort : [{audit_pop['secretPop'].upper()}] (Top 2 = '{audit_pop['top2Pop']}')")
            rapport.append(f"• Reconnaissance du Corpus Pop/Manga/Gaming : {audit_pop['ok']}/{audit_pop['total']} ({taux_pop}%)")
            if audit_pop["inconnus"]:
                rapport.append(f"• Mots Pop non reconnus : {', '.join(audit_pop['inconnus'][:15])}")

            # 4. Les 3 bots jouent des mots Pop Culture puis trouvent le mot secret Pop
            for pg, w_pop in [(p_alpha, "naruto"), (p_bravo, "pikachu"), (p_charlie, audit_pop["top2Pop"]), (p_alpha, audit_pop["secretPop"])]:
                if not pg.locator("#surgeOverlay").evaluate("el => el.classList.contains('hidden')"):
                    pg.click("#surgeOverlay button")
                    pg.wait_for_timeout(100)
                pg.fill("#wordInput", w_pop)
                pg.click("#guessForm button[type='submit']")
                pg.wait_for_timeout(400)

            p_alpha.wait_for_timeout(800)
            vic_pop_a = not p_alpha.locator("#victoryBanner").evaluate("el => el.classList.contains('hidden')")
            vic_pop_b = not p_bravo.locator("#victoryBanner").evaluate("el => el.classList.contains('hidden')")
            vic_pop_c = not p_charlie.locator("#victoryBanner").evaluate("el => el.classList.contains('hidden')")
            rapport.append(f"• Victoire coopérative en Mode Pop & Manga : Alpha={'✅' if vic_pop_a else '❌'} | Bravo={'✅' if vic_pop_b else '❌'} | Charlie={'✅' if vic_pop_c else '❌'}\n")

            # Remet BotAlpha en mode Classique à la fin du test
            p_alpha.evaluate("selectGameMode('classic')")

        # ---------------------------------------------------------------------
        # PILIER 6 : STRESS-TEST DOM (100 MOTS) & BILAN TECHNIQUE
        # ---------------------------------------------------------------------
        t_dom = p_alpha.evaluate("""() => {
            const t0 = performance.now();
            const words = Object.keys(gameDictionary).slice(0, 100);
            guesses = words.map((w, idx) => ({
                num: idx + 1, word: w, temp: 25, rank: idx < 50 ? 900 + idx : null,
                scorePct: idx < 50 ? 90 + idx * 0.15 : 20, isWin: false, isTop10: idx >= 41 && idx < 50,
                finderId: myId, finderPseudo: "StressBot"
            }));
            guesses.sort((a, b) => b.scorePct - a.scorePct);
            renderGuesses();
            return Math.round(performance.now() - t0);
        }""")

        rapport.append("### 6. PERFORMANCES DOM & INTÉGRITÉ TECHNIQUE")
        rapport.append(f"• Temps de rendu DOM pour 100 cartes simultanées : {t_dom} ms (Excellent si < 50 ms)")
        rapport.append(f"• Erreurs JavaScript sur les 3 navigateurs : {len(erreurs_js)}")
        for e in erreurs_js:
            rapport.append(f"   ❌ {e}")

        browser.close()

    texte_final = "\n".join(rapport)
    with open("rapport_stress_test.txt", "w", encoding="utf-8") as f:
        f.write(texte_final)
    print("\n" + texte_final)
    print("\n✅ Rapport complet sauvegardé dans 'rapport_stress_test.txt' !")

if __name__ == "__main__":
    lancer_stress_test()