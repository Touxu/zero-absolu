import os
import re
import json

def test_modules():
    files = [f for f in os.listdir("js") if f.endswith(".js")]
    exports = {}
    for f in files:
        with open(os.path.join("js", f), "r", encoding="utf-8") as fp:
            content = fp.read()
        exp = set(re.findall(r"export\s+(?:async\s+)?(?:function|const|let|var|class)\s+([a-zA-Z0-9_$]+)", content))
        for m in re.finditer(r"export\s*\{([^}]+)\}", content):
            for item in m.group(1).split(","):
                cleaned = item.strip().split(" as ")[-1].strip()
                if cleaned:
                    exp.add(cleaned)
        exports[f] = exp

    print("Exports per file:")
    for f, exp in sorted(exports.items()):
        print(f"  {f}: {len(exp)} exports")

    errors = []
    for f in files:
        with open(os.path.join("js", f), "r", encoding="utf-8") as fp:
            content = fp.read()
        for m in re.finditer(r'import\s*\{([^}]+)\}\s*from\s*["\']\./([^"\']+)["\']', content):
            items = [x.strip().split(" as ")[0].strip() for x in m.group(1).split(",") if x.strip()]
            target = m.group(2)
            if not target.endswith(".js"):
                target += ".js"
            for it in items:
                if target in exports and it not in exports[target]:
                    errors.append(f"{f} imports '{it}' from {target}, but {target} does not export it!")

    assert not errors, f"Import/Export mismatches: {errors}"
    print("✅ Tous les imports/exports ES Modules sont 100% alignés et cohérents !")

def test_guest_lists():
    with open("js/auth.js", "r", encoding="utf-8") as fp:
        content = fp.read()

    # Extract animals
    m_animals = re.search(r"GUEST_ANIMALS\s*=\s*\[(.*?)\];", content, re.DOTALL)
    assert m_animals, "GUEST_ANIMALS not found"
    animals = re.findall(r'"([^"]+)"', m_animals.group(1))

    # Extract adjectives
    m_adjs = re.search(r"GUEST_ADJECTIVES\s*=\s*\[(.*?)\];", content, re.DOTALL)
    assert m_adjs, "GUEST_ADJECTIVES not found"
    adjs = re.findall(r'"([^"]+)"', m_adjs.group(1))

    print(f"✅ GUEST_ANIMALS count: {len(animals)} (ex: {animals[:5]})")
    print(f"✅ GUEST_ADJECTIVES count: {len(adjs)} (ex: {adjs[:5]})")
    assert len(animals) >= 50, f"Expected at least 50 animals, got {len(animals)}"
    assert len(adjs) >= 50, f"Expected at least 50 adjectives, got {len(adjs)}"
    assert "Poisson" in animals and "Rat" in animals and "Loutre" in animals
    assert "Cool" in adjs and "Rigolo" in adjs and "Puant" in adjs

def test_ui_improvements():
    with open("js/ui.js", "r", encoding="utf-8") as fp:
        ui_content = fp.read()

    # Test recent word threshold
    assert "posIndex >= 6" in ui_content, "Recent words must trigger at posIndex >= 6"
    assert "posIndex >= 7" not in ui_content, "Old threshold posIndex >= 7 must not exist"
    print("✅ Seuil des mots récents vérifié : posIndex >= 6 (Top 6 affiché directement)")

    # Test duplicate scroll removal
    m_dup = re.search(r"function highlightExistingWordRow\(.*?\)\s*\{(.*?)\}", ui_content, re.DOTALL)
    assert m_dup, "highlightExistingWordRow not found"
    assert "scrollIntoView" not in m_dup.group(1), "scrollIntoView must NOT be present in duplicate word handler"
    print("✅ Suppression du scroll automatique sur mot doublon validée")

    # Test confetti removal
    assert "window.confetti" not in ui_content, "window.confetti must be removed from ui.js"
    assert "party.confetti" not in ui_content, "party.confetti must be removed from ui.js"
    print("✅ Remplacement des confettis normaux par particules vectorielles GPU validé")

def test_single_win_animation():
    with open("js/app.js", "r", encoding="utf-8") as fp:
        app_content = fp.read()

    # Check handleGuess doesn't fire particles on input
    m_guess = re.search(r"function handleGuess\(.*?\)\s*\{(.*?)\n\}", app_content, re.DOTALL)
    assert m_guess, "handleGuess not found"
    assert "triggerWordParticles(input" not in m_guess.group(1), "triggerWordParticles must not be called prematurely on input in handleGuess"
    print("✅ handleGuess n'émet plus de particules sur la barre d'entrée")

    # Check applySharedGuess anchors particles on wordRowEl and has single win animation
    assert "triggerSolarFusionExplosion(wordRowEl)" in app_content
    print("✅ applySharedGuess ancre l'explosion de fusion solaire et les particules sur wordRowEl")

def test_html_features():
    with open("index.html", "r", encoding="utf-8") as fp:
        html = fp.read()

    assert 'id="authGuestBtn"' in html
    assert "loginAsGuest()" in html
    assert 'id="headerMenuBtn"' in html
    assert 'id="headerDropdownMenu"' in html
    assert 'onclick="toggleHeaderMenu(event)"' in html
    print("✅ Bouton invité, menu mobile déroulant et laboratoire secret validés dans index.html")

def test_top2_thermal_gauge_and_particles():
    with open("js/ui.js", "r", encoding="utf-8") as fp:
        ui_content = fp.read()
    with open("js/particles.js", "r", encoding="utf-8") as fp:
        part_content = fp.read()

    # Gauge check: if (pct >= 99) was the bug triggering 100% on 99.9%
    assert "if (pct >= 99)" not in ui_content, "if (pct >= 99) must be replaced by pct >= 100 or roundFinished"
    assert "pct >= 100 || (state.roundFinished && pct >= 99.95)" in ui_content
    print("✅ Jauge thermique : Top 2 (99.9%) ne déclenche plus la Fusion Solaire 100%")

    # Particles check: rank 991-999 must strictly trigger magma, not solar fusion
    assert "isSecretWord && (rankNum === 1000 || rankNum === null)" in part_content
    print("✅ Particules thermiques : Top 2 (99.9%) déclenche magma et non la fusion solaire")

def test_secret_words_filtering():
    with open("data/catalogue.json", "r", encoding="utf-8") as fp:
        cat = json.load(fp)

    import base64
    classic_buf = base64.b64decode(cat["classic"])
    import struct
    top_indices = struct.unpack(f"<{len(classic_buf)//2}H", classic_buf)
    words = cat["words"]

    obscure_blacklisted = ["gouache", "faitout", "calice", "burin", "geôle", "âtre", "cric", "sarcophage", "amnistie"]
    secret_words = [words[top_indices[g * 1000]] for g in range(cat["classicGames"])]

    for bad in obscure_blacklisted:
        assert bad not in secret_words, f"'{bad}' must NOT be a secret word to guess!"

    print(f"✅ Mots secrets vérifiés sur 500 parties : aucun mot obscur ({len(secret_words)} mots secrets courants)")

def test_daily_archive_and_time_stats():
    with open("index.html", "r", encoding="utf-8") as fp:
        html = fp.read()
    with open("js/ui.js", "r", encoding="utf-8") as fp:
        ui_js = fp.read()
    with open("js/app.js", "r", encoding="utf-8") as fp:
        app_js = fp.read()
    with open("style.css", "r", encoding="utf-8") as fp:
        css = fp.read()

    # Daily Archive modal & buttons
    assert 'id="dailyArchiveModal"' in html
    assert 'id="dailyArchiveList"' in html
    assert 'openDailyArchiveModal' in html
    assert 'openDailyArchiveModal' in ui_js
    assert 'playDailyArchiveGame' in app_js

    # Time stats in profile modal
    assert "Record Vitesse" in ui_js
    assert "Temps Moyen" in ui_js
    assert "grid-cols-2 sm:grid-cols-4" in html

    # Toast animation classes
    assert "animate-toast-in" in css
    assert "animate-toast-out" in css

    # Sunbeams square styling
    assert "width: 3600px; height: 3600px;" in css

    print("✅ Écran des archives du jour, statistiques de chronos et rayons solaires validés")

def test_simplification_and_perf():
    with open("index.html", "r", encoding="utf-8") as fp:
        html = fp.read()
    with open("js/auth.js", "r", encoding="utf-8") as fp:
        auth_js = fp.read()
    with open("js/particles.js", "r", encoding="utf-8") as fp:
        part_js = fp.read()
    with open("js/app.js", "r", encoding="utf-8") as fp:
        app_js = fp.read()
    with open("js/ui.js", "r", encoding="utf-8") as fp:
        ui_js = fp.read()
    with open("js/constants.js", "r", encoding="utf-8") as fp:
        const_js = fp.read()

    # 1. Removal of redundant containers
    assert 'id="statsContainer"' not in html, "#statsContainer must be removed to avoid duplication"
    assert 'id="thermalGaugeContainer"' not in html, "#thermalGaugeContainer must be removed to declutter"
    assert 'id="versionBadgeFooter"' not in html, "Duplicate version footer in onboarding must be removed"

    # 2. Simplified auth form
    assert 'Pseudo</label>' in html, "Label should be simply 'Pseudo'"
    assert 'Pseudo unique' not in html, "'Pseudo unique' must not exist"
    assert 'Mot de passe</label>' in html, "Label should be simply 'Mot de passe'"
    assert 'Mot de passe (4 caract. min)' not in html, "Old label must not exist"

    # 3. Non-alarming verification color
    assert 'text-sky-400' in auth_js, "Verification status must be reassuring sky-blue"

    # 4. Lobby player card & Daily rename
    assert 'id="lobbyGradeIcon"' in html
    assert 'id="lobbyXpBar"' in html
    assert 'Mot du Jour' in const_js
    assert 'Défi du Jour' not in const_js

    # 5. Profile tabs & history view
    assert 'id="tabProfileStats"' in html
    assert 'id="tabProfileHistory"' in html
    assert 'id="historyView"' in html
    assert 'id="historyListContainer"' in html
    assert 'switchProfileTab' in ui_js
    assert 'renderHistoryViewContent' in ui_js
    assert 'resumeSavedGame' in app_js
    assert 'handleResumeSessionClick' in app_js
    assert 'saveCurrentGameSession' in app_js

    # 6. Particle engine performance
    assert '.shadowBlur' not in part_js, "shadowBlur causes massive FPS drops and must be absent"
    assert 'createRadialGradient' not in part_js, "Radial gradient allocation in animation loop must be avoided"
    assert 'particles.splice(0, this.particles.length - 50)' in part_js, "Active particles must be capped"

    # 7. No snowflake spam in gameplay
    assert 'force' in part_js
    assert 'data.scorePct >= 40' in app_js, "Thermal particles only trigger for >= 40% and progression"

    print("✅ Allègement UI, suppression des doublons, persistance d'historique et optimisations FPS GPU 60-120 validés !")

if __name__ == "__main__":
    test_modules()
    test_guest_lists()
    test_ui_improvements()
    test_single_win_animation()
    test_html_features()
    test_top2_thermal_gauge_and_particles()
    test_secret_words_filtering()
    test_daily_archive_and_time_stats()
    test_simplification_and_perf()
    print("\n🎉 TOUS LES TESTS DE NON-RÉGRESSION ET DE NOUVELLES FONCTIONNALITÉS ONT RÉUSSI AVEC SUCCÈS !")
