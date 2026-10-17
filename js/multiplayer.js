// =========================================================================
// MODULE MULTIJOUEUR WSS & SYNCHRONISATION SALONS (MQTT)
// =========================================================================
import { TOPIC_ROOT, WSS_BROKERS, MODE_CONFIG } from "./constants.js";
import { state } from "./state.js";
import { $, showToast, toggleModal } from "./ui.js";

export function handleRoomCodeInput(input) {
  const cleaned = input.value.replace(/[^a-zA-Z]/g, "").toUpperCase().slice(0, 4);
  input.value = cleaned;
  const valid = cleaned.length === 4;
  $("joinRoomBtn").disabled = !valid;
  $("joinRoomBtn").className = valid
    ? "w-full py-2.5 rounded-xl text-sm font-bold transition flex items-center justify-center gap-2 bg-indigo-600 hover:bg-indigo-500 text-white shadow-lg cursor-pointer"
    : "w-full py-2.5 rounded-xl text-sm font-bold transition flex items-center justify-center gap-2 bg-slate-800 text-slate-500 cursor-not-allowed opacity-60";
}

export function disconnectMultiplayer() {
  clearTimeout(state.joinTimeout);
  state.mqttClients.forEach(c => {
    try {
      c.end(true);
    } catch (_) {}
  });
  state.mqttClients = [];
  state.players = { [state.myId]: state.players[state.myId] };
  window.renderLeaderboard?.();
}

export function connectToRoomBrokers(code, onFirstConnected) {
  let firstFired = false;
  const stateTopic = `${TOPIC_ROOT}${code}/state`;
  const eventsTopic = `${TOPIC_ROOT}${code}/events`;

  WSS_BROKERS.forEach(url => {
    try {
      const client = window.mqtt.connect(url, {
        clientId: `za_${state.myId}_${Math.random().toString(36).slice(2, 6)}`,
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
            if (state.seenMsgIds.has(data.uid)) return;
            state.seenMsgIds.add(data.uid);
            if (state.seenMsgIds.size > 400) state.seenMsgIds.delete(state.seenMsgIds.values().next().value);
          }
          handleNetworkPayload(data);
        } catch (_) {}
      });

      state.mqttClients.push(client);
    } catch (_) {}
  });
}

export function publishRoomEvent(payload, isRetainedState = false) {
  if (!state.roomCode || !state.mqttClients.length) return;
  const packet = {
    ...payload,
    uid: payload.uid || `m_${Date.now()}_${Math.random().toString(36).slice(2, 8)}`,
    ts: Date.now()
  };
  const topic = isRetainedState ? `${TOPIC_ROOT}${state.roomCode}/state` : `${TOPIC_ROOT}${state.roomCode}/events`;
  const raw = JSON.stringify(packet);

  state.seenMsgIds.add(packet.uid);
  state.mqttClients.forEach(c => {
    if (c.connected) c.publish(topic, raw, { qos: 1, retain: isRetainedState });
  });
}

export function publishRetainedRoomSnapshot() {
  if (!state.roomCode) return;
  publishRoomEvent({
    type: "STATE_SNAPSHOT",
    hostId: state.isHost ? state.myId : undefined,
    gameId: state.currentGameId,
    gameMode: state.currentGameMode,
    roundNumber: state.roundNumber,
    players: state.players,
    guesses: state.guesses,
    roomBestScorePct: state.roomBestScorePct,
    roomBestRank: state.roomBestRank,
    roundFinished: state.roundFinished
  }, true);
}

export function startSoloMode() {
  if (!state.isAuthenticated) return;
  disconnectMultiplayer();
  state.isHost = true;
  state.roomCode = null;
  if (state.players[state.myId]) {
    state.players[state.myId].sessionPoints = 0;
    state.players[state.myId].sessionWins = 0;
  }
  $("roomCodePill").classList.add("hidden");
  window.closeOnboardingModal?.();
  window.updateLiveTicker?.(`Mode Solo (${MODE_CONFIG[state.currentGameMode].label}) • Manche #${state.roundNumber}`);
  showToast(`Mode Solo (${MODE_CONFIG[state.currentGameMode].label}) activé`, "sky");
}

export function startCreateRoom() {
  if (!state.isAuthenticated) return;
  disconnectMultiplayer();

  state.isHost = true;
  state.roundNumber = 1;
  if (state.players[state.myId]) {
    state.players[state.myId].sessionPoints = 0;
    state.players[state.myId].sessionWins = 0;
  }
  const chars = "ABCDEFGHJKLMNPQRSTUVWXYZ";
  state.roomCode = Array.from({ length: 4 }, () => chars[Math.floor(Math.random() * chars.length)]).join("");
  navigator.clipboard?.writeText(state.roomCode).catch(() => {});

  $("modalError").textContent = "Ouverture du salon...";

  connectToRoomBrokers(state.roomCode, () => {
    $("modalError").textContent = "";
    $("roomCodePill").classList.remove("hidden");
    $("roomCodePill").classList.add("flex");
    $("headerRoomCode").textContent = state.roomCode;
    window.closeOnboardingModal?.();

    publishRetainedRoomSnapshot();
    navigator.clipboard?.writeText(state.roomCode).catch(() => {});
    window.addSystemFeedEvent?.(`Salon ${state.roomCode} créé (${MODE_CONFIG[state.currentGameMode].label})`);
    window.updateLiveTicker?.(`Salon ${state.roomCode} actif • Code copié !`);
    showToast(`Salon ${state.roomCode} créé et copié !`, "amber");
  });
}

export function startJoinRoom() {
  if (!state.isAuthenticated) return;
  const rawCode = $("modalRoomCode").value.trim().toUpperCase();
  if (rawCode === "XXXX") {
    $("modalError").textContent = "Astuce : Cliquez 3 fois sur le logo flamme en haut à gauche !";
    return;
  }
  if (!/^[A-Z]{4}$/.test(rawCode)) return;

  disconnectMultiplayer();
  state.isHost = false;
  state.roomCode = rawCode;
  state.joinResolved = false;

  $("modalError").textContent = `Recherche du salon ${state.roomCode}...`;
  $("joinRoomBtnText").textContent = "Connexion...";
  $("joinRoomBtn").disabled = true;

  connectToRoomBrokers(state.roomCode, () => {
    publishRoomEvent({ type: "JOIN_REQUEST", player: state.players[state.myId] }, false);
  });

  state.joinTimeout = setTimeout(() => {
    if (!state.joinResolved) {
      disconnectMultiplayer();
      state.roomCode = null;
      $("joinRoomBtnText").textContent = "Rejoindre le salon";
      $("joinRoomBtn").disabled = false;
      $("modalError").textContent = `Salon "${rawCode}" introuvable. Vérifiez les 4 lettres.`;
    }
  }, 6000);
}

export function completeJoinSuccess(snapshot) {
  if (state.joinResolved) return;

  const existingPlayers = Object.values(snapshot.players || {});
  const duplicateInRoom = existingPlayers.find(p => p.id !== state.myId && p.pseudo.toLowerCase() === state.myPseudo.toLowerCase());
  if (duplicateInRoom) {
    clearTimeout(state.joinTimeout);
    disconnectMultiplayer();
    state.roomCode = null;
    $("joinRoomBtnText").textContent = "Rejoindre le salon";
    $("joinRoomBtn").disabled = false;
    $("modalError").textContent = `Le compte "${state.myPseudo}" est déjà présent dans ce salon !`;
    return;
  }

  state.joinResolved = true;
  clearTimeout(state.joinTimeout);

  $("modalError").textContent = "";
  $("joinRoomBtnText").textContent = "Rejoindre le salon";
  $("roomCodePill").classList.remove("hidden");
  $("roomCodePill").classList.add("flex");
  $("headerRoomCode").textContent = state.roomCode;
  window.closeOnboardingModal?.();

  const me = state.players[state.myId];
  if (me) {
    me.sessionPoints = 0;
    me.sessionWins = 0;
  }
  state.players = { ...(snapshot.players || {}), [state.myId]: me };
  state.roomBestScorePct = snapshot.roomBestScorePct || 0;
  state.roomBestRank = snapshot.roomBestRank || 0;
  state.roundFinished = !!snapshot.roundFinished;

  const roomMode = snapshot.gameMode || "classic";
  window.loadGame?.(snapshot.gameId || state.currentGameId, snapshot.roundNumber || 1, snapshot.guesses || [], roomMode);
  window.renderLeaderboard?.();

  publishRoomEvent({ type: "PLAYER_JOINED", player: me }, false);
  publishRetainedRoomSnapshot();
  showToast(`Connecté au salon ${state.roomCode} !`, "sky");
}

export function handleNetworkPayload(data) {
  if (data.type === "STATE_SNAPSHOT") {
    if (data.ts && Date.now() - data.ts > 12 * 3600 * 1000) return;
    if (!state.isHost && !state.joinResolved) {
      completeJoinSuccess(data);
      return;
    }
    if (data.players) {
      Object.entries(data.players).forEach(([id, pl]) => {
        if (id !== state.myId) state.players[id] = pl;
      });
      window.renderLeaderboard?.();
    }
    if (data.guesses && Array.isArray(data.guesses)) {
      data.guesses.forEach(g => {
        if (!state.guesses.some(localG => localG.word === g.word)) {
          window.applySharedGuess?.({
            type: "SHARED_GUESS",
            playerId: g.finderId,
            pseudo: g.finderPseudo,
            word: g.word,
            temp: g.temp,
            rank: g.rank,
            scorePct: g.scorePct,
            isWin: g.isWin || g.rank === 1000,
            isTop10: g.isTop10,
            ts: g.ts
          }, false);
        }
      });
    }
    return;
  }

  if (data.type === "JOIN_REQUEST" && data.player) {
    if (data.player.id !== state.myId && (state.isHost || state.joinResolved)) {
      publishRetainedRoomSnapshot();
    }
    return;
  }

  if (data.type === "PLAYER_JOINED" && data.player) {
    if (data.player.id !== state.myId) {
      state.players[data.player.id] = {
        ...data.player,
        pseudo: String(data.player.pseudo || "Joueur").slice(0, 16),
        sessionPoints: Number(data.player.sessionPoints) || 0,
        sessionWins: Number(data.player.sessionWins) || 0,
        gold: Number(data.player.gold) || 0,
        bestScorePct: state.players[data.player.id]?.bestScorePct || 0,
        bestRank: state.players[data.player.id]?.bestRank || 0,
        attempts: state.players[data.player.id]?.attempts || 0
      };
      const joinMsg = `${state.players[data.player.id].pseudo} a rejoint le salon`;
      window.addSystemFeedEvent?.(joinMsg);
      window.updateLiveTicker?.(joinMsg);
      window.renderLeaderboard?.();
      if (state.isHost) publishRetainedRoomSnapshot();
    }
    return;
  }

  if (data.type === "SHARED_GUESS" && data.playerId !== state.myId) {
    window.applySharedGuess?.(data, false);
    return;
  }

  if (data.type === "NEW_ROUND" && data.senderId !== state.myId) {
    if (data.players) {
      Object.entries(data.players).forEach(([id, pl]) => {
        if (id !== state.myId) state.players[id] = pl;
      });
    }
    window.loadGame?.(data.gameId, data.roundNumber, [], data.gameMode || state.currentGameMode);
    window.renderLeaderboard?.();
    return;
  }

  if (data.type === "ROUND_GIVEN_UP" && data.senderId !== state.myId) {
    state.roundFinished = true;
    window.updateHintButtonUI?.();
    window.showVictoryBanner?.("Abandon", data.secretWord, state.guesses.length, true);
    window.addSystemFeedEvent?.(`Mot révélé : ${data.secretWord.toUpperCase()}`);
    window.updateLiveTicker?.(`Réponse : ${data.secretWord.toUpperCase()}`);
  }
}

export const copyRoomCode = () => {
  if (state.roomCode) {
    navigator.clipboard?.writeText(state.roomCode);
    showToast(`Code "${state.roomCode}" copié !`, "sky");
  }
};
