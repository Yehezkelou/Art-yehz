// ico-vid pixel-04-binaire3d : scène 3D « ruban » (44,60–54,90 s, opaque, nuit 1).
//
//   node outils/rendu3d/rendu3d.mjs --scene pixel-04-binaire3d/.montage/3d/ruban.mjs \
//        --out pixel-04-binaire3d/.montage/3d/ruban --debut 44.6 --fin 54.9 --ips 24 --fond 0E0D18
//
// Un ruban plat (2, liserés 4) s'enroule en spirale logarithmique vers le lointain (chaque tour 0,6 fois plus petit
// et un peu plus profond). Ses cases attendent les chiffres de 0,1 en binaire, « 0,0 » puis « 0011 » à l'infini :
// cases fantômes 3 (et 21 pour les groupes « 0011 »), qui s'allument en 4 / rouge 22 quand le chiffre voxel crème (8)
// s'y pose. « 0, » à 45,85, puis un chiffre à chaque mot (47,88 … 52,95), puis 10 chiffres par seconde à partir de
// 53,97 (« à l'infini »). La caméra glisse le long du ruban, suit le dernier chiffre posé (en tournant avec lui pour
// le garder droit), puis recule à 53,97 en ouvrant le champ pour montrer la spirale qui file à l'infini.
// Couleurs « cuites » (MeshBasicMaterial et couleurs d'instance exactes) : rien ne bave à la quantification.
// Zones calmes : y 20–60 (cartouche 2D « 0,1 = ? ») et y 312–352 (sous-titres) restent au fond 1 en phase de suivi.
//
// params (facultatifs) : { "zero_virgule": 45.85, "mots": [47.88, …, 52.95], "infini": 53.97, "cadence": 10 }

export default function creer(THREE, outils, params = {}) {
  const { lisse, ressort } = outils;
  const borne = (u) => Math.min(1, Math.max(0, u));
  const T0 = 44.6;
  const tZV = params.zero_virgule ?? 45.85;
  const mots = params.mots ?? [47.88, 48.26, 48.77, 49.45, 50.0, 50.74, 51.57, 52.28, 52.95];
  const tInf = params.infini ?? 53.97;
  const cadence = params.cadence ?? 10;
  const tFin = 54.9;

  const scene = new THREE.Scene();
  scene.background = outils.couleur(1);
  const FOV0 = 40, FOV1 = 62;
  const camera = new THREE.PerspectiveCamera(FOV0, outils.largeur / outils.hauteur, 1, 3000);

  const cache = new Map();
  const plat = (i) => {
    if (!cache.has(i)) cache.set(i, outils.materiau(i, { ombre: "plat" }));
    return cache.get(i);
  };

  // ---------- la spirale : abscisse u en « cases » (1 case = 7 unités à l'échelle 1) ----------
  const R0 = 120, P = 7, ZH = 100;
  const CASES_PAR_TOUR = (2 * Math.PI * R0) / P;
  const Q = Math.log(0.6) / CASES_PAR_TOUR;            // σ(u) = e^(Q u) : 0,6 par tour
  const sigma = (u) => Math.exp(Q * u);
  const theta = (u) => Math.PI / 2 - (u * P) / R0;      // sens horaire, tête des chiffres vers l'extérieur
  const point = (u, dz = 0) => {
    const s = sigma(u), th = theta(u);
    return new THREE.Vector3(s * R0 * Math.cos(th), s * R0 * Math.sin(th), -ZH * (1 - s) + dz * s);
  };
  // angle de la vraie tangente (la spirale rentre : un peu plus que θ - π/2) ; sert aux chiffres, cases et roulis
  const angle = (u) => {
    const a = point(u - 0.05), b = point(u + 0.05);
    return Math.atan2(b.y - a.y, b.x - a.x);
  };

  // ---------- la suite de caractères et leurs cases ----------
  // 0 « 0 », 1 « , », 2 « 0 » (d1), puis d2… = « 0011 » répété ; les groupes commencent à k = 3
  const KMAX = 1000;
  const car = (k) => (k === 0 ? "0" : k === 1 ? "," : k === 2 ? "0" : "0011"[(k - 3) % 4]);
  const groupe = (k) => k >= 3;
  const pos = [0];
  for (let k = 1; k < KMAX; k++) {
    let pas = k <= 2 ? 0.78 : 1;
    if (k >= 3 && (k - 3) % 4 === 0) pas += 0.42;     // petit écart avant chaque groupe « 0011 »
    pos.push(pos[k - 1] + pas);
  }
  const largeurCase = (k) => (k === 1 ? 0.5 : 0.86);

  // instants de pose
  const poses = [tZV, tZV + 0.16, ...mots];
  for (let t = tInf; t < tFin + 0.2; t += 1 / cadence) poses.push(t);
  const NPOSES = poses.length;

  // ---------- ruban (bande continue) + liserés ----------
  const U0 = -10, U1 = 9 * CASES_PAR_TOUR, DU = 0.25;
  const LARG = 11.4;
  function bande(r0, r1, dz, couleur) {
    const n = Math.ceil((U1 - U0) / DU) + 1;
    const pts = new Float32Array(n * 2 * 3);
    const idx = [];
    for (let i = 0; i < n; i++) {
      const u = U0 + i * DU, s = sigma(u), th = theta(u);
      const c = point(u, dz);
      const ex = Math.cos(th), ey = Math.sin(th);
      pts.set([c.x + ex * r0 * s, c.y + ey * r0 * s, c.z, c.x + ex * r1 * s, c.y + ey * r1 * s, c.z], i * 6);
      if (i > 0) { const a = 2 * (i - 1); idx.push(a, a + 1, a + 2, a + 1, a + 3, a + 2); }
    }
    const geo = new THREE.BufferGeometry();
    geo.setAttribute("position", new THREE.BufferAttribute(pts, 3));
    geo.setIndex(idx);
    const m = new THREE.Mesh(geo, plat(couleur));
    m.material.side = THREE.DoubleSide;
    scene.add(m);
  }
  bande(-LARG / 2, LARG / 2, 0, 2);
  bande(LARG / 2 - 0.9, LARG / 2, 0.15, 4);
  bande(-LARG / 2, -LARG / 2 + 0.9, 0.15, 4);

  // ---------- cases (InstancedMesh, couleurs d'instance exactes) ----------
  const geoCase = new THREE.BoxGeometry(P, 8.6, 0.8);
  const matCase = new THREE.MeshBasicMaterial({ color: 0xffffff });
  const cases = new THREE.InstancedMesh(geoCase, matCase, KMAX);
  const tmp = new THREE.Object3D();
  const placerCase = (k, echelle) => {
    const u = pos[k], s = sigma(u);
    tmp.position.copy(point(u, 0.55));
    tmp.rotation.set(0, 0, angle(u));
    tmp.scale.set(s * largeurCase(k) * echelle, s * echelle, s);
    tmp.updateMatrix();
    cases.setMatrixAt(k, tmp.matrix);
  };
  for (let k = 0; k < KMAX; k++) {
    placerCase(k, 1);
    cases.setColorAt(k, outils.couleur(groupe(k) ? 21 : 3));
  }
  scene.add(cases);

  // ---------- chiffres voxel posés ----------
  const geoVox = new THREE.BoxGeometry(1, 1, 1.2);
  const matChiffre = [plat(6), plat(6), plat(7), plat(5), plat(8), plat(6)];
  const chiffres = [];
  for (let k = 0; k < NPOSES; k++) {
    const src = outils.voxelTexte(car(k), { cube: 1, profondeur: 1 }).children[0];
    const g = new THREE.Group();
    for (const c of src.children) {
      const m = new THREE.Mesh(geoVox, matChiffre);
      m.position.copy(c.position);
      g.add(m);
    }
    g.visible = false;
    scene.add(g);
    chiffres.push(g);
  }

  // chute : tombe vers le ruban (depuis la caméra) et touche la case à l'instant du mot, petit rebond écrasé
  const CHUTE = (k) => (poses[k] >= tInf - 0.01 ? 0.1 : 0.2);
  function reglerChiffre(k, t) {
    const g = chiffres[k], tk = poses[k];
    const debut = tk - CHUTE(k);
    g.visible = t >= debut;
    if (!g.visible) return;
    const u = pos[k], s = sigma(u);
    let dz = 0, ecr = 1;
    if (t < tk) {
      const a = (t - debut) / CHUTE(k);
      dz = 18 * (1 - a * a);
    } else {
      const v = (t - tk) / 0.45;
      if (v < 1) {
        dz = 2.6 * Math.abs(Math.sin(Math.PI * 1.5 * v)) * Math.exp(-3.5 * v);
        ecr = 1 - 0.28 * Math.max(0, Math.cos(Math.PI * 1.5 * v)) * Math.exp(-5 * v);
      }
    }
    g.position.copy(point(u, 1.55 + dz));
    g.rotation.set(0, 0, angle(u));
    g.scale.set(s * (2 - ecr), s * (2 - ecr), s * ecr);
    // la case s'allume au contact, avec un ressort
    const e = (t - tk) / 0.32;
    if (e >= 0) {
      cases.setColorAt(k, outils.couleur(groupe(k) ? 22 : 4));
      placerCase(k, 0.75 + 0.25 * ressort(e));
    } else {
      cases.setColorAt(k, outils.couleur(groupe(k) ? 21 : 3));
      placerCase(k, 1);
    }
  }

  // ---------- caméra ----------
  // abscisse suivie : somme de pas lissés (fonction pure de t) ; démarre en amont sur le ruban vide
  const etapes = [{ t: T0, d: 1.35, de: -3.5, a: (pos[0] + pos[1]) / 2 }];
  etapes.push({ t: mots[0] - 0.3, d: 0.6, a: pos[2] });
  for (let i = 1; i < mots.length; i++) etapes.push({ t: mots[i] - 0.3, d: 0.6, a: pos[2 + i] });
  for (let k = 2 + mots.length; k < NPOSES; k++) etapes.push({ t: poses[k] - 0.1, d: 0.3, a: pos[k] });
  function suivi(t) {
    let f = etapes[0].de, prec = etapes[0].de;
    for (const e of etapes) { f += (e.a - prec) * lisse((t - e.t) / e.d); prec = e.a; }
    return f;
  }
  const DSUIVI = 130;
  const RECUL = 1.0;    // le dernier chiffre posé est un peu à droite du centre : on voit ceux d'avant
  const decalage = (fov, d, px) => (px / (outils.hauteur / 2)) * d * Math.tan((fov / 2) * Math.PI / 180);
  const centreLoin = new THREE.Vector3(0, 0, -ZH * 0.35);
  function placerCamera(t) {
    const f = suivi(t) - RECUL * lisse((t - T0) / 1.35);
    const s = sigma(f);
    const w = lisse((t - tInf) / 0.85);                         // recul final
    const approche = 1 - lisse((t - T0) / 1.4);                 // un peu plus près au tout début (recule en glissant)
    const fov = FOV0 + (FOV1 - FOV0) * w;
    camera.fov = fov;
    camera.updateProjectionMatrix();
    // roulis : garde la tête du chiffre suivi vers le haut, plus une lente dérive
    const roulis = angle(f) + 0.05 * Math.sin(0.7 * (t - T0));
    const haut = new THREE.Vector3(-Math.sin(roulis), Math.cos(roulis), 0);
    const foyer = point(f, 1.5).lerp(centreLoin, w);
    const d = DSUIVI * s * (1 - 0.1 * approche) * (1 - w) + 420 * w;
    const px = 52 + (40 - 52) * w;                              // le foyer est placé px pixels au-dessus du centre
    const dec = decalage(fov, d, px);
    const derive = new THREE.Vector3(1.2 * Math.sin(0.9 * (t - T0)), 0.8 * Math.sin(1.3 * (t - T0) + 1), 0).multiplyScalar(s * (1 - w) + 3 * w);
    const cible = foyer.clone().addScaledVector(haut, -dec).add(derive);
    camera.position.set(cible.x, cible.y, foyer.z + d);
    camera.up.copy(haut);
    camera.lookAt(cible);
  }

  function update(t) {
    for (let k = 0; k < NPOSES; k++) reglerChiffre(k, t);
    cases.instanceMatrix.needsUpdate = true;
    if (cases.instanceColor) cases.instanceColor.needsUpdate = true;
    placerCamera(t);
  }

  return { scene, camera, update };
}
