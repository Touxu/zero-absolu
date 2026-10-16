// =========================================================================
// MOTEUR SÉMANTIQUE, CALCULS VECTORIELS & INDEXATION LINGUISTIQUE
// =========================================================================
import {
  MODE_CONFIG, GRADE_TIERS, XP_PER_LEVEL,
  stripAccents, getReadableTopLabel
} from "./constants.js";
import { state } from "./state.js";

export function base64ToUint8(b64) {
  const bin = atob(b64);
  const len = bin.length;
  const bytes = new Uint8Array(len);
  for (let i = 0; i < len; i++) bytes[i] = bin.charCodeAt(i);
  return bytes;
}

export async function ensureCatalogueLoaded() {
  if (state.catalogueCache) return state.catalogueCache;
  if (!state.cataloguePromise) {
    state.cataloguePromise = fetch("data/catalogue.json")
      .then(r => (r.ok ? r.json() : null))
      .then(raw => {
        if (!raw) return null;
        const vBuf = base64ToUint8(raw.vecs16);
        const cBuf = base64ToUint8(raw.classic);
        const pBuf = base64ToUint8(raw.pop);
        const v8 = new Int8Array(vBuf.buffer, vBuf.byteOffset, vBuf.byteLength);
        const c16 = new Uint16Array(cBuf.buffer, cBuf.byteOffset, cBuf.byteLength / 2);
        const p16 = new Uint16Array(pBuf.buffer, pBuf.byteOffset, pBuf.byteLength / 2);
        MODE_CONFIG.classic.total = raw.classicGames || 500;
        MODE_CONFIG.pop.total = raw.popGames || 91;
        state.catalogueCache = {
          words: raw.words,
          classicCount: raw.classicCount,
          vecs16: v8,
          classicTop: c16,
          popTop: p16
        };
        return state.catalogueCache;
      })
      .catch(() => null);
  }
  return state.cataloguePromise;
}

export function getDailyGameId(totalGames = 500) {
  return getDailyGameIdForDate(new Date(), totalGames);
}

export function getDailyGameIdForDate(dateInput, totalGames = 500) {
  const d = dateInput instanceof Date ? dateInput : new Date(dateInput);
  const dateStr = `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, "0")}-${String(d.getDate()).padStart(2, "0")}`;
  let hash = 0;
  for (let i = 0; i < dateStr.length; i++) {
    hash = (hash * 31 + dateStr.charCodeAt(i)) & 0xffffffff;
  }
  return (Math.abs(hash) % totalGames) + 1;
}

export function getDailyHistory(daysCount = 10) {
  const history = [];
  const today = new Date();
  const maxTotal = MODE_CONFIG.daily?.total || 500;

  for (let i = 0; i < daysCount; i++) {
    const d = new Date(today);
    d.setDate(today.getDate() - i);
    const dateStr = `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, "0")}-${String(d.getDate()).padStart(2, "0")}`;
    const gameId = getDailyGameIdForDate(d, maxTotal);
    const isToday = i === 0;

    let secretWord = null;
    if (state.catalogueCache) {
      const topArray = state.catalogueCache.classicTop;
      const offset = (gameId - 1) * 1000;
      secretWord = state.catalogueCache.words[topArray[offset]];
    }

    let localRecord = null;
    try {
      const saved = localStorage.getItem(`zeroabsolu_daily_${dateStr}`);
      if (saved) localRecord = JSON.parse(saved);
    } catch (_) {}

    // Estimation réaliste des victoires communautaires
    let baseSolvers = 65 + ((gameId * 37) % 75);
    if (isToday) baseSolvers = Math.max(14, Math.floor(baseSolvers * 0.65));

    const topSolvers = [
      { pseudo: "Touxu", timeSec: 36 + (gameId % 22), attempts: 6 + (gameId % 5) },
      { pseudo: "LoutreMaline", timeSec: 58 + (gameId % 28), attempts: 10 + (gameId % 7) },
      { pseudo: "PoissonCool", timeSec: 82 + (gameId % 35), attempts: 14 + (gameId % 9) }
    ];

    if (localRecord && localRecord.timeSeconds) {
      topSolvers.push({
        pseudo: state.myPseudo || "Vous",
        timeSec: localRecord.timeSeconds,
        attempts: localRecord.attempts || 1,
        isMe: true
      });
      topSolvers.sort((a, b) => (a.timeSec - b.timeSec) || (a.attempts - b.attempts));
    }

    history.push({
      dateStr,
      dateObj: d,
      isToday,
      gameId,
      secretWord,
      localRecord,
      solversCount: baseSolvers + (localRecord ? 1 : 0),
      topSolvers: topSolvers.slice(0, 3)
    });
  }
  return history;
}

export function pickUnplayedGameId(mode = state.currentGameMode) {
  if (mode === "daily") {
    return getDailyGameId(MODE_CONFIG.daily?.total || 500);
  }
  const maxGames = MODE_CONFIG[mode]?.total || 500;
  if (state.playedGameIds.size >= maxGames) state.playedGameIds.clear();
  let c;
  do {
    c = Math.floor(Math.random() * maxGames) + 1;
  } while (state.playedGameIds.has(c));
  state.playedGameIds.add(c);
  return c;
}

export function getLevelInfo(xp = 0) {
  const safeXp = Math.max(0, Number(xp) || 0);
  const level = Math.floor(safeXp / XP_PER_LEVEL) + 1;
  const currentLevelXp = safeXp % XP_PER_LEVEL;
  const progressPct = Math.min(100, Math.round((currentLevelXp / XP_PER_LEVEL) * 100));
  const tier = [...GRADE_TIERS].reverse().find(t => level >= t.minLevel) || GRADE_TIERS[0];
  return { level, currentLevelXp, nextLevelXp: XP_PER_LEVEL, progressPct, title: tier.title, icon: tier.icon, color: tier.color, tier };
}

export function computeUnifiedScorePct(temp, rank) {
  if (rank === 1000) return 100;
  if (rank >= 900) return Number((rank / 10).toFixed(1));
  if (rank > 0) return Number((40 + (rank / 900) * 49.9).toFixed(1));
  return Number((1 + Math.max(0, Math.min(1, (temp + 12) / 40)) * 38.5).toFixed(1));
}

export function getTierVisuals(g) {
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

export function buildAccentInsensitiveIndex() {
  state.accentInsensitiveMap = {};
  for (const word of Object.keys(state.gameDictionary)) {
    const s = stripAccents(word);
    state.accentInsensitiveMap[s] = word;
    if (word.includes("-")) state.accentInsensitiveMap[s.replace(/-/g, "")] = word;
  }
}

export const tryDirectMatch = c => (c in state.gameDictionary ? c : (state.accentInsensitiveMap[stripAccents(c)] || null));

export function resolveWordInDictionary(raw) {
  let cleaned = raw.trim().toLowerCase().replace(/['’]/g, "'").replace(/\s+/g, "-");

  // Suppression des articles élidés ou préfixes courants (l', d', un-, le-, etc.)
  cleaned = cleaned.replace(/^(l'|d'|c'|s'|qu'|j'|m'|t'|n')/i, "");
  cleaned = cleaned.replace(/^(le-|la-|un-|une-|les-|des-|du-)/i, "");

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
    ["ées","er"],["er","e"],
    // Terminaisons verbales courantes -> infinitif
    ["aient","er"],["èrent","er"],["eront","er"],["erait","er"],["erions","er"],["eriez","er"],
    ["ait","er"],["ent","er"],["era","er"],["eras","er"],["erez","er"],["erons","er"],
    ["iez","er"],["ions","er"],["ant","er"],["issant","ir"],["issent","ir"],["issait","ir"],["irent","ir"]
  ];
  for (const f of forms) {
    if ((m = tryDirectMatch(f))) return m;
    for (const [end, rep] of rules) {
      if (f.endsWith(end) && f.length - end.length >= 2 && (m = tryDirectMatch(f.slice(0, -end.length) + rep))) return m;
    }
  }
  return null;
}

export function checkPowerSurge(rank, newPct) {
  if (rank === 1000 || state.guesses.length < 2 || state.roomBestScorePct <= 0) return null;
  const jump = newPct - state.roomBestScorePct;
  const milestone = (rank >= 991 && state.roomBestRank < 991) || (rank >= 900 && state.roomBestRank < 750);
  return (newPct > state.roomBestScorePct && newPct >= 45 && (jump >= 15 || milestone)) ? Math.max(15, Math.round(jump)) : null;
}
