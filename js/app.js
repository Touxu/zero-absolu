// =========================================================================
// ZÉROABSOLU v1.3 — CONTRÔLEUR PRINCIPAL (ES MODULE)
// =========================================================================

import {
  APP_VERSION, APP_EDITION, MODE_CONFIG, HINT_COST, FALLBACK_WORDS,
  $, escapeHTML, formatPct, vibrateDevice, getReadableTopLabel, toggleModal
} from "./constants.js";

import { state } from "./state.js";

import {
  ensureCatalogueLoaded, pickUnplayedGameId, getLevelInfo,
  computeUnifiedScorePct, buildAccentInsensitiveIndex,
  resolveWordInDictionary, checkPowerSurge
} from "./engine.js";

import {
  sbClient, switchAuthMode, togglePasswordVisibility,
  handleAuthSubmit, applyCloudProfileToSelf, logoutAccount,
  syncProfileToSupabase, fetchGlobalLeaderboard, switchLeaderboardScope,
  loginAsGuest, generateGuestPseudo
} from "./auth.js";

import {
  handleRoomCodeInput, disconnectMultiplayer, connectToRoomBrokers,
  publishRoomEvent, publishRetainedRoomSnapshot, startSoloMode,
  startCreateRoom, startJoinRoom, copyRoomCode
} from "./multiplayer.js";

import {
  triggerInputShake, highlightExistingWordRow, showVictoryBanner,
  renderRowHTML, animateNewWordBars, renderGuesses,
  updateRecentWordBoxVisibility, updateStatsUI, updateLiveTicker,
  renderLeaderboard, toggleFeedFilter, addWordFeedEvent, addSystemFeedEvent,
  renderFeed, showToast, switchMobileTab, syncMobileViewport,
  resetStatsIdleTimer, toggleStatsMinimized, setStatsMinimized,
  showLevelUpBanner, triggerSurgeAnimation, dismissSurgeOverlay,
  triggerSolarFusionExplosion, openStatsModal, toggleGradesView,
  renderStatsModalContent, openWelcomeModal, closeWelcomeModal,
  openTutorialModal, closeTutorialModal, stepTutorial, updateTutorialCarousel,
  goToTutorialSlide, openDailyArchiveModal, closeDailyArchiveModal, renderDailyArchiveContent,
  openOnboardingModal, closeOnboardingModal, updateLobbyHeaderUI,
  updateHintButtonUI, openConfirmModal, closeConfirmModal,
  soundManager, triggerWordParticles, updateThermalGauge, shareGameResult,
  thermalParticles, toggleHeaderMenu, closeHeaderMenu
} from "./ui.js";

// =========================================================================
// 1. GESTION DES MODES DE JEU (CLASSIQUE VS POP & MANGA)
// =========================================================================
export function updateModeUI(mode = state.currentGameMode) {
  const isPop = mode === "pop";
  const isDaily = mode === "daily";
  const isClassic = !isPop && !isDaily;

  if ($("modeClassicBtn")) {
    $("modeClassicBtn").className = isClassic
      ? "py-2 px-2.5 rounded-xl bg-sky-500/20 border border-sky-400/50 text-sky-200 flex items-center justify-center gap-1.5 transition shadow-sm text-xs font-bold"
      : "py-2 px-2.5 rounded-xl bg-slate-900/60 border border-transparent text-slate-400 hover:text-white flex items-center justify-center gap-1.5 transition text-xs font-semibold";
  }
  if ($("modePopBtn")) {
    $("modePopBtn").className = isPop
      ? "py-2 px-2.5 rounded-xl bg-purple-500/25 border border-purple-400/60 text-purple-100 flex items-center justify-center gap-1.5 transition shadow-sm text-xs font-bold"
      : "py-2 px-2.5 rounded-xl bg-slate-900/60 border border-transparent text-slate-400 hover:text-white flex items-center justify-center gap-1.5 transition text-xs font-semibold";
  }
  if ($("modeDailyBtn")) {
    $("modeDailyBtn").className = isDaily
      ? "py-2 px-2.5 rounded-xl bg-amber-500/25 border border-amber-400/60 text-amber-100 flex items-center justify-center gap-1.5 transition shadow-sm text-xs font-bold"
      : "py-2 px-2.5 rounded-xl bg-slate-900/60 border border-transparent text-slate-400 hover:text-white flex items-center justify-center gap-1.5 transition text-xs font-semibold";
  }

  const cfg = MODE_CONFIG[mode] || MODE_CONFIG.classic;
  if ($("modeHeaderBadge")) {
    $("modeHeaderBadge").className = `cursor-pointer text-[11px] font-bold px-2 py-1 rounded-lg border flex items-center gap-1 shrink-0 ${cfg.pillCls}`;
    $("modeHeaderIcon").className = `ph-duotone ${cfg.icon} text-xs ${cfg.color}`;
    $("modeHeaderText").textContent = cfg.label;
  }
}

export function selectGameMode(mode) {
  if (!MODE_CONFIG[mode]) return;
  if (state.roomCode && !state.isHost) {
    showToast("Seul l'hôte du salon peut changer le mode de jeu.", "amber");
    return;
  }
  const changed = state.currentGameMode !== mode;
  state.currentGameMode = mode;
  localStorage.setItem("zeroabsolu_mode", mode);
  updateModeUI(mode);

  if (changed) {
    state.playedGameIds.clear();
    const nextId = pickUnplayedGameId(mode);
    const nextRound = state.hasStartedSession ? state.roundNumber + 1 : 1;
    loadGame(nextId, nextRound, [], mode);
    if (state.roomCode && state.isHost) {
      publishRoomEvent({ type: "NEW_ROUND", senderId: state.myId, gameId: nextId, roundNumber: nextRound, gameMode: mode, players: state.players }, false);
      publishRetainedRoomSnapshot();
    }
    showToast(`Mode ${MODE_CONFIG[mode].label} activé !`, "sky");
  }
}

// =========================================================================
// 2. PROGRESSION LOCALE ET JOUEUR
// =========================================================================
export function initSelfPlayer() {
  const cur = state.players[state.myId] || {};
  state.players[state.myId] = {
    id: state.myId,
    pseudo: state.myPseudo || "Joueur",
    points: cur.points ?? state.savedStats.points ?? 0,
    xp: cur.xp ?? state.savedStats.xp ?? 0,
    wins: cur.wins ?? state.savedStats.wins ?? 0,
    totalAttempts: cur.totalAttempts ?? state.savedStats.totalAttempts ?? 0,
    hotWordsFound: cur.hotWordsFound ?? state.savedStats.hotWordsFound ?? 0,
    top10Found: cur.top10Found ?? state.savedStats.top10Found ?? 0,
    bestTimeSeconds: cur.bestTimeSeconds ?? state.savedStats.bestTimeSeconds ?? null,
    totalWinTimeSeconds: cur.totalWinTimeSeconds ?? state.savedStats.totalWinTimeSeconds ?? 0,
    bestScorePct: cur.bestScorePct ?? 0,
    bestRank: cur.bestRank ?? 0,
    attempts: cur.attempts ?? 0
  };
  saveLocalProgress();
  updateHintButtonUI();
  renderLeaderboard();
}

export function saveLocalProgress() {
  const me = state.players[state.myId];
  if (!me) return;
  state.savedStats = {
    points: me.points,
    xp: me.xp,
    wins: me.wins,
    totalAttempts: me.totalAttempts,
    hotWordsFound: me.hotWordsFound,
    top10Found: me.top10Found,
    bestTimeSeconds: me.bestTimeSeconds,
    totalWinTimeSeconds: me.totalWinTimeSeconds
  };
  localStorage.setItem("zeroabsolu_profile_v2", JSON.stringify(state.savedStats));
  $("headerPoints").textContent = me.points;
  $("headerLevelBadge").textContent = `N${getLevelInfo(me.xp).level}`;
}

// =========================================================================
// 3. CHARGEMENT D'UNE MANCHE (DEPUIS LE CATALOGUE COMPRESSÉ)
// =========================================================================
export async function loadGame(gameId, displayRound = state.roundNumber, initialGuesses = [], mode = state.currentGameMode) {
  const seq = ++state.currentLoadSeq;
  if (mode && MODE_CONFIG[mode]) {
    state.currentGameMode = mode;
    localStorage.setItem("zeroabsolu_mode", mode);
  }
  updateModeUI(state.currentGameMode);

  const cfg = MODE_CONFIG[state.currentGameMode] || MODE_CONFIG.classic;
  state.currentGameId = gameId;
  state.roundNumber = displayRound;
  state.roundStartTime = Date.now();
  state.guesses = [...initialGuesses];
  state.roundFinished = state.guesses.some(g => g.isWin || g.rank === 1000);
  state.roomBestScorePct = state.guesses.reduce((max, g) => Math.max(max, g.scorePct || 0), 0);
  state.roomBestRank = state.guesses.reduce((max, g) => Math.max(max, g.rank || 0), 0);

  state.feedEvents = [];
  renderFeed();
  dismissSurgeOverlay();

  if (initialGuesses.length === 0) {
    Object.values(state.players).forEach(p => {
      p.bestScorePct = 0;
      p.bestRank = 0;
      p.attempts = 0;
    });
  }

  const roundText = typeof state.roundNumber === "number" ? `#${state.roundNumber}` : `${state.roundNumber}`;
  $("roundBadge").textContent = roundText;
  toggleModal("lastGuessBox", false);
  toggleModal("victoryBanner", false);
  updateStatsUI();
  updateHintButtonUI();
  renderLeaderboard();

  $("guessesList").innerHTML = `<div class="text-slate-400 text-xs text-center my-auto py-8 flex flex-col items-center gap-2"><div class="w-4 h-4 border-2 border-sky-500 border-t-transparent rounded-full animate-spin"></div><span>Manche #${state.roundNumber} (${cfg.label})...</span></div>`;

  let dict = FALLBACK_WORDS;
  const cat = await ensureCatalogueLoaded();
  if (seq !== state.currentLoadSeq) return;

  if (cat) {
    const isPop = state.currentGameMode === "pop";
    const maxWords = isPop ? cat.words.length : cat.classicCount;
    const topArray = isPop ? cat.popTop : cat.classicTop;
    const totalGamesInMode = Math.floor(topArray.length / 1000);
    const safeIdx = Math.max(0, Math.min(totalGamesInMode - 1, gameId - 1));
    const offset = safeIdx * 1000;

    const secretWordIdx = topArray[offset];
    const sOff = secretWordIdx * 16;
    const v8 = cat.vecs16;
    const s0=v8[sOff], s1=v8[sOff+1], s2=v8[sOff+2], s3=v8[sOff+3],
          s4=v8[sOff+4], s5=v8[sOff+5], s6=v8[sOff+6], s7=v8[sOff+7],
          s8=v8[sOff+8], s9=v8[sOff+9], s10=v8[sOff+10], s11=v8[sOff+11],
          s12=v8[sOff+12], s13=v8[sOff+13], s14=v8[sOff+14], s15=v8[sOff+15];

    const newDict = {};
    const words = cat.words;

    for (let i = 0; i < maxWords; i++) {
      const wOff = i * 16;
      const dot = s0*v8[wOff] + s1*v8[wOff+1] + s2*v8[wOff+2] + s3*v8[wOff+3] +
                  s4*v8[wOff+4] + s5*v8[wOff+5] + s6*v8[wOff+6] + s7*v8[wOff+7] +
                  s8*v8[wOff+8] + s9*v8[wOff+9] + s10*v8[wOff+10] + s11*v8[wOff+11] +
                  s12*v8[wOff+12] + s13*v8[wOff+13] + s14*v8[wOff+14] + s15*v8[wOff+15];
      newDict[words[i]] = Math.round(((dot / 16129) * 18 + 8) * 10) / 10;
    }

    for (let r = 0; r < 1000; r++) {
      const wIdx = topArray[offset + r];
      const rank = 1000 - r;
      const temp = rank === 1000 ? 100.0 : Math.round((30 + (rank / 1000) * 65) * 100) / 100;
      newDict[words[wIdx]] = [temp, rank];
    }
    dict = newDict;
  }

  state.gameDictionary = dict;
  buildAccentInsensitiveIndex();

  if (state.guesses.length > 0) {
    renderGuesses();
    updateStatsUI();
  } else {
    $("guessesList").innerHTML = `<p class="text-slate-500 text-xs text-center my-auto py-8">Manche #${state.roundNumber} (${cfg.label}) prête • Montez jusqu'à 100% !</p>`;
  }

  addSystemFeedEvent(`Manche #${state.roundNumber} lancée (${cfg.label})`);
  updateLiveTicker(state.roomCode ? `Salon ${state.roomCode} (${cfg.label}) • Manche #${state.roundNumber}` : `Manche #${state.roundNumber} (${cfg.label}) en cours`);
}

// =========================================================================
// 4. SOUMISSION D'UN MOT (GAMEPLAY PRINCIPAL)
// =========================================================================
export function handleGuess(e) {
  e.preventDefault();
  const input = $("wordInput");
  const rawText = input.value.trim();
  if (!rawText) return;

  if (rawText.toUpperCase() === "XXXX") {
    showToast("Code XXXX actif : cliquez 3 fois sur le logo flamme en haut à gauche !", "amber");
    return;
  }

  const resolvedWord = resolveWordInDictionary(rawText);
  if (!resolvedWord) {
    vibrateDevice(40);
    soundManager.ensureContext() && soundManager.playGuessSound(0);
    triggerInputShake($("guessForm"));
    return showToast(`« ${rawText.toLowerCase()} » inconnu`, "rose");
  }

  const existing = state.guesses.find(g => g.word === resolvedWord);
  if (existing) {
    input.value = "";
    vibrateDevice([30, 50, 30]);
    triggerInputShake($("guessForm"));
    const who = existing.finderId === state.myId ? "vous" : existing.finderPseudo;
    showToast(`« ${existing.word} » déjà trouvé par ${who} (#${existing.num})`, "rose");
    updateRecentWordBoxVisibility(existing, false);
    highlightExistingWordRow(existing.word);
    return;
  }

  input.value = "";
  const entry = state.gameDictionary[resolvedWord];
  const temp = Array.isArray(entry) ? entry[0] : entry;
  const rank = Array.isArray(entry) ? entry[1] : null;
  const isWin = rank === 1000;
  const isTop10 = rank >= 991 && rank < 1000;
  const scorePct = computeUnifiedScorePct(temp, rank);

  soundManager.playGuessSound(scorePct, isWin, isTop10);

  const glowCls = scorePct >= 90 ? "input-glow-hot" : scorePct >= 40 ? "input-glow-warm" : "input-glow-cold";
  input.classList.add(glowCls);
  setTimeout(() => input.classList.remove(glowCls), 420);

  const surgeGain = checkPowerSurge(rank, scorePct);

  let pointsEarned = 0;
  let xpEarned = 2;
  let isNewRecord = false;

  if (!state.roundFinished) {
    if (isWin) {
      pointsEarned += 20 + (state.guesses.length < 25 ? 5 : 0);
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

    if (scorePct > state.roomBestScorePct && rank !== null && !isWin) {
      isNewRecord = true;
      pointsEarned += 3;
      xpEarned += 5;
    }
  }

  const me = state.players[state.myId];
  const prevLevel = getLevelInfo(me.xp).level;
  me.attempts = (me.attempts || 0) + 1;
  me.totalAttempts = (me.totalAttempts || 0) + 1;
  if (rank !== null) me.hotWordsFound = (me.hotWordsFound || 0) + 1;
  if (isTop10 || isWin) me.top10Found = (me.top10Found || 0) + 1;
  me.points += pointsEarned;
  me.xp = (me.xp || 0) + xpEarned;
  if (scorePct > (me.bestScorePct || 0)) me.bestScorePct = scorePct;
  if (rank && rank > me.bestRank) me.bestRank = rank;

  let durationSeconds = null;
  if (state.roundStartTime) {
    durationSeconds = Math.max(1, Math.round((Date.now() - state.roundStartTime) / 1000));
  }

  if (isWin && !state.roundFinished) {
    me.wins += 1;
    if (durationSeconds) {
      me.totalWinTimeSeconds = (me.totalWinTimeSeconds || 0) + durationSeconds;
      if (!me.bestTimeSeconds || durationSeconds < me.bestTimeSeconds) {
        me.bestTimeSeconds = durationSeconds;
      }
    }
    if (state.currentGameMode === "daily") {
      const today = new Date();
      const dateStr = `${today.getFullYear()}-${String(today.getMonth() + 1).padStart(2, "0")}-${String(today.getDate()).padStart(2, "0")}`;
      try {
        localStorage.setItem(`zeroabsolu_daily_${dateStr}`, JSON.stringify({
          solved: true,
          timeSeconds: durationSeconds,
          attempts: me.attempts,
          date: dateStr
        }));
      } catch (_) {}
    }
  }

  const newLvl = getLevelInfo(me.xp);
  if (newLvl.level > prevLevel) showLevelUpBanner(newLvl);

  saveLocalProgress();
  syncProfileToSupabase();
  updateHintButtonUI();

  const payload = {
    type: "SHARED_GUESS",
    playerId: state.myId,
    pseudo: me.pseudo,
    word: resolvedWord,
    temp,
    rank,
    scorePct,
    isWin,
    isTop10,
    isNewRecord,
    surgeGain,
    pointsEarned,
    durationSeconds,
    totalPoints: me.points,
    totalXp: me.xp,
    totalWins: me.wins,
    totalAttempts: me.totalAttempts,
    hotWordsFound: me.hotWordsFound,
    top10Found: me.top10Found,
    bestTimeSeconds: me.bestTimeSeconds,
    totalWinTimeSeconds: me.totalWinTimeSeconds,
    bestScorePct: me.bestScorePct,
    bestRank: me.bestRank,
    playerAttempts: me.attempts
  };

  applySharedGuess(payload, true);
  publishRoomEvent(payload, false);
  publishRetainedRoomSnapshot();
}

export function applySharedGuess(data, isLocal) {
  if (state.guesses.some(g => g.word === data.word)) return;
  const scorePct = data.scorePct ?? computeUnifiedScorePct(data.temp, data.rank);

  state.players[data.playerId] = {
    ...(state.players[data.playerId] || {}),
    id: data.playerId,
    pseudo: data.pseudo,
    points: data.totalPoints,
    xp: data.totalXp ?? data.totalPoints,
    wins: data.totalWins,
    totalAttempts: data.totalAttempts ?? data.playerAttempts,
    hotWordsFound: data.hotWordsFound ?? 0,
    top10Found: data.top10Found ?? 0,
    bestTimeSeconds: data.bestTimeSeconds ?? state.players[data.playerId]?.bestTimeSeconds,
    totalWinTimeSeconds: data.totalWinTimeSeconds ?? state.players[data.playerId]?.totalWinTimeSeconds,
    bestScorePct: data.bestScorePct ?? scorePct,
    bestRank: data.bestRank,
    attempts: data.playerAttempts
  };

  if (scorePct > state.roomBestScorePct) state.roomBestScorePct = scorePct;
  if (data.rank && data.rank > state.roomBestRank) state.roomBestRank = data.rank;

  const guessObj = {
    num: state.guesses.length + 1,
    word: data.word,
    temp: data.temp,
    rank: data.rank,
    scorePct,
    isWin: data.isWin,
    isTop10: data.isTop10,
    finderId: data.playerId,
    finderPseudo: data.pseudo
  };
  state.guesses.push(guessObj);
  state.guesses.sort((a, b) => (b.scorePct - a.scorePct) || (b.temp - a.temp));

  updateRecentWordBoxVisibility(guessObj, true);
  renderGuesses(data.word);
  updateStatsUI();
  renderLeaderboard();
  resetStatsIdleTimer();
  addWordFeedEvent(guessObj, data.surgeGain, data.isNewRecord);

  // Cibler l'élément où le mot vient d'être affiché (boîte récente ou ligne du tableau)
  let wordRowEl = null;
  const recentBox = $("lastGuessBox");
  if (recentBox && !recentBox.classList.contains("hidden")) {
    wordRowEl = document.querySelector(`#lastGuessContent [data-word="${CSS.escape(data.word)}"]`);
  }
  if (!wordRowEl) {
    wordRowEl = document.querySelector(`#guessesList [data-word="${CSS.escape(data.word)}"]`);
  }
  if (!wordRowEl) {
    wordRowEl = $("guessesList") || $("guessForm");
  }

  if (data.surgeGain) {
    triggerSurgeAnimation(data.pseudo, data.word, scorePct, data.rank, data.surgeGain);
    updateLiveTicker(`${data.pseudo} : ${data.word.toUpperCase()} (${formatPct(scorePct)})`);
  } else if (data.isTop10 && isLocal) {
    showToast(`${getReadableTopLabel(data.rank)} (${formatPct(scorePct)}) !`, "amber");
  }

  if (data.isWin) {
    state.roundFinished = true;
    updateHintButtonUI();
    // Unique animation solaire déclenchée à l'endroit précis du mot secret
    triggerSolarFusionExplosion(wordRowEl);
    showVictoryBanner(data.pseudo, data.word, state.guesses.length, false, data.durationSeconds);
    updateLiveTicker(`${data.pseudo} a trouvé ${data.word.toUpperCase()} (100%) !`);
  } else {
    // Émission de particules thermiques proportionnelles au rang/température
    triggerWordParticles(wordRowEl, scorePct, false, data.rank);
    if (data.isNewRecord && !data.surgeGain) {
      updateLiveTicker(`Record par ${data.pseudo} : ${data.word} • ${formatPct(scorePct)}`);
    }
  }
}

export function playDailyArchiveGame(gameId, dateStr, isToday = false) {
  closeDailyArchiveModal();
  closeOnboardingModal();
  if (state.currentGameMode !== "daily") {
    state.currentGameMode = "daily";
    localStorage.setItem("zeroabsolu_mode", "daily");
    updateModeUI("daily");
  }
  const displayLabel = isToday ? 1 : `Défi ${dateStr}`;
  loadGame(gameId, displayLabel, [], "daily");
  showToast(isToday ? "Défi du jour lancé !" : `Défi archivé du ${dateStr} chargé !`, "amber");
}

// =========================================================================
// 5. INDICE & CONFIRMATIONS D'ABANDON / SUIVANT
// =========================================================================
export function useHint() {
  if (state.roundFinished) return showToast("Manche terminée : passez à la suivante !", "amber");
  const me = state.players[state.myId];
  if (!me || me.points < HINT_COST) {
    vibrateDevice(50);
    triggerInputShake($("hintBtn"));
    return showToast(`Il manque ${HINT_COST - (me?.points || 0)} ⚡ (Coût : ${HINT_COST} ⚡)`, "rose");
  }
  const targetRank = state.roomBestRank > 0 ? Math.min(998, Math.floor((state.roomBestRank + 1000) / 2)) : 600;
  const guessedSet = new Set(state.guesses.map(g => g.word));
  let bestCandidate = null;
  let minDiff = 9999;

  for (const [w, val] of Object.entries(state.gameDictionary)) {
    if (Array.isArray(val) && val[1] < 1000 && !guessedSet.has(w)) {
      const diff = Math.abs(val[1] - targetRank);
      if (diff < minDiff) {
        minDiff = diff;
        bestCandidate = w;
      }
    }
  }
  if (!bestCandidate) return;
  me.points -= HINT_COST;
  saveLocalProgress();
  syncProfileToSupabase();
  updateHintButtonUI();
  soundManager.playHintSound();
  $("wordInput").value = bestCandidate;
  showToast(`Indice débloqué (-${HINT_COST} ⚡) : « ${bestCandidate} »`, "amber");
  handleGuess(new Event("submit"));
}

export function askGiveUpRound() {
  if (state.roundFinished) return showToast("La manche est déjà terminée !", "amber");
  if (state.roomCode && !state.isHost) return showToast("Seul l'hôte peut révéler le mot.", "amber");
  openConfirmModal({
    icon: "ph-flag-banner",
    colorCls: "bg-rose-500/15 border-rose-500/30 text-rose-400",
    title: "Révéler le mot secret ?",
    desc: "Cette action terminera la manche en cours et affichera la réponse pour tout le salon.",
    btnText: "Oui, révéler",
    onConfirm: executeGiveUpRound
  });
}

export function executeGiveUpRound() {
  const secret = Object.entries(state.gameDictionary).find(([, v]) => Array.isArray(v) && v[1] === 1000)?.[0] || "inconnu";
  state.roundFinished = true;
  updateHintButtonUI();
  showVictoryBanner("Abandon", secret, state.guesses.length, true);
  addSystemFeedEvent(`Mot révélé : ${secret.toUpperCase()}`);
  updateLiveTicker(`Réponse : ${secret.toUpperCase()}`);
  if (state.roomCode && state.isHost) {
    publishRoomEvent({ type: "ROUND_GIVEN_UP", senderId: state.myId, secretWord: secret }, false);
    publishRetainedRoomSnapshot();
  }
}

export function askNextGame() {
  if (state.roomCode && !state.isHost) return showToast("Seul l'hôte peut changer de manche.", "amber");
  if (state.roundFinished) return executeNextGame();
  openConfirmModal({
    icon: "ph-skip-forward-circle",
    colorCls: "bg-sky-500/15 border-sky-500/30 text-sky-400",
    title: "Passer à la manche suivante ?",
    desc: "Le mot actuel n'a pas encore été trouvé. Voulez-vous lancer un nouveau mot ?",
    btnText: "Oui, passer",
    onConfirm: executeNextGame
  });
}

export function executeNextGame() {
  if (state.roomCode && !state.isHost) return showToast("Seul l'hôte peut changer de manche.", "amber");
  const nextId = pickUnplayedGameId(state.currentGameMode);
  const nextRound = state.roundNumber + 1;
  loadGame(nextId, nextRound, [], state.currentGameMode);
  if (state.roomCode && state.isHost) {
    publishRoomEvent({ type: "NEW_ROUND", senderId: state.myId, gameId: nextId, roundNumber: nextRound, gameMode: state.currentGameMode, players: state.players }, false);
    publishRetainedRoomSnapshot();
  }
}

// =========================================================================
// 6. MENU SECRET SANDBOX ("XXXX" + 3 CLICS)
// =========================================================================
export function isSecretCodeEntered() {
  const codeModal = ($("modalRoomCode")?.value || "").trim().toUpperCase();
  const codeInput = ($("wordInput")?.value || "").trim().toUpperCase();
  const codeAuth = ($("authPseudo")?.value || "").trim().toUpperCase();
  return codeModal === "XXXX" || codeInput === "XXXX" || codeAuth === "XXXX";
}

export function handleLogoSecretClick() {
  if (!isSecretCodeEntered()) return false;
  state.secretClickCount++;
  clearTimeout(state.secretClickTimer);
  state.secretClickTimer = setTimeout(() => { state.secretClickCount = 0; }, 2200);

  if (state.secretClickCount >= 3) {
    state.secretClickCount = 0;
    if ($("wordInput")?.value.trim().toUpperCase() === "XXXX") $("wordInput").value = "";
    $("debugSecretWord").textContent = "•••";
    toggleModal("debugModal", true);
    vibrateDevice([40, 60, 40]);
    return true;
  }
  return true;
}

export function handleHeaderLogoClick() {
  if (isSecretCodeEntered()) {
    handleLogoSecretClick();
    return;
  }
  openOnboardingModal();
}

export function revealSecretInDebug() {
  const secret = Object.entries(state.gameDictionary).find(([, v]) => Array.isArray(v) && v[1] === 1000)?.[0] || "inconnu";
  $("debugSecretWord").textContent = secret.toUpperCase();
}

export function debugAddPointsAndXp(pts, xp) {
  const me = state.players[state.myId];
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

export async function debugResetAllScores() {
  const me = state.players[state.myId];
  if (!me) return;
  me.points = 0; me.xp = 0; me.wins = 0; me.totalAttempts = 0; me.hotWordsFound = 0; me.top10Found = 0;
  saveLocalProgress();
  await syncProfileToSupabase();
  updateHintButtonUI();
  renderLeaderboard();
  toggleModal("debugModal", false);
  showToast("Scores et niveau remis à zéro !", "rose");
}

// =========================================================================
// 7. INITIALISATION DU MODULE SUR DOMContentLoaded
// =========================================================================
let initialScreenHeight = window.screen?.availHeight || window.innerHeight;

window.addEventListener("DOMContentLoaded", () => {
  document.title = `ZéroAbsolu — ${APP_VERSION}`;
  $("versionBadgeTop").textContent = APP_VERSION;
  $("versionBadgeFooter").textContent = `${APP_VERSION} • ${APP_EDITION}`;
  $("cloudStatusText").textContent = sbClient ? "Supabase Cloud Actif" : "Clés Supabase manquantes";
  $("cloudStatusDot").className = sbClient ? "w-1.5 h-1.5 rounded-full bg-emerald-400" : "w-1.5 h-1.5 rounded-full bg-rose-500";
  initialScreenHeight = window.screen?.availHeight || window.innerHeight;

  if (state.myPseudo) $("authPseudo").value = state.myPseudo;
  if (state.myPassword) $("authPassword").value = state.myPassword;

  soundManager.updateSoundButtonUI();
  updateModeUI(state.currentGameMode);
  initSelfPlayer();
  state.currentGameId = pickUnplayedGameId(state.currentGameMode);
  loadGame(state.currentGameId, 1, [], state.currentGameMode);
  resetStatsIdleTimer();
  updateThermalGauge(0);

  $("modalRoomCode").addEventListener("keydown", e => {
    if (e.key === "Enter" && !$("joinRoomBtn").disabled) startJoinRoom();
  });
  $("wordInput").addEventListener("focus", () => {
    if (window.innerWidth < 1024) {
      document.body.classList.add("keyboard-active");
      setTimeout(syncMobileViewport, 60);
    }
  });
  $("wordInput").addEventListener("blur", () => {
    setTimeout(() => {
      document.body.classList.remove("keyboard-active");
      syncMobileViewport();
    }, 120);
  });
  window.visualViewport?.addEventListener("resize", syncMobileViewport);
  window.visualViewport?.addEventListener("scroll", syncMobileViewport);
});

// =========================================================================
// 8. EXPOSITION SUR window POUR LES HANDLERS HTML (onclick, onsubmit, oninput)
// =========================================================================
Object.assign(window, {
  $,
  state,
  APP_VERSION,
  APP_EDITION,
  toggleModal,
  showToast,
  getLevelInfo,
  triggerInputShake,
  showLevelUpBanner,
  triggerSolarFusionExplosion,
  triggerSurgeAnimation,
  dismissSurgeOverlay,
  updateLobbyHeaderUI,
  updateHintButtonUI,
  saveLocalProgress,
  renderLeaderboard,
  renderStatsModalContent,
  updateModeUI,
  loadGame,
  applySharedGuess,
  addSystemFeedEvent,
  updateLiveTicker,
  switchAuthMode,
  togglePasswordVisibility,
  handleAuthSubmit,
  logoutAccount,
  loginAsGuest,
  generateGuestPseudo,
  toggleHeaderMenu,
  closeHeaderMenu,
  openWelcomeModal,
  closeWelcomeModal,
  openTutorialModal,
  closeTutorialModal,
  stepTutorial,
  goToTutorialSlide,
  openDailyArchiveModal,
  closeDailyArchiveModal,
  renderDailyArchiveContent,
  playDailyArchiveGame,
  switchLeaderboardScope,
  handleLogoSecretClick,
  handleHeaderLogoClick,
  revealSecretInDebug,
  debugAddPointsAndXp,
  debugResetAllScores,
  openStatsModal,
  toggleGradesView,
  openConfirmModal,
  closeConfirmModal,
  toggleStatsMinimized,
  handleRoomCodeInput,
  closeOnboardingModal,
  openOnboardingModal,
  startSoloMode,
  startCreateRoom,
  startJoinRoom,
  copyRoomCode,
  selectGameMode,
  handleGuess,
  useHint,
  askGiveUpRound,
  executeGiveUpRound,
  askNextGame,
  executeNextGame,
  toggleFeedFilter,
  switchMobileTab,
  soundManager,
  shareGameResult,
  updateThermalGauge,
  triggerWordParticles,
  thermalParticles,
  vibrateDevice
});

// Rétrocompatibilité pour les expressions inline accédant directement à myId / myPseudo / players
Object.defineProperty(window, "myId", { get: () => state.myId });
Object.defineProperty(window, "myPseudo", { get: () => state.myPseudo });
Object.defineProperty(window, "players", { get: () => state.players });
Object.defineProperty(window, "hasStartedSession", { get: () => state.hasStartedSession });
Object.defineProperty(window, "currentGameMode", { get: () => state.currentGameMode });
