// =========================================================================
// CONSTANTES & CONFIGURATION DU JEU
// =========================================================================
export const APP_VERSION = "v1.3";
export const APP_EDITION = "Édition Solaire";

export const $ = id => document.getElementById(id);

export const MODE_CONFIG = {
  classic: {
    total: 500,
    label: "Classique",
    icon: "ph-compass-rose",
    color: "text-sky-400",
    pillCls: "bg-sky-500/10 text-sky-300 border-sky-500/25"
  },
  pop: {
    total: 91,
    label: "Pop & Manga",
    icon: "ph-game-controller",
    color: "text-purple-400",
    pillCls: "bg-purple-500/15 text-purple-200 border-purple-500/40"
  },
  daily: {
    total: 500,
    label: "Mot du Jour",
    icon: "ph-calendar-star",
    color: "text-amber-400",
    pillCls: "bg-amber-500/15 text-amber-200 border-amber-500/40"
  }
};

export const HINT_COST = 35;
export const XP_PER_LEVEL = 100;
export const TOPIC_ROOT = "zeroabsolu/v12/rooms/";

export const WSS_BROKERS = [
  "wss://broker.emqx.io:8084/mqtt",
  "wss://broker.hivemq.com:8884/mqtt"
];

export const GRADE_TIERS = [
  { minLevel: 1,  xpReq: 0,    icon: "ph-snowflake",    color: "text-sky-300",    title: "Flocon Curieux",      desc: "Premiers pas dans le froid absolu" },
  { minLevel: 3,  xpReq: 200,  icon: "ph-compass-tool", color: "text-cyan-300",   title: "Sondeur Polaire",     desc: "Capable de détecter les signaux tièdes" },
  { minLevel: 5,  xpReq: 400,  icon: "ph-flame",        color: "text-orange-400", title: "Chasseur de Braises", desc: "Habitué des mots du Top 1000" },
  { minLevel: 9,  xpReq: 800,  icon: "ph-lightning",    color: "text-purple-300", title: "Oracle Thermique",    desc: "Maîtrise des connexions sémantiques" },
  { minLevel: 14, xpReq: 1300, icon: "ph-meteor",       color: "text-red-400",    title: "Maître du Magma",     desc: "Plonge régulièrement dans le Top 10" },
  { minLevel: 20, xpReq: 1900, icon: "ph-sun-dim",      color: "text-amber-300",  title: "Cœur Solaire",        desc: "Entité en fusion sémantique permanente" }
];

export const FALLBACK_WORDS = {
  "océan": [100, 1000], "mer": [92.4, 999], "maritime": [86.1, 998], "atlantique": [84.5, 997],
  "pacifique": [83.2, 996], "vague": [78.9, 995], "navire": [76.4, 994], "marin": [75.1, 993],
  "bateau": [70.5, 990], "plage": [66.2, 980], "île": [61.5, 950], "eau": [58.3, 920],
  "poisson": [55.1, 890], "vent": [46.8, 760], "soleil": [32.1, 450], "forêt": 18.5, "plante": 16.0
};

export const escapeHTML = s => String(s)
  .replace(/&/g, "&amp;")
  .replace(/</g, "&lt;")
  .replace(/>/g, "&gt;")
  .replace(/"/g, "&quot;")
  .replace(/'/g, "&#039;");

export const stripAccents = s => s
  .replace(/œ/g, "oe")
  .replace(/æ/g, "ae")
  .normalize("NFD")
  .replace(/[\u0300-\u036f]/g, "")
  .trim()
  .toLowerCase();

export const vibrateDevice = pattern => {
  try {
    navigator.vibrate?.(pattern);
  } catch (_) {}
};

export const formatPct = v => (v >= 100 ? "100%" : `${Number(v).toFixed(1)}%`);

export const formatDuration = sec => {
  if (!sec || sec <= 0) return "--";
  if (sec < 60) return `${sec}s`;
  const m = Math.floor(sec / 60);
  const s = sec % 60;
  return `${m}m ${s < 10 ? '0' : ''}${s}s`;
};

export const getReadableTopLabel = r => (r === 1000 ? "FUSION" : r ? `Top ${1001 - r}` : null);

export const toggleModal = (id, show) => $(id)?.classList.toggle("hidden", !show);

export const getTodayDateStr = () => {
  const d = new Date();
  return `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, "0")}-${String(d.getDate()).padStart(2, "0")}`;
};

export const formatDailyDateLabel = dateStr => {
  if (!dateStr) return "";
  const parts = String(dateStr).split("-");
  if (parts.length === 3) {
    const year = parseInt(parts[0], 10);
    const month = parseInt(parts[1], 10) - 1;
    const day = parseInt(parts[2], 10);
    const months = ["janvier", "février", "mars", "avril", "mai", "juin", "juillet", "août", "septembre", "octobre", "novembre", "décembre"];
    return `${day} ${months[month]} ${year}`;
  }
  return dateStr;
};
