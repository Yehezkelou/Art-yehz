// ico-vid : scène de contrôle de la potion voxel (potion.py) : la fiole flotte devant un halo pixel,
// ses 6 particules montent en se balançant, la caméra tourne autour (orbite).
//
//   python3 -I assets/3d/objets/potion/potion.py
//   node outils/rendu3d/rendu3d.mjs --scene assets/3d/objets/potion/controle.mjs --out <dossier> --debut 0 --fin 4 --ips 12 \
//        [--params '{"couleur": "rouge", "tours": 1, "duree": 4}']
//
// params : couleur "bleue" | "rouge", tours (tours de caméra sur la durée), duree (s), distance, occlusion.
// Mouvements cadencés à 12 i/s (outils.pas12), positions arrondies au quart de voxel.

const DOSSIER = "assets/3d/objets/potion/";
const HALOS = { bleue: [3], rouge: [21] };

export default async function creer(THREE, outils, params = {}) {
  const p = { couleur: "bleue", tours: 1, duree: 4, distance: 54, occlusion: 2, ...params };
  const V = outils.voxel;
  if (!HALOS[p.couleur]) throw new Error(`controle potion : couleur « ${p.couleur} » (bleue ou rouge)`);

  const scene = new THREE.Scene();
  scene.background = outils.couleur(2);
  const camera = new THREE.PerspectiveCamera(30, outils.largeur / outils.hauteur, 1, 400);

  // verre : 12 sur le dessus et la face, 11 sur les côtés ; pour la bleue, la surface 11 du liquide reste 11 vue
  // de dessus (le 12 est au verre) et le liquide 9 garde 10 sur ses dessus
  const rampe = { 12: { dessus: 12, face: 12, cote: 11, dessous: 11 }, 11: { dessus: 12, face: 11, cote: 11, dessous: 11 } };
  if (p.couleur === "bleue") rampe[11] = { dessus: 11, face: 11, cote: 10, dessous: 10 };

  const fioles = await V.charger(DOSSIER + "potion.vox");
  const grille = fioles.find((g) => g.nom === p.couleur);
  const potion = new THREE.Group();
  const corps = V.maillage(grille, { centre: "milieu", occlusion: p.occlusion, rampe });
  potion.add(corps);
  scene.add(potion);

  // halo : anneaux pleins face caméra, dessinés avant tout le reste (toujours derrière la fiole)
  const halo = outils.halo(9, HALOS[p.couleur], { interieur: 0, segments: 40, camera: true });
  halo.traverse((o) => {
    if (o.material) { o.material.depthTest = false; o.material.depthWrite = false; }
    o.renderOrder = -10;
  });
  scene.add(halo);

  // particules : 6 voxels, chacun son départ, sa période et son balancement
  const grains = (await V.charger(DOSSIER + "potion-particules.vox")).filter((g) => g.nom.startsWith(p.couleur + "_"));
  const parts = grains.map((g, k) => {
    const m = V.maillage(g, { centre: "milieu", occlusion: false });
    scene.add(m);
    return { m, phase: k / grains.length, periode: 2.4 + 0.4 * (k % 3), dx: [-2, 2, 0, -1, 1, 2][k], amp: 1 + (k % 2) };
  });

  const q = (v) => Math.round(v * 4) / 4;

  function update(t) {
    const u = outils.pas12(t);
    // la fiole flotte (±1 voxel, 2,5 s) et penche à peine
    const yb = q(Math.sin((2 * Math.PI * u) / 2.5));
    potion.position.set(0, yb, 0);
    corps.rotation.z = Math.round(Math.sin((2 * Math.PI * u) / 5) * 4) * 0.01;
    halo.position.set(0, yb + 1, 0);
    // particules : montent de 7 voxels au-dessus du bouchon puis disparaissent, en se balançant
    for (const g of parts) {
      const s = ((u / g.periode) + g.phase) % 1;
      const x = g.dx + g.amp * Math.sin(2 * Math.PI * (s * 1.5 + g.phase));
      g.m.position.set(q(x), q(yb + 6.5 + 1 + s * 8), q(Math.cos(2 * Math.PI * (s + g.phase)) * 1.5));
      g.m.visible = s < 0.9;
    }
    const a = -0.55 + 2 * Math.PI * p.tours * (t / p.duree);
    camera.position.set(Math.sin(a) * p.distance, 16, Math.cos(a) * p.distance);
    camera.lookAt(0, 3, 0);
  }

  return { scene, camera, update };
}
