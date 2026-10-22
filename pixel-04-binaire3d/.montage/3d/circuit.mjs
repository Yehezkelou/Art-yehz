// ico-vid pixel-04-binaire3d : scène 3D « circuit » (40,30–44,60 s, opaque).
//
//   node outils/rendu3d/rendu3d.mjs --scene pixel-04-binaire3d/.montage/3d/circuit.mjs \
//        --out pixel-04-binaire3d/.montage/3d/circuit --debut 40.3 --fin 44.6 --ips 24 --fond 1E4D3A
//
// La caméra plonge (40,27 « plongée ») puis file en rase-mottes de gauche à droite au-dessus d'une carte
// électronique (plan 13, pistes 14/15, puces 2/3 à pattes 6), et se pose face à une rangée de 8 bits
// (dalles qui montrent « 0 » ou « 1 » en relief, une face devant, une derrière). Les bits se retournent en vague,
// les pistes d'alimentation s'allument à 41,835, tous se retournent ensemble à 42,14 (« deux »), montrent 0 gris (5)
// à 43,23 (« zéros ») et 1 or (19) à 44,12 (« uns »).
// Couleurs « cuites » par face (MeshBasicMaterial, couleur exacte de la palette) : rien ne bave à la quantification.
// Zones calmes : ciel = brume = 13 au-dessus de y ≈ 160 (titre 2D « BASE 2 » en y 40–110) ; la bande de carte vue en
// y 312–352 (z ≈ 36–72) ne porte ni puce ni piste.
//
// params (facultatifs) : { "vague1": 40.85, "vague2": 41.40, "allume": 41.835, "deux": 42.14,
//                          "zeros": 43.23, "uns": 44.12 }

export default function creer(THREE, outils, params = {}) {
  const T = {
    vague1: params.vague1 ?? 40.85,
    vague2: params.vague2 ?? 41.40,
    allume: params.allume ?? 41.835,
    deux: params.deux ?? 42.14,
    zeros: params.zeros ?? 43.23,
    uns: params.uns ?? 44.12,
  };
  const { lisse, entre, ressort } = outils;
  const borne = (u) => Math.min(1, Math.max(0, u));

  const VERT = 13;
  const scene = new THREE.Scene();
  scene.background = outils.couleur(VERT);
  scene.fog = new THREE.Fog(outils.couleur(VERT), 175, 300);

  const camera = new THREE.PerspectiveCamera(50 /* = FOV */, outils.largeur / outils.hauteur, 1, 600);

  // ---------- matériaux plats (un par couleur, partagés) ----------
  const cache = new Map();
  const plat = (i) => {
    if (!cache.has(i)) cache.set(i, outils.materiau(i, { ombre: "plat" }));
    return cache.get(i);
  };
  // ordre des faces de BoxGeometry : +x, -x, +y, -y, +z, -z
  const faces = (cote, dessus, devant) => [plat(cote), plat(cote), plat(dessus), plat(dessus), plat(devant), plat(devant)];

  // ---------- la carte ----------
  const plan = new THREE.Mesh(new THREE.PlaneGeometry(700, 500), plat(VERT));
  plan.rotation.x = -Math.PI / 2;
  plan.position.set(0, 0, -100);
  scene.add(plan);

  // zone interdite aux pistes et puces : la bande des sous-titres (vue en y 312–352) et la rangée de bits
  // caméra posée (fin du vol) : la bande d'écran y 312–352 voit la carte entre deux z, calculés ici
  const CAM = { y: 42, z: 128, visee: 7.5 };
  const FOV = 50;
  const zDeY = (ys) => {
    const tang = Math.tan((FOV / 2) * Math.PI / 180);
    const tangage = Math.atan((CAM.y - CAM.visee) / CAM.z);
    const a = tangage + Math.atan(((ys - outils.hauteur / 2) / (outils.hauteur / 2)) * tang);
    return CAM.z - CAM.y / Math.tan(a);
  };
  const BANDE = [zDeY(300) - 9, zDeY(372) + 4];   // y plus bas à l'écran = plus près = z plus grand
  const libre = (x0, z0, x1, z1) => {
    const za = Math.min(z0, z1), zb = Math.max(z0, z1);
    if (zb > BANDE[0] && za < BANDE[1]) return false;
    const xa = Math.min(x0, x1), xb = Math.max(x0, x1);
    if (zb > -16 && za < 14 && xb > -42 && xa < 42) return false;   // rangée de bits + socles
    return true;
  };

  const h = outils.hasard(2026);
  const geoBoite = new THREE.BoxGeometry(1, 1, 1);
  const pistes = [];        // { mesh } pour les pistes 14 (fixes)
  function piste(x0, z0, x1, z1, couleur = 14, ep = 1.2) {
    const m = new THREE.Mesh(geoBoite, plat(couleur));
    const lx = Math.abs(x1 - x0) + ep, lz = Math.abs(z1 - z0) + ep;
    m.scale.set(lx, 0.2, lz);
    m.position.set((x0 + x1) / 2, 0.1, (z0 + z1) / 2);
    scene.add(m);
    pistes.push(m);
    return m;
  }
  function pastille(x, z, couleur = 15) {
    const m = new THREE.Mesh(geoBoite, plat(couleur));
    m.scale.set(2.6, 0.3, 2.6);
    m.position.set(x, 0.15, z);
    scene.add(m);
  }

  // pistes en L sur une grille de 6 unités (pas de piste dans la bande)
  const G = 6;
  const g = (v) => Math.round(v / G) * G;
  let posees = 0, essais = 0;
  while (posees < 320 && essais < 9000) {
    essais++;
    const x0 = g(-230 + h() * 330), z0 = g(-170 + h() * 310);
    const lx = g((h() < 0.5 ? -1 : 1) * (12 + h() * 50));
    const lz = g((h() < 0.5 ? -1 : 1) * (6 + h() * 24));
    const x1 = x0 + lx, z1 = z0 + lz, x2 = x1 + g((h() < 0.5 ? -1 : 1) * (6 + h() * 30));
    if (!libre(x0, z0, x1, z0) || !libre(x1, z0, x1, z1) || !libre(x1, z1, x2, z1)) continue;
    const c = h() < 0.18 ? 15 : 14;
    piste(x0, z0, x1, z0, c);
    piste(x1, z0, x1, z1, c);
    piste(x1, z1, x2, z1, c);
    pastille(x0, z0, c === 15 ? 16 : 15);
    pastille(x2, z1, c === 15 ? 16 : 15);
    posees++;
  }

  // puces : boîtier 2 (côtés 3), pattes 6, repère 4
  const geoPatte = new THREE.BoxGeometry(1, 0.6, 1.8);
  function puce(x, z, larg, prof) {
    const grp = new THREE.Group();
    const corps = new THREE.Mesh(new THREE.BoxGeometry(larg, 2.2, prof), faces(3, 2, 3));
    corps.position.y = 1.5;
    grp.add(corps);
    const n = Math.max(2, Math.floor((larg - 2) / 2.4));
    for (let k = 0; k < n; k++) {
      const px = -larg / 2 + 1.6 + k * ((larg - 3.2) / Math.max(1, n - 1));
      for (const s of [-1, 1]) {
        const p = new THREE.Mesh(geoPatte, plat(6));
        p.position.set(px, 0.4, s * (prof / 2 + 0.6));
        grp.add(p);
      }
    }
    const repere = new THREE.Mesh(geoBoite, plat(4));
    repere.scale.set(1.2, 0.2, 1.2);
    repere.position.set(-larg / 2 + 1.8, 2.7, -prof / 2 + 1.8);
    grp.add(repere);
    grp.position.set(x, 0, z);
    scene.add(grp);
  }
  posees = 0; essais = 0;
  const puces = [];
  while (posees < 70 && essais < 6000) {
    essais++;
    const larg = 10 + Math.floor(h() * 4) * 3, prof = 7 + Math.floor(h() * 2) * 3;
    const x = g(-240 + h() * 350), z = g(-170 + h() * 310);
    if (!libre(x - larg / 2 - 3, z - prof / 2 - 3, x + larg / 2 + 3, z + prof / 2 + 3)) continue;
    if (puces.some((p) => Math.abs(p.x - x) < (p.l + larg) / 2 + 4 && Math.abs(p.z - z) < (p.p + prof) / 2 + 4)) continue;
    puces.push({ x, z, l: larg, p: prof });
    puce(x, z, larg, prof);
    posees++;
  }

  // ---------- la rangée de 8 bits ----------
  const N = 8, PAS = 7.6, LB = 6.6, HB = 9, PB = 3;     // largeur, hauteur, épaisseur d'une dalle
  const xBit = (i) => (i - (N - 1) / 2) * PAS;
  const YC = 1.2 + HB / 2 + 0.2;                         // centre de la dalle au repos

  // valeurs : motif de départ, deux vagues (complément), « deux » (complément), zéros gris, uns or
  const depart = [1, 0, 1, 1, 0, 0, 1, 0];
  const DUREE = 0.42;
  const bits = [];
  for (let i = 0; i < N; i++) {
    const ev = [{ t: -Infinity, v: depart[i], c: 8 }];
    const ajoute = (t, v, c) => ev.push({ t, v, c });
    let v = depart[i];
    v = 1 - v; ajoute(T.vague1 + 0.05 * i, v, 8);
    v = 1 - v; ajoute(T.vague2 + 0.04 * i, v, 8);
    v = 1 - v; ajoute(T.deux, v, 8);
    ajoute(T.zeros, 0, 5);
    ajoute(T.uns, 1, 19);
    bits.push({ ev });
  }
  const OMBRE = { 8: 6, 5: 4, 19: 18 };   // côté des chiffres en relief : même rampe, un cran plus sombre

  // pistes d'alimentation derrière chaque bit (s'allument en remontant vers le bit à « allume »)
  const SEG = 10;
  const feeders = [];
  for (let i = 0; i < N; i++) {
    const segs = [];
    for (let s = 0; s < SEG; s++) {
      const za = -16 - s * 9, zb = za - 9;
      segs.push(piste(xBit(i), za, xBit(i), zb, 14, 1.6));
    }
    pastille(xBit(i), -16, 15);
    feeders.push(segs);
  }
  // impulsions (16) qui arrivent au bit à chaque retournement
  const geoImp = new THREE.BoxGeometry(2.2, 0.5, 4);
  const impulsions = [];
  for (let i = 0; i < N; i++) {
    const lst = [];
    for (let k = 1; k < bits[i].ev.length; k++) {
      const m = new THREE.Mesh(geoImp, plat(16));
      m.visible = false;
      scene.add(m);
      lst.push({ m, t: bits[i].ev[k].t });
    }
    impulsions.push(lst);
  }

  const geoDalle = new THREE.BoxGeometry(LB, HB, PB);
  const geoSocle = new THREE.BoxGeometry(LB + 1.6, 1.2, PB + 3);
  const geoVox = new THREE.BoxGeometry(1, 1, 1);
  function glyphe(car, matDevant, matCote) {
    const src = outils.voxelTexte(car, { cube: 1, profondeur: 1 }).children[0];
    const grp = new THREE.Group();
    for (const cube of src.children) {
      const m = new THREE.Mesh(geoVox, [matCote, matCote, matCote, matCote, matDevant, matCote]);
      m.position.copy(cube.position);
      grp.add(m);
    }
    return grp;
  }
  for (let i = 0; i < N; i++) {
    const b = bits[i];
    const socle = new THREE.Mesh(geoSocle, faces(2, 4, 2));
    socle.position.set(xBit(i), 0.6, 0);
    scene.add(socle);
    b.pivot = new THREE.Group();
    b.pivot.position.set(xBit(i), YC, 0);
    scene.add(b.pivot);
    b.pivot.add(new THREE.Mesh(geoDalle, faces(2, 4, 3)));
    b.face = [];
    for (let f = 0; f < 2; f++) {
      const devant = outils.materiau(8, { ombre: "plat" });
      const cote = outils.materiau(6, { ombre: "plat" });
      const support = new THREE.Group();
      support.position.z = (f === 0 ? 1 : -1) * (PB / 2 + 0.5);
      if (f === 1) support.rotation.x = Math.PI;      // à l'envers : se lit droit une fois la dalle retournée
      const g0 = glyphe("0", devant, cote), g1 = glyphe("1", devant, cote);
      support.add(g0, g1);
      b.pivot.add(support);
      b.face.push({ devant, cote, g0, g1 });
    }
  }

  // retournement : anticipation (recul de 10 %), demi-tour avec dépassement amorti, petit saut
  function tour(u) {
    if (u <= 0) return 0;
    if (u >= 1) return 1;
    const anticip = -0.1 * Math.sin(Math.PI * borne(u / 0.3));
    return anticip + ressort((u - 0.12) / 0.88);
  }

  function regler(i, t) {
    const b = bits[i];
    let k = 0;
    while (k + 1 < b.ev.length && b.ev[k + 1].t <= t) k++;
    // k = dernier événement commencé ; la face (k % 2) montre ev[k], l'autre montre ev[k-1]
    const montrer = (f, e) => {
      const F = b.face[f];
      F.g0.visible = e.v === 0;
      F.g1.visible = e.v === 1;
      F.devant.color.copy(outils.couleur(e.c));
      F.cote.color.copy(outils.couleur(OMBRE[e.c]));
    };
    montrer(k % 2, b.ev[k]);
    montrer((k + 1) % 2, k > 0 ? b.ev[k - 1] : b.ev[k]);
    const u = k > 0 ? (t - b.ev[k].t) / DUREE : 1;
    const avant = Math.max(0, k - 1);
    b.pivot.rotation.x = Math.PI * (avant + (k > 0 ? tour(u) : 0));
    const enCours = k > 0 && u < 1;
    const saut = enCours ? 1.6 * Math.sin(Math.PI * borne((u - 0.12) / 0.6)) : 0;
    const ecrase = enCours ? 1 - 0.08 * Math.sin(Math.PI * borne(u / 0.2)) : 1;
    b.pivot.position.y = YC + Math.max(0, saut) + (ecrase - 1) * HB / 2;
    b.pivot.scale.set(1 + (1 - ecrase) * 0.6, ecrase, 1);
    // impulsions : remontent la piste en 0,7 s et touchent le socle au début du retournement
    for (const imp of impulsions[i]) {
      const a = (t - (imp.t - 0.7)) / 0.7;
      imp.m.visible = a >= 0 && a < 1;
      if (imp.m.visible) imp.m.position.set(xBit(i), 0.35, -100 + 84 * a);
    }
    // pistes d'alimentation : 14 → 15 en remontant vers le bit
    feeders[i].forEach((seg, s) => {
      const ts = T.allume + 0.025 * i + 0.03 * (SEG - 1 - s);
      seg.material = plat(t >= ts ? 15 : 14);
    });
  }

  // ---------- caméra : plongée puis rase-mottes latéral, puis dérive lente ----------
  const t0 = 40.3, tPose = 41.95;
  const cible = new THREE.Vector3();
  function placerCamera(t) {
    const u = borne((t - t0) / (tPose - t0));
    const sortie = 1 - Math.pow(1 - u, 3);                // rapide au départ, se pose en douceur
    const plonge = lisse(borne((t - t0) / 1.3));
    const x = -105 + 105 * sortie + 1.6 * Math.sin(0.9 * (t - t0));
    const y = 95 - (95 - CAM.y) * plonge + 0.5 * Math.sin(1.4 * (t - t0));
    const z = 150 - (150 - CAM.z) * sortie - 2.5 * entre(t, tPose, 44.6);
    camera.position.set(x, y, z);
    // regard : en avance dans le sens du vol au départ, puis sur la rangée
    const avance = 34 * (1 - lisse(u));
    cible.set(x * 0.15 + avance, CAM.visee - 12 * (1 - plonge), 0);
    camera.lookAt(cible);
  }

  function update(t) {
    placerCamera(t);
    for (let i = 0; i < N; i++) regler(i, t);
  }

  return { scene, camera, update };
}
