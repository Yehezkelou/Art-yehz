// ico-vid pixel-04-binaire3d : « 0,1 + 0,2 = 0,3 » en voxels (fenêtre 0,00–6,60 s, fond transparent, haut d'écran).
//
//   node outils/rendu3d/rendu3d.mjs --scene pixel-04-binaire3d/.montage/3d/equation.mjs \
//        --out pixel-04-binaire3d/.montage/3d/equation --debut 0 --fin 6.6 --ips 24 --fond transparent
//
// « 0,1 » (crème 8) tombe et rebondit, « + » puis « 0,2 » tombent, la ligne tangue ; « Facile ! » : la ligne remonte
// d'un cran ; « = » or puis « 0,3 » or jaillissent sur une 2e ligne. Instants absolus (mots du dialogue) en params.
// Ombrage : faces en couleurs exactes de la palette (MeshBasicMaterial), choisies chaque image selon l'orientation de
// la face vis-à-vis d'une lumière fixe : rampe [ombre, côté, face, dessus].

const AXES = [[1, 0, 0], [-1, 0, 0], [0, 1, 0], [0, -1, 0], [0, 0, 1], [0, 0, -1]];

function voxel(THREE, outils, texte, rampe, profondeur = 3) {
  const g = outils.voxelTexte(texte, { cube: 1, profondeur, ombre: "plat" });
  g.children.forEach((l) => {
    const mats = AXES.map(() => new THREE.MeshBasicMaterial({ color: outils.couleur(rampe[2]) }));
    l.userData.mats = mats;
    l.userData.rampe = rampe;
    l.children.forEach((c) => { c.material = mats; });
  });
  // pivot au pied du texte (écrasement et rebond depuis le sol)
  const pivot = new THREE.Group();
  g.position.y = 3.5;
  pivot.add(g);
  pivot.userData.largeur = new THREE.Box3().setFromObject(g).getSize(new THREE.Vector3()).x;
  return pivot;
}

function ombreur(THREE, outils, camera) {
  // couleur d'une face selon sa normale vue de la caméra : dessus = reflet, face = couleur, gauche = côté, droite et
  // dessous = ombre (lumière « de face, un peu en haut à gauche » ; couleurs exactes, rien ne bave entre deux rampes)
  const cache = new Map();
  const col = (i) => { if (!cache.has(i)) cache.set(i, outils.couleur(i)); return cache.get(i); };
  const q = new THREE.Quaternion(), qc = new THREE.Quaternion(), n = new THREE.Vector3();
  return function ombrer(racine) {
    racine.updateMatrixWorld(true);
    camera.updateMatrixWorld(true);
    camera.getWorldQuaternion(qc).invert();
    racine.traverse((o) => {
      if (!o.userData.mats || !o.visible) return;
      o.getWorldQuaternion(q).premultiply(qc);
      AXES.forEach((a, i) => {
        n.set(a[0], a[1], a[2]).applyQuaternion(q);
        const k = n.y > 0.5 ? 3 : n.y < -0.5 ? 0 : n.z > 0.6 ? 2 : n.x < 0 ? 1 : 0;
        o.userData.mats[i].color.copy(col(o.userData.rampe[k]));
      });
    });
  };
}

export default function creer(THREE, outils, params = {}) {
  const T = {
    zero: 0.02, plus: 1.837, deux: 2.103, facile: 3.867, egal: 4.807, trois: 5.767,
    ...(params.instants || {}),
  };
  const CREME = [5, 6, 8, 7], OR = [17, 18, 19, 20];
  const ppc = 5.5;                                      // pixels par cube à la profondeur 0
  const fov = 22;
  const D = (outils.hauteur / ppc / 2) / Math.tan((fov / 2) * Math.PI / 180);
  const wy = (sy) => (outils.hauteur / 2 - sy) / ppc;  // y écran (px, depuis le haut) → y monde à z = 0

  const scene = new THREE.Scene();
  scene.add(new THREE.AmbientLight(0xffffff, 1));
  const camera = new THREE.PerspectiveCamera(fov, outils.largeur / outils.hauteur, 10, 1000);
  const ombrer = ombreur(THREE, outils, camera);

  // ligne 1 : 0,1 + 0,2
  const ligne1 = new THREE.Group();
  const a = voxel(THREE, outils, "0,1", CREME);
  const p = voxel(THREE, outils, "+", CREME);
  const b = voxel(THREE, outils, "0,2", CREME);
  const ecart = 3;
  const l1 = a.userData.largeur + p.userData.largeur + b.userData.largeur + 2 * ecart;
  a.position.x = -l1 / 2 + a.userData.largeur / 2;
  p.position.x = a.position.x + a.userData.largeur / 2 + ecart + p.userData.largeur / 2;
  b.position.x = p.position.x + p.userData.largeur / 2 + ecart + b.userData.largeur / 2;
  [a, p, b].forEach((o) => { o.userData.x0 = o.position.x; ligne1.add(o); });
  const pied1 = new THREE.Group();          // pivot de tangage au centre de la ligne
  pied1.add(ligne1);
  ligne1.position.y = -3.5;
  scene.add(pied1);

  // ligne 2 : = 0,3 (or ; 0,3 plus gros)
  const ligne2 = new THREE.Group();
  const e = voxel(THREE, outils, "=", OR);
  const r = voxel(THREE, outils, "0,3", OR);
  const gros = 1.25;
  const l2 = e.userData.largeur + ecart + r.userData.largeur * gros;
  e.position.x = -l2 / 2 + e.userData.largeur / 2;
  r.position.x = l2 / 2 - (r.userData.largeur * gros) / 2;
  e.position.y = 0.5;
  [e, r].forEach((o) => ligne2.add(o));
  const pied2 = new THREE.Group();
  pied2.add(ligne2);
  ligne2.position.y = -3.5 * gros;
  scene.add(pied2);

  const Y1 = wy(params.y_ligne1 ?? 122), Y1h = wy(params.y_ligne1_haut ?? 96), Y2 = wy(params.y_ligne2 ?? 186);

  // chute : arrive au sol à tl (accélération), puis écrasement amorti et petit rebond
  function chute(o, t, tl, haut = 70, duree = 0.32) {
    const tau = t - tl;
    o.visible = tau > -duree;
    if (!o.visible) return;
    if (tau < 0) {
      const u = -tau / duree;
      o.position.y = haut * u * u;
      o.scale.set(0.9, 1.14, 1);
      o.rotation.z = 0.25 * u * Math.sign(o.userData.x0 || 1);
      return;
    }
    const s = 1 - 0.34 * Math.exp(-11 * tau) * Math.cos(26 * tau);   // écrasement → étirement → repos
    o.scale.set(1 / Math.sqrt(s), s, 1);
    o.position.y = 3.2 * Math.exp(-5 * tau) * Math.abs(Math.sin(Math.PI * tau / 0.3)) * (tau > 0.06 ? 1 : 0);
    o.rotation.z = 0;
  }

  function update(t) {
    // caméra : dérive lente, toujours un peu en mouvement
    camera.position.set(14 * Math.sin(0.55 * t + 0.4), 34 + 6 * Math.sin(0.42 * t), D + 6 * Math.sin(0.3 * t));
    camera.lookAt(1.2 * Math.sin(0.35 * t), 0.6 * Math.sin(0.5 * t + 1), 0);

    chute(a, t, T.zero + 0.12, 70, 0.30);
    chute(p, t, T.plus + 0.06);
    chute(b, t, T.deux + 0.06);

    // ligne 1 : remonte d'un cran à « Facile ! » (anticipation : petit tassement avant)
    const ant = t > T.facile - 0.12 && t < T.facile ? -0.8 * Math.sin(Math.PI * (t - T.facile + 0.12) / 0.12) : 0;
    const monte = outils.ressort((t - T.facile) / 0.55);
    pied1.position.y = Y1 + (Y1h - Y1) * monte + ant + 0.5 * Math.sin(2 * Math.PI * t / 2.3);
    // tangage : ±10° d'amplitude, entrée en douceur, et rotation douce en profondeur
    const amp = 10 * Math.PI / 180 * outils.entre(t, 0.2, 1.6);
    pied1.rotation.z = amp * Math.sin(2 * Math.PI * (t - 0.2) / 3.4);
    pied1.rotation.y = 0.32 * Math.sin(2 * Math.PI * t / 4.6 + 0.6);
    pied1.rotation.x = 0.06 * Math.sin(2 * Math.PI * t / 3.1);

    // ligne 2 : « = » glisse et claque, « 0,3 » jaillit avec un ressort
    const ue = (t - T.egal) / 0.5;
    e.visible = ue > 0;
    if (e.visible) {
      const se = outils.ressort(ue);
      e.scale.set(se, se, se);
      e.position.x = -l2 / 2 + e.userData.largeur / 2 - 9 * (1 - outils.lisse(ue * 1.6));
    }
    const ur = (t - T.trois) / 0.6;
    r.visible = ur > 0;
    if (r.visible) {
      const sr = gros * outils.ressort(ur);
      r.scale.set(sr, sr * (1 + 0.25 * Math.exp(-8 * Math.max(0, t - T.trois))), sr);
      r.position.y = -6 * (1 - outils.ressort(ur * 1.2));
      r.rotation.x = -1.2 * (1 - outils.ressort(ur));
    }
    pied2.position.y = Y2 + 0.6 * Math.sin(2 * Math.PI * t / 2.0 + 1.3) * outils.entre(t, T.trois, T.trois + 0.6);
    pied2.rotation.z = (6 * Math.PI / 180) * Math.sin(2 * Math.PI * (t - T.egal) / 3.0) * outils.entre(t, T.trois, T.trois + 0.8);
    pied2.rotation.y = 0.3 * Math.sin(2 * Math.PI * t / 3.7 + 2.0);

    ombrer(scene);
  }

  return { scene, camera, update };
}
