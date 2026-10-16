// =========================================================================
// ZÉROABSOLU — POINT D'ENTRÉE DE COMPATIBILITÉ
// L'architecture modulaire ES est désormais distribuée dans js/ :
// - js/constants.js   : Configurations, tiers et helpers
// - js/state.js       : Store d'état centralisé
// - js/engine.js      : Moteur sémantique, vecteurs et normalisation
// - js/auth.js        : Supabase, hachage SHA-256 et profils
// - js/multiplayer.js : Multijoueur WSS MQTT et salons
// - js/ui.js          : Rendu DOM, modales et animations
// - js/app.js         : Contrôleur applicatif et bootstrap
// =========================================================================
import "./js/app.js";