// =========================================================================
// MODULE AUTHENTIFICATION SUPABASE & SÉCURITÉ
// =========================================================================
import { $, triggerInputShake } from "./ui.js";
import { state } from "./state.js";

export const SUPABASE_URL = (() => {
  try {
    return window.SUPABASE_URL ? new URL(window.SUPABASE_URL.trim()).origin : "";
  } catch (_) {
    return "";
  }
})();

export const SUPABASE_ANON_KEY = (window.SUPABASE_ANON_KEY || "").trim();

export const sbClient = (SUPABASE_URL && SUPABASE_ANON_KEY && window.supabase)
  ? window.supabase.createClient(SUPABASE_URL, SUPABASE_ANON_KEY)
  : null;

export async function hashPassword(pseudo, password) {
  const cleanPseudo = (pseudo || "").trim().toLowerCase();
  const raw = `zeroabsolu_salt_v2_${cleanPseudo}_${(password || "").trim()}`;
  const msgBuffer = new TextEncoder().encode(raw);
  const hashBuffer = await crypto.subtle.digest("SHA-256", msgBuffer);
  const hashArray = Array.from(new Uint8Array(hashBuffer));
  return "za2_" + hashArray.map(b => b.toString(16).padStart(2, "0")).join("");
}

// Listes de 50 animaux connus et 50 adjectifs rigolos pour les joueurs invités
export const GUEST_ANIMALS = [
  "Loutre", "Poisson", "Rat", "Renard", "Panda", "Faucon", "Castor", "Blaireau",
  "Hérisson", "Lynx", "Lémurien", "Poulpe", "Dauphin", "Corbeau", "Koala", "Pingouin",
  "Hamster", "Canard", "Chouette", "Furet", "Caméléon", "Crapaud", "Écureuil", "Loup",
  "Ours", "Tigre", "Lion", "Girafe", "Paresseux", "Marmotte", "Phoque", "Pélican",
  "Iguane", "Crabe", "Lézard", "Baleine", "Requin", "Suricate", "Flamant", "Kangourou",
  "Zèbre", "Guépard", "Gorille", "Aigle", "Tortue", "Toucan", "ChauveSouris", "Morse",
  "Putois", "Pangolin"
];

export const GUEST_ADJECTIVES = [
  "Cool", "Rigolo", "Puant", "Malin", "Furtif", "Masqué", "Électrique", "Timide",
  "Bavard", "Glouton", "Cosmique", "Dormeur", "Furieux", "Givré", "Brûlant", "Speed",
  "Joyeux", "Farceur", "Ronchon", "Ninja", "Pixel", "Volant", "Sauvage", "Zen",
  "Lunatique", "Gourmand", "Savant", "Espiègle", "Curieux", "Rêveur", "Mignon", "Agile",
  "Bizarre", "Brave", "Chaleureux", "Délirant", "Dynamique", "Étourdi", "Fantaisiste", "Gaffeur",
  "Héroïque", "Intrépide", "Jovial", "Kitsch", "Loufoque", "Magique", "Mystérieux", "Optimiste",
  "Piquant", "Turbulent"
];

export function generateGuestPseudo() {
  const animal = GUEST_ANIMALS[Math.floor(Math.random() * GUEST_ANIMALS.length)];
  const adj = GUEST_ADJECTIVES[Math.floor(Math.random() * GUEST_ADJECTIVES.length)];
  return `${animal}${adj}`;
}

export function loginAsGuest() {
  const guestPseudo = generateGuestPseudo();
  state.myPseudo = guestPseudo;
  state.myPassword = "";
  state.isGuest = true;
  state.isAuthenticated = true;

  localStorage.setItem("zeroabsolu_pseudo", guestPseudo);
  localStorage.removeItem("zeroabsolu_pwd");

  state.players[state.myId] = {
    id: state.myId,
    pseudo: guestPseudo,
    points: 0,
    xp: 0,
    wins: 0,
    totalAttempts: 0,
    hotWordsFound: 0,
    top10Found: 0,
    bestScorePct: 0,
    bestRank: 0,
    attempts: 0
  };

  window.saveLocalProgress?.();
  window.updateLobbyHeaderUI?.();
  window.updateHintButtonUI?.();
  window.renderLeaderboard?.();

  $("authError").textContent = "";
  $("authView").classList.add("hidden");
  $("lobbyView").classList.remove("hidden");

  window.showToast?.(`Bienvenue ${guestPseudo} ! Mode invité activé.`, "sky");
  window.openWelcomeModal?.(true);
}

export function switchAuthMode(mode) {
  state.authMode = mode;
  $("authError").textContent = "";
  const isLogin = mode === "login";
  $("tabLoginBtn").className = isLogin
    ? "py-1.5 rounded-lg bg-sky-500 text-slate-950 transition"
    : "py-1.5 rounded-lg text-slate-400 hover:text-white transition";
  $("tabRegisterBtn").className = !isLogin
    ? "py-1.5 rounded-lg bg-amber-400 text-slate-950 transition"
    : "py-1.5 rounded-lg text-slate-400 hover:text-white transition";
  $("authSubmitText").textContent = isLogin ? "Se connecter" : "Créer mon compte";
}

export function togglePasswordVisibility() {
  const inp = $("authPassword");
  const isPwd = inp.type === "password";
  inp.type = isPwd ? "text" : "password";
  $("eyeIcon").className = isPwd ? "ph-duotone ph-eye-slash text-base text-sky-400" : "ph-duotone ph-eye text-base";
}

export async function handleAuthSubmit(e) {
  e.preventDefault();
  const pseudo = $("authPseudo").value.trim();
  const pwd = $("authPassword").value.trim();
  const errEl = $("authError");

  if (pseudo.length < 2) {
    errEl.textContent = "Le pseudo doit contenir au moins 2 caractères.";
    triggerInputShake($("authPseudo"));
    return;
  }
  if (pwd.length < 4) {
    errEl.textContent = "Le mot de passe doit contenir au moins 4 caractères.";
    triggerInputShake($("authPassword"));
    return;
  }

  errEl.textContent = "Vérification Cloud en cours...";
  $("authSubmitBtn").disabled = true;

  const cleanKey = pseudo.toLowerCase();

  if (!sbClient) {
    $("authSubmitBtn").disabled = false;
    errEl.textContent = "Clés Supabase absentes dans config.js !";
    return;
  }

  try {
    const isAlreadyHashed = pwd.startsWith("za2_") && pwd.length === 68 && /^[0-9a-f]+$/.test(pwd.slice(4));
    const hashedPwd = isAlreadyHashed ? pwd : await hashPassword(cleanKey, pwd);

    const { data: existing, error: selErr } = await sbClient
      .from("players")
      .select("*")
      .eq("pseudo_lower", cleanKey)
      .maybeSingle();

    if (selErr) {
      $("authSubmitBtn").disabled = false;
      errEl.textContent = `Erreur Supabase (${selErr.code || 'SQL'}) : ${selErr.message}`;
      return;
    }

    let isNewAccount = false;

    if (state.authMode === "register") {
      if (existing) {
        $("authSubmitBtn").disabled = false;
        errEl.textContent = `Le pseudo "${pseudo}" est déjà pris ! Choisissez-en un autre ou cliquez sur Connexion.`;
        triggerInputShake($("authPseudo"));
        return;
      }

      const newRow = {
        pseudo_lower: cleanKey,
        pseudo_display: pseudo,
        pin_code: hashedPwd,
        points: 0,
        xp: 0,
        wins: 0,
        total_attempts: 0,
        hot_words: 0,
        top10_words: 0,
        updated_at: new Date().toISOString()
      };

      const { error: insErr } = await sbClient.from("players").insert(newRow);
      if (insErr) {
        $("authSubmitBtn").disabled = false;
        errEl.textContent = `Création refusée par Supabase : ${insErr.message}`;
        return;
      }

      isNewAccount = true;
      applyCloudProfileToSelf(pseudo, hashedPwd, newRow);
    } else {
      if (!existing) {
        $("authSubmitBtn").disabled = false;
        errEl.textContent = `Aucun compte "${pseudo}" trouvé. Cliquez sur l'onglet Inscription !`;
        triggerInputShake($("tabRegisterBtn"));
        return;
      }

      let isMatch = false;
      if (existing.pin_code === hashedPwd) {
        isMatch = true;
      } else if (existing.pin_code === pwd) {
        // Ancien compte v1.1 en clair : validé et mis à niveau automatiquement vers SHA-256
        isMatch = true;
        try {
          await sbClient.from("players").update({ pin_code: hashedPwd }).eq("pseudo_lower", cleanKey);
          existing.pin_code = hashedPwd;
        } catch (_) {}
      }

      if (!isMatch) {
        $("authSubmitBtn").disabled = false;
        errEl.textContent = "Mot de passe incorrect pour ce pseudo.";
        triggerInputShake($("authPassword"));
        return;
      }

      applyCloudProfileToSelf(existing.pseudo_display || pseudo, hashedPwd, existing);
    }

    $("authSubmitBtn").disabled = false;
    errEl.textContent = "";
    state.isAuthenticated = true;
    window.updateLobbyHeaderUI?.();
    $("authView").classList.add("hidden");
    $("lobbyView").classList.remove("hidden");

    window.openWelcomeModal?.(isNewAccount);

  } catch (err) {
    $("authSubmitBtn").disabled = false;
    errEl.textContent = "Erreur réseau : impossible de joindre Supabase.";
  }
}

export function applyCloudProfileToSelf(pseudo, pwd, row) {
  state.myPseudo = pseudo;
  state.myPassword = pwd;
  localStorage.setItem("zeroabsolu_pseudo", state.myPseudo);
  localStorage.setItem("zeroabsolu_pwd", state.myPassword);

  state.players[state.myId] = {
    id: state.myId,
    pseudo: state.myPseudo,
    points: Number(row.points) || 0,
    xp: Number(row.xp) || 0,
    wins: Number(row.wins) || 0,
    totalAttempts: Number(row.total_attempts) || 0,
    hotWordsFound: Number(row.hot_words) || 0,
    top10Found: Number(row.top10_words) || 0,
    bestScorePct: state.players[state.myId]?.bestScorePct || 0,
    bestRank: state.players[state.myId]?.bestRank || 0,
    attempts: state.players[state.myId]?.attempts || 0
  };
  window.saveLocalProgress?.();
  window.updateHintButtonUI?.();
  window.renderLeaderboard?.();
}

export function logoutAccount() {
  state.isAuthenticated = false;
  localStorage.removeItem("zeroabsolu_pwd");
  state.myPassword = "";
  $("authPassword").value = "";
  $("lobbyView").classList.add("hidden");
  $("authView").classList.remove("hidden");
  switchAuthMode("login");
}

export async function syncProfileToSupabase() {
  if (!sbClient || !state.isAuthenticated || !state.myPseudo || !state.myPassword) return;
  const me = state.players[state.myId];
  if (!me) return;
  try {
    const { error } = await sbClient.from("players").upsert({
      pseudo_lower: state.myPseudo.toLowerCase(),
      pseudo_display: state.myPseudo,
      pin_code: state.myPassword,
      points: me.points || 0,
      xp: me.xp || 0,
      wins: me.wins || 0,
      total_attempts: me.totalAttempts || 0,
      hot_words: me.hotWordsFound || 0,
      top10_words: me.top10Found || 0,
      updated_at: new Date().toISOString()
    }, { onConflict: "pseudo_lower" });

    if (!error) window.updateLobbyHeaderUI?.();
  } catch (_) {}
}

export async function fetchGlobalLeaderboard() {
  if (!sbClient) return;
  try {
    const { data } = await sbClient
      .from("players")
      .select("pseudo_display, points, xp, wins, total_attempts, hot_words, top10_words")
      .order("xp", { ascending: false })
      .limit(30);
    if (data) {
      state.globalLeaderboardCache = data.map((row, idx) => ({
        id: `cloud_${idx}`,
        pseudo: row.pseudo_display,
        points: row.points || 0,
        xp: row.xp || 0,
        wins: row.wins || 0,
        totalAttempts: row.total_attempts || 0,
        hotWordsFound: row.hot_words || 0,
        top10Found: row.top10_words || 0
      }));
      window.renderStatsModalContent?.();
    }
  } catch (_) {}
}

export function switchLeaderboardScope(scope) {
  state.leaderboardScope = scope;
  $("btnRankRoom").className = scope === "room"
    ? "px-2 py-0.5 rounded-md bg-sky-500/20 text-sky-300 border border-sky-500/40 text-[10px] font-bold"
    : "px-2 py-0.5 rounded-md bg-slate-800 text-slate-400 hover:text-white text-[10px] font-bold";
  $("btnRankGlobal").className = scope === "global"
    ? "px-2 py-0.5 rounded-md bg-amber-500/20 text-amber-300 border border-amber-500/40 text-[10px] font-bold"
    : "px-2 py-0.5 rounded-md bg-slate-800 text-slate-400 hover:text-white text-[10px] font-bold";
  if (scope === "global") fetchGlobalLeaderboard();
  window.renderStatsModalContent?.();
}
