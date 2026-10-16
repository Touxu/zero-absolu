// =========================================================================
// MOTEUR DE PARTICULES THERMIQUES AVANCÉ (CANVAS VECTORIEL GPU PUR)
// - Fini les confettis normaux !
// - Durées prolongées et majestueuses (2.5 à 5 secondes)
// - Givre (<40%) : Vrais flocons de neige géométriques à 6 branches
// - Flammèches (40-89%) : Flammes ardentes dansantes & braises montantes
// - Lave/Magma (90-99%) : Éruption volcanique de lave & gerbes de braises incandescentes
// - Fusion Solaire (100%) : Étoiles solaires à 8 branches, ondes de choc dorées & rayons de photons
// =========================================================================

class ThermalParticleEngine {
  constructor() {
    this.canvas = null;
    this.ctx = null;
    this.particles = [];
    this.shockwaves = [];
    this.animId = null;
    this.lastTime = performance.now();

    if (document.readyState === "loading") {
      window.addEventListener("DOMContentLoaded", () => this.initCanvas());
    } else {
      this.initCanvas();
    }
  }

  initCanvas() {
    this.canvas = document.getElementById("thermalFxCanvas");
    if (!this.canvas) {
      this.canvas = document.createElement("canvas");
      this.canvas.id = "thermalFxCanvas";
      this.canvas.className = "fixed inset-0 pointer-events-none z-[60] w-full h-full";
      document.body.appendChild(this.canvas);
    }
    this.ctx = this.canvas.getContext("2d");
    this.resize();
    window.addEventListener("resize", () => this.resize());
  }

  resize() {
    if (!this.canvas) return;
    const dpr = Math.min(window.devicePixelRatio || 1, 2);
    this.canvas.width = window.innerWidth * dpr;
    this.canvas.height = window.innerHeight * dpr;
    this.ctx?.scale(dpr, dpr);
  }

  startLoop() {
    if (this.animId) return;
    this.lastTime = performance.now();
    const frame = () => {
      this.updateAndDraw();
      if (this.particles.length > 0 || this.shockwaves.length > 0) {
        this.animId = requestAnimationFrame(frame);
      } else {
        this.ctx?.clearRect(0, 0, window.innerWidth, window.innerHeight);
        this.animId = null;
      }
    };
    this.animId = requestAnimationFrame(frame);
  }

  // Déclencheur principal d'effets thermiques
  trigger(targetEl, scorePct, isWin = false, rankOrTop10 = null) {
    if (!this.canvas) this.initCanvas();
    let cx = window.innerWidth / 2;
    let cy = window.innerHeight / 2;
    if (targetEl && typeof targetEl.getBoundingClientRect === "function") {
      const rect = targetEl.getBoundingClientRect();
      if (rect.width > 0 && rect.height > 0) {
        cx = rect.left + rect.width / 2;
        cy = Math.max(50, Math.min(window.innerHeight - 50, rect.top + rect.height / 2));
      }
    }
    const pct = Number(scorePct) || 0;
    const rankNum = typeof rankOrTop10 === "number" ? rankOrTop10 : null;

    const isSecretWord = isWin || rankNum === 1000 || (rankNum === null && pct >= 100);

    if (isSecretWord && (rankNum === 1000 || rankNum === null)) {
      // Palier 4 : Fusion Solaire (100% / Victoire STRICTEMENT)
      this.spawnSolarFusion(cx, cy);
    } else if ((rankNum !== null && rankNum >= 991 && rankNum <= 999) || rankOrTop10 === true || pct >= 90) {
      // Palier 3 : Magma / Lave (Top 10 à Top 2 : rank 991 à 999)
      // Proportionnel : Top 2 a beaucoup plus de particules que Top 10
      const ratio = rankNum !== null ? Math.max(0, Math.min(1, (rankNum - 991) / 8)) : 0.5;
      this.spawnMagmaEruption(cx, cy, ratio);
    } else if (rankNum !== null && rankNum >= 901 && rankNum <= 990) {
      // Palier 2 : Flammèches vives (Top 100 à Top 11 : rank 901 à 990)
      // Proportionnel au rang : plus proche du Top 11 = plus de flammes
      const ratio = Math.max(0, Math.min(1, (rankNum - 901) / 89));
      this.spawnFlames(cx, cy, ratio);
    } else {
      // Palier 1 : Givre / Flocons (< Top 100 / Froid)
      // Inversément proportionnel : beaucoup plus de flocons quand proche de 0% que de 40%
      const coldRatio = pct <= 0 ? 1.0 : (pct >= 40 ? 0.0 : (40 - pct) / 40);
      this.spawnFrost(cx, cy, coldRatio);
    }

    this.startLoop();
  }

  // 1. PALIER FROID : FLOCONS GÉOMÉTRIQUES & CRISTAUX DE GLACE
  // Durée : ~3.5 à 4.5 secondes - Beaucoup plus de flocons vers 0% (blizzard) que vers 40%
  spawnFrost(x, y, coldRatio = 0.5) {
    const count = Math.round(10 + coldRatio * 38); // 10 flocons à 40% -> 48 flocons à 0%
    for (let i = 0; i < count; i++) {
      const angle = (Math.PI * 2 * i) / count + (Math.random() - 0.5) * 0.4;
      const speed = 0.6 + Math.random() * (2.2 + coldRatio * 1.4);
      this.particles.push({
        type: "snowflake",
        x: x + (Math.random() - 0.5) * (40 + coldRatio * 50),
        y: y + (Math.random() - 0.5) * 16,
        vx: Math.cos(angle) * speed * 0.7,
        vy: -0.6 - Math.random() * (1.2 + coldRatio * 1.0),
        gravity: 0.03 + Math.random() * 0.02,
        swayPhase: Math.random() * Math.PI * 2,
        swaySpeed: 0.02 + Math.random() * 0.02,
        swayAmp: 1.0 + Math.random() * (1.2 + coldRatio * 1.5),
        rotation: Math.random() * Math.PI * 2,
        rotSpeed: (Math.random() - 0.5) * 0.03,
        radius: (5 + coldRatio * 3) + Math.random() * (5 + coldRatio * 5),
        alpha: 1.0,
        decay: 0.005 + Math.random() * 0.0035, // Lenteur et persistance
        color: ["#38bdf8", "#7dd3fc", "#bae6fd", "#e0f2fe", "#ffffff"][Math.floor(Math.random() * 5)]
      });
    }
  }

  // 2. PALIER CHALEUR : FLAMMÈCHES VIVES & BRAISES MONTANTES (Top 100 à Top 11)
  // Durée : ~2.5 à 3.5 secondes - Proportionnel au rang
  spawnFlames(x, y, ratio = 0.5) {
    // A. Flammes principales dansantes (18 à 52)
    const flameCount = Math.round(18 + ratio * 34);
    for (let i = 0; i < flameCount; i++) {
      this.particles.push({
        type: "flame",
        x: x + (Math.random() - 0.5) * (45 + ratio * 35),
        y: y + (Math.random() - 0.5) * 12,
        vx: (Math.random() - 0.5) * (2.0 + ratio * 1.2),
        vy: -2.0 - Math.random() * (3.0 + ratio * 2.0),
        buoyancy: -0.025 - ratio * 0.015,
        turbPhase: Math.random() * Math.PI * 2,
        turbSpeed: 0.06 + Math.random() * 0.05,
        size: (8 + ratio * 3) + Math.random() * (10 + ratio * 4),
        alpha: 1.0,
        decay: 0.006 + Math.random() * 0.004,
        color: ["#facc15", "#f59e0b", "#f97316", "#fb923c", "#ef4444"][Math.floor(Math.random() * 5)]
      });
    }

    // B. Micro-braises dorées ascendantes (10 à 28)
    const emberCount = Math.round(10 + ratio * 18);
    for (let i = 0; i < emberCount; i++) {
      this.particles.push({
        type: "ember",
        x: x + (Math.random() - 0.5) * 35,
        y: y + (Math.random() - 0.5) * 10,
        vx: (Math.random() - 0.5) * 2.0,
        vy: -2.5 - Math.random() * (3.5 + ratio * 1.5),
        buoyancy: -0.015,
        size: 2.0 + Math.random() * 2.6,
        alpha: 1.0,
        decay: 0.005 + Math.random() * 0.003,
        color: ["#fef08a", "#facc15", "#f59e0b"][Math.floor(Math.random() * 3)]
      });
    }
  }

  // 3. PALIER MAGMA : ÉRUPTION VOLCANIQUE & LAVE ARDENTE (Top 10 à Top 2)
  // Durée : ~3.5 à 4.5 secondes - Proportionnel au rang (Top 2 en a beaucoup plus que Top 10)
  spawnMagmaEruption(x, y, ratio = 0.5) {
    // A. Roches et boules de lave incandescente (25 à 70)
    const magmaCount = Math.round(25 + ratio * 45);
    for (let i = 0; i < magmaCount; i++) {
      const angle = -Math.PI / 2 + (Math.random() - 0.5) * (1.3 + ratio * 0.4);
      const speed = (5.5 + ratio * 2.5) + Math.random() * (6.5 + ratio * 3.5);
      this.particles.push({
        type: "magma",
        x: x + (Math.random() - 0.5) * (20 + ratio * 20),
        y: y,
        vx: Math.cos(angle) * speed,
        vy: Math.sin(angle) * speed,
        gravity: 0.15 + Math.random() * 0.03,
        radius: (4 + ratio * 3) + Math.random() * (6 + ratio * 5),
        trail: [],
        alpha: 1.0,
        decay: 0.005 + Math.random() * 0.0035,
        coreColor: "#fef08a",
        outerColor: ["#ef4444", "#dc2626", "#b91c1c", "#ea580c"][Math.floor(Math.random() * 4)]
      });
    }

    // B. Éclats de braises volcaniques crépitantes (15 à 40)
    const sparkCount = Math.round(15 + ratio * 25);
    for (let i = 0; i < sparkCount; i++) {
      const angle = (Math.PI * 2 * i) / sparkCount + (Math.random() - 0.5) * 0.35;
      const speed = (3.0 + ratio * 1.5) + Math.random() * (5.0 + ratio * 3.0);
      this.particles.push({
        type: "ember",
        x, y,
        vx: Math.cos(angle) * speed,
        vy: Math.sin(angle) * speed * 0.85,
        gravity: 0.11,
        size: 3 + Math.random() * (3 + ratio * 2),
        alpha: 1.0,
        decay: 0.006 + Math.random() * 0.004,
        color: ["#ffedd5", "#fde047", "#f97316"][Math.floor(Math.random() * 3)]
      });
    }
  }

  // 4. PALIER FUSION SOLAIRE : ÉTOILES SOLAIRES, RAYONS & ONDES DE PLASMA (100%)
  // Durée : ~4.0 à 5.5 secondes (AUCUN CONFETTI)
  spawnSolarFusion(x, y) {
    // A. 2 Ondes de choc circulaires concentriques
    this.shockwaves.push({
      x, y,
      radius: 12,
      maxRadius: Math.max(window.innerWidth, window.innerHeight) * 0.65,
      speed: 12,
      lineWidth: 9,
      alpha: 1.0,
      color: "#fef08a"
    });
    this.shockwaves.push({
      x, y,
      radius: 5,
      maxRadius: Math.max(window.innerWidth, window.innerHeight) * 0.45,
      speed: 8,
      lineWidth: 5,
      alpha: 1.0,
      color: "#facc15"
    });

    // B. Étoiles solaires à 8 branches et éclats de photons
    const starCount = 65;
    for (let i = 0; i < starCount; i++) {
      const angle = (Math.PI * 2 * i) / starCount + (Math.random() - 0.5) * 0.35;
      const speed = 3.5 + Math.random() * 8.5;
      this.particles.push({
        type: "sunStar",
        x, y,
        vx: Math.cos(angle) * speed,
        vy: Math.sin(angle) * speed,
        friction: 0.978, // Décélération très douce
        rotation: Math.random() * Math.PI,
        rotSpeed: (Math.random() - 0.5) * 0.04,
        spikes: Math.random() > 0.35 ? 8 : 4,
        outerR: 10 + Math.random() * 14,
        innerR: 4 + Math.random() * 5,
        alpha: 1.0,
        decay: 0.0045 + Math.random() * 0.003, // ~4 à 5 secondes
        color: ["#ffffff", "#fef08a", "#facc15", "#f59e0b"][Math.floor(Math.random() * 4)]
      });
    }

    // C. Rayons de plasma solaire
    const beamCount = 30;
    for (let i = 0; i < beamCount; i++) {
      const angle = Math.random() * Math.PI * 2;
      const speed = 2.0 + Math.random() * 5.0;
      this.particles.push({
        type: "sunRay",
        x, y,
        vx: Math.cos(angle) * speed,
        vy: Math.sin(angle) * speed,
        length: 20 + Math.random() * 30,
        angle,
        alpha: 1.0,
        decay: 0.005 + Math.random() * 0.003,
        color: "#fef08a"
      });
    }
  }

  // Mise à jour de la physique et rendu graphique
  updateAndDraw() {
    const ctx = this.ctx;
    if (!ctx) return;
    ctx.clearRect(0, 0, window.innerWidth, window.innerHeight);

    // 1. Dessin des ondes de choc de fusion
    for (let i = this.shockwaves.length - 1; i >= 0; i--) {
      const sw = this.shockwaves[i];
      sw.radius += sw.speed;
      sw.alpha = Math.max(0, 1.0 - sw.radius / sw.maxRadius);
      sw.lineWidth = Math.max(1, 9 * sw.alpha);

      ctx.save();
      ctx.beginPath();
      ctx.arc(sw.x, sw.y, sw.radius, 0, Math.PI * 2);
      ctx.strokeStyle = sw.color;
      ctx.lineWidth = sw.lineWidth;
      ctx.globalAlpha = sw.alpha * 0.9;
      ctx.shadowColor = "#facc15";
      ctx.shadowBlur = 24;
      ctx.stroke();
      ctx.restore();

      if (sw.alpha <= 0 || sw.radius >= sw.maxRadius) {
        this.shockwaves.splice(i, 1);
      }
    }

    // 2. Dessin des particules thématiques
    for (let i = this.particles.length - 1; i >= 0; i--) {
      const p = this.particles[i];
      p.alpha -= p.decay;

      if (p.alpha <= 0) {
        this.particles.splice(i, 1);
        continue;
      }

      ctx.save();
      ctx.globalAlpha = Math.max(0, p.alpha);

      switch (p.type) {
        case "snowflake":
          this.drawSnowflake(ctx, p);
          break;
        case "flame":
          this.drawFlame(ctx, p);
          break;
        case "ember":
          this.drawEmber(ctx, p);
          break;
        case "magma":
          this.drawMagma(ctx, p);
          break;
        case "sunStar":
          this.drawSunStar(ctx, p);
          break;
        case "sunRay":
          this.drawSunRay(ctx, p);
          break;
      }

      ctx.restore();
    }
  }

  // Traceur vectoriel de flocon de neige à 6 branches
  drawSnowflake(ctx, p) {
    p.swayPhase += p.swaySpeed;
    p.x += p.vx + Math.sin(p.swayPhase) * p.swayAmp;
    p.y += p.vy;
    p.vy += p.gravity;
    p.rotation += p.rotSpeed;

    ctx.translate(p.x, p.y);
    ctx.rotate(p.rotation);
    ctx.strokeStyle = p.color;
    ctx.fillStyle = p.color;
    ctx.lineWidth = 1.8;
    ctx.lineCap = "round";
    ctx.shadowColor = "#38bdf8";
    ctx.shadowBlur = 8;

    const r = p.radius;
    for (let i = 0; i < 6; i++) {
      ctx.save();
      ctx.rotate((Math.PI / 3) * i);
      ctx.beginPath();
      ctx.moveTo(0, 0);
      ctx.lineTo(0, -r);
      // Ramifications en V
      ctx.moveTo(0, -r * 0.55);
      ctx.lineTo(-r * 0.3, -r * 0.82);
      ctx.moveTo(0, -r * 0.55);
      ctx.lineTo(r * 0.3, -r * 0.82);
      ctx.stroke();
      ctx.restore();
    }
    // Cristal central
    ctx.beginPath();
    ctx.arc(0, 0, 2.0, 0, Math.PI * 2);
    ctx.fill();
  }

  // Traceur vectoriel de flammèche ardente
  drawFlame(ctx, p) {
    p.turbPhase += p.turbSpeed;
    p.x += p.vx + Math.sin(p.turbPhase) * 1.1;
    p.y += p.vy;
    p.vy += p.buoyancy;
    p.size = Math.max(1, p.size * 0.992);

    ctx.translate(p.x, p.y);
    ctx.shadowColor = p.color;
    ctx.shadowBlur = 14;

    // Corps de la flamme en goutte étirée
    ctx.beginPath();
    const s = p.size;
    ctx.moveTo(0, -s * 1.6);
    ctx.quadraticCurveTo(s * 0.85, -s * 0.2, s * 0.55, s * 0.65);
    ctx.quadraticCurveTo(0, s * 1.15, -s * 0.55, s * 0.65);
    ctx.quadraticCurveTo(-s * 0.85, -s * 0.2, 0, -s * 1.6);
    ctx.fillStyle = p.color;
    ctx.fill();

    // Cœur incandescent blanc/jaune
    ctx.beginPath();
    ctx.arc(0, s * 0.45, s * 0.38, 0, Math.PI * 2);
    ctx.fillStyle = "#fef08a";
    ctx.fill();
  }

  // Traceur de micro-braises / étincelles
  drawEmber(ctx, p) {
    p.x += p.vx;
    p.y += p.vy;
    if (p.buoyancy) p.vy += p.buoyancy;
    if (p.gravity) p.vy += p.gravity;

    ctx.translate(p.x, p.y);
    ctx.shadowColor = p.color;
    ctx.shadowBlur = 8;
    ctx.beginPath();
    ctx.arc(0, 0, p.size, 0, Math.PI * 2);
    ctx.fillStyle = p.color;
    ctx.fill();
  }

  // Traceur de goutte de lave incandescente
  drawMagma(ctx, p) {
    p.x += p.vx;
    p.y += p.vy;
    p.vy += p.gravity;

    ctx.translate(p.x, p.y);
    ctx.shadowColor = p.outerColor;
    ctx.shadowBlur = 16;

    // Cœur en fusion
    const grad = ctx.createRadialGradient(0, 0, 1, 0, 0, p.radius);
    grad.addColorStop(0, p.coreColor);
    grad.addColorStop(0.55, p.outerColor);
    grad.addColorStop(1, "rgba(69, 10, 10, 0.85)");

    ctx.beginPath();
    ctx.arc(0, 0, p.radius, 0, Math.PI * 2);
    ctx.fillStyle = grad;
    ctx.fill();
  }

  // Traceur d'étoile solaire à 4 ou 8 branches
  drawSunStar(ctx, p) {
    p.x += p.vx;
    p.y += p.vy;
    p.vx *= p.friction;
    p.vy *= p.friction;
    p.rotation += p.rotSpeed;

    ctx.translate(p.x, p.y);
    ctx.rotate(p.rotation);
    ctx.shadowColor = "#facc15";
    ctx.shadowBlur = 20;

    const spikes = p.spikes;
    const outerR = p.outerR;
    const innerR = p.innerR;
    let rot = (Math.PI / 2) * 3;
    const step = Math.PI / spikes;

    ctx.beginPath();
    ctx.moveTo(0, -outerR);
    for (let i = 0; i < spikes; i++) {
      let x = Math.cos(rot) * outerR;
      let y = Math.sin(rot) * outerR;
      ctx.lineTo(x, y);
      rot += step;

      x = Math.cos(rot) * innerR;
      y = Math.sin(rot) * innerR;
      ctx.lineTo(x, y);
      rot += step;
    }
    ctx.lineTo(0, -outerR);
    ctx.closePath();

    ctx.fillStyle = p.color;
    ctx.fill();

    // Halo central blanc éclatant
    ctx.beginPath();
    ctx.arc(0, 0, innerR * 0.9, 0, Math.PI * 2);
    ctx.fillStyle = "#ffffff";
    ctx.fill();
  }

  // Traceur de rayon de plasma solaire
  drawSunRay(ctx, p) {
    p.x += p.vx;
    p.y += p.vy;

    ctx.translate(p.x, p.y);
    ctx.rotate(p.angle);
    ctx.strokeStyle = p.color;
    ctx.lineWidth = 2.2;
    ctx.lineCap = "round";
    ctx.shadowColor = "#facc15";
    ctx.shadowBlur = 12;

    ctx.beginPath();
    ctx.moveTo(0, 0);
    ctx.lineTo(p.length, 0);
    ctx.stroke();
  }
}

export const thermalParticles = new ThermalParticleEngine();
