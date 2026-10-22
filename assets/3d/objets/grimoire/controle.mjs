// ico-vid : scène de contrôle du grimoire (grimoire.py + texture grimoire-plat.png) : le livre tourne en orbite,
// son couvercle s'entrouvre (charnière au dos), les pages luisent d'or et quelques étincelles en sortent, puis il
// se referme avec un petit rebond.
//
//   python3 -I assets/3d/objets/grimoire/grimoire.py && python3 -I assets/3d/textures/grimoire-plat.py
//   node outils/rendu3d/rendu3d.mjs --scene assets/3d/objets/grimoire/controle.mjs --out <dossier> --debut 0 --fin 4 --ips 12
//
// params : tours (tours de caméra sur la durée), duree (s, = un cycle d'ouverture), angle (ouverture max, degrés),
// distance, hauteur (caméra), occlusion. Mouvements cadencés à 12 i/s (outils.pas12).

const VOX = "assets/3d/objets/grimoire/grimoire.vox";
const TEXTURE = "assets/3d/textures/grimoire-plat.png";
const CHARNIERE = [0, 5, 0];          // grille commune (grimoire.py)
const PLATEAU = [2, 1, 17, 16];       // x0, z0, x1, z1 du plateau texturé, repère du couvercle
const L = [19, 8, 19];

export default async function creer(THREE, outils, params = {}) {
  const p = { tours: 1, duree: 4, angle: 18, distance: 82, hauteur: 52, occlusion: 2, ...params };
  const V = outils.voxel;

  const scene = new THREE.Scene();
  scene.background = outils.couleur(1);
  const camera = new THREE.PerspectiveCamera(30, outils.largeur / outils.hauteur, 1, 600);

  // le dessus du cuir garde le 30 (comme le fond de la texture), les coins le 31
  const rampe = { 30: { dessus: 30, face: 30, cote: 29, dessous: 29 }, 31: { dessus: 31, face: 31, cote: 30, dessous: 29 } };
  const opt = { centre: "coin", occlusion: p.occlusion, rampe };
  const grilles = await V.charger(VOX);
  const partie = (nom) => V.maillage(grilles.find((g) => g.nom === nom), opt);

  const livre = new THREE.Group();                 // origine = milieu du dessous du livre
  const base = new THREE.Group();
  base.position.set(-L[0] / 2, 0, -L[2] / 2);
  livre.add(base);
  base.add(partie("corps"), partie("signet"));

  const charniere = new THREE.Group();
  charniere.position.set(...CHARNIERE);
  base.add(charniere);
  const couvercle = partie("couvercle");           // son coin (0, 0, 0) = la charnière
  charniere.add(couvercle);
  const [x0, z0, x1, z1] = PLATEAU;
  const plat = new THREE.Mesh(new THREE.PlaneGeometry(x1 - x0 + 1, z1 - z0 + 1),
    new THREE.MeshBasicMaterial({ map: outils.texturePixel(TEXTURE) }));
  plat.rotation.x = -Math.PI / 2;                  // haut de l'image vers le fond (−z)
  plat.position.set((x0 + x1 + 1) / 2, 2.02, (z0 + z1 + 1) / 2);
  charniere.add(plat);
  scene.add(livre);

  // ombre de contact : dalle pleine un cran plus sombre que le fond
  const ombre = new THREE.Mesh(new THREE.PlaneGeometry(L[0] + 2, L[2] + 2), new THREE.MeshBasicMaterial({ color: outils.couleur(2) }));
  ombre.rotation.x = -Math.PI / 2;
  ombre.position.y = -0.05;
  scene.add(ombre);

  // lueur dans l'entrebâillement : deux lames dorées posées sur les pages (vues quand le couvercle est levé)
  const lueur = new THREE.Group();
  for (const [w, h, c, y] of [[12, 11, 19, 5.02], [6, 5, 20, 5.04]]) {
    const m = new THREE.Mesh(new THREE.PlaneGeometry(w, h), new THREE.MeshBasicMaterial({ color: outils.couleur(c) }));
    m.rotation.x = -Math.PI / 2;
    m.position.set(10, y, 8.5);
    lueur.add(m);
  }
  base.add(lueur);

  // étincelles : 5 voxels dorés qui montent de la tranche quand le livre est ouvert
  const grain = V.grille(1, 1, 1, "etincelle").boite(0, 0, 0, 0, 0, 0, 20);
  const etincelles = [0, 1, 2, 3, 4].map((k) => {
    const m = V.maillage(grain, { centre: "milieu", occlusion: false });
    base.add(m);
    return { m, x: 5 + 2.5 * k, z: 4 + ((k * 7) % 11), phase: k / 5 };
  });

  const q = (v) => Math.round(v * 4) / 4;
  const lisse = (x) => { x = Math.min(1, Math.max(0, x)); return x * x * (3 - 2 * x); };

  // ouverture sur un cycle : fermé (0–25 %), s'ouvre (25–45 %), ouvert (45–75 %), se referme avec rebond (75–90 %)
  function ouverture(s) {
    if (s < 0.25) return 0;
    if (s < 0.45) return lisse((s - 0.25) / 0.2);
    if (s < 0.75) return 1;
    if (s < 0.85) return 1 - lisse((s - 0.75) / 0.1);
    if (s < 0.9) return 0.12 * Math.sin(Math.PI * (s - 0.85) / 0.05);
    return 0;
  }

  function update(t) {
    const u = outils.pas12(t);
    const s = (u / p.duree) % 1;
    const o = ouverture(s);
    charniere.rotation.z = Math.round(o * p.angle) * Math.PI / 180;
    lueur.visible = o > 0.2;
    for (const e of etincelles) {
      const k = ((u / 1.2) + e.phase) % 1;
      e.m.visible = o > 0.6 && k < 0.85;
      e.m.position.set(q(e.x + Math.sin(2 * Math.PI * (k + e.phase))), q(6 + k * 9), q(e.z));
    }
    livre.position.y = 0;
    const a = -0.6 + 2 * Math.PI * p.tours * (t / p.duree);
    camera.position.set(Math.sin(a) * p.distance, p.hauteur, Math.cos(a) * p.distance);
    camera.lookAt(0, 4, 0);
  }

  return { scene, camera, update };
}
