// =========================================================================
// ÉTAT GLOBAL DE L'APPLICATION (STORE CENTRALISÉ)
// =========================================================================

const initialTabId = sessionStorage.getItem("za_tab_id") || ("p_" + Math.random().toString(36).slice(2, 10));
sessionStorage.setItem("za_tab_id", initialTabId);

let initialStats = {};
try {
  initialStats = JSON.parse(localStorage.getItem("zeroabsolu_profile_v2") || "{}");
} catch (_) {
  initialStats = {};
}

export const state = {
  // Mode de jeu (classic vs pop)
  currentGameMode: localStorage.getItem("zeroabsolu_mode") || "classic",

  // Cache du catalogue compressé (catalogue.json)
  catalogueCache: null,
  cataloguePromise: null,

  // Profil et session du joueur local
  myId: initialTabId,
  myPseudo: localStorage.getItem("zeroabsolu_pseudo") || "",
  myPassword: localStorage.getItem("zeroabsolu_pwd") || "",
  isAuthenticated: false,
  authMode: "login",
  currentTutoSlide: 0,
  savedStats: initialStats,

  // Session de jeu et salon multijoueur
  hasStartedSession: false,
  roomCode: null,
  isHost: true,
  roundNumber: 1,
  playedGameIds: new Set(),
  currentGameId: 1,
  currentLoadSeq: 0,

  // Moteur de dictionnaire et manche en cours
  gameDictionary: {},
  accentInsensitiveMap: {},
  guesses: [],
  roundFinished: false,
  roomBestScorePct: 0,
  roomBestRank: 0,
  roundStartTime: null,
  dailyArchiveCache: [],

  // Joueurs et classements
  players: {},
  globalLeaderboardCache: [],
  leaderboardScope: "room",
  selectedStatsPlayerId: initialTabId,
  showingGradesCatalog: false,

  // Timers et filtres UI
  statsMinimized: false,
  statsIdleTimer: null,
  surgeHideTimer: null,
  levelUpTimer: null,
  feedOnlyHot: false,
  feedEvents: [],

  // Easter egg / Debug
  secretClickCount: 0,
  secretClickTimer: null,

  // Réseau MQTT
  mqttClients: [],
  seenMsgIds: new Set(),
  joinTimeout: null,
  joinResolved: false
};
