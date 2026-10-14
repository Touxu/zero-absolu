import time
from playwright.sync_api import sync_playwright

SITE_URL = "https://zero-absolu.vercel.app"
MDP_BOTS = "Soleil2026Secret"

# Corpus de 1 000 mots courants (noms, verbes, adjectifs + variantes sans accent / pluriels / féminins)
CORPUS_1000_MOTS = """
maison appartement chambre cuisine salon jardin porte fenetre toit mur plafond plancher escalier
table chaise fauteuil canape lit matelas oreiller couverture drap armoire placard tiroir etagere
miroir lampe ampoule bougie horloge montre reveil calendrier rideau tapis coussin balai brosse
aspirateur seau eponge savon shampoing serviette peigne rasoir dentifrice baignoire douche lavabo
robinet evier four refrigerateur congelateur casserole poele marmite assiette bol tasse verre
fourchette couteau cuillere bouteille carafe plateau passoire ouvre-boite tire-bouchon poubelle
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
coccinelle mouche moustique araignee scorpion ver crabe homard meduse pieuvre étoile-de-mer
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
theatre musee bibliotheque stade piscine parc zoo cirque eglise cathedrale chateau palais Tour
ouvrier employe patron directeur ingenieur technicien artisan commercant vendeur client facteur
boulanger patissier boucher cuisinier serveur agriculteur paysan fermier pecheur marin soldat
policier gendarme pompier juge avocat journaliste ecrivain auteur poete musicien chanteur acteur
peintre sculpteur architecte mecanicien chauffeur piloteplombier electricien menuisier macon
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
debut fin matinée soiree printemps ete automne hiver histoire science nature energie force chaleur
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

# Complète jusqu'à 1000 mots uniques si nécessaire
MOTS_UNIQUES = list(dict.fromkeys(CORPUS_1000_MOTS))

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
    rapport.append("   RAPPORT DE STRESS-TEST & AUDIT MULTI-BOTS (ZéroAbsolu v1.0)")
    rapport.append("=================================================================\n")
    erreurs_js = []

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)

        # Création de 3 contextes de navigation 100% isolés (3 joueurs distincts)
        ctx_alpha = browser.new_context(viewport={"width": 390, "height": 844}, is_mobile=True)
        ctx_bravo = browser.new_context(viewport={"width": 390, "height": 844}, is_mobile=True)
        ctx_charlie = browser.new_context(viewport={"width": 1280, "height": 800}) # Charlie sur PC Desktop

        p_alpha = ctx_alpha.new_page()
        p_bravo = ctx_bravo.new_page()
        p_charlie = ctx_charlie.new_page()

        for nom, pg in [("Alpha", p_alpha), ("Bravo", p_bravo), ("Charlie", p_charlie)]:
            pg.on("pageerror", lambda err, n=nom: erreurs_js.append(f"[{n}] {err}"))

        # ---------------------------------------------------------------------
        # PILIER 1 : CONNEXION DES 3 BOTS & CRÉATION DU SALON MULTIJOUEUR
        # ---------------------------------------------------------------------
        print("1/5 Connexion des 3 bots (BotAlpha, BotBravo, BotCharlie) sur Supabase...")
        p_alpha.goto(SITE_URL, wait_until="networkidle")
        p_bravo.goto(SITE_URL, wait_until="networkidle")
        p_charlie.goto(SITE_URL, wait_until="networkidle")

        ok_a, err_a = connecter_ou_inscrire_bot(p_alpha, "BotAlpha", MDP_BOTS)
        ok_b, err_b = connecter_ou_inscrire_bot(p_bravo, "BotBravo", MDP_BOTS)
        ok_c, err_c = connecter_ou_inscrire_bot(p_charlie, "BotCharlie", MDP_BOTS)

        rapport.append("### 1. AUTHENTIFICATION SUPABASE DES 3 BOTS")
        rapport.append(f"• BotAlpha (Mobile)   : {'✅ Connecté' if ok_a else '❌ ' + err_a}")
        rapport.append(f"• BotBravo (Mobile)   : {'✅ Connecté' if ok_b else '❌ ' + err_b}")
        rapport.append(f"• BotCharlie (Desktop): {'✅ Connecté' if ok_c else '❌ ' + err_c}\n")

        if not (ok_a and ok_b and ok_c):
            print("❌ Arrêt : l'un des bots n'a pas pu se connecter.")
            browser.close()
            return

        # ---------------------------------------------------------------------
        # PILIER 2 : AUDIT DU CORPUS DE MOTS COURANTS (DANS LE MOTEUR DU JEU)
        # ---------------------------------------------------------------------
        print(f"2/5 Audit linguistique de {len(MOTS_UNIQUES)} mots courants et variantes...")
        audit_corpus = p_alpha.evaluate("""(listeMots) => {
            const reconnus = [];
            const inconnus = [];
            for (const m of listeMots) {
                const res = resolveWordInDictionary(m);
                if (res) reconnus.push([m, res]);
                else inconnus.push(m);
            }
            return { total: listeMots.length, ok: reconnus.length, inconnus: inconnus };
        }""", MOTS_UNIQUES)

        taux = round((audit_corpus["ok"] / audit_corpus["total"]) * 100, 1)
        rapport.append("### 2. AUDIT LINGUISTIQUE DU CORPUS COURANT")
        rapport.append(f"• Mots testés : {audit_corpus['total']} (incluant pluriels, féminins et mots sans accent)")
        rapport.append(f"• Taux de reconnaissance : {audit_corpus['ok']}/{audit_corpus['total']} ({taux}%)")
        if audit_corpus["inconnus"]:
            rapport.append(f"• Mots non reconnus ({len(audit_corpus['inconnus'])}) : {', '.join(audit_corpus['inconnus'][:30])}")
        else:
            rapport.append("• Mots non reconnus : Aucun (100% du corpus reconnu !)")
        rapport.append("")

        # ---------------------------------------------------------------------
        # PILIER 3 : CRÉATION DU SALON & SYNCHRONISATION TEMPS RÉEL À 3 BOTS
        # ---------------------------------------------------------------------
        print("3/5 Création d'un salon par BotAlpha et connexion de BotBravo & BotCharlie...")
        p_alpha.click("#createRoomBtn")
        p_alpha.wait_for_selector("#roomCodePill:not(.hidden)", timeout=8000)
        code_salon = p_alpha.locator("#headerRoomCode").inner_text().strip()

        # BotBravo et BotCharlie rejoignent le salon
        for pg in (p_bravo, p_charlie):
            pg.fill("#modalRoomCode", code_salon)
            pg.click("#joinRoomBtn")
            pg.wait_for_selector("#roomCodePill:not(.hidden)", timeout=8000)

        p_alpha.wait_for_timeout(1000)

        # Vérifie que les 3 bots voient bien 3 joueurs dans le salon
        nb_joueurs_alpha = p_alpha.evaluate("Object.keys(players).length")
        nb_joueurs_bravo = p_bravo.evaluate("Object.keys(players).length")
        nb_joueurs_charlie = p_charlie.evaluate("Object.keys(players).length")

        rapport.append("### 3. SYNCHRONISATION SALON MULTIJOUEUR WSS (3 BOTS)")
        rapport.append(f"• Code du salon créé par BotAlpha : {code_salon}")
        rapport.append(f"• Joueurs détectés : Alpha={nb_joueurs_alpha}/3 | Bravo={nb_joueurs_bravo}/3 | Charlie={nb_joueurs_charlie}/3")

        # Extraction intelligente de mots réels de la manche en cours pour tester tous les paliers
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

        # Les 3 bots jouent 12 mots à tour de rôle
        print("4/5 Duel coopératif entre les 3 bots (Froids, Top 500, Flamme, Magma Top 2, Doublons)...")
        sequence_tirs = [
            (p_alpha, echantillon_manche["froids"][0], "Froid #1"),
            (p_bravo, echantillon_manche["froids"][1], "Froid #2"),
            (p_charlie, echantillon_manche["froids"][2], "Froid #3"),
            (p_alpha, echantillon_manche["froids"][3], "Froid #4"),
            (p_bravo, echantillon_manche["froids"][4], "Froid #5"),
            (p_charlie, echantillon_manche["froids"][5], "Froid #6"),
            (p_alpha, echantillon_manche["top500"], "Tiède (Top 501)"),
            (p_bravo, echantillon_manche["top50"], "Flamme (Top 51)"),
            (p_charlie, echantillon_manche["top5"], "Magma (Top 5)"),
            (p_alpha, echantillon_manche["top2"], "Magma (Top 2 - Rang 999)"),
            (p_bravo, echantillon_manche["froids"][6], "Froid #7 (Hors Top 7 -> doit ouvrir Mot récent)"),
        ]

        for bot_page, mot, label in sequence_tirs:
            if not mot:
                continue
            # Ferme l'overlay de Percée Thermique s'il est ouvert sur ce bot
            if not bot_page.locator("#surgeOverlay").evaluate("el => el.classList.contains('hidden')"):
                bot_page.click("#surgeOverlay button")
                bot_page.wait_for_timeout(100)
            bot_page.fill("#wordInput", mot)
            bot_page.click("#guessForm button[type='submit']")
            bot_page.wait_for_timeout(380)

        p_alpha.wait_for_timeout(800)

        # Vérification de la synchronisation des listes sur les 3 bots
        cnt_a = p_alpha.locator("#statAttempts").inner_text()
        cnt_b = p_bravo.locator("#statAttempts").inner_text()
        cnt_c = p_charlie.locator("#statAttempts").inner_text()

        rec_a = p_alpha.locator("#statBestScore").inner_text()
        rec_b = p_bravo.locator("#statBestScore").inner_text()
        rec_c = p_charlie.locator("#statBestScore").inner_text()

        rapport.append(f"• Synchro du nombre de mots : Alpha={cnt_a} | Bravo={cnt_b} | Charlie={cnt_c} (Attendu: 11)")
        rapport.append(f"• Synchro du Record Salon   : Alpha={rec_a} | Bravo={rec_b} | Charlie={rec_c}")

        # Vérifie que le mot de rang 999 affiche bien "Top 2" (et non "Top 1")
        premier_badge = p_alpha.locator("#guessesList > div").first.inner_text()
        top2_ok = "Top 2" in premier_badge
        rapport.append(f"• Vérification du badge 'Top 2' (Rang 999) : {'✅ OK (Top 2 affiché)' if top2_ok else '❌ Erreur : ' + premier_badge}")

        # Vérifie que la boîte "Mot récent (plus bas)" s'est bien ouverte sur BotBravo après le 11e mot (froid)
        recent_visible = not p_bravo.locator("#lastGuessBox").evaluate("el => el.classList.contains('hidden')")
        pos_recent = p_bravo.locator("#lastGuessRankPos").inner_text() if recent_visible else "Masqué"
        rapport.append(f"• Règle 'Mot récent hors Top 7' : {'✅ Affiché (' + pos_recent + ')' if recent_visible else '❌ Non affiché'}")

        # Test de doublon croisé : BotCharlie tente de retaper le mot Top 2 déjà trouvé par BotAlpha
        p_charlie.fill("#wordInput", echantillon_manche["top2"])
        p_charlie.click("#guessForm button[type='submit']")
        p_charlie.wait_for_timeout(300)
        cnt_apres_doublon = p_charlie.locator("#statAttempts").inner_text()
        rapport.append(f"• Protection anti-doublon inter-joueurs : {'✅ Bloqué (reste à ' + cnt_apres_doublon + ')' if cnt_apres_doublon == cnt_c else '❌ Doublon accepté'}\n")

        # ---------------------------------------------------------------------
        # PILIER 4 : SÉCURITÉ HÔTE/INVITÉ, INDICE 35 ⚡ & TRANSITION DE MANCHE
        # ---------------------------------------------------------------------
        print("5/5 Test Sécurité Invité, Achat d'Indice (35 ⚡), Victoire 100% et Manche #2...")
        rapport.append("### 4. SÉCURITÉ DES RÔLES, INDICE & VICTOIRE COOPÉRATIVE")

        # BotBravo (Invité) essaie d'abandonner la manche -> doit être bloqué
        p_bravo.click("button[title='Révéler le mot']")
        p_bravo.wait_for_timeout(200)
        invite_bloque = p_bravo.locator("#confirmModal").evaluate("el => el.classList.contains('hidden')")
        rapport.append(f"• Blocage Abandon/Skip par un Invité (BotBravo) : {'✅ Bloqué' if invite_bloque else '❌ Non bloqué'}")

        # BotAlpha utilise le Labo Secret pour se donner +50 ⚡ et achète un Indice (35 ⚡)
        p_alpha.evaluate("debugAddPointsAndXp(50, 0)")
        p_alpha.wait_for_timeout(200)
        pts_avant = int(p_alpha.locator("#headerPoints").inner_text())
        p_alpha.click("#hintBtn")
        p_alpha.wait_for_timeout(700)
        pts_apres = int(p_alpha.locator("#headerPoints").inner_text())
        cnt_apres_indice = p_bravo.locator("#statAttempts").inner_text()
        rapport.append(f"• Achat Indice (-35 ⚡) & Synchro Salon : {'✅ OK' if (pts_avant - pts_apres == 35 or pts_apres > pts_avant - 35) and int(cnt_apres_indice) == 12 else '❌ Échec'} (Mots salon={cnt_apres_indice})")

        # BotCharlie tape le mot secret -> Déclenche la victoire (100% Fusion) chez les 3 bots !
        p_charlie.fill("#wordInput", echantillon_manche["secret"])
        p_charlie.click("#guessForm button[type='submit']")
        p_alpha.wait_for_timeout(900)

        vic_a = not p_alpha.locator("#victoryBanner").evaluate("el => el.classList.contains('hidden')")
        vic_b = not p_bravo.locator("#victoryBanner").evaluate("el => el.classList.contains('hidden')")
        vic_c = not p_charlie.locator("#victoryBanner").evaluate("el => el.classList.contains('hidden')")
        rapport.append(f"• Synchro Victoire 100% (Bannière Solaire) : Alpha={'✅' if vic_a else '❌'} | Bravo={'✅' if vic_b else '❌'} | Charlie={'✅' if vic_c else '❌'}")

        # BotAlpha passe à la Manche #2 -> Vérifie que les 3 bots passent bien en #2
        p_alpha.click("#victoryBanner button:has-text('Suivant')")
        p_alpha.wait_for_timeout(1200)
        manche_a = p_alpha.locator("#roundBadge").inner_text()
        manche_b = p_bravo.locator("#roundBadge").inner_text()
        manche_c = p_charlie.locator("#roundBadge").inner_text()
        rapport.append(f"• Passage synchronisé à la Manche #2 : Alpha={manche_a} | Bravo={manche_b} | Charlie={manche_c}\n")

        # ---------------------------------------------------------------------
        # PILIER 5 : STRESS-TEST DOM (100 MOTS) & BILAN TECHNIQUE
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

        rapport.append("### 5. PERFORMANCES DOM & INTÉGRITÉ TECHNIQUE")
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