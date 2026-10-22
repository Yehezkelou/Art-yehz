// ico-vid : démo de outils.voxel, le chibi de voxel_demo.py qui marche sur sa dalle, caméra en orbite.
//
//   python3 -I outils/rendu3d/exemples/voxel_demo.py          # fabrique voxel_demo.vox / .rig.toml / .caisse.png
//   node outils/rendu3d/rendu3d.mjs --scene outils/rendu3d/exemples/voxel_demo.mjs --out <dossier> --debut 0 --fin 2 --ips 12
//
// params : { "rig": "./voxel_demo.rig.toml", "clip": "marche", "tours": 0.5, "duree": 2, "contour": 1, "occlusion": true }
// (« ./ » = dossier de cette scène ; un chemin sans « ./ » part de la racine du dépôt). Démo seulement.

export default async function creer(THREE, outils, params = {}) {
  const p = { rig: "./voxel_demo.rig.toml", clip: "marche", tours: 0.5, duree: 2, contour: 1, occlusion: true, ...params };
  const V = outils.voxel;

  const scene = new THREE.Scene();
  scene.background = outils.couleur(2);
  const camera = new THREE.PerspectiveCamera(30, outils.largeur / outils.hauteur, 1, 400);

  // dalle : 16 × 16 voxels d'herbe (bord plus sombre), posée pour que son dessus soit à y = 0
  const g = V.grille(16, 2, 16, "dalle");
  g.boite(0, 0, 0, 15, 0, 15, 26);
  g.boite(0, 1, 0, 15, 1, 15, 14);
  g.boite(1, 1, 1, 14, 1, 14, 15);
  for (const [x, z] of [[3, 4], [11, 3], [5, 12], [12, 11], [8, 2]]) g.set(x, 1, z, 16);
  const dalle = V.maillage(g, { centre: "bas", occlusion: p.occlusion });
  dalle.position.y = -2;
  scene.add(dalle);

  // ombre de contact : tache pleine, un cran plus sombre que l'herbe
  const ombre = new THREE.Mesh(new THREE.CircleGeometry(4, 24), new THREE.MeshBasicMaterial({ color: outils.couleur(14) }));
  ombre.rotation.x = -Math.PI / 2;
  ombre.position.y = 0.02;
  scene.add(ombre);

  const perso = await V.chargerRig(p.rig, { contour: p.contour, occlusion: p.occlusion });
  scene.add(perso);

  // caisse en boîte texturée (style n° 6) et lanterne avec son halo d'anneaux
  const caisse = new THREE.Mesh(new THREE.BoxGeometry(4, 4, 4),
    new THREE.MeshBasicMaterial({ map: outils.texturePixel("./voxel_demo.caisse.png") }));
  caisse.position.set(-5, 2, -4);
  scene.add(caisse);
  const lanterne = new THREE.Group();
  const lg = V.grille(2, 2, 2, "lanterne").boite(0, 0, 0, 1, 1, 1, 19);
  lanterne.add(V.maillage(lg, { centre: "milieu", occlusion: false }));
  const halo = outils.halo(3, [19, 18, 3], { interieur: 1.2, camera: true });
  lanterne.add(halo);
  lanterne.position.set(10, 13, 1);
  scene.add(lanterne);

  function update(t) {
    perso.poser(p.clip, t);
    lanterne.position.y = 13 + Math.round(Math.sin(2 * Math.PI * outils.pas12(t) / 2));
    const a = -0.35 + 2 * Math.PI * p.tours * (t / p.duree);
    camera.position.set(Math.sin(a) * 72, 24, Math.cos(a) * 72);
    camera.lookAt(0, 8, 0);
  }

  return { scene, camera, update };
}
