// =========================================================================
// MODULE AUDIO & SOUND DESIGN (WEB AUDIO API + HOWLER)
// =========================================================================
import { $, showToast } from "./ui.js";

class SoundEngine {
  constructor() {
    this.ctx = null;
    this.isMuted = localStorage.getItem("zeroabsolu_sound_muted") === "true";
  }

  ensureContext() {
    if (this.isMuted) return null;
    if (!this.ctx) {
      const AudioCtx = window.AudioContext || window.webkitAudioContext;
      if (AudioCtx) {
        this.ctx = new AudioCtx();
      }
    }
    if (this.ctx && this.ctx.state === "suspended") {
      this.ctx.resume().catch(() => {});
    }
    return this.ctx;
  }

  toggleMute() {
    this.isMuted = !this.isMuted;
    localStorage.setItem("zeroabsolu_sound_muted", String(this.isMuted));
    this.updateSoundButtonUI();
    showToast(this.isMuted ? "Sons désactivés 🔇" : "Sons activés 🔊", "sky");
  }

  updateSoundButtonUI() {
    const btn = $("soundToggleBtn");
    const icon = $("soundToggleIcon");
    if (!btn || !icon) return;
    if (this.isMuted) {
      btn.className = "w-8 h-8 flex items-center justify-center rounded-lg bg-slate-900 border border-slate-800 text-slate-500 hover:text-slate-300 transition shrink-0";
      icon.className = "ph-duotone ph-speaker-slash text-base";
      btn.title = "Activer les sons";
    } else {
      btn.className = "w-8 h-8 flex items-center justify-center rounded-lg bg-amber-500/15 border border-amber-500/30 text-amber-300 hover:bg-amber-500/25 transition shrink-0";
      icon.className = "ph-duotone ph-speaker-high text-base";
      btn.title = "Couper les sons";
    }
  }

  // Bip thermique à la soumission d'un mot
  playGuessSound(scorePct, isWin = false, isTop10 = false) {
    const ctx = this.ensureContext();
    if (!ctx) return;

    if (isWin) {
      this.playSolarFusionFanfare();
      return;
    }
    if (isTop10) {
      this.playMagmaChord();
      return;
    }

    const now = ctx.currentTime;
    const osc = ctx.createOscillator();
    const gain = ctx.createGain();

    // Fréquence calculée selon la température (180 Hz pour froid jusqu'à 880 Hz pour très chaud)
    const normalized = Math.max(0, Math.min(100, scorePct)) / 100;
    const startFreq = 180 + Math.pow(normalized, 1.8) * 650;
    const endFreq = startFreq + (normalized > 0.6 ? 120 : -20);

    osc.type = normalized > 0.7 ? "triangle" : "sine";
    osc.frequency.setValueAtTime(startFreq, now);
    osc.frequency.exponentialRampToValueAtTime(Math.max(60, endFreq), now + 0.16);

    gain.gain.setValueAtTime(0.001, now);
    gain.gain.linearRampToValueAtTime(0.18, now + 0.02);
    gain.gain.exponentialRampToValueAtTime(0.001, now + 0.22);

    osc.connect(gain);
    gain.connect(ctx.destination);

    osc.start(now);
    osc.stop(now + 0.24);
  }

  // Son accord Magma (Top 10)
  playMagmaChord() {
    const ctx = this.ensureContext();
    if (!ctx) return;
    const now = ctx.currentTime;
    const freqs = [440, 554.37, 659.25]; // Accord majeur La (A4, C#5, E5)

    freqs.forEach((f, i) => {
      const osc = ctx.createOscillator();
      const gain = ctx.createGain();
      osc.type = "triangle";
      osc.frequency.setValueAtTime(f, now + i * 0.03);

      gain.gain.setValueAtTime(0.001, now);
      gain.gain.linearRampToValueAtTime(0.12, now + 0.04 + i * 0.03);
      gain.gain.exponentialRampToValueAtTime(0.001, now + 0.45);

      osc.connect(gain);
      gain.connect(ctx.destination);

      osc.start(now + i * 0.03);
      osc.stop(now + 0.48);
    });
  }

  // Fanfare cosmique de Fusion Solaire (100% Victoire)
  playSolarFusionFanfare() {
    const ctx = this.ensureContext();
    if (!ctx) return;
    const now = ctx.currentTime;
    const notes = [
      { f: 523.25, t: 0.00 }, // Do
      { f: 659.25, t: 0.10 }, // Mi
      { f: 783.99, t: 0.20 }, // Sol
      { f: 1046.50, t: 0.32, d: 0.7 } // Do aigu
    ];

    notes.forEach(n => {
      const startT = now + n.t;
      const dur = n.d || 0.25;
      const osc = ctx.createOscillator();
      const gain = ctx.createGain();

      osc.type = "sawtooth";
      osc.frequency.setValueAtTime(n.f, startT);

      // Filtre passe-bas pour adoucir le timbre
      const filter = ctx.createBiquadFilter();
      filter.type = "lowpass";
      filter.frequency.setValueAtTime(2200, startT);
      filter.frequency.exponentialRampToValueAtTime(800, startT + dur);

      gain.gain.setValueAtTime(0.001, startT);
      gain.gain.linearRampToValueAtTime(0.18, startT + 0.03);
      gain.gain.exponentialRampToValueAtTime(0.001, startT + dur);

      osc.connect(filter);
      filter.connect(gain);
      gain.connect(ctx.destination);

      osc.start(startT);
      osc.stop(startT + dur + 0.05);
    });
  }

  // Son de percée thermique (Surge)
  playSurgeSound() {
    const ctx = this.ensureContext();
    if (!ctx) return;
    const now = ctx.currentTime;
    const osc = ctx.createOscillator();
    const gain = ctx.createGain();

    osc.type = "triangle";
    osc.frequency.setValueAtTime(240, now);
    osc.frequency.exponentialRampToValueAtTime(720, now + 0.35);

    gain.gain.setValueAtTime(0.001, now);
    gain.gain.linearRampToValueAtTime(0.2, now + 0.05);
    gain.gain.exponentialRampToValueAtTime(0.001, now + 0.4);

    osc.connect(gain);
    gain.connect(ctx.destination);

    osc.start(now);
    osc.stop(now + 0.42);
  }

  // Son de passage de niveau (Level Up)
  playLevelUpSound() {
    const ctx = this.ensureContext();
    if (!ctx) return;
    const now = ctx.currentTime;
    const melody = [587.33, 739.99, 880.00, 1174.66]; // Ré, Fa#, La, Ré

    melody.forEach((f, i) => {
      const t = now + i * 0.08;
      const osc = ctx.createOscillator();
      const gain = ctx.createGain();

      osc.type = "sine";
      osc.frequency.setValueAtTime(f, t);

      gain.gain.setValueAtTime(0.001, t);
      gain.gain.linearRampToValueAtTime(0.15, t + 0.02);
      gain.gain.exponentialRampToValueAtTime(0.001, t + 0.35);

      osc.connect(gain);
      gain.connect(ctx.destination);

      osc.start(t);
      osc.stop(t + 0.38);
    });
  }

  // Son d'achat d'indice
  playHintSound() {
    const ctx = this.ensureContext();
    if (!ctx) return;
    const now = ctx.currentTime;
    const osc = ctx.createOscillator();
    const gain = ctx.createGain();

    osc.type = "sine";
    osc.frequency.setValueAtTime(987.77, now); // Si5
    osc.frequency.exponentialRampToValueAtTime(1318.51, now + 0.22); // Mi6

    gain.gain.setValueAtTime(0.001, now);
    gain.gain.linearRampToValueAtTime(0.16, now + 0.03);
    gain.gain.exponentialRampToValueAtTime(0.001, now + 0.3);

    osc.connect(gain);
    gain.connect(ctx.destination);

    osc.start(now);
    osc.stop(now + 0.32);
  }
}

export const soundManager = new SoundEngine();
