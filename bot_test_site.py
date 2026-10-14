import time
from playwright.sync_api import sync_playwright

SITE_URL = "https://zero-absolu.vercel.app"
BOT_PSEUDO = "BotTesteur"
BOT_PASSWORD = "Soleil2026Secret"

def auditer_site_v1():
    rapport = ["=== RAPPORT COMPLET DU BOT D'AUDIT (v1.0) ==="]
    erreurs_js = []
    erreurs_reseau = []

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(viewport={"width": 390, "height": 844}, is_mobile=True)
        page = context.new_page()

        page.on("pageerror", lambda err: erreurs_js.append(str(err)))
        page.on("console", lambda msg: erreurs_js.append(f"Console {msg.type}: {msg.text}") if msg.type == "error" else None)
        page.on("requestfailed", lambda req: erreurs_reseau.append(f"{req.url} ({req.failure})"))

        print(f"1/6 Ouverture de {SITE_URL}...")
        page.goto(SITE_URL, wait_until="networkidle")
        page.wait_for_timeout(1000)

        version = page.locator("#versionBadgeTop").inner_text() if page.locator("#versionBadgeTop").count() else "?"
        cloud = page.locator("#cloudStatusText").inner_text() if page.locator("#cloudStatusText").count() else "?"
        rapport.append(f"• Version en ligne : {version} | Statut Cloud : {cloud}")

        # 2. Test Authentification (Connexion ou Inscription automatique)
        print("2/6 Test Authentification Supabase (Connexion / Inscription)...")
        page.fill("#authPseudo", BOT_PSEUDO)
        page.fill("#authPassword", BOT_PASSWORD)
        page.click("#authSubmitBtn")
        page.wait_for_timeout(1800)

        err_msg = page.locator("#authError").inner_text().strip()
        if "Aucun compte" in err_msg:
            rapport.append("• Compte BotTesteur inexistant -> Passage automatique sur l'onglet Inscription")
            page.click("#tabRegisterBtn")
            page.fill("#authPseudo", BOT_PSEUDO)
            page.fill("#authPassword", BOT_PASSWORD)
            page.click("#authSubmitBtn")
            page.wait_for_timeout(1800)
            err_msg = page.locator("#authError").inner_text().strip()

        welcome_visible = not page.locator("#welcomeModal").evaluate("el => el.classList.contains('hidden')")
        rapport.append(f"• Authentification Cloud : {'✅ Réussie' if welcome_visible else f'❌ Échec ({err_msg})'}")

        if not welcome_visible:
            rapport.append("⚠️ Arrêt anticipé : la connexion Supabase a échoué, vérifiez config.js et le déploiement Vercel.")
        else:
            # 3. Test Pop-up Bienvenue & Carrousel Tutoriel (3 slides)
            print("3/6 Test de la Pop-up Bienvenue et du Carrousel Tutoriel...")
            welcome_title = page.locator("#welcomeTitle").inner_text()
            welcome_lvl = page.locator("#welcomeLevel").inner_text()
            rapport.append(f"• Pop-up Bienvenue : '{welcome_title}' ({welcome_lvl})")
            page.click("#welcomeTutoBtn")
            page.wait_for_timeout(400)

            tuto_open = not page.locator("#tutorialModal").evaluate("el => el.classList.contains('hidden')")
            positions = []
            if tuto_open:
                for _ in range(3):
                    tr = page.locator("#tutorialTrack").evaluate("el => el.style.transform")
                    positions.append(tr)
                    page.click("#tutoNextBtn")
                    page.wait_for_timeout(380)
            tuto_closed = page.locator("#tutorialModal").evaluate("el => el.classList.contains('hidden')")
            rapport.append(f"• Carrousel Tutoriel (3 slides) : {'✅ Fluide' if tuto_closed else '❌ Bloqué'} | Slides={positions}")

            # 4. Vérification de sécurité du mot de passe
            print("4/6 Vérification de sécurité du mot de passe...")
            page.click("button[title='Changer de compte']")
            page.wait_for_timeout(250)
            page.fill("#authPseudo", BOT_PSEUDO)
            page.fill("#authPassword", "MauvaisMdp999")
            page.click("#authSubmitBtn")
            page.wait_for_timeout(1400)
            wrong_pwd_err = page.locator("#authError").inner_text().strip()
            rapport.append(f"• Sécurité mauvais mot de passe : {'✅ Bloqué (' + wrong_pwd_err + ')' if wrong_pwd_err else '❌ Non bloqué !'}")

            # Reconnexion avec le bon mot de passe
            page.fill("#authPassword", BOT_PASSWORD)
            page.click("#authSubmitBtn")
            page.wait_for_timeout(1500)
            if not page.locator("#welcomeModal").evaluate("el => el.classList.contains('hidden')"):
                page.click("#welcomePlayBtn")
                page.wait_for_timeout(300)

            # Lancement du mode Solo
            page.click("button:has-text('Solo')")
            page.wait_for_timeout(1200)

            # 5. Test Gameplay, Plante, Doublons & Modales de confirmation
            print("5/6 Test Gameplay, 'plante', doublons et fenêtres de confirmation...")
            for m in ["plante", "plantes", "forêt", "océan", "voiture"]:
                page.fill("#wordInput", m)
                page.click("#guessForm button[type='submit']")
                page.wait_for_timeout(450)

            essais = page.locator("#statAttempts").inner_text()
            rapport.append(f"• Test Mots ('plante' + doublon 'plantes' + 3 mots) : {essais}/4 validés (Attendu: 4)")

            page.click("button[title='Révéler le mot']")
            page.wait_for_timeout(250)
            confirm_visible = not page.locator("#confirmModal").evaluate("el => el.classList.contains('hidden')")
            rapport.append(f"• Modale de confirmation (Abandon/Suivant) : {'✅ OK' if confirm_visible else '❌ Absente'}")
            if confirm_visible:
                page.click("button:has-text('Annuler')")
                page.wait_for_timeout(200)

            # 6. Test du Laboratoire Secret (XXXX + 3 clics) & Chronométrage des Animations
            print("6/6 Test du Laboratoire Secret et chronométrage des animations...")
            page.fill("#wordInput", "XXXX")
            for _ in range(3):
                page.click("#headerLogoBtn")
                page.wait_for_timeout(90)

            debug_open = not page.locator("#debugModal").evaluate("el => el.classList.contains('hidden')")
            rapport.append(f"• Ouverture Laboratoire Secret (XXXX + 3 clics) : {'✅ OK' if debug_open else '❌ Échec'}")

            if debug_open:
                page.click("button:has-text('Afficher')")
                secret_word = page.locator("#debugSecretWord").inner_text()
                rapport.append(f"• Mot secret lu dans le Labo : {secret_word}")

                t0 = time.time()
                page.click("button:has-text('Fusion 100%')")
                while not page.locator("#solarExplosionOverlay").evaluate("el => el.classList.contains('hidden')"):
                    page.wait_for_timeout(50)
                    if time.time() - t0 > 4:
                        break
                duree_fusion = round((time.time() - t0) * 1000)
                rapport.append(f"• Durée animation Explosion Fusion Solaire : {duree_fusion} ms (Attendu: ~1550 ms)")

        debordements = page.evaluate("""() => {
            const vw = window.innerWidth, out = [];
            document.querySelectorAll('header *, main *').forEach(el => {
                const r = el.getBoundingClientRect();
                if (r.width > 0 && r.height > 0 && (r.right > vw + 2 || r.left < -2)) {
                    out.push(`${el.tagName}#${el.id || el.className.toString().slice(0,20)} (${Math.round(r.right)}px > ${vw}px)`);
                }
            });
            return out.slice(0, 10);
        }""")
        rapport.append(f"• Débordements d'écran mobile (390px) : {len(debordements)}")
        for d in debordements:
            rapport.append(f"   ⚠️ {d}")

        rapport.append(f"• Erreurs JavaScript : {len(erreurs_js)}")
        for e in erreurs_js:
            rapport.append(f"   ❌ {e}")

        browser.close()

    texte = "\n".join(rapport)
    with open("rapport_test_bot.txt", "w", encoding="utf-8") as f:
        f.write(texte)
    print("\n" + texte)

if __name__ == "__main__":
    auditer_site_v1()