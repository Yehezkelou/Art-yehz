// ico-vid : boîte à outils passée aux scènes de rendu3d (deuxième argument de creer(THREE, outils, params)).
//
//   outils.palette            les 32 couleurs « #RRGGBB » de bible/palette/ico-pixel-32.hex (palette[0] = couleur 1)
//   outils.couleur(i)         couleur i (1–32, ordre du .hex) → THREE.Color
//   outils.materiau(i, {ombre = "toon"})   matériau mat de la couleur i :
//                             "toon" ou true → MeshToonMaterial à 3 paliers (dégradé sans filtrage),
//                             "lambert" → MeshLambertMaterial, false ou "plat" → MeshBasicMaterial (couleur exacte)
//   outils.voxelTexte(texte, {cube = 1, profondeur = 1, couleur = 8, ombre = "toon"})
//                             THREE.Group centré sur l'origine : un sous-groupe par caractère (userData.caractere,
//                             userData.index), un cube par « # » des glyphes ico5x7, 1 colonne entre deux lettres
//   outils.hasard(graine)     générateur reproductible (mulberry32) : () => nombre dans [0, 1)
//   outils.lisse(u)           smoothstep sur [0, 1] (u borné)
//   outils.entre(t, t0, t1)   lisse((t - t0) / (t1 - t0)) ; marche si t1 <= t0
//   outils.ressort(u)         0 → 1 avec dépassement amorti (≈ +12 % vers u = 0,4), exactement 1 à u >= 1
//   outils.largeur, outils.hauteur, outils.ips : taille de la toile et cadence du rendu en cours
//
// Le module ne dépend que de THREE (injecté) : il tourne dans la page de rendu, pas dans Node.

export function hasard(graine) {
  let a = (Math.floor(Number(graine) || 0) >>> 0) || 0x9e3779b9;
  return function () {
    a = (a + 0x6d2b79f5) >>> 0;
    let t = a;
    t = Math.imul(t ^ (t >>> 15), t | 1);
    t ^= t + Math.imul(t ^ (t >>> 7), t | 61);
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
  };
}

export function lisse(u) {
  u = Math.min(1, Math.max(0, u));
  return u * u * (3 - 2 * u);
}

export function entre(t, t0, t1) {
  return t1 > t0 ? lisse((t - t0) / (t1 - t0)) : (t >= t0 ? 1 : 0);
}

export function ressort(u) {
  if (u <= 0) return 0;
  if (u >= 1) return 1;
  return 1 - Math.cos(2.5 * Math.PI * u) * Math.exp(-4 * u) * (1 - u);
}

export function fabriquerOutils(THREE, { palette, glyphes, largeur, hauteur, ips }) {
  if (!Array.isArray(palette) || palette.length !== 32) {
    throw new Error(`rendu3d : palette de ${palette && palette.length} couleurs (32 attendues)`);
  }
  const pal = Object.freeze(palette.map((c) => c.toUpperCase()));

  function verifierIndex(i) {
    if (!Number.isInteger(i) || i < 1 || i > 32) {
      throw new Error(`rendu3d : couleur ${i} hors palette (index entier 1–32, ordre de ico-pixel-32.hex)`);
    }
  }

  function couleur(i) {
    verifierIndex(i);
    return new THREE.Color(pal[i - 1]);
  }

  // Dégradé toon partagé : 3 paliers nets (ombre, mi-ton, lumière), donnée scalaire (pas de colorSpace)
  let degrade = null;
  function degradeToon() {
    if (!degrade) {
      degrade = new THREE.DataTexture(new Uint8Array([90, 170, 255]), 3, 1, THREE.RedFormat);
      degrade.minFilter = THREE.NearestFilter;
      degrade.magFilter = THREE.NearestFilter;
      degrade.generateMipmaps = false;
      degrade.needsUpdate = true;
    }
    return degrade;
  }

  function materiau(i, { ombre = "toon" } = {}) {
    const color = couleur(i);
    if (ombre === true || ombre === "toon") return new THREE.MeshToonMaterial({ color, gradientMap: degradeToon() });
    if (ombre === "lambert") return new THREE.MeshLambertMaterial({ color });
    if (ombre === false || ombre === "plat") return new THREE.MeshBasicMaterial({ color });
    throw new Error(`rendu3d : ombre « ${ombre} » inconnue (toon, lambert, plat/false)`);
  }

  const cubeGeo = new Map();
  function voxelTexte(texte, { cube = 1, profondeur = 1, couleur: c = 8, ombre = "toon" } = {}) {
    texte = String(texte);
    const absents = [...new Set([...texte].filter((ch) => !(ch in glyphes)))];
    if (absents.length) {
      throw new Error(`rendu3d : voxelTexte(« ${texte} ») : caractère(s) absent(s) de ico5x7 : `
        + absents.map((ch) => `« ${ch} »`).join(", ") + ` (disponibles : ${Object.keys(glyphes).join("")})`);
    }
    const cle = `${cube}x${profondeur}`;
    if (!cubeGeo.has(cle)) cubeGeo.set(cle, new THREE.BoxGeometry(cube, cube, cube * profondeur));
    const geo = cubeGeo.get(cle);
    const mat = materiau(c, { ombre });
    const chars = [...texte];
    const largeurs = chars.map((ch) => glyphes[ch][0].length);
    const total = largeurs.reduce((s, l) => s + l + 1, 0) - (chars.length ? 1 : 0);
    const H = 7;
    const groupe = new THREE.Group();
    groupe.name = `voxelTexte ${texte}`;
    let x0 = 0;
    chars.forEach((ch, k) => {
      const g = new THREE.Group();
      g.name = ch;
      g.userData = { caractere: ch, index: k };
      const lignes = glyphes[ch];
      // centre de la colonne du milieu du glyphe, pour que chaque lettre tourne sur elle-même
      const cx = (x0 + (largeurs[k] - 1) / 2 - (total - 1) / 2) * cube;
      g.position.set(cx, 0, 0);
      lignes.forEach((ligne, y) => {
        [...ligne].forEach((p, x) => {
          if (p !== "#") return;
          const m = new THREE.Mesh(geo, mat);
          m.position.set((x - (largeurs[k] - 1) / 2) * cube, ((H - 1) / 2 - y) * cube, 0);
          g.add(m);
        });
      });
      groupe.add(g);
      x0 += largeurs[k] + 1;
    });
    return groupe;
  }

  return Object.freeze({
    palette: pal, couleur, materiau, voxelTexte, hasard, lisse, entre, ressort,
    largeur, hauteur, ips,
  });
}
