// ico-vid : vitrine 3D (≈ 20 s, 24 i/s, 270 × 480) : présente les premiers modèles voxel pour valider le style.
//
//   node outils/rendu3d/rendu3d.mjs --scene pixel-05-vitrine3d/.montage/3d/vitrine.mjs \
//        --out pixel-05-vitrine3d/.montage/3d/vitrine --debut 0 --fin 20 --ips 24 --fond 0E0D18
//
// Plans (instants exacts dans PLANS ci-dessous et dans agents/rapports/claude/2026-10-22-vitrine3d.md) :
//   1. 0–4 s     ciel couchant + boutique en plan large, la caméra descend et s'approche
//   2. 4–8 s     Tim entre en marchant, s'arrête, se tourne et fait coucou        } plan-séquence continu 0–11 s
//   3. 8–11 s    le marchand bondit de derrière Tim, fait « non » ; Tim en colère  }
//   4. 11–15 s   gros plan potion rouge puis travelling vers la potion bleue
//   5. 15–18 s   le grimoire s'entrouvre, étincelles
//   6. 18–20 s   plan large : Tim et le marchand côte à côte ; la caméra recule jusqu'au cadre de t = 0 (boucle)
// Persos à 12 i/s (clips + positions au pas de 1/12 s) ; caméra lisse à 24 i/s.

import { installer as installerTim } from "/depot/assets/3d/persos/tim/tim.clips.mjs";
import { installer as installerMarchand } from "/depot/assets/3d/persos/marchand/marchand.clips.mjs";

const DECOR = "assets/3d/decors/boutique/";
const CIEL = "assets/3d/ciels/couchant/";
const POTION = "assets/3d/objets/potion/";
const GRIMOIRE = "assets/3d/objets/grimoire/grimoire.vox";
const TEXTURE_GRIMOIRE = "assets/3d/textures/grimoire-plat.png";

// studios des gros plans, loin du diorama (hors champ l'un de l'autre)
const STUDIO_POTIONS = [1000, 0, 0];
const ECART_POTIONS = 34;                 // la bleue est à droite de la rouge
const STUDIO_GRIMOIRE = [2000, 0, 0];

export const PLANS = [
  { n: 1, debut: 0, fin: 4, nom: "boutique en plan large" },
  { n: 2, debut: 4, fin: 8, nom: "Tim entre, coucou" },
  { n: 3, debut: 8, fin: 11, nom: "le marchand bondit, non ; Tim en colère" },
  { n: 4, debut: 11, fin: 15, nom: "potions rouge puis bleue" },
  { n: 5, debut: 15, fin: 18, nom: "grimoire" },
  { n: 6, debut: 18, fin: 20, nom: "retour plan large, boucle" },
];

const TAU = 2 * Math.PI;
const lisse = (x) => { x = Math.min(1, Math.max(0, x)); return x * x * (3 - 2 * x); };
const entre = (t, a, b) => Math.min(1, Math.max(0, (t - a) / (b - a)));
const q = (v) => Math.round(v * 4) / 4;

// ---- caméra : images clés [t, cx, cy, cz, distance, hauteur, azimut] interpolées en Hermite (tangentes
// de Catmull-Rom, nulles aux extrémités) : mouvement continu, sans à-coup aux clés
function trajectoire(cles) {
  const n = cles.length, dim = cles[0].length - 1;
  const tangentes = cles.map((c, i) => {
    if (i === 0 || i === n - 1) return new Array(dim).fill(0);
    const a = cles[i - 1], b = cles[i + 1];
    return Array.from({ length: dim }, (_, k) => (b[k + 1] - a[k + 1]) / (b[0] - a[0]));
  });
  return (t) => {
    if (t <= cles[0][0]) return cles[0].slice(1);
    if (t >= cles[n - 1][0]) return cles[n - 1].slice(1);
    let i = 0;
    while (t > cles[i + 1][0]) i++;
    const a = cles[i], b = cles[i + 1], h = b[0] - a[0], s = (t - a[0]) / h;
    const h00 = 2 * s ** 3 - 3 * s ** 2 + 1, h10 = s ** 3 - 2 * s ** 2 + s, h01 = -2 * s ** 3 + 3 * s ** 2, h11 = s ** 3 - s ** 2;
    return Array.from({ length: dim }, (_, k) =>
      h00 * a[k + 1] + h10 * h * tangentes[i][k] + h01 * b[k + 1] + h11 * h * tangentes[i + 1][k]);
  };
}

// cadre de départ = cadre d'arrivée (boucle)
const DEPART = [0, 24, 0, 290, 100, -0.2];
const SEQUENCE = trajectoire([          // plans 1 à 3 (0–11 s)
  [0, ...DEPART],
  [4, -8, 14, 6, 175, 44, -0.12],
  [6.3, -7, 11, 9, 140, 24, -0.05],
  [8, -6, 12, 9, 132, 22, 0.0],
  [9, 0.5, 17, 9, 165, 30, 0.05],
  [11, 1.5, 11, 9, 140, 19, 0.1],
]);
const RETOUR = trajectoire([            // plan 6 (18–20 s)
  [18, 1.5, 13, 9, 170, 30, 0.14],
  [20, ...DEPART],
]);

// ---- marche de Tim : de x = −21 à −7 entre 4,0 et 6,2 s, au bord du trottoir (z = 10,5)
const TIM_Z = 10.5, TIM_X0 = -21, TIM_X1 = -7, MARCHE = [4.0, 6.2];
// ---- bond du marchand : de derrière Tim (contre la façade), par-dessus sa tête, jusqu'à sa droite
const MAR_X1 = 10, MAR_Z1 = 9, BOND = [8.0, 9.0], HAUT_BOND = 20;

export default async function creer(THREE, outils, params = {}) {
  const V = outils.voxel;
  const texte = async (c) => {
    const r = await fetch(V.url(c));
    if (!r.ok) throw new Error(`vitrine : « ${c} » introuvable (HTTP ${r.status})`);
    return r.text();
  };

  const scene = new THREE.Scene();
  const camera = new THREE.PerspectiveCamera(24, outils.largeur / outils.hauteur, 1, 1200);

  // ================= diorama (boutique.scene.toml)
  const def = V.lireToml(await texte(DECOR + "boutique.scene.toml"));
  const [cx, cy, cz] = def.centre;
  const fichiers = new Map();
  for (const part of def.partie) {
    if (!fichiers.has(part.fichier)) fichiers.set(part.fichier, await V.charger(DECOR + part.fichier));
    const g = fichiers.get(part.fichier).find((m) => m.nom === part.modele);
    if (!g) throw new Error(`vitrine : modèle « ${part.modele} » absent de ${part.fichier}`);
    const mesh = V.maillage(g, { centre: "coin", occlusion: def.occlusion ?? 2 });
    mesh.position.set(part.origine[0] - cx, part.origine[1] - cy, part.origine[2] - cz);
    scene.add(mesh);
  }
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

  // ================= ciel couchant : cartes empilées, décalées selon l'azimut de la caméra (parallaxe)
  const ciel = V.lireToml(await texte(CIEL + "couchant.toml"));
  const toile = document.createElement("canvas");
  toile.width = ciel.largeur; toile.height = ciel.hauteur;
  const ctx = toile.getContext("2d");
  ctx.imageSmoothingEnabled = false;
  const couches = ciel.couche.map((c) => ({ ...c, tex: outils.texturePixel(CIEL + c.fichier) }));
  const fondCiel = new THREE.CanvasTexture(toile);
  fondCiel.magFilter = fondCiel.minFilter = THREE.NearestFilter;
  fondCiel.generateMipmaps = false;
  fondCiel.colorSpace = THREE.SRGBColorSpace;
  let dernierCiel = null;
  function peindreCiel(angle, lever = 0) {
    const cle = `${Math.round(angle * 1000)}:${lever}`;
    if (cle === dernierCiel) return;
    dernierCiel = cle;
    ctx.clearRect(0, 0, toile.width, toile.height);
    for (const c of couches) {
      const img = c.tex.image;
      const dx = Math.round(-ciel.glissement * c.profondeur * angle);
      const dy = Math.round(lever * c.profondeur);
      ctx.drawImage(img, Math.round((toile.width - img.width) / 2) + dx, dy);
    }
    fondCiel.needsUpdate = true;
  }
  const fondPotions = outils.couleur(2);
  const fondGrimoire = outils.couleur(1);

  // ================= persos
  const ombreDe = (r) => {
    const m = new THREE.Mesh(new THREE.CircleGeometry(r, 24), new THREE.MeshBasicMaterial({ color: outils.couleur(5) }));
    m.rotation.x = -Math.PI / 2;
    m.position.y = 0.03;
    scene.add(m);
    return m;
  };
  const tim = installerTim(await V.chargerRig("assets/3d/persos/tim/tim.rig.toml"));
  const marchand = installerMarchand(await V.chargerRig("assets/3d/persos/marchand/marchand.rig.toml"));
  scene.add(tim, marchand);
  const ombreTim = ombreDe(4.5), ombreMar = ombreDe(5.5);

  // ================= potions (studio 1)
  const fioles = await V.charger(POTION + "potion.vox");
  const grainsTous = await V.charger(POTION + "potion-particules.vox");
  function fabriquerPotion(couleur, x) {
    const rampe = { 12: { dessus: 12, face: 12, cote: 11, dessous: 11 }, 11: { dessus: 12, face: 11, cote: 11, dessous: 11 } };
    if (couleur === "bleue") rampe[11] = { dessus: 11, face: 11, cote: 10, dessous: 10 };
    const racine = new THREE.Group();
    racine.position.set(STUDIO_POTIONS[0] + x, STUDIO_POTIONS[1], STUDIO_POTIONS[2]);
    scene.add(racine);
    const fiole = new THREE.Group();
    const corps = V.maillage(fioles.find((g) => g.nom === couleur), { centre: "milieu", occlusion: 2, rampe });
    fiole.add(corps);
    racine.add(fiole);
    const halo = outils.halo(9, couleur === "rouge" ? [21] : [3], { interieur: 0, segments: 40, camera: true });
    halo.traverse((o) => {
      if (o.material) { o.material.depthTest = false; o.material.depthWrite = false; }
      o.renderOrder = -10;
    });
    racine.add(halo);
    const parts = grainsTous.filter((g) => g.nom.startsWith(couleur + "_")).map((g, k, tous) => {
      const m = V.maillage(g, { centre: "milieu", occlusion: false });
      racine.add(m);
      return { m, phase: k / tous.length, periode: 2.4 + 0.4 * (k % 3), dx: [-2, 2, 0, -1, 1, 2][k], amp: 1 + (k % 2) };
    });
    return {
      racine,
      animer(u, decalage) {
        const yb = q(Math.sin((TAU * (u + decalage)) / 2.5));
        fiole.position.set(0, yb, 0);
        corps.rotation.z = Math.round(Math.sin((TAU * (u + decalage)) / 5) * 4) * 0.01;
        halo.position.set(0, yb + 1, 0);
        for (const g of parts) {
          const s = ((u / g.periode) + g.phase) % 1;
          const px = g.dx + g.amp * Math.sin(TAU * (s * 1.5 + g.phase));
          g.m.position.set(q(px), q(yb + 7.5 + s * 8), q(Math.cos(TAU * (s + g.phase)) * 1.5));
          g.m.visible = s < 0.9;
        }
      },
    };
  }
  const rouge = fabriquerPotion("rouge", 0);
  const bleue = fabriquerPotion("bleue", ECART_POTIONS);

  // ================= grimoire (studio 2) : même montage que sa scène de contrôle
  const L = [19, 8, 19], CHARNIERE = [0, 5, 0], PLATEAU = [2, 1, 17, 16];
  const rampeLivre = { 30: { dessus: 30, face: 30, cote: 29, dessous: 29 }, 31: { dessus: 31, face: 31, cote: 30, dessous: 29 } };
  const grillesLivre = await V.charger(GRIMOIRE);
  const partie = (nom) => V.maillage(grillesLivre.find((g) => g.nom === nom), { centre: "coin", occlusion: 2, rampe: rampeLivre });
  const livre = new THREE.Group();
  livre.position.set(...STUDIO_GRIMOIRE);
  const base = new THREE.Group();
  base.position.set(-L[0] / 2, 0, -L[2] / 2);
  livre.add(base);
  base.add(partie("corps"), partie("signet"));
  const charniere = new THREE.Group();
  charniere.position.set(...CHARNIERE);
  base.add(charniere);
  charniere.add(partie("couvercle"));
  {
    const [x0, z0, x1, z1] = PLATEAU;
    const plat = new THREE.Mesh(new THREE.PlaneGeometry(x1 - x0 + 1, z1 - z0 + 1),
      new THREE.MeshBasicMaterial({ map: outils.texturePixel(TEXTURE_GRIMOIRE) }));
    plat.rotation.x = -Math.PI / 2;
    plat.position.set((x0 + x1 + 1) / 2, 2.02, (z0 + z1 + 1) / 2);
    charniere.add(plat);
  }
  const ombreLivre = new THREE.Mesh(new THREE.PlaneGeometry(L[0] + 2, L[2] + 2), new THREE.MeshBasicMaterial({ color: outils.couleur(2) }));
  ombreLivre.rotation.x = -Math.PI / 2;
  ombreLivre.position.set(STUDIO_GRIMOIRE[0], -0.05, STUDIO_GRIMOIRE[2]);
  scene.add(livre, ombreLivre);
  const lueur = new THREE.Group();
  for (const [w, h, c, y] of [[12, 11, 19, 5.02], [6, 5, 20, 5.04]]) {
    const m = new THREE.Mesh(new THREE.PlaneGeometry(w, h), new THREE.MeshBasicMaterial({ color: outils.couleur(c) }));
    m.rotation.x = -Math.PI / 2;
    m.position.set(10, y, 8.5);
    lueur.add(m);
  }
  base.add(lueur);
  const grain = V.grille(1, 1, 1, "etincelle").boite(0, 0, 0, 0, 0, 0, 20);
  const grain8 = V.grille(1, 1, 1, "etincelle-claire").boite(0, 0, 0, 0, 0, 0, 8);
  const etincelles = [0, 1, 2, 3, 4, 5, 6, 7].map((k) => {
    const m = V.maillage(k % 3 === 2 ? grain8 : grain, { centre: "milieu", occlusion: false });
    base.add(m);
    return { m, x: 4 + 1.6 * k, z: 4 + ((k * 7) % 11), phase: k / 8, periode: 1.1 + 0.15 * (k % 3) };
  });
  // ouverture : fermé jusqu'à 15,5 s, s'ouvre jusqu'à 16,3 s (petit rebond), reste entrouvert
  function ouvertureLivre(t) {
    if (t < 15.5) return 0;
    if (t < 16.2) return lisse((t - 15.5) / 0.7) * 1.08;
    if (t < 16.4) return 1.08 - 0.08 * lisse((t - 16.2) / 0.2);
    return 1;
  }

  // ================= animation
  function poserCamera(c, regard = null) {
    const [x, y, z, d, h, a] = c;
    camera.position.set(x + Math.sin(a) * d, y + h, z + Math.cos(a) * d);
    camera.lookAt(...(regard || [x, y, z]));
    return a;
  }

  function animerPersos(t) {
    const u = outils.pas12(t);
    const enScene = t < 11 || t >= 18;
    tim.visible = ombreTim.visible = enScene && t >= MARCHE[0];
    marchand.visible = ombreMar.visible = false;

    // --- Tim
    let tx = TIM_X1, rot = 0;
    if (t >= 18) {
      tim.poser("idle", u - 18);
      rot = 0.12;
    } else if (u < MARCHE[1]) {
      const s = entre(u, MARCHE[0], MARCHE[1]);
      tx = TIM_X0 + (TIM_X1 - TIM_X0) * s;
      tim.poser("marche", u - MARCHE[0]);
      rot = Math.PI / 2;
    } else if (u < 6.6) {
      tim.poser("idle", u - MARCHE[1]);
      rot = (Math.PI / 2) * (1 - lisse((u - MARCHE[1]) / 0.35));        // se tourne vers la caméra
    } else if (u < 8.4) {
      tim.poser("coucou", u - 6.6);
    } else if (u < 9.6) {
      tim.poser("idle", u - 8.4);
      rot = 0.25 * lisse((u - 8.6) / 0.3);                              // se tourne vers le marchand
    } else {
      tim.poser("colere", u - 9.6);
      rot = 0.25;
    }
    tim.position.set(q(tx), 0, TIM_Z);
    tim.rotation.y = rot;
    ombreTim.position.set(q(tx), 0.03, TIM_Z);

    // --- le marchand
    if (t >= 18) {
      marchand.visible = ombreMar.visible = true;
      marchand.poser("parle", u - 18);
      marchand.position.set(MAR_X1, 0, MAR_Z1);
      marchand.rotation.y = -0.15;
      ombreMar.position.set(MAR_X1, 0.03, MAR_Z1);
    } else if (t >= BOND[0] && t < 11) {
      let mx = MAR_X1, my = 0, mz = MAR_Z1, mrot = -0.25;
      if (u < BOND[1]) {
        const s = entre(u, BOND[0], BOND[1]);
        mx = TIM_X1 + (MAR_X1 - TIM_X1) * s;
        mz = 0.5 + (MAR_Z1 - 0.5) * s;
        my = 4 * HAUT_BOND * s * (1 - s);
        mrot = -0.25 * s;
        marchand.poser("saut", 0.24 + 0.66 * s);                      // phase de vol du clip (bras levés)
        // caché tant qu'il est derrière Tim ou dans la façade (pieds sous le haut de sa tête)
        marchand.visible = my + 3 > 17.5 || s > 0.5;
      } else if (u < 9.3) {
        marchand.poser("saut", 0.9 + (u - BOND[1]));                   // réception (hochement)
        marchand.visible = true;
      } else {
        marchand.poser("non_de_la_tete", u - 9.3);
        marchand.visible = true;
      }
      marchand.position.set(q(mx), q(my), q(mz));
      marchand.rotation.y = mrot;
      ombreMar.visible = marchand.visible;
      ombreMar.position.set(q(mx), 0.03, q(mz));
      ombreMar.scale.setScalar(1 / (1 + my / 20));
    }
  }

  function update(t) {
    const u = outils.pas12(t);
    animerPersos(t);
    let angle = 0;
    if (t < 11) {
      scene.background = fondCiel;
      angle = poserCamera(SEQUENCE(t));
      peindreCiel(angle);
    } else if (t < 15) {
      // plan 4 : potion rouge (11–12,7), travelling (12,7–13,5), potion bleue (13,5–15)
      scene.background = fondPotions;
      const k = lisse(entre(t, 12.7, 13.5));
      const cxp = STUDIO_POTIONS[0] + ECART_POTIONS * k;
      const loc = t < 13.1 ? t - 11 : t - 13.5;
      const a = -0.5 + 0.22 * loc;
      const d = 84 - 3 * Math.max(0, loc) + 10 * Math.sin(Math.PI * k);
      poserCamera([cxp, 2, 0, d, 16, a]);
      rouge.animer(u, 0);
      bleue.animer(u, 1.2);
    } else if (t < 18) {
      // plan 5 : grimoire en orbite lente, rapprochement
      scene.background = fondGrimoire;
      const s = (t - 15) / 3;
      const a = -0.75 + 0.6 * s;
      poserCamera([STUDIO_GRIMOIRE[0], 4, 0, 120 - 12 * lisse(s), 58 - 10 * lisse(s), a]);
      const o = ouvertureLivre(u);
      charniere.rotation.z = Math.round(o * 18) * Math.PI / 180;
      lueur.visible = o > 0.2;
      for (const e of etincelles) {
        const k = ((u / e.periode) + e.phase) % 1;
        e.m.visible = o > 0.6 && k < 0.85;
        e.m.position.set(q(e.x + Math.sin(TAU * (k + e.phase))), q(6 + k * 11), q(e.z));
      }
    } else {
      scene.background = fondCiel;
      angle = poserCamera(RETOUR(t));
      peindreCiel(angle);
    }
    const vacille = Math.floor(t * 6) % 5 === 3 ? 1 : 0;
    for (const h of halos) h.variantes.forEach((v, i) => { v.visible = i === (h.nom === "lanterne" ? vacille : 0); });
  }

  return { scene, camera, update };
}
