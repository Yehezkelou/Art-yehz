// ico-vid : démo de rendu3d, un « 0,1 » en voxels qui tourne (sert aussi au test outils/tests/test_rendu3d.py).
//
//   node outils/rendu3d/rendu3d.mjs --scene outils/rendu3d/exemples/demo.mjs --out /tmp/demo --debut 0 --fin 1
//
// params : { "texte": "0,1", "tours_par_seconde": 0.25 }

export default function creer(THREE, outils, params = {}) {
  const texte = params.texte ?? "0,1";
  const vitesse = params.tours_par_seconde ?? 0.25;

  const scene = new THREE.Scene();
  const camera = new THREE.PerspectiveCamera(35, outils.largeur / outils.hauteur, 1, 200);
  camera.position.set(0, 6, 52);
  camera.lookAt(0, 0, 0);

  scene.add(new THREE.AmbientLight(0xffffff, 0.8));
  const soleil = new THREE.DirectionalLight(0xffffff, 2.4);
  soleil.position.set(-4, 6, 8);
  scene.add(soleil);

  const mot = outils.voxelTexte(texte, { cube: 1, profondeur: 2, couleur: 8 });
  const teintes = [19, 8, 12];  // jaune, crème, bleu clair (index de la palette, 1–32)
  mot.children.forEach((lettre, k) => {
    const m = outils.materiau(teintes[k % teintes.length]);
    lettre.children.forEach((cube) => { cube.material = m; });
  });
  scene.add(mot);

  // quelques « poussières » fixes, tirées avec une graine (déterministe)
  const h = outils.hasard(7);
  const geo = new THREE.BoxGeometry(0.6, 0.6, 0.6);
  const mat = outils.materiau(30, { ombre: false });
  for (let i = 0; i < 14; i++) {
    const p = new THREE.Mesh(geo, mat);
    p.position.set((h() - 0.5) * 22, (h() - 0.5) * 34, (h() - 0.5) * 10 - 6);
    scene.add(p);
  }

  function update(t) {
    mot.rotation.y = 2 * Math.PI * vitesse * t;
    mot.children.forEach((lettre, k) => {
      const s = 0.4 + 0.6 * outils.ressort((t - 0.08 * k) / 0.5);  // pop à l'entrée, une lettre après l'autre
      lettre.scale.setScalar(s);
      lettre.position.y = Math.sin(2 * Math.PI * (t * 0.8 + k / 3)) * 0.8;
    });
  }

  return { scene, camera, update };
}
