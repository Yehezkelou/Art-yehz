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
//   outils.pas12(t)           t ramené au pas de 1/12 s inférieur (persos animés à 12 i/s dans une vidéo à 24)
//   outils.voxel              voxels : charger(.vox), maillage(grille, {rampe, contour, occlusion, centre}), rig(parties,
//                             rigToml), chargerRig(.rig.toml), grille(lx, ly, lz), rampe(i), lireToml… (voir voxel.mjs)
//   outils.texturePixel(chemin, {repeter = false})   THREE.Texture d'un PNG du dépôt (« assets/… » ou « ./… » relatif à la
//                             scène) : NearestFilter, sans mipmaps, sRGB ; chargée avant la 1re image (outils.attendre)
//   outils.halo(rayon, couleurs, {segments = 48, interieur = 0, camera = false})   THREE.Group d'anneaux plats pleins
//                             (couleurs du centre vers le bord, largeurs égales) dans le plan XY ; camera : toujours de face
//   outils.attendre()         Promise : fin des chargements en cours (la page l'attend avant chaque image)
//
// Le module ne dépend que de THREE (injecté) : il tourne dans la page de rendu, pas dans Node.

import { fabriquerVoxel } from "./voxel.mjs";

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

export function pas12(t) {
  return Math.floor(t * 12 + 1e-6) / 12;
}

export function fabriquerOutils(THREE, { palette, glyphes, largeur, hauteur, ips, scene = "/scene/" }) {
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

  const voxel = fabriquerVoxel(THREE, { couleur, scene });

  const enCours = new Set();
  function suivre(promesse) {
    const p = promesse.finally(() => enCours.delete(p));
    enCours.add(p);
    return p;
  }
  async function attendre() {
    while (enCours.size) await Promise.all([...enCours]);
  }

  const erreursTexture = [];
  function texturePixel(chemin, { repeter = false } = {}) {
    const adresse = voxel.url(chemin);
    const tex = new THREE.Texture();
    tex.name = String(chemin);
    tex.magFilter = THREE.NearestFilter;
    tex.minFilter = THREE.NearestFilter;
    tex.generateMipmaps = false;
    tex.colorSpace = THREE.SRGBColorSpace;
    if (repeter) tex.wrapS = tex.wrapT = THREE.RepeatWrapping;
    suivre(new Promise((ok, ko) => {
      const img = new Image();
      img.onload = () => { tex.image = img; tex.needsUpdate = true; ok(); };
      img.onerror = () => ko(new Error(`rendu3d : texturePixel : « ${chemin} » introuvable ou illisible`));
      img.src = adresse;
    }).catch((e) => { erreursTexture.push(e); }));
    return tex;
  }
  async function attendreTout() {
    await attendre();
    if (erreursTexture.length) throw erreursTexture[0];
  }

  function halo(rayon, couleurs, { segments = 48, interieur = 0, camera = false } = {}) {
    if (!(rayon > 0)) throw new Error(`rendu3d : halo : rayon ${rayon} (> 0)`);
    if (!Array.isArray(couleurs) || !couleurs.length) throw new Error("rendu3d : halo : liste de couleurs (index 1–32) attendue");
    if (!(interieur >= 0 && interieur < rayon)) throw new Error(`rendu3d : halo : interieur ${interieur} (0 ≤ interieur < rayon)`);
    const g = new THREE.Group();
    g.name = "halo";
    const n = couleurs.length, pas = (rayon - interieur) / n;
    const q = new THREE.Quaternion();
    let derniere = null;
    const tourner = (renderer, _s, cam) => {
      const marque = `${renderer.info.render.frame}:${cam.uuid}`;
      if (marque === derniere) return;
      derniere = marque;
      if (g.parent) g.parent.getWorldQuaternion(q).invert(); else q.identity();
      g.quaternion.copy(q.multiply(cam.getWorldQuaternion(new THREE.Quaternion())));
      g.updateMatrixWorld(true);
    };
    couleurs.forEach((c, k) => {
      const r0 = interieur + k * pas, r1 = interieur + (k + 1) * pas;
      const geo = r0 === 0 ? new THREE.CircleGeometry(r1, segments) : new THREE.RingGeometry(r0, r1, segments, 1);
      const m = new THREE.Mesh(geo, new THREE.MeshBasicMaterial({ color: couleur(c), side: THREE.DoubleSide }));
      m.name = `anneau ${k}`;
      if (camera) m.onBeforeRender = tourner;
      g.add(m);
    });
    return g;
  }

  return Object.freeze({
    palette: pal, couleur, materiau, voxelTexte, hasard, lisse, entre, ressort, pas12,
    voxel, texturePixel, halo, attendre: attendreTout,
    largeur, hauteur, ips,
  });
}
