// =========================================================================
// 1. CONFIGURATION, SUPABASE CLOUD & CONSTANTES (v1.1)
// =========================================================================
const APP_VERSION = "v1.1";
const APP_EDITION = "Édition Solaire";
const $ = id => document.getElementById(id);

const MODE_CONFIG = {
  classic: {
    total: 500,
    folder: "parties",
    label: "Classique",
    icon: "ph-compass-rose",
    color: "text-sky-400",
    pillCls: "bg-sky-500/10 text-sky-300 border-sky-500/25"
  },
  pop: {
    total: 91,
    folder: "parties_pop",
    label: "Pop & Manga",
    icon: "ph-game-controller",
    color: "text-purple-400",
    pillCls: "bg-purple-500/15 text-purple-200 border-purple-500/40"
  }
};
let currentGameMode = localStorage.getItem("zeroabsolu_mode") || "classic";

const SUPABASE_URL = (() => {
  try {
    return window.SUPABASE_URL ? new URL(window.SUPABASE_URL.trim()).origin : "";
  } catch (_) {
    return "";
  }
})();
const SUPABASE_ANON_KEY = (window.SUPABASE_ANON_KEY || "").trim();

const sbClient = (SUPABASE_URL && SUPABASE_ANON_KEY && window.supabase)
  ? window.supabase.createClient(SUPABASE_URL, SUPABASE_ANON_KEY)
  : null;

const HINT_COST = 35, XP_PER_LEVEL = 100;
const TOPIC_ROOT = "zeroabsolu/v11/rooms/";

const WSS_BROKERS = [
  "wss://broker.emqx.io:8084/mqtt",
  "wss://broker.hivemq.com:8884/mqtt"
];

const GRADE_TIERS = [
  { minLevel: 1,  xpReq: 0,    icon: "ph-snowflake",    color: "text-sky-300",    title: "Flocon Curieux",      desc: "Premiers pas dans le froid absolu" },
  { minLevel: 3,  xpReq: 200,  icon: "ph-compass-tool", color: "text-cyan-300",   title: "Sondeur Polaire",     desc: "Capable de détecter les signaux tièdes" },
  { minLevel: 5,  xpReq: 400,  icon: "ph-flame",        color: "text-orange-400", title: "Chasseur de Braises", desc: "Habitué des mots du Top 1000" },
  { minLevel: 9,  xpReq: 800,  icon: "ph-lightning",    color: "text-purple-300", title: "Oracle Thermique",    desc: "Maîtrise des connexions sémantiques" },
  { minLevel: 14, xpReq: 1300, icon: "ph-meteor",       color: "text-red-400",    title: "Maître du Magma",     desc: "Plonge régulièrement dans le Top 10" },
  { minLevel: 20, xpReq: 1900, icon: "ph-sun-dim",      color: "text-amber-300",  title: "Cœur Solaire",        desc: "Entité en fusion sémantique permanente" }
];

const FALLBACK_WORDS = {
  "océan": [100, 1000], "mer": [92.4, 999], "maritime": [86.1, 998], "atlantique": [84.5, 997],
  "pacifique": [83.2, 996], "vague": [78.9, 995], "navire": [76.4, 994], "marin": [75.1, 993],
  "bateau": [70.5, 990], "plage": [66.2, 980], "île": [61.5, 950], "eau": [58.3, 920],
  "poisson": [55.1, 890], "vent": [46.8, 760], "soleil": [32.1, 450], "forêt": 18.5, "plante": 16.0
};

let myId = sessionStorage.getItem("za_tab_id") || ("p_" + Math.random().toString(36).slice(2, 10));
sessionStorage.setItem("za_tab_id", myId);

let myPseudo = localStorage.getItem("zeroabsolu_pseudo") || "";
let myPassword = localStorage.getItem("zeroabsolu_pwd") || "";
let isAuthenticated = false;
let authMode = "login";
let currentTutoSlide = 0;

let savedStats = JSON.parse(localStorage.getItem("zeroabsolu_profile_v2") || "{}");

let hasStartedSession = false, roomCode = null, isHost = true;
let roundNumber = 1, playedGameIds = new Set(), currentGameId = pickUnplayedGameId(currentGameMode);
let currentLoadSeq = 0;
let gameDictionary = {}, accentInsensitiveMap = {}, guesses = [];
let roundFinished = false, roomBestScorePct = 0, roomBestRank = 0;
let players = {}, globalLeaderboardCache = [], leaderboardScope = "room";
let selectedStatsPlayerId = myId, showingGradesCatalog = false;
let statsMinimized = false, statsIdleTimer = null, surgeHideTimer = null, levelUpTimer = null, feedOnlyHot = false, feedEvents = [];

let secretClickCount = 0, secretClickTimer = null;

const escapeHTML = s => String(s).replace(/&/g,"&amp;").replace(/</g,"&lt;").replace(/>/g,"&gt;").replace(/"/g,"&quot;").replace(/'/g,"&#039;");
const stripAccents = s => s.replace(/œ/g, "oe").replace(/æ/g, "ae").normalize("NFD").replace(/[\u0300-\u036f]/g, "").trim().toLowerCase();
const vibrateDevice = p => { try { navigator.vibrate?.(p); } catch (_) {} };
const formatPct = v => v >= 100 ? "100%" : `${Number(v).toFixed(1)}%`;
const getReadableTopLabel = r => r === 1000 ? "FUSION" : r ? `Top ${1001 - r}` : null;
const toggleModal = (id, show) => $(id)?.classList.toggle("hidden", !show);

function pickUnplayedGameId(mode = currentGameMode) {
  const maxGames = MODE_CONFIG[mode]?.total || 500;
  if (playedGameIds.size >= maxGames) playedGameIds.clear();
  let c;
  do {
    c = Math.floor(Math.random() * maxGames) + 1;
  } while (playedGameIds.has(c));
  playedGameIds.add(c);
  return c;
}

function updateModeUI(mode = currentGameMode) {
  const isPop = mode === "pop";
  if ($("modeClassicBtn") && $("modePopBtn")) {
    $("modeClassicBtn").className = !isPop
      ? "py-2 px-2.5 rounded-xl bg-sky-500/20 border border-sky-400/50 text-sky-200 flex items-center justify-center gap-2 transition shadow-sm"
      : "py-2 px-2.5 rounded-xl bg-slate-900/60 border border-transparent text-slate-400 hover:text-white flex items-center justify-center gap-2 transition";
    $("modePopBtn").className = isPop
      ? "py-2 px-2.5 rounded-xl bg-purple-500/25 border border-purple-400/60 text-purple-100 flex items-center justify-center gap-2 transition shadow-sm"
      : "py-2 px-2.5 rounded-xl bg-slate-900/60 border border-transparent text-slate-400 hover:text-white flex items-center justify-center gap-2 transition";
  }

  const cfg = MODE_CONFIG[mode] || MODE_CONFIG.classic;
  if ($("modeHeaderBadge")) {
    $("modeHeaderBadge").className = `cursor-pointer text-[11px] font-bold px-2 py-1 rounded-lg border flex items-center gap-1 shrink-0 ${cfg.pillCls}`;
    $("modeHeaderIcon").className = `ph-duotone ${cfg.icon} text-xs ${cfg.color}`;
    $("modeHeaderText").textContent = cfg.label;
  }
}

function selectGameMode(mode) {
  if (!MODE_CONFIG[mode]) return;
  if (roomCode && !isHost) {
    showToast("Seul l'hôte du salon peut changer le mode de jeu.", "amber");
    return;
  }
  const changed = currentGameMode !== mode;
  currentGameMode = mode;
  localStorage.setItem("zeroabsolu_mode", mode);
  updateModeUI(mode);

  if (changed) {
    playedGameIds.clear();
    const nextId = pickUnplayedGameId(mode);
    const nextRound = hasStartedSession ? roundNumber + 1 : 1;
    loadGame(nextId, nextRound, [], mode);
    if (roomCode && isHost) {
      publishRoomEvent({ type: "NEW_ROUND", senderId: myId, gameId: nextId, roundNumber: nextRound, gameMode: mode, players }, false);
      publishRetainedRoomSnapshot();
    }
    showToast(`Mode ${MODE_CONFIG[mode].label} activé !`, "sky");
  }
}

function getLevelInfo(xp = 0) {
  const safeXp = Math.max(0, Number(xp) || 0);
  const level = Math.floor(safeXp / XP_PER_LEVEL) + 1;
  const currentLevelXp = safeXp % XP_PER_LEVEL;
  const progressPct = Math.min(100, Math.round((currentLevelXp / XP_PER_LEVEL) * 100));
  const tier = [...GRADE_TIERS].reverse().find(t => level >= t.minLevel) || GRADE_TIERS[0];
  return { level, currentLevelXp, nextLevelXp: XP_PER_LEVEL, progressPct, title: tier.title, icon: tier.icon, color: tier.color, tier };
}

function computeUnifiedScorePct(temp, rank) {
  if (rank === 1000) return 100;
  if (rank >= 900) return Number((rank / 10).toFixed(1));
  if (rank > 0) return Number((40 + (rank / 900) * 49.9).toFixed(1));
  return Number((1 + Math.max(0, Math.min(1, (temp + 12) / 40)) * 38.5).toFixed(1));
}

function getTierVisuals(g) {
  const topLabel = getReadableTopLabel(g.rank);
  if (g.isWin || g.rank === 1000) {
    return {
      cardCls: "tier-fusion-card border-2", wordCls: "fusion-word-glow", barCls: "solar-fusion-bar",
      pctCls: "text-white", feedRowCls: "tier-fusion-card",
      badgeHTML: `<span class="bg-amber-300/30 text-white border border-amber-200 text-[10px] font-extrabold px-2 py-0.2 rounded shadow-sm inline-flex items-center gap-1"><i class="ph-fill ph-sun-dim text-xs text-amber-200"></i>FUSION</span>`
    };
  }
  if (g.isTop10 || g.rank >= 991) {
    return {
      cardCls: "tier-magma-card", wordCls: "magma-word-glow", barCls: "magma-lava-bar",
      pctCls: "text-red-300", feedRowCls: "bg-red-950/50 border-red-500/50",
      badgeHTML: `<span class="bg-red-900/70 text-red-200 border border-red-500/70 text-[10px] font-extrabold px-1.5 py-0.2 rounded inline-flex items-center gap-1"><i class="ph-fill ph-meteor text-xs text-red-400"></i>${topLabel}</span>`
    };
  }
  if (g.rank >= 900) {
    return {
      cardCls: "tier-flame-card", wordCls: "flame-word-glow", barCls: "thermal-spectrum",
      pctCls: "text-orange-400", feedRowCls: "bg-orange-950/35 border-orange-500/40",
      badgeHTML: `<span class="bg-orange-500/20 text-orange-200 border border-orange-400/50 text-[10px] font-bold px-1.5 py-0.2 rounded inline-flex items-center gap-1"><i class="ph-fill ph-flame text-xs text-orange-400"></i>${topLabel}</span>`
    };
  }
  if (g.rank) {
    return {
      cardCls: "border-slate-800/70 bg-slate-800/35", wordCls: "text-slate-100", barCls: "thermal-spectrum",
      pctCls: "text-purple-300", feedRowCls: "bg-purple-950/25 border-purple-500/30",
      badgeHTML: `<span class="bg-purple-500/15 text-purple-300 border border-purple-500/30 text-[10px] font-semibold px-1.5 py-0.2 rounded inline-flex items-center gap-1"><i class="ph-duotone ph-sparkle text-xs"></i>${topLabel}</span>`
    };
  }
  return {
    cardCls: "border-slate-800/70 bg-slate-800/35", wordCls: "text-slate-100", barCls: "thermal-spectrum",
    pctCls: "text-slate-300", feedRowCls: "bg-slate-800/30 border-slate-800/70", badgeHTML: ""
  };
}

// =========================================================================
// 2. AUTHENTIFICATION SUPABASE (CONNEXION / INSCRIPTION) & BIENVENUE / TUTO
// =========================================================================
function switchAuthMode(mode) {
  authMode = mode;
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

function togglePasswordVisibility() {
  const inp = $("authPassword");
  const isPwd = inp.type === "password";
  inp.type = isPwd ? "text" : "password";
  $("eyeIcon").className = isPwd ? "ph-duotone ph-eye-slash text-base text-sky-400" : "ph-duotone ph-eye text-base";
}

async function handleAuthSubmit(e) {
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

    if (authMode === "register") {
      if (existing) {
        $("authSubmitBtn").disabled = false;
        errEl.textContent = `Le pseudo "${pseudo}" est déjà pris ! Choisissez-en un autre ou cliquez sur Connexion.`;
        triggerInputShake($("authPseudo"));
        return;
      }

      const newRow = {
        pseudo_lower: cleanKey,
        pseudo_display: pseudo,
        pin_code: pwd,
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
      applyCloudProfileToSelf(pseudo, pwd, newRow);
    } else {
      if (!existing) {
        $("authSubmitBtn").disabled = false;
        errEl.textContent = `Aucun compte "${pseudo}" trouvé. Cliquez sur l'onglet Inscription !`;
        triggerInputShake($("tabRegisterBtn"));
        return;
      }
      if (existing.pin_code !== pwd) {
        $("authSubmitBtn").disabled = false;
        errEl.textContent = "Mot de passe incorrect pour ce pseudo.";
        triggerInputShake($("authPassword"));
        return;
      }

      applyCloudProfileToSelf(existing.pseudo_display || pseudo, pwd, existing);
    }

    $("authSubmitBtn").disabled = false;
    errEl.textContent = "";
    isAuthenticated = true;
    updateLobbyHeaderUI();
    $("authView").classList.add("hidden");
    $("lobbyView").classList.remove("hidden");

    openWelcomeModal(isNewAccount);

  } catch (err) {
    $("authSubmitBtn").disabled = false;
    errEl.textContent = "Erreur réseau : impossible de joindre Supabase.";
  }
}

function applyCloudProfileToSelf(pseudo, pwd, row) {
  myPseudo = pseudo;
  myPassword = pwd;
  localStorage.setItem("zeroabsolu_pseudo", myPseudo);
  localStorage.setItem("zeroabsolu_pwd", myPassword);

  players[myId] = {
    id: myId,
    pseudo: myPseudo,
    points: Number(row.points) || 0,
    xp: Number(row.xp) || 0,
    wins: Number(row.wins) || 0,
    totalAttempts: Number(row.total_attempts) || 0,
    hotWordsFound: Number(row.hot_words) || 0,
    top10Found: Number(row.top10_words) || 0,
    bestScorePct: players[myId]?.bestScorePct || 0,
    bestRank: players[myId]?.bestRank || 0,
    attempts: players[myId]?.attempts || 0
  };
  saveLocalProgress();
  updateHintButtonUI();
  renderLeaderboard();
}

function updateLobbyHeaderUI() {
  const me = players[myId] || {};
  const lvl = getLevelInfo(me.xp || 0);
  $("lobbyLevelBadge").textContent = `N${lvl.level}`;
  $("lobbyPseudoDisplay").textContent = me.pseudo || myPseudo;
  $("lobbyStatsDisplay").textContent = `${me.points || 0} ⚡ • ${me.xp || 0} XP (${lvl.title})`;
  updateModeUI(currentGameMode);
}

function logoutAccount() {
  isAuthenticated = false;
  localStorage.removeItem("zeroabsolu_pwd");
  $("authPassword").value = "";
  $("lobbyView").classList.add("hidden");
  $("authView").classList.remove("hidden");
  switchAuthMode("login");
}

function openWelcomeModal(isNewUser) {
  const me = players[myId] || {};
  const lvl = getLevelInfo(me.xp || 0);
  const isExperienced = !isNewUser && ((me.xp || 0) > 0 || (me.totalAttempts || 0) > 0);

  $("welcomeTitle").textContent = `Bienvenue ${me.pseudo} !`;
  $("welcomeSub").textContent = isExperienced
    ? "Votre profil Cloud est synchronisé."
    : "Votre compte est prêt ! Découvrez comment faire monter la température.";

  $("welcomeLevel").textContent = `Niv. ${lvl.level}`;
  $("welcomeGrade").textContent = lvl.title;
  $("welcomePoints").textContent = `${me.points || 0} ⚡`;

  if (isExperienced) {
    $("welcomeButtons").innerHTML = `
      <button id="welcomePlayBtn" onclick="closeWelcomeModal()" class="w-full py-2.5 rounded-xl text-xs font-extrabold bg-gradient-to-r from-sky-500 to-indigo-600 hover:from-sky-400 hover:to-indigo-500 text-white shadow-lg transition">
        Continuer vers le salon
      </button>
      <button id="welcomeTutoBtn" onclick="closeWelcomeModal(); openTutorialModal();" class="w-full py-2 rounded-xl text-xs font-bold bg-slate-800 hover:bg-slate-700 text-sky-300 transition flex items-center justify-center gap-1.5">
        <i class="ph-duotone ph-compass-tool text-sm"></i> Revoir le tutoriel
      </button>
    `;
  } else {
    $("welcomeButtons").innerHTML = `
      <button id="welcomeTutoBtn" onclick="closeWelcomeModal(); openTutorialModal();" class="w-full py-2.5 rounded-xl text-xs font-extrabold bg-gradient-to-r from-amber-400 to-orange-500 text-slate-950 shadow-lg transition flex items-center justify-center gap-1.5">
        <i class="ph-bold ph-sparkle text-sm"></i> Découvrir le tutoriel (30s)
      </button>
      <button id="welcomePlayBtn" onclick="closeWelcomeModal()" class="w-full py-2 rounded-xl text-xs font-bold bg-slate-800 hover:bg-slate-700 text-slate-300 transition">
        Passer directement au salon
      </button>
    `;
  }

  toggleModal("welcomeModal", true);
}

function closeWelcomeModal() {
  toggleModal("welcomeModal", false);
}

function openTutorialModal() {
  currentTutoSlide = 0;
  updateTutorialCarousel();
  toggleModal("tutorialModal", true);
}

function closeTutorialModal() {
  toggleModal("tutorialModal", false);
}

function stepTutorial(delta) {
  if (currentTutoSlide + delta >= 3) {
    closeTutorialModal();
    return;
  }
  currentTutoSlide = Math.max(0, Math.min(2, currentTutoSlide + delta));
  updateTutorialCarousel();
}

function updateTutorialCarousel() {
  $("tutorialTrack").style.transform = `translateX(-${currentTutoSlide * 100}%)`;
  $("tutoPrevBtn").classList.toggle("invisible", currentTutoSlide === 0);
  $("tutoNextBtn").textContent = currentTutoSlide === 2 ? "C'est parti !" : "Suivant →";

  const dots = $("tutoDots").children;
  for (let i = 0; i < dots.length; i++) {
    dots[i].className = i === currentTutoSlide
      ? "w-5 h-1.5 rounded-full bg-sky-400 transition-all"
      : "w-1.5 h-1.5 rounded-full bg-slate-700 transition-all";
  }
}

async function syncProfileToSupabase() {
  if (!sbClient || !isAuthenticated || !myPseudo || !myPassword) return;
  const me = players[myId];
  if (!me) return;
  try {
    const { error } = await sbClient.from("players").upsert({
      pseudo_lower: myPseudo.toLowerCase(),
      pseudo_display: myPseudo,
      pin_code: myPassword,
      points: me.points || 0,
      xp: me.xp || 0,
      wins: me.wins || 0,
      total_attempts: me.totalAttempts || 0,
      hot_words: me.hotWordsFound || 0,
      top10_words: me.top10Found || 0,
      updated_at: new Date().toISOString()
    }, { onConflict: "pseudo_lower" });

    if (!error) updateLobbyHeaderUI();
  } catch (_) {}
}

async function fetchGlobalLeaderboard() {
  if (!sbClient) return;
  try {
    const { data } = await sbClient
      .from("players")
      .select("pseudo_display, points, xp, wins, total_attempts, hot_words, top10_words")
      .order("xp", { ascending: false })
      .limit(30);
    if (data) {
      globalLeaderboardCache = data.map((row, idx) => ({
        id: `cloud_${idx}`,
        pseudo: row.pseudo_display,
        points: row.points || 0,
        xp: row.xp || 0,
        wins: row.wins || 0,
        totalAttempts: row.total_attempts || 0,
        hotWordsFound: row.hot_words || 0,
        top10Found: row.top10_words || 0
      }));
      renderStatsModalContent();
    }
  } catch (_) {}
}

function switchLeaderboardScope(scope) {
  leaderboardScope = scope;
  $("btnRankRoom").className = scope === "room"
    ? "px-2 py-0.5 rounded-md bg-sky-500/20 text-sky-300 border border-sky-500/40 text-[10px] font-bold"
    : "px-2 py-0.5 rounded-md bg-slate-800 text-slate-400 hover:text-white text-[10px] font-bold";
  $("btnRankGlobal").className = scope === "global"
    ? "px-2 py-0.5 rounded-md bg-amber-500/20 text-amber-300 border border-amber-500/40 text-[10px] font-bold"
    : "px-2 py-0.5 rounded-md bg-slate-800 text-slate-400 hover:text-white text-[10px] font-bold";
  if (scope === "global") fetchGlobalLeaderboard();
  renderStatsModalContent();
}

// =========================================================================
// 3. MENU SECRET SANDBOX (CODE "XXXX" + 3 CLICS SUR LE LOGO) & CONFIRMATIONS
// =========================================================================
function isSecretCodeEntered() {
  const codeModal = ($("modalRoomCode")?.value || "").trim().toUpperCase();
  const codeInput = ($("wordInput")?.value || "").trim().toUpperCase();
  const codeAuth = ($("authPseudo")?.value || "").trim().toUpperCase();
  return codeModal === "XXXX" || codeInput === "XXXX" || codeAuth === "XXXX";
}

function handleLogoSecretClick() {
  if (!isSecretCodeEntered()) return false;
  secretClickCount++;
  clearTimeout(secretClickTimer);
  secretClickTimer = setTimeout(() => { secretClickCount = 0; }, 2200);

  if (secretClickCount >= 3) {
    secretClickCount = 0;
    if ($("wordInput")?.value.trim().toUpperCase() === "XXXX") $("wordInput").value = "";
    $("debugSecretWord").textContent = "•••";
    toggleModal("debugModal", true);
    vibrateDevice([40, 60, 40]);
    return true;
  }
  return true;
}

function handleHeaderLogoClick() {
  if (isSecretCodeEntered()) {
    handleLogoSecretClick();
    return;
  }
  openOnboardingModal();
}

function revealSecretInDebug() {
  const secret = Object.entries(gameDictionary).find(([, v]) => Array.isArray(v) && v[1] === 1000)?.[0] || "inconnu";
  $("debugSecretWord").textContent = secret.toUpperCase();
}

function debugAddPointsAndXp(pts, xp) {
  const me = players[myId];
  if (!me) return;
  const prevLvl = getLevelInfo(me.xp).level;
  me.points = (me.points || 0) + pts;
  me.xp = (me.xp || 0) + xp;
  saveLocalProgress();
  syncProfileToSupabase();
  updateHintButtonUI();
  renderLeaderboard();
  const newLvl = getLevelInfo(me.xp);
  if (newLvl.level > prevLvl) showLevelUpBanner(newLvl);
  showToast(`+${pts} ⚡ et +${xp} XP ajoutés !`, "amber");
}

async function debugResetAllScores() {
  const me = players[myId];
  if (!me) return;
  me.points = 0; me.xp = 0; me.wins = 0; me.totalAttempts = 0; me.hotWordsFound = 0; me.top10Found = 0;
  saveLocalProgress();
  await syncProfileToSupabase();
  updateHintButtonUI();
  renderLeaderboard();
  toggleModal("debugModal", false);
  showToast("Scores et niveau remis à zéro !", "rose");
}

let pendingConfirmAction = null;

function openConfirmModal({ icon, colorCls, title, desc, btnText, onConfirm }) {
  $("confirmIcon").className = `ph-duotone ${icon} text-2xl`;
  $("confirmIconBox").className = `w-11 h-11 rounded-2xl flex items-center justify-center mx-auto mb-3 border ${colorCls}`;
  $("confirmTitle").textContent = title;
  $("confirmDesc").textContent = desc;
  $("confirmActionBtn").textContent = btnText;
  pendingConfirmAction = onConfirm;
  $("confirmActionBtn").onclick = () => {
    const fn = pendingConfirmAction;
    closeConfirmModal();
    fn?.();
  };
  toggleModal("confirmModal", true);
}

function closeConfirmModal() {
  pendingConfirmAction = null;
  toggleModal("confirmModal", false);
}

// =========================================================================
// 4. INDEXATION LÉGÈRE DE SAISIE (TOLÉRANCE ACCENTS, PLURIELS & LIGATURES)
// =========================================================================
function buildAccentInsensitiveIndex() {
  accentInsensitiveMap = {};
  for (const word of Object.keys(gameDictionary)) {
    const s = stripAccents(word);
    accentInsensitiveMap[s] = word;
    if (word.includes("-")) accentInsensitiveMap[s.replace(/-/g, "")] = word;
  }
}

const tryDirectMatch = c => (c in gameDictionary) ? c : (accentInsensitiveMap[stripAccents(c)] || null);

function resolveWordInDictionary(raw) {
  const cleaned = raw.trim().toLowerCase().replace(/\s+/g, "-");
  let m = tryDirectMatch(cleaned);
  if (m) return m;

  if (cleaned === "yeux") return tryDirectMatch("œil") || tryDirectMatch("oeil");
  if (cleaned === "cieux") return tryDirectMatch("ciel");

  const forms = [cleaned];
  if (cleaned.endsWith("eaux") && cleaned.length > 5) forms.push(cleaned.slice(0, -1));
  if ((cleaned.endsWith("s") || cleaned.endsWith("x")) && cleaned.length > 3) forms.push(cleaned.slice(0, -1));

  const rules = [
    ["aux","al"],["aux","ail"],["euse","eur"],["euse","eux"],["rice","eur"],["trice","teur"],
    ["ive","if"],["ienne","ien"],["onne","on"],["elle","el"],["elle","eau"],["ère","er"],
    ["ere","er"],["ette","et"],["otte","ot"],["e",""],["ée","er"],["é","er"],["és","er"],
    ["ées","er"],["er","e"]
  ];
  for (const f of forms) {
    if ((m = tryDirectMatch(f))) return m;
    for (const [end, rep] of rules) {
      if (f.endsWith(end) && f.length - end.length >= 2 && (m = tryDirectMatch(f.slice(0, -end.length) + rep))) return m;
    }
  }
  return null;
}

// =========================================================================
// 5. INITIALISATION, CLAVIER MOBILE & STATS AUTO-MINIMISÉES
// =========================================================================
let initialScreenHeight = window.innerHeight;

function syncMobileViewport() {
  const vv = window.visualViewport;
  if (!vv) return;
  $("appViewport").style.height = `${vv.height}px`;
  $("appViewport").style.top = `${vv.offsetTop}px`;
  document.body.classList.toggle("keyboard-active", (initialScreenHeight - vv.height) > 140 && window.innerWidth < 1024);
}

function resetStatsIdleTimer() {
  clearTimeout(statsIdleTimer);
  statsIdleTimer = setTimeout(() => setStatsMinimized(true), 10000);
}
function toggleStatsMinimized() { setStatsMinimized(!statsMinimized); if (!statsMinimized) resetStatsIdleTimer(); }
function setStatsMinimized(min) {
  statsMinimized = min;
  $("statsExpanded").classList.toggle("hidden", min);
  $("statsCollapsed").classList.toggle("hidden", !min);
}

window.addEventListener("DOMContentLoaded", () => {
  $("versionBadgeTop").textContent = APP_VERSION;
  $("versionBadgeFooter").textContent = `${APP_VERSION} • ${APP_EDITION}`;
  $("cloudStatusText").textContent = sbClient ? "Supabase Cloud Actif" : "Clés Supabase manquantes";
  $("cloudStatusDot").className = sbClient ? "w-1.5 h-1.5 rounded-full bg-emerald-400" : "w-1.5 h-1.5 rounded-full bg-rose-500";
  initialScreenHeight = window.screen?.availHeight || window.innerHeight;

  if (myPseudo) $("authPseudo").value = myPseudo;
  if (myPassword) $("authPassword").value = myPassword;

  updateModeUI(currentGameMode);
  initSelfPlayer();
  loadGame(currentGameId, 1, [], currentGameMode);
  resetStatsIdleTimer();

  $("modalRoomCode").addEventListener("keydown", e => { if (e.key === "Enter" && !$("joinRoomBtn").disabled) startJoinRoom(); });
  $("wordInput").addEventListener("focus", () => { if (window.innerWidth < 1024) { document.body.classList.add("keyboard-active"); setTimeout(syncMobileViewport, 60); } });
  $("wordInput").addEventListener("blur", () => setTimeout(() => { document.body.classList.remove("keyboard-active"); syncMobileViewport(); }, 120));
  window.visualViewport?.addEventListener("resize", syncMobileViewport);
  window.visualViewport?.addEventListener("scroll", syncMobileViewport);
});

function initSelfPlayer() {
  const cur = players[myId] || {};
  players[myId] = {
    id: myId, pseudo: myPseudo || "Joueur",
    points: cur.points ?? savedStats.points ?? 0,
    xp: cur.xp ?? savedStats.xp ?? 0,
    wins: cur.wins ?? savedStats.wins ?? 0,
    totalAttempts: cur.totalAttempts ?? savedStats.totalAttempts ?? 0,
    hotWordsFound: cur.hotWordsFound ?? savedStats.hotWordsFound ?? 0,
    top10Found: cur.top10Found ?? savedStats.top10Found ?? 0,
    bestScorePct: cur.bestScorePct ?? 0, bestRank: cur.bestRank ?? 0, attempts: cur.attempts ?? 0
  };
  saveLocalProgress();
  updateHintButtonUI();
  renderLeaderboard();
}

function saveLocalProgress() {
  const me = players[myId];
  if (!me) return;
  savedStats = { points: me.points, xp: me.xp, wins: me.wins, totalAttempts: me.totalAttempts, hotWordsFound: me.hotWordsFound, top10Found: me.top10Found };
  localStorage.setItem("zeroabsolu_profile_v2", JSON.stringify(savedStats));
  $("headerPoints").textContent = me.points;
  $("headerLevelBadge").textContent = `N${getLevelInfo(me.xp).level}`;
}

function updateHintButtonUI() {
  const me = players[myId], hasPts = me && me.points >= HINT_COST;
  $("hintBtn").className = hasPts
    ? `flex items-center justify-center gap-1 bg-amber-500/20 hover:bg-amber-500/30 border border-amber-400/50 text-amber-300 text-xs font-bold px-2 py-1 rounded-lg transition shadow-sm shrink-0 ${roundFinished ? 'opacity-50' : ''}`
    : "flex items-center justify-center gap-1 bg-slate-900/70 border border-slate-800 text-slate-500 text-xs font-semibold px-2 py-1 rounded-lg transition opacity-75 shrink-0";
  $("hintBtnContent").innerHTML = `<i class="ph-duotone ${hasPts ? 'ph-lightbulb-filament text-amber-300' : 'ph-lock-key text-slate-500'} text-sm"></i><span class="font-mono-num text-[11px]">${HINT_COST}</span>`;
}

function showLevelUpBanner(newLevelInfo) {
  const banner = $("levelUpBanner");
  $("levelUpIcon").className = `ph-duotone ${newLevelInfo.icon} text-2xl text-white`;
  $("levelUpNumText").textContent = `Niveau ${newLevelInfo.level}`;
  $("levelUpTitleText").textContent = newLevelInfo.title;

  banner.classList.remove("hidden", "animate-levelup");
  void banner.offsetWidth;
  banner.classList.add("animate-levelup");

  vibrateDevice([50, 40, 80]);
  clearTimeout(levelUpTimer);
  levelUpTimer = setTimeout(() => banner.classList.add("hidden"), 4200);
}

// =========================================================================
// 6. MODALE PROFIL JOUEUR & CATALOGUE DES GRADES
// =========================================================================
function openStatsModal(targetId = myId) {
  selectedStatsPlayerId = players[targetId] ? targetId : myId;
  showingGradesCatalog = false;
  updateGradesViewVisibility();
  renderStatsModalContent();
  toggleModal("statsModal", true);
}

function toggleGradesView() {
  showingGradesCatalog = !showingGradesCatalog;
  updateGradesViewVisibility();
  renderStatsModalContent();
}

function updateGradesViewVisibility() {
  $("gradesCatalogView").classList.toggle("hidden", !showingGradesCatalog);
  $("gradesCatalogView").classList.toggle("flex", showingGradesCatalog);
  $("statsMainView").classList.toggle("hidden", showingGradesCatalog);
}

function renderStatsModalContent() {
  const roomPlayers = Object.values(players).sort((a, b) => (b.xp - a.xp) || (b.points - a.points));
  const listSource = (leaderboardScope === "global" && globalLeaderboardCache.length) ? globalLeaderboardCache : roomPlayers;
  const p = players[selectedStatsPlayerId] || players[myId];
  if (!p) return;

  $("statsPlayerTabs").innerHTML = roomPlayers.map(pl => `
    <button onclick="selectedStatsPlayerId='${escapeHTML(pl.id)}'; renderStatsModalContent();"
      class="px-3 py-1 rounded-xl text-xs font-bold transition shrink-0 ${pl.id === p.id ? 'bg-sky-500 text-slate-950' : 'bg-slate-800 text-slate-300 hover:bg-slate-700'}">
      ${escapeHTML(pl.pseudo)}
    </button>`).join("");

  const lvl = getLevelInfo(p.xp || 0);
  $("profileLevelNum").textContent = lvl.level;
  $("profileName").textContent = p.pseudo;
  $("profileRankIcon").className = `ph-duotone ${lvl.icon} text-xs ${lvl.color}`;
  $("profileRankText").textContent = lvl.title;
  $("profileXpText").textContent = `${lvl.currentLevelXp} / ${lvl.nextLevelXp} XP (Total: ${p.xp || 0} XP)`;
  $("profileNextLevelXp").textContent = `Niv. ${lvl.level + 1}`;
  $("profileXpBar").style.width = `${Math.max(6, lvl.progressPct)}%`;

  $("gradesListContainer").innerHTML = GRADE_TIERS.map(g => {
    const unlocked = lvl.level >= g.minLevel, isCur = lvl.tier.minLevel === g.minLevel;
    const badge = isCur ? `<span class="text-[10px] font-extrabold bg-emerald-500/20 text-emerald-300 border border-emerald-500/40 px-2 py-0.5 rounded-full">Actuel</span>`
                        : unlocked ? `<span class="text-[10px] font-bold text-sky-400">✓ Débloqué</span>`
                                   : `<span class="text-[10px] font-mono-num text-slate-500">Niv.${g.minLevel}</span>`;
    return `
      <div class="p-2.5 rounded-xl border flex items-center justify-between gap-2 ${isCur ? 'bg-slate-800/90 border-sky-400/60' : unlocked ? 'bg-slate-900/80 border-slate-800' : 'bg-slate-950/60 border-slate-900 opacity-55'}">
        <div class="flex items-center gap-2.5 min-w-0">
          <div class="w-8 h-8 rounded-lg bg-slate-950 border border-slate-800 flex items-center justify-center shrink-0">
            <i class="ph-duotone ${g.icon} text-lg ${g.color}"></i>
          </div>
          <div class="min-w-0">
            <div class="flex items-center gap-2"><span class="text-xs font-extrabold text-white">${g.title}</span><span class="text-[10px] font-mono-num text-slate-400">(Niv.${g.minLevel} • ${g.xpReq} XP)</span></div>
            <p class="text-[10px] text-slate-400 mt-0.5">${g.desc}</p>
          </div>
        </div>
        <div class="shrink-0">${badge}</div>
      </div>`;
  }).join("");

  const totalAtt = p.totalAttempts || p.attempts || 0, hotCount = p.hotWordsFound || 0;
  const cards = [
    ["ph-sun-dim", "Victoires", p.wins || 0, "text-amber-300"],
    ["ph-crosshair", "Mots testés", totalAtt, "text-white"],
    ["ph-flame", "Top 1000", hotCount, "text-orange-400"],
    ["ph-meteor", "Top 10", p.top10Found || 0, "text-red-400"],
    ["ph-chart-polar", "Précision", `${totalAtt > 0 ? Math.round((hotCount / totalAtt) * 100) : 0}%`, "text-sky-400"],
    ["ph-lightning", "Points", p.points || 0, "text-amber-400"]
  ];
  $("profileStatsGrid").innerHTML = cards.map(([ic, lbl, val, col]) => `
    <div class="bg-slate-800/40 border border-slate-800 rounded-xl p-2.5 text-center">
      <span class="text-[10px] text-slate-400 flex items-center justify-center gap-1"><i class="ph-duotone ${ic} ${col} text-xs"></i>${lbl}</span>
      <strong class="font-mono-num text-base font-extrabold ${col} block mt-0.5">${val}</strong>
    </div>`).join("");

  $("modalLeaderboardList").innerHTML = listSource.map((pl, i) => {
    const plLvl = getLevelInfo(pl.xp || 0);
    const rankColors = ["text-amber-400", "text-slate-300", "text-amber-600"];
    const rankBadge = i < 3 ? `<i class="ph-fill ph-medal text-sm ${rankColors[i]}"></i>` : `<span class="text-xs font-mono-num text-slate-500">${i + 1}.</span>`;
    return `
      <div class="flex items-center justify-between px-3 py-2 rounded-xl border transition ${pl.pseudo === p.pseudo ? 'bg-sky-950/40 border-sky-500/50' : 'bg-slate-800/40 border-slate-800'}">
        <div class="flex items-center gap-2.5 min-w-0">
          <span class="w-4 text-center flex justify-center">${rankBadge}</span>
          <span class="text-[10px] font-extrabold bg-indigo-500/20 text-indigo-300 border border-indigo-500/30 px-1.5 py-0.5 rounded">Niv.${plLvl.level}</span>
          <div class="min-w-0">
            <span class="font-bold text-xs text-white truncate block">${escapeHTML(pl.pseudo)}</span>
            <span class="text-[10px] text-slate-400 flex items-center gap-1"><i class="ph-duotone ${plLvl.icon} ${plLvl.color}"></i>${plLvl.title} • ${pl.wins || 0} vict.</span>
          </div>
        </div>
        <div class="text-right shrink-0 font-mono-num">
          <div class="text-xs font-extrabold text-amber-400">${pl.points || 0} ⚡</div>
          <div class="text-[10px] text-sky-400">${pl.xp || 0} XP</div>
        </div>
      </div>`;
  }).join("");
}

// =========================================================================
// 7. PERCÉE THERMIQUE & EXPLOSION DE FUSION SOLAIRE
// =========================================================================
function checkPowerSurge(rank, newPct) {
  if (rank === 1000 || guesses.length < 2 || roomBestScorePct <= 0) return null;
  const jump = newPct - roomBestScorePct;
  const milestone = (rank >= 991 && roomBestRank < 991) || (rank >= 900 && roomBestRank < 750);
  return (newPct > roomBestScorePct && newPct >= 45 && (jump >= 15 || milestone)) ? Math.max(15, Math.round(jump)) : null;
}

function triggerSurgeAnimation(pseudo, word, scorePct, rank, gainPct) {
  $("surgePlayerName").textContent = pseudo;
  $("surgeWord").textContent = word;
  $("surgeScore").textContent = formatPct(scorePct);
  const topLbl = getReadableTopLabel(rank);
  $("surgeBadge").textContent = topLbl ? topLbl : `+${gainPct}%`;
  toggleModal("surgeOverlay", true);
  vibrateDevice([40, 50, 90]);
  confetti?.({ particleCount: 22, spread: 55, origin: { y: 0.55 }, shapes: ["circle"], colors: ["#991b1b", "#dc2626", "#ea580c"] });
  clearTimeout(surgeHideTimer);
  surgeHideTimer = setTimeout(dismissSurgeOverlay, 6500);
}

function dismissSurgeOverlay() { clearTimeout(surgeHideTimer); toggleModal("surgeOverlay", false); }

function triggerSolarFusionExplosion() {
  const ov = $("solarExplosionOverlay"), fl = $("solarFlashBg"), ry = $("solarRaysBurst"), rg = $("solarShockwave");
  ov.classList.remove("hidden");
  fl.classList.remove("animate-solar-flash"); ry.classList.remove("animate-solar-rays"); rg.classList.remove("animate-solar-ring");
  void ov.offsetWidth;
  fl.classList.add("animate-solar-flash"); ry.classList.add("animate-solar-rays"); rg.classList.add("animate-solar-ring");
  setTimeout(() => ov.classList.add("hidden"), 1550);

  if (typeof confetti !== "function") return;
  const fire = (cnt, vel, sc) => confetti({
    particleCount: cnt, spread: 360, startVelocity: vel, decay: 0.91, gravity: 0.22, ticks: 150,
    origin: { x: 0.5, y: 0.42 }, shapes: ["star", "circle"], scalar: sc,
    colors: ["#ffffff", "#fef08a", "#facc15", "#f59e0b", "#ea580c"]
  });
  fire(70, 42, 1.35);
  setTimeout(() => fire(55, 30, 1.6), 240);
}

// =========================================================================
// 8. MULTIJOUEUR CLOUD WSS (AVEC SYNCHRO DU MODE CLASSIQUE / POP & MANGA)
// =========================================================================
let mqttClients = [];
let seenMsgIds = new Set();
let joinTimeout = null;
let joinResolved = false;

function handleRoomCodeInput(input) {
  const cleaned = input.value.replace(/[^a-zA-Z]/g, "").toUpperCase().slice(0, 4);
  input.value = cleaned;
  const valid = cleaned.length === 4;
  $("joinRoomBtn").disabled = !valid;
  $("joinRoomBtn").className = valid
    ? "w-full py-2.5 rounded-xl text-sm font-bold transition flex items-center justify-center gap-2 bg-indigo-600 hover:bg-indigo-500 text-white shadow-lg cursor-pointer"
    : "w-full py-2.5 rounded-xl text-sm font-bold transition flex items-center justify-center gap-2 bg-slate-800 text-slate-500 cursor-not-allowed opacity-60";
}

function closeOnboardingModal() {
  if (!isAuthenticated) return;
  hasStartedSession = true;
  $("closeModalBtn").classList.remove("hidden");
  toggleModal("onboardingModal", false);
}
function openOnboardingModal() {
  $("modalError").textContent = "";
  if (isAuthenticated) {
    updateLobbyHeaderUI();
    $("authView").classList.add("hidden");
    $("lobbyView").classList.remove("hidden");
  }
  if (hasStartedSession) $("closeModalBtn").classList.remove("hidden");
  toggleModal("onboardingModal", true);
}

function disconnectMultiplayer() {
  clearTimeout(joinTimeout);
  mqttClients.forEach(c => { try { c.end(true); } catch (_) {} });
  mqttClients = [];
  players = { [myId]: players[myId] };
  renderLeaderboard();
}

function connectToRoomBrokers(code, onFirstConnected) {
  let firstFired = false;
  const stateTopic = `${TOPIC_ROOT}${code}/state`;
  const eventsTopic = `${TOPIC_ROOT}${code}/events`;

  WSS_BROKERS.forEach(url => {
    try {
      const client = mqtt.connect(url, {
        clientId: `za_${myId}_${Math.random().toString(36).slice(2, 6)}`,
        clean: true,
        connectTimeout: 5000,
        reconnectPeriod: 2000
      });

      client.on("connect", () => {
        client.subscribe([stateTopic, eventsTopic], { qos: 1 }, () => {
          if (!firstFired) {
            firstFired = true;
            onFirstConnected?.();
          }
        });
      });

      client.on("message", (topic, message) => {
        try {
          const data = JSON.parse(message.toString());
          if (!data || !data.uid) return;
          if (data.type !== "STATE_SNAPSHOT") {
            if (seenMsgIds.has(data.uid)) return;
            seenMsgIds.add(data.uid);
            if (seenMsgIds.size > 400) seenMsgIds.delete(seenMsgIds.values().next().value);
          }
          handleNetworkPayload(data);
        } catch (_) {}
      });

      mqttClients.push(client);
    } catch (_) {}
  });
}

function publishRoomEvent(payload, isRetainedState = false) {
  if (!roomCode || !mqttClients.length) return;
  const packet = {
    ...payload,
    uid: payload.uid || (`m_${Date.now()}_${Math.random().toString(36).slice(2, 8)}`),
    ts: Date.now()
  };
  const topic = isRetainedState ? `${TOPIC_ROOT}${roomCode}/state` : `${TOPIC_ROOT}${roomCode}/events`;
  const raw = JSON.stringify(packet);

  seenMsgIds.add(packet.uid);
  mqttClients.forEach(c => {
    if (c.connected) c.publish(topic, raw, { qos: 1, retain: isRetainedState });
  });
}

function publishRetainedRoomSnapshot() {
  if (!roomCode) return;
  publishRoomEvent({
    type: "STATE_SNAPSHOT",
    hostId: isHost ? myId : undefined,
    gameId: currentGameId,
    gameMode: currentGameMode,
    roundNumber,
    players,
    guesses,
    roomBestScorePct,
    roomBestRank,
    roundFinished
  }, true);
}

function startSoloMode() {
  if (!isAuthenticated) return;
  disconnectMultiplayer();
  isHost = true; roomCode = null;
  $("roomCodePill").classList.add("hidden");
  closeOnboardingModal();
  updateLiveTicker(`Mode Solo (${MODE_CONFIG[currentGameMode].label}) • Manche #${roundNumber}`);
  showToast(`Mode Solo (${MODE_CONFIG[currentGameMode].label}) activé`, "sky");
}

function startCreateRoom() {
  if (!isAuthenticated) return;
  disconnectMultiplayer();

  isHost = true; roundNumber = 1;
  const chars = "ABCDEFGHJKLMNPQRSTUVWXYZ";
  roomCode = Array.from({ length: 4 }, () => chars[Math.floor(Math.random() * chars.length)]).join("");
  navigator.clipboard?.writeText(roomCode).catch(() => {});

  $("modalError").textContent = "Ouverture du salon...";

  connectToRoomBrokers(roomCode, () => {
    $("modalError").textContent = "";
    $("roomCodePill").classList.remove("hidden"); $("roomCodePill").classList.add("flex");
    $("headerRoomCode").textContent = roomCode;
    closeOnboardingModal();

    publishRetainedRoomSnapshot();
    navigator.clipboard?.writeText(roomCode).catch(() => {});
    addSystemFeedEvent(`Salon ${roomCode} créé (${MODE_CONFIG[currentGameMode].label})`);
    updateLiveTicker(`Salon ${roomCode} actif • Code copié !`);
    showToast(`Salon ${roomCode} créé et copié !`, "amber");
  });
}

function startJoinRoom() {
  if (!isAuthenticated) return;
  const rawCode = $("modalRoomCode").value.trim().toUpperCase();
  if (rawCode === "XXXX") {
    $("modalError").textContent = "Astuce : Cliquez 3 fois sur le logo flamme en haut à gauche !";
    return;
  }
  if (!/^[A-Z]{4}$/.test(rawCode)) return;

  disconnectMultiplayer();
  isHost = false;
  roomCode = rawCode;
  joinResolved = false;

  $("modalError").textContent = `Recherche du salon ${roomCode}...`;
  $("joinRoomBtnText").textContent = "Connexion...";
  $("joinRoomBtn").disabled = true;

  connectToRoomBrokers(roomCode, () => {
    publishRoomEvent({ type: "JOIN_REQUEST", player: players[myId] }, false);
  });

  joinTimeout = setTimeout(() => {
    if (!joinResolved) {
      disconnectMultiplayer();
      roomCode = null;
      $("joinRoomBtnText").textContent = "Rejoindre le salon";
      $("joinRoomBtn").disabled = false;
      $("modalError").textContent = `Salon "${rawCode}" introuvable. Vérifiez les 4 lettres.`;
    }
  }, 6000);
}

function completeJoinSuccess(snapshot) {
  if (joinResolved) return;

  const existingPlayers = Object.values(snapshot.players || {});
  const duplicateInRoom = existingPlayers.find(p => p.id !== myId && p.pseudo.toLowerCase() === myPseudo.toLowerCase());
  if (duplicateInRoom) {
    clearTimeout(joinTimeout);
    disconnectMultiplayer();
    roomCode = null;
    $("joinRoomBtnText").textContent = "Rejoindre le salon";
    $("joinRoomBtn").disabled = false;
    $("modalError").textContent = `Le compte "${myPseudo}" est déjà présent dans ce salon !`;
    return;
  }

  joinResolved = true;
  clearTimeout(joinTimeout);

  $("modalError").textContent = "";
  $("joinRoomBtnText").textContent = "Rejoindre le salon";
  $("roomCodePill").classList.remove("hidden"); $("roomCodePill").classList.add("flex");
  $("headerRoomCode").textContent = roomCode;
  closeOnboardingModal();

  const me = players[myId];
  players = { ...(snapshot.players || {}), [myId]: me };
  roomBestScorePct = snapshot.roomBestScorePct || 0;
  roomBestRank = snapshot.roomBestRank || 0;
  roundFinished = !!snapshot.roundFinished;

  const roomMode = snapshot.gameMode || "classic";
  loadGame(snapshot.gameId || currentGameId, snapshot.roundNumber || 1, snapshot.guesses || [], roomMode);
  renderLeaderboard();

  publishRoomEvent({ type: "PLAYER_JOINED", player: me }, false);
  publishRetainedRoomSnapshot();
  showToast(`Connecté au salon ${roomCode} !`, "sky");
}

function handleNetworkPayload(data) {
  if (data.type === "STATE_SNAPSHOT") {
    if (data.ts && (Date.now() - data.ts > 12 * 3600 * 1000)) return;
    if (!isHost && !joinResolved) {
      completeJoinSuccess(data);
      return;
    }
    if (data.players) {
      Object.entries(data.players).forEach(([id, pl]) => { if (id !== myId) players[id] = pl; });
      renderLeaderboard();
    }
    return;
  }

  if (data.type === "JOIN_REQUEST" && data.player) {
    if (data.player.id !== myId && (isHost || joinResolved)) {
      publishRetainedRoomSnapshot();
    }
    return;
  }

  if (data.type === "PLAYER_JOINED" && data.player) {
    if (data.player.id !== myId) {
      players[data.player.id] = {
        ...data.player,
        pseudo: String(data.player.pseudo || "Pierre").slice(0, 16),
        bestScorePct: players[data.player.id]?.bestScorePct || 0,
        bestRank: players[data.player.id]?.bestRank || 0,
        attempts: players[data.player.id]?.attempts || 0
      };
      const joinMsg = `${players[data.player.id].pseudo} a rejoint le salon`;
      addSystemFeedEvent(joinMsg);
      updateLiveTicker(joinMsg);
      renderLeaderboard();
      if (isHost) publishRetainedRoomSnapshot();
    }
    return;
  }

  if (data.type === "SHARED_GUESS" && data.playerId !== myId) {
    applySharedGuess(data, false);
    return;
  }

  if (data.type === "NEW_ROUND" && data.senderId !== myId) {
    if (data.players) {
      Object.entries(data.players).forEach(([id, pl]) => { if (id !== myId) players[id] = pl; });
    }
    loadGame(data.gameId, data.roundNumber, [], data.gameMode || currentGameMode);
    renderLeaderboard();
    return;
  }

  if (data.type === "ROUND_GIVEN_UP" && data.senderId !== myId) {
    roundFinished = true;
    updateHintButtonUI();
    showVictoryBanner("Abandon", data.secretWord, guesses.length, true);
    addSystemFeedEvent(`Mot révélé : ${data.secretWord.toUpperCase()}`);
    updateLiveTicker(`Réponse : ${data.secretWord.toUpperCase()}`);
  }
}

const copyRoomCode = () => { if (roomCode) { navigator.clipboard.writeText(roomCode); showToast(`Code "${roomCode}" copié !`, "sky"); } };

// =========================================================================
// 9. CHARGEMENT DE MANCHE (CLASSIQUE OU POP & MANGA) & VALIDATION DES MOTS
// =========================================================================
async function loadGame(gameId, displayRound = roundNumber, initialGuesses = [], mode = currentGameMode) {
  const seq = ++currentLoadSeq;
  if (mode && MODE_CONFIG[mode]) {
    currentGameMode = mode;
    localStorage.setItem("zeroabsolu_mode", mode);
  }
  updateModeUI(currentGameMode);

  const cfg = MODE_CONFIG[currentGameMode] || MODE_CONFIG.classic;
  currentGameId = gameId;
  roundNumber = displayRound;
  guesses = [...initialGuesses];
  roundFinished = guesses.some(g => g.isWin || g.rank === 1000);
  roomBestScorePct = guesses.reduce((max, g) => Math.max(max, g.scorePct || 0), 0);
  roomBestRank = guesses.reduce((max, g) => Math.max(max, g.rank || 0), 0);

  feedEvents = [];
  renderFeed();
  dismissSurgeOverlay();

  if (initialGuesses.length === 0) {
    Object.values(players).forEach(p => { p.bestScorePct = 0; p.bestRank = 0; p.attempts = 0; });
  }

  $("roundBadge").textContent = `#${roundNumber}`;
  toggleModal("lastGuessBox", false);
  toggleModal("victoryBanner", false);
  updateStatsUI(); updateHintButtonUI(); renderLeaderboard();

  $("guessesList").innerHTML = `<div class="text-slate-400 text-xs text-center my-auto py-8 flex flex-col items-center gap-2"><div class="w-4 h-4 border-2 border-sky-500 border-t-transparent rounded-full animate-spin"></div><span>Manche #${roundNumber} (${cfg.label})...</span></div>`;

  let dict = FALLBACK_WORDS;
  try {
    const res = await fetch(`${cfg.folder}/partie_${gameId}.json`);
    if (res.ok) dict = (await res.json()).words;
  } catch (_) {}

  if (seq !== currentLoadSeq) return;

  gameDictionary = dict;
  buildAccentInsensitiveIndex();

  if (guesses.length > 0) {
    renderGuesses();
    updateStatsUI();
  } else {
    $("guessesList").innerHTML = `<p class="text-slate-500 text-xs text-center my-auto py-8">Manche #${roundNumber} (${cfg.label}) prête • Montez jusqu'à 100% !</p>`;
  }

  addSystemFeedEvent(`Manche #${roundNumber} lancée (${cfg.label})`);
  updateLiveTicker(roomCode ? `Salon ${roomCode} (${cfg.label}) • Manche #${roundNumber}` : `Manche #${roundNumber} (${cfg.label}) en cours`);
}

function handleGuess(e) {
  e.preventDefault();
  const input = $("wordInput"), rawText = input.value.trim();
  if (!rawText) return;

  if (rawText.toUpperCase() === "XXXX") {
    showToast("Code XXXX actif : cliquez 3 fois sur le logo flamme en haut à gauche !", "amber");
    return;
  }

  const resolvedWord = resolveWordInDictionary(rawText);
  if (!resolvedWord) {
    vibrateDevice(40); triggerInputShake($("guessForm"));
    return showToast(`« ${rawText.toLowerCase()} » inconnu`, "rose");
  }

  const existing = guesses.find(g => g.word === resolvedWord);
  if (existing) {
    input.value = ""; vibrateDevice([30, 50, 30]); triggerInputShake($("guessForm"));
    const who = existing.finderId === myId ? "vous" : existing.finderPseudo;
    showToast(`« ${existing.word} » déjà trouvé par ${who} (#${existing.num})`, "rose");
    updateRecentWordBoxVisibility(existing, false);
    highlightExistingWordRow(existing.word);
    return;
  }

  input.value = "";
  const entry = gameDictionary[resolvedWord];
  const temp = Array.isArray(entry) ? entry[0] : entry;
  const rank = Array.isArray(entry) ? entry[1] : null;
  const isWin = rank === 1000, isTop10 = rank >= 991 && rank < 1000;
  const scorePct = computeUnifiedScorePct(temp, rank);

  const glowCls = scorePct >= 90 ? "input-glow-hot" : scorePct >= 40 ? "input-glow-warm" : "input-glow-cold";
  input.classList.add(glowCls); setTimeout(() => input.classList.remove(glowCls), 420);

  const surgeGain = checkPowerSurge(rank, scorePct);

  let pointsEarned = 0, xpEarned = 2, isNewRecord = false;

  if (!roundFinished) {
    if (isWin) {
      pointsEarned += 20 + (guesses.length < 25 ? 5 : 0);
      xpEarned = 45;
    } else if (isTop10) {
      pointsEarned += 10;
      xpEarned = 25;
    } else if (rank >= 900) {
      pointsEarned += 5;
      xpEarned = 12;
    } else if (rank !== null) {
      pointsEarned += 2;
      xpEarned = 5;
    }

    if (scorePct > roomBestScorePct && rank !== null && !isWin) {
      isNewRecord = true;
      pointsEarned += 3;
      xpEarned += 5;
    }
  }

  const me = players[myId], prevLevel = getLevelInfo(me.xp).level;
  me.attempts = (me.attempts || 0) + 1;
  me.totalAttempts = (me.totalAttempts || 0) + 1;
  if (rank !== null) me.hotWordsFound = (me.hotWordsFound || 0) + 1;
  if (isTop10 || isWin) me.top10Found = (me.top10Found || 0) + 1;
  me.points += pointsEarned;
  me.xp = (me.xp || 0) + xpEarned;
  if (scorePct > (me.bestScorePct || 0)) me.bestScorePct = scorePct;
  if (rank && rank > me.bestRank) me.bestRank = rank;
  if (isWin && !roundFinished) me.wins += 1;

  const newLvl = getLevelInfo(me.xp);
  if (newLvl.level > prevLevel) showLevelUpBanner(newLvl);

  saveLocalProgress();
  syncProfileToSupabase();
  updateHintButtonUI();

  const payload = {
    type: "SHARED_GUESS", playerId: myId, pseudo: me.pseudo, word: resolvedWord,
    temp, rank, scorePct, isWin, isTop10, isNewRecord, surgeGain, pointsEarned,
    totalPoints: me.points, totalXp: me.xp, totalWins: me.wins,
    totalAttempts: me.totalAttempts, hotWordsFound: me.hotWordsFound, top10Found: me.top10Found,
    bestScorePct: me.bestScorePct, bestRank: me.bestRank, playerAttempts: me.attempts
  };

  applySharedGuess(payload, true);
  publishRoomEvent(payload, false);
  publishRetainedRoomSnapshot();
}

function applySharedGuess(data, isLocal) {
  if (guesses.some(g => g.word === data.word)) return;
  const scorePct = data.scorePct ?? computeUnifiedScorePct(data.temp, data.rank);

  players[data.playerId] = {
    ...(players[data.playerId] || {}),
    id: data.playerId, pseudo: data.pseudo, points: data.totalPoints,
    xp: data.totalXp ?? data.totalPoints, wins: data.totalWins,
    totalAttempts: data.totalAttempts ?? data.playerAttempts,
    hotWordsFound: data.hotWordsFound ?? 0, top10Found: data.top10Found ?? 0,
    bestScorePct: data.bestScorePct ?? scorePct, bestRank: data.bestRank, attempts: data.playerAttempts
  };

  if (scorePct > roomBestScorePct) roomBestScorePct = scorePct;
  if (data.rank && data.rank > roomBestRank) roomBestRank = data.rank;

  const guessObj = {
    num: guesses.length + 1, word: data.word, temp: data.temp, rank: data.rank,
    scorePct, isWin: data.isWin, isTop10: data.isTop10, finderId: data.playerId, finderPseudo: data.pseudo
  };
  guesses.push(guessObj);
  guesses.sort((a, b) => (b.scorePct - a.scorePct) || (b.temp - a.temp));

  updateRecentWordBoxVisibility(guessObj, true);
  renderGuesses(data.word); updateStatsUI(); renderLeaderboard(); resetStatsIdleTimer();
  addWordFeedEvent(guessObj, data.surgeGain, data.isNewRecord);

  if (data.surgeGain) {
    triggerSurgeAnimation(data.pseudo, data.word, scorePct, data.rank, data.surgeGain);
    updateLiveTicker(`${data.pseudo} : ${data.word.toUpperCase()} (${formatPct(scorePct)})`);
  } else if (data.isTop10 && isLocal) {
    showToast(`${getReadableTopLabel(data.rank)} (${formatPct(scorePct)}) !`, "amber");
  }

  if (data.isWin) {
    roundFinished = true; updateHintButtonUI();
    triggerSolarFusionExplosion();
    showVictoryBanner(data.pseudo, data.word, guesses.length, false);
    updateLiveTicker(`${data.pseudo} a trouvé ${data.word.toUpperCase()} (100%) !`);
  } else if (data.isNewRecord && !data.surgeGain) {
    updateLiveTicker(`Record par ${data.pseudo} : ${data.word} • ${formatPct(scorePct)}`);
  }
}

function updateRecentWordBoxVisibility(guessObj, animateBar = true) {
  const posIndex = guesses.findIndex(g => g.word === guessObj.word);
  if (posIndex >= 7) {
    toggleModal("lastGuessBox", true);
    $("lastGuessRankPos").textContent = `${posIndex + 1}e / ${guesses.length}`;
    $("lastGuessContent").innerHTML = renderRowHTML(guessObj, animateBar);
    if (animateBar) animateNewWordBars();
  } else {
    toggleModal("lastGuessBox", false);
    $("guessesList").scrollTop = 0;
  }
}

// =========================================================================
// 10. INDICE (35 PTS) & CONFIRMATIONS D'ABANDON / MANCHE SUIVANTE
// =========================================================================
function useHint() {
  if (roundFinished) return showToast("Manche terminée : passez à la suivante !", "amber");
  const me = players[myId];
  if (!me || me.points < HINT_COST) {
    vibrateDevice(50); triggerInputShake($("hintBtn"));
    return showToast(`Il manque ${HINT_COST - (me?.points || 0)} ⚡ (Coût : ${HINT_COST} ⚡)`, "rose");
  }
  const targetRank = roomBestRank > 0 ? Math.min(998, Math.floor((roomBestRank + 1000) / 2)) : 600;
  const guessedSet = new Set(guesses.map(g => g.word));
  let bestCandidate = null, minDiff = 9999;

  for (const [w, val] of Object.entries(gameDictionary)) {
    if (Array.isArray(val) && val[1] < 1000 && !guessedSet.has(w)) {
      const diff = Math.abs(val[1] - targetRank);
      if (diff < minDiff) { minDiff = diff; bestCandidate = w; }
    }
  }
  if (!bestCandidate) return;
  me.points -= HINT_COST;
  saveLocalProgress();
  syncProfileToSupabase();
  updateHintButtonUI();
  $("wordInput").value = bestCandidate;
  showToast(`Indice débloqué (-${HINT_COST} ⚡) : « ${bestCandidate} »`, "amber");
  handleGuess(new Event("submit"));
}

function askGiveUpRound() {
  if (roundFinished) return showToast("La manche est déjà terminée !", "amber");
  if (roomCode && !isHost) return showToast("Seul l'hôte peut révéler le mot.", "amber");
  openConfirmModal({
    icon: "ph-flag-banner",
    colorCls: "bg-rose-500/15 border-rose-500/30 text-rose-400",
    title: "Révéler le mot secret ?",
    desc: "Cette action terminera la manche en cours et affichera la réponse pour tout le salon.",
    btnText: "Oui, révéler",
    onConfirm: executeGiveUpRound
  });
}

function executeGiveUpRound() {
  const secret = Object.entries(gameDictionary).find(([, v]) => Array.isArray(v) && v[1] === 1000)?.[0] || "inconnu";
  roundFinished = true; updateHintButtonUI();
  showVictoryBanner("Abandon", secret, guesses.length, true);
  addSystemFeedEvent(`Mot révélé : ${secret.toUpperCase()}`);
  updateLiveTicker(`Réponse : ${secret.toUpperCase()}`);
  if (roomCode && isHost) {
    publishRoomEvent({ type: "ROUND_GIVEN_UP", senderId: myId, secretWord: secret }, false);
    publishRetainedRoomSnapshot();
  }
}

function askNextGame() {
  if (roomCode && !isHost) return showToast("Seul l'hôte peut changer de manche.", "amber");
  if (roundFinished) return executeNextGame();
  openConfirmModal({
    icon: "ph-skip-forward-circle",
    colorCls: "bg-sky-500/15 border-sky-500/30 text-sky-400",
    title: "Passer à la manche suivante ?",
    desc: "Le mot actuel n'a pas encore été trouvé. Voulez-vous lancer un nouveau mot ?",
    btnText: "Oui, passer",
    onConfirm: executeNextGame
  });
}

function executeNextGame() {
  if (roomCode && !isHost) return showToast("Seul l'hôte peut changer de manche.", "amber");
  const nextId = pickUnplayedGameId(currentGameMode), nextRound = roundNumber + 1;
  loadGame(nextId, nextRound, [], currentGameMode);
  if (roomCode && isHost) {
    publishRoomEvent({ type: "NEW_ROUND", senderId: myId, gameId: nextId, roundNumber: nextRound, gameMode: currentGameMode, players }, false);
    publishRetainedRoomSnapshot();
  }
}

// =========================================================================
// 11. RENDU UI FACTORISÉ
// =========================================================================
function triggerInputShake(el) { if (el) { el.classList.remove("animate-shake"); void el.offsetWidth; el.classList.add("animate-shake"); } }

function highlightExistingWordRow(word) {
  const row = document.querySelector(`#guessesList [data-word="${CSS.escape(word)}"]`);
  if (row) { row.scrollIntoView({ behavior: "smooth", block: "nearest" }); row.classList.remove("animate-duplicate"); void row.offsetWidth; row.classList.add("animate-duplicate"); }
}

function showVictoryBanner(winner, secretWord, total, isGiveUp = false) {
  toggleModal("victoryBanner", true);
  $("victoryTitle").textContent = `Réponse : ${secretWord.toUpperCase()} (100%)`;
  $("victorySub").textContent = isGiveUp ? "Manche révélée" : `Fusion atteinte par ${winner} (${total} mots)`;
}

function renderRowHTML(g, isNewWord = false) {
  const targetClip = (100 - Math.max(4, Math.min(100, g.scorePct))).toFixed(1);
  const initClip = isNewWord ? "100" : targetClip;
  const tv = getTierVisuals(g);
  const authorCol = g.finderId === myId ? "text-sky-300" : "text-indigo-300";

  return `
    <div data-word="${escapeHTML(g.word)}" class="rounded-xl px-2.5 py-1.5 border ${tv.cardCls} ${isNewWord ? 'animate-word-entry' : ''} flex flex-col gap-1 transition-all shrink-0">
      <div class="flex justify-between items-center text-xs gap-2">
        <div class="flex items-center gap-1.5 min-w-0">
          <span class="text-slate-400 font-mono-num text-[10px]">#${g.num}</span>
          <strong class="capitalize truncate ${tv.wordCls}">${escapeHTML(g.word)}</strong>
          <span class="text-[10px] ${authorCol} truncate max-w-[75px]">• ${escapeHTML(g.finderPseudo || "Joueur")}</span>
        </div>
        <div class="flex items-center gap-1.5 shrink-0">
          ${tv.badgeHTML}
          <span class="font-mono-num font-extrabold text-xs ${tv.pctCls} ${isNewWord ? 'pct-counter-anim' : ''}" data-target-pct="${g.scorePct}">
            ${isNewWord ? '0.0%' : formatPct(g.scorePct)}
          </span>
        </div>
      </div>
      <div class="w-full bg-slate-950 h-1.5 rounded-full overflow-hidden">
        <div class="w-full h-full ${tv.barCls} thermal-bar-fill transition-[clip-path] duration-[440ms] ease-out"
             data-target-clip="${targetClip}" style="clip-path: inset(0 ${initClip}% 0 0 round 9999px);"></div>
      </div>
    </div>`;
}

function animateNewWordBars() {
  requestAnimationFrame(() => requestAnimationFrame(() => {
    document.querySelectorAll(".thermal-bar-fill[data-target-clip]").forEach(b => {
      b.style.clipPath = `inset(0 ${b.getAttribute("data-target-clip")}% 0 0 round 9999px)`;
    });
    document.querySelectorAll(".pct-counter-anim[data-target-pct]").forEach(el => {
      const target = parseFloat(el.getAttribute("data-target-pct")) || 0;
      el.classList.remove("pct-counter-anim");
      const t0 = performance.now();
      const step = now => {
        const p = Math.min(1, (now - t0) / 400);
        const cur = target * (1 - Math.pow(1 - p, 3));
        el.textContent = target >= 100 && p === 1 ? "100%" : `${cur.toFixed(1)}%`;
        if (p < 1) requestAnimationFrame(step);
      };
      requestAnimationFrame(step);
    });
  }));
}

function renderGuesses(latestWord = "") {
  $("guessesList").innerHTML = guesses.map(g => renderRowHTML(g, g.word === latestWord)).join("");
  if (latestWord) animateNewWordBars();
}

function updateStatsUI() {
  const total = guesses.length, bestStr = roomBestScorePct > 0 ? formatPct(roomBestScorePct) : "0%", topCnt = guesses.filter(g => g.rank !== null).length;
  $("statAttempts").textContent = $("mobileAttemptCount").textContent = $("miniAttempts").textContent = total;
  $("statBestScore").textContent = $("miniBestScore").textContent = bestStr;
  $("statTopWords").textContent = $("miniTopWords").textContent = topCnt;
}

function updateLiveTicker(msg) {
  const el = $("liveTickerText"); el.textContent = msg;
  el.className = (msg.length > 34 && window.innerWidth < 640) ? "text-slate-300 font-medium text-[11px] ticker-scroll" : "text-slate-300 font-medium text-[11px] block truncate";
}

function renderLeaderboard() {
  const all = Object.values(players);
  const sorted = [...all].sort((a, b) => (b.points - a.points) || (b.wins - a.wins));
  const leader = [...all].sort((a, b) => (b.bestScorePct || 0) - (a.bestScorePct || 0))[0];

  $("liveLeaderBadge").innerHTML = (leader && leader.bestScorePct > 0)
    ? `<i class="ph-fill ph-crown text-amber-400 text-xs"></i><span>${escapeHTML(leader.pseudo)} (${formatPct(leader.bestScorePct)})</span>`
    : `<i class="ph-fill ph-crown text-amber-400 text-xs"></i><span>${escapeHTML(sorted[0]?.pseudo || "--")}</span>`;

  const medalColors = ["text-amber-400", "text-slate-300", "text-amber-600"];

  $("leaderboardList").innerHTML = sorted.map((p, i) => {
    const isMe = p.id === myId, lvl = getLevelInfo(p.xp || 0);
    const medalHTML = i < 3 ? `<i class="ph-fill ph-medal text-sm ${medalColors[i]}"></i>` : `<span class="text-xs font-mono-num text-slate-500">${i + 1}.</span>`;
    const bestInfo = p.bestRank ? `${getReadableTopLabel(p.bestRank)} (${formatPct(p.bestScorePct)})` : p.bestScorePct > 0 ? formatPct(p.bestScorePct) : "--";
    return `
      <div onclick="openStatsModal('${escapeHTML(p.id)}')" class="cursor-pointer flex items-center justify-between px-2.5 py-1.5 rounded-xl border transition hover:border-sky-500/50 ${isMe ? 'bg-sky-950/30 border-sky-500/40' : 'bg-slate-800/40 border-slate-800'}">
        <div class="flex items-center gap-2 min-w-0">
          <span class="w-4 flex justify-center">${medalHTML}</span>
          <span class="text-[10px] font-extrabold bg-slate-800 text-sky-300 border border-slate-700 px-1.5 py-0.2 rounded">N${lvl.level}</span>
          <div class="min-w-0">
            <span class="font-bold text-xs text-white truncate block">${escapeHTML(p.pseudo)}</span>
            <span class="text-[10px] text-slate-400">${bestInfo} • ${p.attempts || 0} essais</span>
          </div>
        </div>
        <div class="text-right shrink-0">
          <div class="font-mono-num text-xs font-extrabold text-amber-400 flex items-center justify-end gap-0.5"><i class="ph-fill ph-lightning text-[10px]"></i>${p.points}</div>
          <div class="text-[10px] text-slate-400 flex items-center justify-end gap-0.5"><i class="ph-fill ph-sun-dim text-amber-300 text-[10px]"></i>${p.wins}</div>
        </div>
      </div>`;
  }).join("");

  if (!$("statsModal").classList.contains("hidden")) renderStatsModalContent();
}

function toggleFeedFilter() {
  feedOnlyHot = !feedOnlyHot;
  $("feedFilterBtn").innerHTML = feedOnlyHot
    ? `<i class="ph-duotone ph-list-bullets text-xs"></i><span>Tout afficher</span>`
    : `<i class="ph-duotone ph-fire text-xs"></i><span>Chauds seuls</span>`;
  $("feedFilterBtn").className = feedOnlyHot
    ? "text-[10px] font-bold px-2 py-0.5 rounded-md bg-sky-500/20 text-sky-300 border border-sky-500/40 transition flex items-center gap-1"
    : "text-[10px] font-semibold px-2 py-0.5 rounded-md bg-slate-800 text-amber-300 hover:bg-slate-700 border border-slate-700 transition flex items-center gap-1";
  renderFeed();
}

function addWordFeedEvent(g, surgeGain, isNewRecord) {
  const isHot = g.isWin || g.rank !== null || surgeGain || isNewRecord;
  feedEvents.unshift({ kind: "word", ...g, isHot });
  if (feedEvents.length > 40) feedEvents.pop();
  renderFeed();
  if (isHot && $("socialSection").classList.contains("hidden")) $("unreadDot").classList.remove("hidden");
}

function addSystemFeedEvent(text) {
  feedEvents.unshift({ kind: "system", text, isHot: true });
  if (feedEvents.length > 40) feedEvents.pop();
  renderFeed();
}

function renderFeed() {
  const filtered = feedOnlyHot ? feedEvents.filter(e => e.isHot) : feedEvents;
  if (!filtered.length) return $("liveFeed").innerHTML = `<p class="text-slate-500 text-[11px] text-center my-auto py-6">Aucun événement.</p>`;

  $("liveFeed").innerHTML = filtered.map(ev => {
    if (ev.kind === "system") return `<div class="px-2.5 py-1.5 rounded-lg bg-slate-800/40 border border-slate-800 text-[11px] text-sky-300 font-medium flex items-center gap-1.5"><i class="ph-duotone ph-sparkle text-xs"></i><span>${escapeHTML(ev.text)}</span></div>`;
    const tv = getTierVisuals(ev);
    return `
      <div class="px-2.5 py-1.5 rounded-lg border ${tv.feedRowCls} flex items-center justify-between gap-2 text-[11px]">
        <div class="flex items-center gap-1.5 min-w-0">
          <span class="text-slate-400 truncate max-w-[70px]">${escapeHTML(ev.finderPseudo)}</span>
          <strong class="text-slate-100 capitalize truncate">${escapeHTML(ev.word)}</strong>
        </div>
        <div class="flex items-center gap-1.5 font-mono-num shrink-0">
          ${tv.badgeHTML}
          <span class="font-bold text-slate-200">${formatPct(ev.scorePct)}</span>
        </div>
      </div>`;
  }).join("");
}

function showToast(msg, color = "sky") {
  const colors = { sky: "bg-sky-950/95 border-sky-500/50 text-sky-100", amber: "bg-amber-950/95 border-amber-500/60 text-amber-100", rose: "bg-rose-950/95 border-rose-500/60 text-rose-100" };
  const t = document.createElement("div");
  t.className = `pointer-events-auto cursor-pointer px-3.5 py-2 rounded-xl border shadow-xl backdrop-blur-md text-xs font-semibold text-center animate-pop ${colors[color] || colors.sky}`;
  t.textContent = msg; t.onclick = () => t.remove();
  $("toastContainer").appendChild(t);
  setTimeout(() => { if (t.parentElement) { t.style.opacity = "0"; t.style.transition = "opacity 0.25s"; setTimeout(() => t.remove(), 250); } }, 3500);
}

function switchMobileTab(tab) {
  const isGame = tab === "game";
  $("gameSection").classList.toggle("hidden", !isGame);
  $("socialSection").classList.toggle("hidden", isGame);
  $("socialSection").classList.toggle("flex", !isGame);
  if (!isGame) $("unreadDot").classList.add("hidden");
  $("tabGameBtn").className = `py-1 rounded-lg transition flex items-center justify-center gap-1.5 ${isGame ? 'bg-slate-800 text-white' : 'text-slate-400'}`;
  $("tabSocialBtn").className = `py-1 rounded-lg transition flex items-center justify-center gap-1.5 relative ${!isGame ? 'bg-slate-800 text-white' : 'text-slate-400'}`;
}