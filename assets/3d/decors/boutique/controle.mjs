// ico-vid : scène de contrôle du diorama « boutique du marchand » devant le ciel couchant.
// Orbite lente en plan large, puis rapprochement sur la vitrine ; les cartes du ciel glissent avec l'orbite (parallaxe).
//
//   python3 -I assets/3d/decors/boutique/boutique.py && python3 -I assets/3d/ciels/couchant/couchant.py
//   node outils/rendu3d/rendu3d.mjs --scene assets/3d/decors/boutique/controle.mjs --out <dossier> --debut 0 --fin 10 --ips 12
//
// params : { "duree": 10, "orbite": 0.55, "bascule": 6, "plan": "les-deux" | "large" | "rapproche", "ciel": true }
// Lit boutique.scene.toml (parties, lumières, cadrages) et couchant.toml (couches, profondeurs).

const DECOR = "assets/3d/decors/boutique/";
const CIEL = "assets/3d/ciels/couchant/";

export default async function creer(THREE, outils, params = {}) {
  const p = { duree: 10, orbite: 0.55, bascule: 6, plan: "les-deux", ciel: true, ...params };
  const V = outils.voxel;
  const texte = async (c) => {
    const r = await fetch(V.url(c));
    if (!r.ok) throw new Error(`controle : « ${c} » introuvable (HTTP ${r.status})`);
    return r.text();
  };

  const scene = new THREE.Scene();
  scene.background = outils.couleur(1);
  const camera = new THREE.PerspectiveCamera(24, outils.largeur / outils.hauteur, 1, 1000);

  // ---- diorama : parties posées par boutique.scene.toml
  const def = V.lireToml(await texte(DECOR + "boutique.scene.toml"));
  const [cx, cy, cz] = def.centre;
  const fichiers = new Map();
  for (const part of def.partie) {
    if (!fichiers.has(part.fichier)) fichiers.set(part.fichier, await V.charger(DECOR + part.fichier));
    const g = fichiers.get(part.fichier).find((m) => m.nom === part.modele);
    if (!g) throw new Error(`controle : modèle « ${part.modele} » absent de ${part.fichier}`);
    const mesh = V.maillage(g, { centre: "coin", occlusion: def.occlusion ?? 2 });
    mesh.position.set(part.origine[0] - cx, part.origine[1] - cy, part.origine[2] - cz);
    scene.add(mesh);
  }
  // ---- lumières : halo pixel (anneaux pleins de la palette), face caméra ; la lanterne vacille par paliers
  const halos = [];
  for (const l of def.lumiere || []) {
    const h = l.halo;
    const variantes = [h.rayon, h.rayon - 0.5].map((r) => outils.halo(r, h.couleurs, { interieur: h.interieur, camera: true }));
    const g = new THREE.Group();
    variantes.forEach((v) => g.add(v));
    g.position.set(l.position[0] - cx, l.position[1] - cy, l.position[2] - cz);
    scene.add(g);
    halos.push({ nom: l.nom, variantes });
  }

  // ---- ciel : cartes empilées dans un canevas 270 × 480 (fond de scène), décalées selon l'angle d'orbite
  const ciel = V.lireToml(await texte(CIEL + "couchant.toml"));
  const toile = document.createElement("canvas");
  toile.width = ciel.largeur; toile.height = ciel.hauteur;
  const ctx = toile.getContext("2d");
  ctx.imageSmoothingEnabled = false;
  const couches = ciel.couche.map((c) => ({ ...c, tex: outils.texturePixel(CIEL + c.fichier) }));
  const fond = new THREE.CanvasTexture(toile);
  fond.magFilter = fond.minFilter = THREE.NearestFilter;
  fond.generateMipmaps = false;
  fond.colorSpace = THREE.SRGBColorSpace;
  if (p.ciel) scene.background = fond;
  function peindreCiel(angle) {
    ctx.clearRect(0, 0, toile.width, toile.height);
    for (const c of couches) {
      const img = c.tex.image;
      const dx = Math.round(-ciel.glissement * c.profondeur * angle);
      ctx.drawImage(img, Math.round((toile.width - img.width) / 2) + dx, 0);
    }
    fond.needsUpdate = true;
  }

  // ---- caméra : plan large en orbite, puis rapprochement sur la vitrine (fondu de cadrage en 1 s)
  const L = def.cadrage.large, R = def.cadrage.rapproche;
  const lisse = (u) => u * u * (3 - 2 * u);
  function update(t) {
    const u = t / p.duree;
    const angle = p.orbite * Math.sin(2 * Math.PI * (u - 0.25)) * -1;   // −orbite → +orbite → retour
    let k = p.plan === "large" ? 0 : p.plan === "rapproche" ? 1 : lisse(Math.min(1, Math.max(0, t - p.bascule)));
    const mix = (a, b) => a + (b - a) * k;
    const cible = [0, 1, 2].map((i) => mix(L.cible[i], R.cible[i]));
    const d = mix(L.distance, R.distance), h = mix(L.hauteur, R.hauteur);
    const a = angle * mix(1, 0.6);
    camera.position.set(cible[0] + Math.sin(a) * d, cible[1] + h, cible[2] + Math.cos(a) * d);
    camera.lookAt(cible[0], cible[1], cible[2]);
    peindreCiel(a);
    const vacille = Math.floor(t * 6) % 5 === 3 ? 1 : 0;   // un pas sur cinq, à 6 i/s
    for (const h of halos) h.variantes.forEach((v, i) => { v.visible = i === (h.nom === "lanterne" ? vacille : 0); });
  }

  return { scene, camera, update };
}
