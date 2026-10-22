// ico-vid pixel-04-binaire3d : « Le fameux… quatre. » (fenêtre 68,60–70,85 s, opaque, plein cadre).
//
//   node outils/rendu3d/rendu3d.mjs --scene pixel-04-binaire3d/.montage/3d/fameux.mjs \
//        --out pixel-04-binaire3d/.montage/3d/fameux --debut 68.6 --fin 70.85 --ips 24 --fond 1D1B2E
//
// Fond nuit (2), rayons (3) qui tournent derrière, poursuite (faisceau 4, flaque 5) sur un « 4 » voxel or (19) ;
// travelling avant lent ; à « quatre » (69,454) le 4 passe au rouge (23), sursaut et tour rapide sur lui-même.
// Bande des sous-titres (y 312–352) recouverte d'un aplat nuit attaché à la caméra (fond uni).

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
      const ex = v.map((x) => (x ? 0 : contour));
      const geo = new THREE.BoxGeometry(1 + ex[0] + ex[1], 1 + ex[2] + ex[3], profondeur - 0.04);
      const m = new THREE.Mesh(geo, [...v.map((x) => (x ? cache : noir)), noir, noir]);
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
  const T = { debut: 68.6, quatre: 69.454, fin: 70.85, ...(params.instants || {}) };
  const OR = [17, 18, 19, 20], ROUGE = [21, 22, 23, 24];
  const fov = 30, tg = Math.tan((fov / 2) * Math.PI / 180);
  const yCentre = params.y_quatre ?? 172;              // y écran du centre du 4

  const scene = new THREE.Scene();
  scene.background = outils.couleur(2);
  scene.add(new THREE.AmbientLight(0xffffff, 1));
  const camera = new THREE.PerspectiveCamera(fov, outils.largeur / outils.hauteur, 1, 300);
  scene.add(camera);
  const ombrer = ombreur(THREE, outils, camera);

  // rayons : éventail de triangles (3) dans un plan lointain, centré derrière le 4
  const rayons = new THREE.Group();
  const nb = 9, R = 140;
  const pos = [];
  for (let i = 0; i < nb; i++) {
    const a = (2 * Math.PI * i) / nb, w = Math.PI / nb * 0.38;
    pos.push(0, 0, 0, R * Math.cos(a - w), R * Math.sin(a - w), 0, R * Math.cos(a + w), R * Math.sin(a + w), 0);
  }
  const geoR = new THREE.BufferGeometry();
  geoR.setAttribute("position", new THREE.Float32BufferAttribute(pos, 3));
  rayons.add(new THREE.Mesh(geoR, new THREE.MeshBasicMaterial({ color: outils.couleur(3), side: THREE.DoubleSide })));
  rayons.position.set(0, 4, -45);
  scene.add(rayons);

  // poursuite : faisceau (face intérieure du cône seulement, donc derrière le 4) et flaque au sol
  const faisceau = new THREE.Mesh(
    new THREE.ConeGeometry(4.6, 40, 32, 1, true),
    new THREE.MeshBasicMaterial({ color: outils.couleur(4), side: THREE.BackSide }),
  );
  faisceau.position.set(0, 20, 0);
  scene.add(faisceau);
  // plancher de scène (nuit 2) : cache les rayons sous l'horizon
  const sol = new THREE.Mesh(new THREE.PlaneGeometry(400, 400), new THREE.MeshBasicMaterial({ color: outils.couleur(2) }));
  sol.rotation.x = -Math.PI / 2;
  scene.add(sol);
  const flaque = new THREE.Mesh(new THREE.CircleGeometry(5.0, 48), new THREE.MeshBasicMaterial({ color: outils.couleur(4) }));
  flaque.rotation.x = -Math.PI / 2;
  flaque.position.y = 0.06;
  scene.add(flaque);
  const flaque2 = new THREE.Mesh(new THREE.CircleGeometry(3.1, 40), new THREE.MeshBasicMaterial({ color: outils.couleur(5) }));
  flaque2.rotation.x = -Math.PI / 2;
  flaque2.position.y = 0.12;
  scene.add(flaque2);

  const quatre = voxel(THREE, outils, "4", OR, 2, 0.1);
  const lettre = quatre.children[0].children[0];
  scene.add(quatre);

  // aplat nuit sur la bande des sous-titres (attaché à la caméra, devant tout le reste du décor)
  const dist = 1.5;
  const ndc = (sy) => 1 - 2 * sy / outils.hauteur;
  const yh = ndc(304) * dist * tg, yb = ndc(360) * dist * tg;
  const bande = new THREE.Mesh(new THREE.PlaneGeometry(10, yh - yb), new THREE.MeshBasicMaterial({ color: outils.couleur(2) }));
  bande.position.set(0, (yh + yb) / 2, -dist);
  bande.renderOrder = 10;
  camera.add(bande);

  function update(t) {
    const u = (t - T.debut) / (T.fin - T.debut);
    const kick = outils.ressort((t - T.quatre) / 0.5);          // 0 → 1 avec dépassement, au « quatre »
    // travelling avant lent (ease-in-out), poussée sèche au « quatre », légère orbite et roulis
    const D = 54 - 18 * outils.lisse(u) - 4 * kick;
    const ppc = outils.hauteur / (2 * D * tg);
    const az = 0.22 * Math.sin(1.1 * (t - T.debut) + 0.3) * (1 - 0.4 * u);
    const lookY = 3.5 - (240 - yCentre) / ppc;
    camera.position.set(D * Math.sin(az), lookY + 4 + 0.5 * Math.sin(1.7 * t), D * Math.cos(az));
    camera.lookAt(0, lookY, 0);
    camera.rotateZ(0.035 * Math.sin(1.3 * (t - T.debut)));

    rayons.rotation.z = 0.22 * (t - T.debut) + 0.9 * kick;
    const cy = camera.position.y, k = (D + 45) / D;                // centre des rayons dans l'axe caméra → 4
    rayons.position.set(camera.position.x * (1 - k), cy + (3.5 - cy) * k, -45);

    // le 4 : respiration douce, puis rouge + sursaut + tour rapide
    const rouge = t >= T.quatre;
    lettre.userData.rampe = rouge ? ROUGE : OR;
    const tq = t - T.quatre;
    let y = 0.15 * Math.sin(2 * Math.PI * (t - T.debut) / 1.6);
    let sx = 1, sy = 1, ry = 0.28 * Math.sin(1.4 * (t - T.debut) - 0.6);
    if (tq > -0.1 && tq < 0) {                                    // anticipation : il se tasse
      const a = outils.lisse((tq + 0.1) / 0.1);
      sy = 1 - 0.12 * a; sx = 1 + 0.06 * a;
    } else if (tq >= 0) {
      y += 1.4 * Math.exp(-7 * tq) * Math.sin(Math.min(Math.PI, Math.PI * tq / 0.3));
      const s = 1 + 0.22 * Math.exp(-8 * tq) * Math.cos(22 * tq);
      sy = s; sx = 1 / Math.sqrt(s);
      const tour = outils.lisse(Math.min(1, tq / 0.42));
      ry = ry * (1 - outils.lisse(tq / 0.2)) + 2 * Math.PI * tour + 0.18 * Math.sin(2.2 * tq) * outils.lisse((tq - 0.4) / 0.3);
    }
    quatre.position.set(0, y, 0);
    quatre.scale.set(sx, sy, 1);
    quatre.rotation.set(0, ry, 0);

    const pulse = 1 + 0.05 * Math.sin(2 * Math.PI * (t - T.debut) / 0.8) + 0.12 * Math.exp(-6 * Math.max(0, tq)) * (tq >= 0 ? 1 : 0);
    flaque.scale.setScalar(pulse);
    flaque2.scale.setScalar(pulse);

    ombrer(scene);
  }

  return { scene, camera, update };
}
