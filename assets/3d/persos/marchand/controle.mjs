// ico-vid : scène de contrôle de le marchand en voxels : il joue ses clips l'un après l'autre, caméra en orbite lente.
//
//   python3 -I assets/3d/persos/marchand/marchand.py
//   node outils/rendu3d/rendu3d.mjs --scene assets/3d/persos/marchand/controle.mjs --out <dossier> --debut 0 --fin 18 --ips 12
//
// params : { "rig": "./marchand.rig.toml", "clips": ["idle", …], "duree": 3, "tours": 1, "clip": null (un seul clip),
//            "angle": null (caméra fixe, radians), "distance": 92 }
// Chaque clip dure `duree` s (3 s par défaut : idle 0–3, marche 3–6, saut 6–9, parle 9–12, coucou 12–15, non_de_la_tete 15–18).

import { installer } from "./marchand.clips.mjs";

export default async function creer(THREE, outils, params = {}) {
  const p = { rig: "./marchand.rig.toml", clips: ["idle", "marche", "saut", "parle", "coucou", "non_de_la_tete"], duree: 3,
    tours: 1, clip: null, angle: null, distance: 92, ...params };
  const V = outils.voxel;

  const scene = new THREE.Scene();
  scene.background = outils.couleur(3);
  const camera = new THREE.PerspectiveCamera(24, outils.largeur / outils.hauteur, 1, 500);

  // dalle de pierre 14 × 14 (dessus à y = 0)
  const g = V.grille(14, 2, 14, "dalle");
  g.boite(0, 0, 0, 13, 0, 13, 4);
  g.boite(0, 1, 0, 13, 1, 13, 6);
  for (const [x, z] of [[2, 3], [9, 2], [4, 10], [11, 9], [6, 6]]) g.set(x, 1, z, 5);
  const dalle = V.maillage(g, { centre: "bas" });
  dalle.position.y = -2;
  scene.add(dalle);
  const ombre = new THREE.Mesh(new THREE.CircleGeometry(5.5, 24), new THREE.MeshBasicMaterial({ color: outils.couleur(5) }));
  ombre.rotation.x = -Math.PI / 2;
  ombre.position.y = 0.02;
  scene.add(ombre);

  const perso = installer(await V.chargerRig(p.rig));
  scene.add(perso);
  const total = p.clips.length * p.duree;

  function update(t) {
    const k = Math.min(p.clips.length - 1, Math.floor(t / p.duree));
    const clip = p.clip || p.clips[k];
    perso.poser(clip, p.clip ? t : t - k * p.duree);
    const a = p.angle !== null ? p.angle : 0.5 + TAU * p.tours * (t / total);
    camera.position.set(Math.sin(a) * p.distance, 30, Math.cos(a) * p.distance);
    camera.lookAt(0, 9, 0);
  }
  return { scene, camera, update };
}

const TAU = 2 * Math.PI;
