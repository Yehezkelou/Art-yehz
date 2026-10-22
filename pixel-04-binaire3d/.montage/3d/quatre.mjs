// ico-vid pixel-04-binaire3d : le « 4 » géant rouge (fenêtre 12,60–15,30 s, fond transparent, centre de l'écran).
//
//   node outils/rendu3d/rendu3d.mjs --scene pixel-04-binaire3d/.montage/3d/quatre.mjs \
//        --out pixel-04-binaire3d/.montage/3d/quatre --debut 12.6 --fin 15.3 --ips 24 --fond transparent
//
// Le 4 tombe et s'écrase (impact calé sur le son « impact » du compositeur, M(18) + 0,12 s), écrasement, étirement,
// poussière ; « Quatre ?! » (13,47) : tassement, saut avec un tour complet sur lui-même, puis il flotte en tournant
// lentement. Faces en couleurs exactes (rampe [ombre, côté, face, dessus]) choisies selon la normale vue de la caméra,
// contour sombre (coques en face arrière) pour le détacher de la scène 2D.

const AXES = [[1, 0, 0], [-1, 0, 0], [0, 1, 0], [0, -1, 0], [0, 0, 1], [0, 0, -1]];

function voxel(THREE, outils, texte, rampe, profondeur = 2, contour = 0) {
  const g = outils.voxelTexte(texte, { cube: 1, profondeur, ombre: "plat" });
  const noir = new THREE.MeshBasicMaterial({ color: outils.couleur(1), side: THREE.BackSide });
  const cache = new THREE.MeshBasicMaterial({ visible: false });
  g.children.forEach((l) => {
    const mats = AXES.map(() => new THREE.MeshBasicMaterial({ color: outils.couleur(rampe[2]) }));
    l.userData.mats = mats;
    l.userData.rampe = rampe;
    const cles = new Set(l.children.map((c) => `${Math.round(c.position.x * 2)},${Math.round(c.position.y * 2)}`));
    const voisin = (c, dx, dy) => cles.has(`${Math.round((c.position.x + dx) * 2)},${Math.round((c.position.y + dy) * 2)}`);
    [...l.children].forEach((c) => {
      c.material = mats;
      if (!contour) return;
      // coque de contour : élargie seulement vers les cases vides, faces intérieures masquées (pas de joint sombre)
      const v = [voisin(c, 1, 0), voisin(c, -1, 0), voisin(c, 0, 1), voisin(c, 0, -1)];
      const ex = [v[0] ? 0 : contour, v[1] ? 0 : contour, v[2] ? 0 : contour, v[3] ? 0 : contour];
      const geo = new THREE.BoxGeometry(1 + ex[0] + ex[1], 1 + ex[2] + ex[3], profondeur - 0.04);
      const m = new THREE.Mesh(geo, [v[0] ? cache : noir, v[1] ? cache : noir, v[2] ? cache : noir, v[3] ? cache : noir, noir, noir]);
      m.position.set(c.position.x + (ex[0] - ex[1]) / 2, c.position.y + (ex[2] - ex[3]) / 2, 0);
      l.add(m);
    });
  });
  const pivot = new THREE.Group();     // pivot au pied du glyphe
  g.position.y = 3.5;
  pivot.add(g);
  return pivot;
}

function ombreur(THREE, outils, camera) {
  // dessus = reflet, face = couleur, gauche = côté, droite et dessous = ombre (normale vue de la caméra)
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
  const T = { impact: 12.832, quatre: 13.471, ...(params.instants || {}) };
  const ROUGE = params.rampe ?? [21, 22, 23, 24];
  const ppc = 20, fov = 26;
  const D = (outils.hauteur / ppc / 2) / Math.tan((fov / 2) * Math.PI / 180);
  const wy = (sy) => (outils.hauteur / 2 - sy) / ppc;

  const scene = new THREE.Scene();
  scene.add(new THREE.AmbientLight(0xffffff, 1));
  const camera = new THREE.PerspectiveCamera(fov, outils.largeur / outils.hauteur, 1, 500);
  const ombrer = ombreur(THREE, outils, camera);

  const sol = wy(params.y_sol ?? 268);
  const quatre = voxel(THREE, outils, "4", ROUGE, 2, 0.09);
  const racine = new THREE.Group();
  racine.add(quatre);
  scene.add(racine);

  // poussière à l'impact : petits cubes gris éjectés au pied, qui rapetissent (pas de transparence)
  const h = outils.hasard(4);
  const geoP = new THREE.BoxGeometry(0.45, 0.45, 0.45);
  const matsP = [outils.materiau(7, { ombre: "plat" }), outils.materiau(6, { ombre: "plat" })];
  const poussieres = [];
  for (let i = 0; i < 10; i++) {
    const cote = i % 2 ? 1 : -1;
    const m = new THREE.Mesh(geoP, matsP[i % 3 === 0 ? 1 : 0]);
    m.userData = { cote, vx: cote * (4 + 4 * h()), vy: 3 + 5 * h(), z: (h() - 0.5) * 3, vie: 0.35 + 0.25 * h(), x0: cote * (1.6 + h()) };
    scene.add(m);
    poussieres.push(m);
  }

  function update(t) {
    // caméra : légère orbite et dérive, toujours en mouvement
    const az = 0.16 * Math.sin(0.9 * (t - 12.6) + 0.5);
    camera.position.set(D * Math.sin(az), 9 + 1.5 * Math.sin(1.1 * t), D * Math.cos(az) - 2 * outils.lisse((t - 12.6) / 2.7));
    camera.lookAt(0.3 * Math.sin(0.7 * t), 0.2 * Math.sin(0.8 * t + 1), 0);

    let y = 0, sx = 1, sy = 1, ry = 0, rz = 0;
    const tau = t - T.impact;
    if (tau < 0) {                                       // chute accélérée, étiré
      const u = -tau / 0.23;
      y = 26 * u * u;
      sx = 0.88; sy = 1.18;
      rz = -0.12 * u;
    } else if (t < T.quatre - 0.14) {                    // écrasement → étirement → repos en < 0,2 s, petit rebond
      const s = 1 - 0.45 * Math.exp(-16 * tau) * Math.cos(30 * tau);
      sy = s; sx = 1 / Math.sqrt(s);
      y = 1.1 * Math.exp(-7 * tau) * Math.max(0, Math.sin(Math.PI * (tau - 0.07) / 0.22)) * (tau > 0.07 ? 1 : 0);
      ry = 0.12 * Math.sin(2 * Math.PI * (t - T.impact) / 1.6) * outils.entre(t, T.impact + 0.2, T.impact + 0.5);
    } else {
      const ta = T.quatre - 0.14;                        // anticipation : il se tasse
      const air = 0.62;                                  // temps de vol
      if (t < T.quatre) {
        const u = (t - ta) / 0.14;
        sy = 1 - 0.2 * outils.lisse(u); sx = 1 / Math.sqrt(sy);
        ry = 0.12 * Math.sin(2 * Math.PI * (t - T.impact) / 1.6) * (1 - outils.lisse(u));
      } else {
        const v = (t - T.quatre) / air;                  // 0 → 1 pendant le vol
        const flot = 0.9;                                // hauteur où il finit par flotter
        if (v < 1) {
          const haut = 3.0;
          y = haut * 4 * v * (1 - v) + flot * outils.lisse(v);      // parabole qui retombe sur la hauteur de flottement
          const st = 1 + 0.16 * Math.exp(-9 * v) - 0.02;            // étiré au décollage
          sy = st; sx = 1 / Math.sqrt(st);
          ry = 2 * Math.PI * outils.lisse(Math.min(1, v * 1.08));   // un tour complet
        } else {
          const w = t - T.quatre - air;
          y = flot + 0.35 * Math.sin(2 * Math.PI * w / 1.3) * outils.lisse(w / 0.4)
            - 0.35 * Math.exp(-6 * w) * Math.sin(Math.PI * Math.min(1, w / 0.25));
          const s = 1 - 0.08 * Math.exp(-9 * w) * Math.cos(20 * w);
          sy = s; sx = 1 / Math.sqrt(s);
          ry = 2 * Math.PI + 0.42 * Math.sin(1.5 * w);                     // rotation lente
          rz = 0.05 * Math.sin(2 * Math.PI * w / 1.7);
        }
      }
    }
    racine.position.set(0, sol + y, 0);
    quatre.scale.set(sx, sy, 1);
    quatre.rotation.set(0, ry, rz);

    poussieres.forEach((p) => {
      const d = p.userData, u = tau / d.vie;
      p.visible = tau > 0 && u < 1;
      if (!p.visible) return;
      p.position.set(d.x0 + d.vx * tau, sol + 0.2 + d.vy * tau - 14 * tau * tau, d.z);
      p.scale.setScalar(1 - u);
      p.rotation.set(5 * tau * d.cote, 3 * tau, 0);
    });

    ombrer(scene);
  }

  return { scene, camera, update };
}
