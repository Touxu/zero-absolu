// =========================================================================
// MODULE UI : RENDU DOM, MODALES, ANIMATIONS & CLAVIER MOBILE
// =========================================================================
import {
  $, escapeHTML, formatPct, formatDuration, vibrateDevice, getReadableTopLabel,
  toggleModal, GRADE_TIERS, HINT_COST, MODE_CONFIG
} from "./constants.js";
import { state } from "./state.js";
import { getLevelInfo, getTierVisuals, getDailyHistory } from "./engine.js";
import { soundManager } from "./audio.js";
import { thermalParticles } from "./particles.js";

export { $, toggleModal, soundManager, thermalParticles };

let initialScreenHeight = window.innerHeight;
let pendingConfirmAction = null;

export function triggerWordParticles(targetEl, scorePct, isWin = false, rank = null) {
  const el = targetEl || $("guessForm") || document.body;
  thermalParticles.trigger(el, scorePct, isWin, rank);
}

export function updateThermalGauge(scorePct = state.roomBestScorePct) {
  const bar = $("thermalGaugeLiquid");
  const valText = $("thermalGaugeVal");
  const bulb = $("thermalGaugeBulb");
  const icon = $("thermalGaugeIcon");
  const badge = $("thermalTierBadge");
  const status = $("thermalStatusText");
  if (!bar) return;

  const pct = Math.max(0, Math.min(100, Number(scorePct) || 0));
  if (valText) valText.textContent = `${pct.toFixed(1)}%`;

  // Animation fluide de la largeur avec Motion One
  if (window.Motion?.animate) {
    window.Motion.animate(bar, { width: `${Math.max(4, pct)}%` }, { duration: 0.55, easing: "ease-out" });
  } else {
    bar.style.width = `${Math.max(4, pct)}%`;
  }

  if (pct >= 100 || (state.roundFinished && pct >= 99.95)) {
    bar.className = "h-full rounded-full transition-all duration-300 solar-fusion-bar shadow-[0_0_18px_#facc15]";
    if (bulb) {
      bulb.className = "w-8 h-8 rounded-xl bg-amber-400/25 border border-amber-300/70 text-amber-300 flex items-center justify-center text-lg shadow-[0_0_20px_#facc15] transition-all duration-500 shrink-0";
    }
    if (icon) icon.className = "ph-fill ph-sun-dim text-lg text-amber-300 animate-pulse";
    if (badge) {
      badge.textContent = "FUSION SOLAIRE 100%";
      badge.className = "text-[10px] font-extrabold px-1.5 py-0.2 rounded bg-amber-500/25 text-amber-200 border border-amber-300/60 shadow-[0_0_8px_#facc15]";
    }
    if (status) status.textContent = "Fusion thermonucléaire atteinte ! Mot secret découvert ! ☀️";
    if (valText) valText.className = "font-mono-num text-xs sm:text-sm font-extrabold text-amber-300 min-w-[3.2rem] text-right fusion-word-glow";
  } else if (pct >= 90) {
    bar.className = "h-full rounded-full transition-all duration-300 magma-lava-bar shadow-[0_0_14px_#ef4444]";
    if (bulb) {
      bulb.className = "w-8 h-8 rounded-xl bg-red-500/25 border border-red-400/60 text-red-400 flex items-center justify-center text-lg shadow-[0_0_16px_#ef4444] transition-all duration-500 shrink-0";
    }
    if (icon) icon.className = "ph-fill ph-meteor text-lg text-red-400 animate-bounce";
    if (badge) {
      badge.textContent = "MAGMA SOLAIRE (TOP 10)";
      badge.className = "text-[10px] font-extrabold px-1.5 py-0.2 rounded bg-red-500/20 text-red-300 border border-red-400/40 shadow-[0_0_8px_#ef4444]";
    }
    if (status) status.textContent = "Ébullition critique ! Vous êtes dans le Top 10 ! (90% à 99.9%)";
    if (valText) valText.className = "font-mono-num text-xs sm:text-sm font-extrabold text-red-400 min-w-[3.2rem] text-right magma-word-glow";
  } else if (pct >= 75) {
    bar.className = "h-full rounded-full transition-all duration-300 bg-gradient-to-r from-orange-500 to-amber-400 shadow-[0_0_10px_#f97316]";
    if (bulb) {
      bulb.className = "w-8 h-8 rounded-xl bg-orange-500/20 border border-orange-400/50 text-orange-400 flex items-center justify-center text-lg shadow-[0_0_12px_#f97316] transition-all duration-500 shrink-0";
    }
    if (icon) icon.className = "ph-duotone ph-fire text-lg text-orange-400";
    if (badge) {
      badge.textContent = "CHALEUR VIVE";
      badge.className = "text-[10px] font-bold px-1.5 py-0.2 rounded bg-orange-500/20 text-orange-300 border border-orange-400/30";
    }
    if (status) status.textContent = "Ça brûle ! Vous vous rapprochez du mot secret.";
    if (valText) valText.className = "font-mono-num text-xs sm:text-sm font-extrabold text-orange-400 min-w-[3.2rem] text-right";
  } else if (pct >= 40) {
    bar.className = "h-full rounded-full transition-all duration-300 bg-gradient-to-r from-indigo-500 to-purple-500 shadow-[0_0_10px_#a855f7]";
    if (bulb) {
      bulb.className = "w-8 h-8 rounded-xl bg-purple-500/20 border border-purple-400/50 text-purple-400 flex items-center justify-center text-lg shadow-[0_0_10px_#a855f7] transition-all duration-500 shrink-0";
    }
    if (icon) icon.className = "ph-duotone ph-thermometer-simple text-lg text-purple-400";
    if (badge) {
      badge.textContent = "TRACTION THERMIQUE";
      badge.className = "text-[10px] font-bold px-1.5 py-0.2 rounded bg-purple-500/20 text-purple-300 border border-purple-400/30";
    }
    if (status) status.textContent = "Réaction amorcée... Poursuivez dans cette thématique !";
    if (valText) valText.className = "font-mono-num text-xs sm:text-sm font-extrabold text-purple-300 min-w-[3.2rem] text-right";
  } else {
    bar.className = "h-full rounded-full transition-all duration-300 bg-sky-500 shadow-[0_0_8px_#0ea5e9]";
    if (bulb) {
      bulb.className = "w-8 h-8 rounded-xl bg-sky-500/20 border border-sky-400/40 text-sky-400 flex items-center justify-center text-lg shadow-[0_0_10px_rgba(14,165,233,0.3)] transition-all duration-500 shrink-0";
    }
    if (icon) icon.className = "ph-duotone ph-thermometer-cold text-lg text-sky-400";
    if (badge) {
      badge.textContent = "ZÉRO ABSOLU";
      badge.className = "text-[10px] font-bold px-1.5 py-0.2 rounded bg-sky-500/20 text-sky-300 border border-sky-400/30";
    }
    if (status) status.textContent = pct > 0 ? "Froid polaire... Cherchez une autre direction." : "Proposez un mot pour amorcer la réaction...";
    if (valText) valText.className = "font-mono-num text-xs sm:text-sm font-extrabold text-sky-300 min-w-[3.2rem] text-right";
  }
}

export function shareGameResult() {
  const me = state.players[state.myId] || {};
  const cfg = MODE_CONFIG[state.currentGameMode] || MODE_CONFIG.classic;
  const isWin = state.guesses.some(g => g.isWin || g.rank === 1000);
  const total = state.guesses.length;
  const bestPct = state.roomBestScorePct > 0 ? formatPct(state.roomBestScorePct) : "0%";

  const steps = [
    { threshold: 10, emoji: "🧊" },
    { threshold: 30, emoji: "❄️" },
    { threshold: 50, emoji: "🌡️" },
    { threshold: 75, emoji: "🔥" },
    { threshold: 90, emoji: "🌋" },
    { threshold: 99, emoji: "✨" },
    { threshold: 100, emoji: "☀️" }
  ];
  const bar = steps.map(s => (state.roomBestScorePct >= s.threshold ? s.emoji : "⬛")).join("");

  const titleStatus = isWin
    ? `☀️ Fusion solaire atteinte en ${total} mots !`
    : `Manche #${state.roundNumber} terminée • Record : ${bestPct}`;

  const text = `ZéroAbsolu v1.3 • ${cfg.label} #${state.roundNumber}
${titleStatus}
${bar}
⚡ ${me.points || 0} pts • N${getLevelInfo(me.xp || 0).level} (${getLevelInfo(me.xp || 0).title})
Jouer en direct : https://zero-absolu.vercel.app/`;

  if (navigator.clipboard?.writeText) {
    navigator.clipboard.writeText(text).then(() => {
      showToast("Résultat copié dans le presse-papier ! 📋", "amber");
    }).catch(() => {
      showToast("Impossible de copier automatiquement", "rose");
    });
  } else {
    showToast("Presse-papier indisponible sur ce navigateur", "rose");
  }
}

export function triggerInputShake(el) {
  if (el) {
    el.classList.remove("animate-shake");
    void el.offsetWidth;
    el.classList.add("animate-shake");
  }
}

export function highlightExistingWordRow(word) {
  const row = document.querySelector(`#guessesList [data-word="${CSS.escape(word)}"]`);
  if (row) {
    row.classList.remove("animate-duplicate");
    void row.offsetWidth;
    row.classList.add("animate-duplicate");
  }
}

export function showVictoryBanner(winner, secretWord, total, isGiveUp = false, timeSeconds = null) {
  toggleModal("victoryBanner", true);
  $("victoryTitle").textContent = `Réponse : ${secretWord.toUpperCase()} (100%)`;
  const timeStr = timeSeconds ? ` • ⏱️ ${formatDuration(timeSeconds)}` : "";
  $("victorySub").textContent = isGiveUp ? "Manche révélée" : `Fusion atteinte par ${winner} (${total} mots${timeStr})`;
}

export function renderRowHTML(g, isNewWord = false) {
  const targetClip = (100 - Math.max(4, Math.min(100, g.scorePct))).toFixed(1);
  const initClip = isNewWord ? "100" : targetClip;
  const tv = getTierVisuals(g);
  const authorCol = g.finderId === state.myId ? "text-sky-300" : "text-indigo-300";

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

export function animateNewWordBars() {
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

export function renderGuesses(latestWord = "") {
  $("guessesList").innerHTML = state.guesses.map(g => renderRowHTML(g, g.word === latestWord)).join("");
  if (latestWord) animateNewWordBars();
}

export function updateRecentWordBoxVisibility(guessObj, animateBar = true) {
  const posIndex = state.guesses.findIndex(g => g.word === guessObj.word);
  if (posIndex >= 6) {
    toggleModal("lastGuessBox", true);
    $("lastGuessRankPos").textContent = `${posIndex + 1}e / ${state.guesses.length}`;
    $("lastGuessContent").innerHTML = renderRowHTML(guessObj, animateBar);
    if (animateBar) animateNewWordBars();
  } else {
    toggleModal("lastGuessBox", false);
    $("guessesList").scrollTop = 0;
  }
}

export function updateStatsUI() {
  const total = state.guesses.length;
  const bestStr = state.roomBestScorePct > 0 ? formatPct(state.roomBestScorePct) : "0%";
  const topCnt = state.guesses.filter(g => g.rank !== null).length;
  $("statAttempts").textContent = $("mobileAttemptCount").textContent = $("miniAttempts").textContent = total;
  $("statBestScore").textContent = $("miniBestScore").textContent = bestStr;
  $("statTopWords").textContent = $("miniTopWords").textContent = topCnt;
  updateThermalGauge(state.roomBestScorePct);
}

export function updateLiveTicker(msg) {
  const el = $("liveTickerText");
  if (!el) return;
  el.textContent = msg;
  el.className = (msg.length > 34 && window.innerWidth < 640)
    ? "text-slate-300 font-medium text-[11px] ticker-scroll"
    : "text-slate-300 font-medium text-[11px] block truncate";
}

export function renderLeaderboard() {
  const all = Object.values(state.players);
  const sorted = [...all].sort((a, b) => (b.points - a.points) || (b.wins - a.wins));
  const leader = [...all].sort((a, b) => (b.bestScorePct || 0) - (a.bestScorePct || 0))[0];

  $("liveLeaderBadge").innerHTML = (leader && leader.bestScorePct > 0)
    ? `<i class="ph-fill ph-crown text-amber-400 text-xs"></i><span>${escapeHTML(leader.pseudo)} (${formatPct(leader.bestScorePct)})</span>`
    : `<i class="ph-fill ph-crown text-amber-400 text-xs"></i><span>${escapeHTML(sorted[0]?.pseudo || "--")}</span>`;

  const medalColors = ["text-amber-400", "text-slate-300", "text-amber-600"];

  $("leaderboardList").innerHTML = sorted.map((p, i) => {
    const isMe = p.id === state.myId;
    const lvl = getLevelInfo(p.xp || 0);
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

export function toggleFeedFilter() {
  state.feedOnlyHot = !state.feedOnlyHot;
  $("feedFilterBtn").innerHTML = state.feedOnlyHot
    ? `<i class="ph-duotone ph-list-bullets text-xs"></i><span>Tout afficher</span>`
    : `<i class="ph-duotone ph-fire text-xs"></i><span>Chauds seuls</span>`;
  $("feedFilterBtn").className = state.feedOnlyHot
    ? "text-[10px] font-bold px-2 py-0.5 rounded-md bg-sky-500/20 text-sky-300 border border-sky-500/40 transition flex items-center gap-1"
    : "text-[10px] font-semibold px-2 py-0.5 rounded-md bg-slate-800 text-amber-300 hover:bg-slate-700 border border-slate-700 transition flex items-center gap-1";
  renderFeed();
}

export function addWordFeedEvent(g, surgeGain, isNewRecord) {
  const isHot = g.isWin || g.rank !== null || surgeGain || isNewRecord;
  state.feedEvents.unshift({ kind: "word", ...g, isHot });
  if (state.feedEvents.length > 40) state.feedEvents.pop();
  renderFeed();
  if (isHot && $("socialSection").classList.contains("hidden")) $("unreadDot").classList.remove("hidden");
}

export function addSystemFeedEvent(text) {
  state.feedEvents.unshift({ kind: "system", text, isHot: true });
  if (state.feedEvents.length > 40) state.feedEvents.pop();
  renderFeed();
}

export function renderFeed() {
  const filtered = state.feedOnlyHot ? state.feedEvents.filter(e => e.isHot) : state.feedEvents;
  if (!filtered.length) {
    $("liveFeed").innerHTML = `<p class="text-slate-500 text-[11px] text-center my-auto py-6">Aucun événement.</p>`;
    return;
  }

  $("liveFeed").innerHTML = filtered.map(ev => {
    if (ev.kind === "system") {
      return `<div class="px-2.5 py-1.5 rounded-lg bg-slate-800/40 border border-slate-800 text-[11px] text-sky-300 font-medium flex items-center gap-1.5"><i class="ph-duotone ph-sparkle text-xs"></i><span>${escapeHTML(ev.text)}</span></div>`;
    }
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

export function showToast(msg, color = "sky") {
  const container = $("toastContainer");
  if (!container) return;

  const styles = {
    sky: {
      bg: "bg-slate-900/95 border-sky-500/50 shadow-[0_4px_25px_rgba(14,165,233,0.3)] text-sky-100",
      icon: "ph-duotone ph-sparkle text-sky-400 text-base"
    },
    amber: {
      bg: "bg-slate-900/95 border-amber-500/60 shadow-[0_4px_25px_rgba(245,158,11,0.3)] text-amber-100",
      icon: "ph-duotone ph-fire text-amber-400 text-base"
    },
    rose: {
      bg: "bg-slate-900/95 border-rose-500/60 shadow-[0_4px_25px_rgba(244,63,94,0.3)] text-rose-100",
      icon: "ph-duotone ph-warning-circle text-rose-400 text-base"
    },
    emerald: {
      bg: "bg-slate-900/95 border-emerald-500/60 shadow-[0_4px_25px_rgba(16,185,129,0.3)] text-emerald-100",
      icon: "ph-duotone ph-check-circle text-emerald-400 text-base"
    },
    purple: {
      bg: "bg-slate-900/95 border-purple-500/60 shadow-[0_4px_25px_rgba(168,85,247,0.3)] text-purple-100",
      icon: "ph-duotone ph-game-controller text-purple-400 text-base"
    }
  };

  const current = styles[color] || styles.sky;
  const t = document.createElement("div");
  t.className = `pointer-events-auto cursor-pointer flex items-center gap-2.5 px-4 py-2.5 rounded-2xl border backdrop-blur-xl text-xs font-semibold shadow-2xl transition-all duration-300 animate-toast-in select-none ${current.bg}`;
  t.innerHTML = `
    <i class="${current.icon} shrink-0"></i>
    <span class="truncate max-w-[260px] sm:max-w-xs leading-snug">${escapeHTML(msg)}</span>
    <i class="ph-bold ph-x text-xs text-slate-400 hover:text-white shrink-0 ml-1"></i>
  `;

  let isRemoving = false;
  const dismiss = () => {
    if (isRemoving) return;
    isRemoving = true;
    t.classList.remove("animate-toast-in");
    t.classList.add("animate-toast-out");
    setTimeout(() => {
      if (t.parentElement) t.remove();
    }, 280);
  };

  t.onclick = dismiss;
  container.appendChild(t);

  setTimeout(() => {
    if (t.parentElement) dismiss();
  }, 3800);
}

export function switchMobileTab(tab) {
  const isGame = tab === "game";
  $("gameSection").classList.toggle("hidden", !isGame);
  $("socialSection").classList.toggle("hidden", isGame);
  $("socialSection").classList.toggle("flex", !isGame);
  if (!isGame) $("unreadDot").classList.add("hidden");
  $("tabGameBtn").className = `py-1 rounded-lg transition flex items-center justify-center gap-1.5 ${isGame ? 'bg-slate-800 text-white' : 'text-slate-400'}`;
  $("tabSocialBtn").className = `py-1 rounded-lg transition flex items-center justify-center gap-1.5 relative ${!isGame ? 'bg-slate-800 text-white' : 'text-slate-400'}`;
}

export function syncMobileViewport() {
  const vv = window.visualViewport;
  if (!vv) return;
  $("appViewport").style.height = `${vv.height}px`;
  $("appViewport").style.top = `${vv.offsetTop}px`;
  document.body.classList.toggle("keyboard-active", (initialScreenHeight - vv.height) > 140 && window.innerWidth < 1024);
}

export function resetStatsIdleTimer() {
  clearTimeout(state.statsIdleTimer);
  state.statsIdleTimer = setTimeout(() => setStatsMinimized(true), 10000);
}

export function toggleStatsMinimized() {
  setStatsMinimized(!state.statsMinimized);
  if (!state.statsMinimized) resetStatsIdleTimer();
}

export function setStatsMinimized(min) {
  state.statsMinimized = min;
  $("statsExpanded").classList.toggle("hidden", min);
  $("statsCollapsed").classList.toggle("hidden", !min);
}

export function showLevelUpBanner(newLevelInfo) {
  const banner = $("levelUpBanner");
  $("levelUpIcon").className = `ph-duotone ${newLevelInfo.icon} text-2xl text-white`;
  $("levelUpNumText").textContent = `Niveau ${newLevelInfo.level}`;
  $("levelUpTitleText").textContent = newLevelInfo.title;

  banner.classList.remove("hidden", "animate-levelup");
  void banner.offsetWidth;
  banner.classList.add("animate-levelup");

  soundManager.playLevelUpSound();
  vibrateDevice([50, 40, 80]);
  clearTimeout(state.levelUpTimer);
  state.levelUpTimer = setTimeout(() => banner.classList.add("hidden"), 4200);
}

export function triggerSurgeAnimation(pseudo, word, scorePct, rank, gainPct) {
  $("surgePlayerName").textContent = pseudo;
  $("surgeWord").textContent = word;
  $("surgeScore").textContent = formatPct(scorePct);
  const topLbl = getReadableTopLabel(rank);
  $("surgeBadge").textContent = topLbl ? topLbl : `+${gainPct}%`;
  toggleModal("surgeOverlay", true);
  soundManager.playSurgeSound();
  vibrateDevice([40, 50, 90]);

  // Déclencher un jaillissement de flammes et braises ardentes adaptées (sans confettis papier)
  const surgeBox = $("surgeOverlay");
  thermalParticles.trigger(surgeBox, scorePct, false, rank || 995);

  clearTimeout(state.surgeHideTimer);
  state.surgeHideTimer = setTimeout(dismissSurgeOverlay, 6500);
}

export function dismissSurgeOverlay() {
  clearTimeout(state.surgeHideTimer);
  toggleModal("surgeOverlay", false);
}

export function triggerSolarFusionExplosion(targetEl) {
  const ov = $("solarExplosionOverlay"), fl = $("solarFlashBg"), ry = $("solarRaysBurst"), rg = $("solarShockwave");
  ov.classList.remove("hidden");
  fl.classList.remove("animate-solar-flash");
  ry.classList.remove("animate-solar-rays");
  rg.classList.remove("animate-solar-ring");
  void ov.offsetWidth;
  fl.classList.add("animate-solar-flash");
  ry.classList.add("animate-solar-rays");
  rg.classList.add("animate-solar-ring");
  soundManager.playSolarFusionFanfare();
  setTimeout(() => ov.classList.add("hidden"), 1550);

  // Animation unique et grandiose : étoiles solaires 8 branches, faisceaux de photons & double onde de plasma
  const el = targetEl || $("guessesList") || document.body;
  const rect = el.getBoundingClientRect ? el.getBoundingClientRect() : null;
  const cx = rect && rect.width > 0 ? rect.left + rect.width / 2 : window.innerWidth / 2;
  const cy = rect && rect.height > 0 ? Math.max(70, Math.min(window.innerHeight - 70, rect.top + rect.height / 2)) : window.innerHeight / 3;
  thermalParticles.spawnSolarFusion(cx, cy);
}

export function openStatsModal(targetId = state.myId) {
  state.selectedStatsPlayerId = state.players[targetId] ? targetId : state.myId;
  state.showingGradesCatalog = false;
  updateGradesViewVisibility();
  renderStatsModalContent();
  toggleModal("statsModal", true);
}

export function toggleGradesView() {
  state.showingGradesCatalog = !state.showingGradesCatalog;
  updateGradesViewVisibility();
  renderStatsModalContent();
}

export function updateGradesViewVisibility() {
  $("gradesCatalogView").classList.toggle("hidden", !state.showingGradesCatalog);
  $("gradesCatalogView").classList.toggle("flex", state.showingGradesCatalog);
  $("statsMainView").classList.toggle("hidden", state.showingGradesCatalog);
}

export function renderStatsModalContent() {
  const roomPlayers = Object.values(state.players).sort((a, b) => (b.xp - a.xp) || (b.points - a.points));
  const listSource = (state.leaderboardScope === "global" && state.globalLeaderboardCache.length) ? state.globalLeaderboardCache : roomPlayers;
  const p = state.players[state.selectedStatsPlayerId] || state.players[state.myId];
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
  const bestTimeStr = p.bestTimeSeconds ? formatDuration(p.bestTimeSeconds) : "--";
  const avgTimeStr = (p.wins > 0 && p.totalWinTimeSeconds) ? formatDuration(Math.round(p.totalWinTimeSeconds / p.wins)) : "--";
  const cards = [
    ["ph-sun-dim", "Victoires", p.wins || 0, "text-amber-300"],
    ["ph-crosshair", "Mots testés", totalAtt, "text-white"],
    ["ph-flame", "Top 1000", hotCount, "text-orange-400"],
    ["ph-meteor", "Top 10", p.top10Found || 0, "text-red-400"],
    ["ph-chart-polar", "Précision", `${totalAtt > 0 ? Math.round((hotCount / totalAtt) * 100) : 0}%`, "text-sky-400"],
    ["ph-lightning", "Points", p.points || 0, "text-amber-400"],
    ["ph-timer", "Record Vitesse", bestTimeStr, "text-emerald-400"],
    ["ph-hourglass-medium", "Temps Moyen", avgTimeStr, "text-indigo-400"]
  ];
  $("profileStatsGrid").innerHTML = cards.map(([ic, lbl, val, col]) => `
    <div class="bg-slate-800/40 border border-slate-800 rounded-xl p-2.5 text-center">
      <span class="text-[10px] text-slate-400 flex items-center justify-center gap-1"><i class="ph-duotone ${ic} ${col} text-xs"></i>${lbl}</span>
      <strong class="font-mono-num text-sm sm:text-base font-extrabold ${col} block mt-0.5">${val}</strong>
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

export function openWelcomeModal(isNewUser) {
  const me = state.players[state.myId] || {};
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

export function closeWelcomeModal() {
  toggleModal("welcomeModal", false);
}

export function openTutorialModal() {
  state.currentTutoSlide = 0;
  updateTutorialCarousel();
  toggleModal("tutorialModal", true);
}

export function closeTutorialModal() {
  toggleModal("tutorialModal", false);
}

export function stepTutorial(delta) {
  if (state.currentTutoSlide + delta >= 3) {
    closeTutorialModal();
    return;
  }
  state.currentTutoSlide = Math.max(0, Math.min(2, state.currentTutoSlide + delta));
  updateTutorialCarousel();
}

export function goToTutorialSlide(idx) {
  state.currentTutoSlide = Math.max(0, Math.min(2, idx));
  updateTutorialCarousel();
}

export function updateTutorialCarousel() {
  const track = $("tutorialTrack");
  if (track) {
    if (window.Motion?.animate) {
      window.Motion.animate(track, { transform: `translateX(-${state.currentTutoSlide * 100}%)` }, { duration: 0.38, easing: [0.16, 1, 0.3, 1] });
    } else {
      track.style.transform = `translateX(-${state.currentTutoSlide * 100}%)`;
    }
  }
  $("tutoPrevBtn").classList.toggle("invisible", state.currentTutoSlide === 0);
  $("tutoNextBtn").textContent = state.currentTutoSlide === 2 ? "C'est parti !" : "Suivant →";

  const dots = $("tutoDots")?.children;
  if (dots) {
    for (let i = 0; i < dots.length; i++) {
      dots[i].className = i === state.currentTutoSlide
        ? "w-6 h-1.5 rounded-full bg-gradient-to-r from-sky-400 to-indigo-400 transition-all cursor-pointer shadow-[0_0_8px_rgba(56,189,248,0.5)]"
        : "w-2 h-1.5 rounded-full bg-slate-700 hover:bg-slate-500 transition-all cursor-pointer";
    }
  }
}

export function openDailyArchiveModal() {
  renderDailyArchiveContent();
  toggleModal("dailyArchiveModal", true);
}

export function closeDailyArchiveModal() {
  toggleModal("dailyArchiveModal", false);
}

export function renderDailyArchiveContent() {
  const listEl = $("dailyArchiveList");
  if (!listEl) return;

  const history = getDailyHistory(10);
  state.dailyArchiveCache = history;

  listEl.innerHTML = history.map(item => {
    const isToday = item.isToday;
    const isSolved = Boolean(item.localRecord?.solved);
    const dateLabel = isToday
      ? "Aujourd'hui"
      : new Intl.DateTimeFormat("fr-FR", { weekday: "short", day: "numeric", month: "short" }).format(item.dateObj);

    let wordDisplay = "••••";
    let wordBadge = `<span class="bg-amber-500/20 text-amber-300 border border-amber-500/40 text-[10px] font-bold px-2 py-0.5 rounded-full flex items-center gap-1"><i class="ph-fill ph-hourglass text-xs"></i>En cours</span>`;

    if (isSolved) {
      wordDisplay = item.secretWord ? item.secretWord.toUpperCase() : "TROUVÉ";
      wordBadge = `<span class="bg-emerald-500/20 text-emerald-300 border border-emerald-500/40 text-[10px] font-extrabold px-2 py-0.5 rounded-full flex items-center gap-1"><i class="ph-bold ph-check text-xs"></i>Trouvé</span>`;
    } else if (!isToday && item.secretWord) {
      wordDisplay = item.secretWord.toUpperCase();
      wordBadge = `<span class="bg-slate-800 text-slate-400 border border-slate-700 text-[10px] font-semibold px-2 py-0.5 rounded-full">Passé</span>`;
    }

    const solversStr = `${item.solversCount} vainqueur${item.solversCount > 1 ? "s" : ""}`;

    const topSolversHTML = item.topSolvers.map((s, idx) => {
      const medal = idx === 0 ? "🥇" : idx === 1 ? "🥈" : "🥉";
      const highlight = s.isMe ? "bg-amber-500/20 text-amber-200 border border-amber-400/40 px-1.5 py-0.5 rounded" : "text-slate-300";
      return `<div class="flex items-center justify-between text-[10px] ${highlight}">
        <span class="flex items-center gap-1"><span>${medal}</span><strong class="truncate max-w-[85px]">${escapeHTML(s.pseudo)}</strong></span>
        <span class="font-mono-num font-bold text-slate-400">${formatDuration(s.timeSec)} <span class="text-[9px] text-slate-500">(${s.attempts} m)</span></span>
      </div>`;
    }).join("");

    const actionBtn = isToday
      ? `<button onclick="window.playDailyArchiveGame(${item.gameId}, '${item.dateStr}', true)" class="w-full py-1.5 rounded-xl text-xs font-extrabold bg-gradient-to-r from-amber-400 to-orange-500 hover:from-amber-300 hover:to-orange-400 text-slate-950 transition shadow-md flex items-center justify-center gap-1.5 active:scale-98">
          <i class="ph-fill ph-play text-xs"></i> Jouer le défi du jour
         </button>`
      : `<button onclick="window.playDailyArchiveGame(${item.gameId}, '${item.dateStr}', false)" class="w-full py-1 rounded-xl text-[11px] font-bold bg-slate-800 hover:bg-slate-700 text-sky-300 hover:text-white transition flex items-center justify-center gap-1 active:scale-98">
          <i class="ph-duotone ph-arrow-counter-clockwise text-xs"></i> Rejouer cette archive
         </button>`;

    return `
      <div class="bg-slate-950/80 border ${isToday ? 'border-amber-400/50 bg-gradient-to-b from-amber-950/20 to-slate-950/90 shadow-sm' : 'border-slate-800/80'} rounded-2xl p-3 flex flex-col gap-2">
        <div class="flex items-center justify-between gap-2">
          <div class="flex items-center gap-2 min-w-0">
            <span class="text-xs font-extrabold text-white capitalize">${dateLabel}</span>
            <span class="text-[10px] font-mono-num text-slate-500">#${item.gameId}</span>
          </div>
          <div>${wordBadge}</div>
        </div>

        <div class="flex items-baseline justify-between bg-slate-900/70 border border-slate-800/60 rounded-xl px-2.5 py-1.5">
          <div>
            <span class="text-[9px] uppercase tracking-wider text-slate-500 block">Mot du jour</span>
            <span class="text-sm font-extrabold tracking-wide ${isSolved ? 'text-amber-300' : 'text-slate-300'} font-mono">${wordDisplay}</span>
          </div>
          <div class="text-right">
            <span class="text-[9px] uppercase tracking-wider text-slate-500 block">Succès</span>
            <span class="text-[11px] font-bold text-sky-300 flex items-center gap-1 justify-end">
              <i class="ph-duotone ph-users-three text-xs"></i>${solversStr}
            </span>
          </div>
        </div>

        <div class="bg-slate-900/40 rounded-xl p-2 border border-slate-800/40 flex flex-col gap-1">
          <span class="text-[9px] uppercase tracking-wider font-bold text-slate-500 flex items-center gap-1">
            <i class="ph-duotone ph-trophy text-amber-400"></i> Meilleurs chronos
          </span>
          ${topSolversHTML}
        </div>

        <div>${actionBtn}</div>
      </div>
    `;
  }).join("");
}

export function openOnboardingModal() {
  $("modalError").textContent = "";
  if (state.isAuthenticated) {
    updateLobbyHeaderUI();
    $("authView").classList.add("hidden");
    $("lobbyView").classList.remove("hidden");
  }
  if (state.hasStartedSession) $("closeModalBtn").classList.remove("hidden");
  toggleModal("onboardingModal", true);
}

export function closeOnboardingModal() {
  if (!state.isAuthenticated) return;
  state.hasStartedSession = true;
  $("closeModalBtn").classList.remove("hidden");
  toggleModal("onboardingModal", false);
}

export function updateLobbyHeaderUI() {
  const me = state.players[state.myId] || {};
  const lvl = getLevelInfo(me.xp || 0);
  $("lobbyLevelBadge").textContent = `N${lvl.level}`;
  $("lobbyPseudoDisplay").textContent = me.pseudo || state.myPseudo;
  $("lobbyStatsDisplay").textContent = `${me.points || 0} ⚡ • ${me.xp || 0} XP (${lvl.title})`;
  window.updateModeUI?.(state.currentGameMode);
}

export function updateHintButtonUI() {
  const me = state.players[state.myId];
  const hasPts = me && me.points >= HINT_COST;
  $("hintBtn").className = hasPts
    ? `flex items-center justify-center gap-1 bg-amber-500/20 hover:bg-amber-500/30 border border-amber-400/50 text-amber-300 text-xs font-bold px-2 py-1 rounded-lg transition shadow-sm shrink-0 ${state.roundFinished ? 'opacity-50' : ''}`
    : "flex items-center justify-center gap-1 bg-slate-900/70 border border-slate-800 text-slate-500 text-xs font-semibold px-2 py-1 rounded-lg transition opacity-75 shrink-0";
  $("hintBtnContent").innerHTML = `<i class="ph-duotone ${hasPts ? 'ph-lightbulb-filament text-amber-300' : 'ph-lock-key text-slate-500'} text-sm"></i><span class="font-mono-num text-[11px]">${HINT_COST}</span>`;
}

export function openConfirmModal({ icon, colorCls, title, desc, btnText, onConfirm }) {
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

export function closeConfirmModal() {
  pendingConfirmAction = null;
  toggleModal("confirmModal", false);
}

export function toggleHeaderMenu(e) {
  e?.stopPropagation();
  const menu = $("headerDropdownMenu");
  if (!menu) return;
  menu.classList.toggle("hidden");
}

export function closeHeaderMenu() {
  const menu = $("headerDropdownMenu");
  if (menu && !menu.classList.contains("hidden")) {
    menu.classList.add("hidden");
  }
}

document.addEventListener("click", e => {
  const menu = $("headerDropdownMenu");
  const btn = $("headerMenuBtn");
  if (menu && !menu.classList.contains("hidden")) {
    if (!menu.contains(e.target) && (!btn || !btn.contains(e.target))) {
      closeHeaderMenu();
    }
  }
});

