// pixel-04-binaire3d : scène 3D « ecrans » (26,90–29,40, opaque, mur 4).
// Carrousel de 4 écrans (JAVASCRIPT, PYTHON, JAVA, RUBY) qui tourne sur « Presque tous les langages donnent ce
// résultat » : JAVA puis RUBY défilent, JAVASCRIPT se pose de face (dépassement amorti) et reste lisible pendant
// « langages donnent », puis le carrousel repart vers PYTHON. Caméra en orbite lente (passe de face au milieu).
//
//   node outils/rendu3d/rendu3d.mjs --scene pixel-04-binaire3d/.montage/3d/ecrans.mjs \
//        --out pixel-04-binaire3d/.montage/3d/ecrans --debut 26.9 --fin 29.4 --ips 24 --fond 4A4663
//
// Ombrage : matériau « rampe » maison (3 couleurs exactes de la palette choisies selon l'orientation de la face
// par rapport à une lumière fixe) : aucune teinte intermédiaire, donc rien ne bave à la quantification.
// params (facultatifs) : { "debut": 26.9, "fin": 29.4, "pose": 28.0, "repart": 28.75 }

function rampe(THREE, outils, couleurs, seuils, lumiere) {
  const [a, b, c] = couleurs.length === 3 ? couleurs : [couleurs[0], couleurs[1], couleurs[1]];
  return new THREE.ShaderMaterial({
    uniforms: {
      c0: { value: outils.couleur(a) }, c1: { value: outils.couleur(b) }, c2: { value: outils.couleur(c) },
      s: { value: new THREE.Vector2(seuils[0], seuils[1]) }, L: { value: lumiere },
    },
    vertexShader: `varying vec3 vN;
      void main() { vN = normalize(mat3(modelMatrix) * normal);
        gl_Position = projectionMatrix * modelViewMatrix * vec4(position, 1.0); }`,
    fragmentShader: `uniform vec3 c0; uniform vec3 c1; uniform vec3 c2; uniform vec2 s; uniform vec3 L; varying vec3 vN;
      void main() { vec3 n = normalize(vN); if (!gl_FrontFacing) n = -n; float d = dot(n, L);
        vec3 c = d > s.y ? c2 : (d > s.x ? c1 : c0); gl_FragColor = vec4(c, 1.0);
        #include <colorspace_fragment>
      }`,
  });
}

export default function creer(THREE, outils, params = {}) {
  const T0 = params.debut ?? 26.9, T1 = params.fin ?? 29.4;
  const POSE = params.pose ?? 28.0, REPART = params.repart ?? 28.75;
  const MILIEU = (T0 + T1) / 2;

  const scene = new THREE.Scene();
  scene.background = outils.couleur(4);
  const camera = new THREE.PerspectiveCamera(30, outils.largeur / outils.hauteur, 20, 2000);

  // lumière fixe du monde : haut, un peu à gauche, de face
  const L = new THREE.Vector3(-0.35, 0.72, 0.6).normalize();
  const plat = (i) => outils.materiau(i, { ombre: "plat" });

  // --- mur du fond et sol (plats) ---
  const mur = new THREE.Mesh(new THREE.PlaneGeometry(2000, 1200), plat(4));
  mur.position.set(0, 0, -260);
  scene.add(mur);
  const SOL_Y = -150;
  const sol = new THREE.Mesh(new THREE.PlaneGeometry(2000, 900), plat(26));
  sol.rotation.x = -Math.PI / 2;
  sol.position.set(0, SOL_Y, 0);
  scene.add(sol);
  const plinthe = new THREE.Mesh(new THREE.BoxGeometry(2000, 4, 2), plat(3));
  plinthe.position.set(0, SOL_Y + 2, -259);
  scene.add(plinthe);
  // lambris du décor 2D (lignes verticales 3) au-dessus d'une cimaise, mur uni en dessous (bande des sous-titres)
  const CIMAISE = -106;
  const rail = new THREE.Mesh(new THREE.BoxGeometry(2000, 2.4, 2), plat(3));
  rail.position.set(0, CIMAISE, -258.5);
  scene.add(rail);
  const latte = plat(3);
  const geoLatte = new THREE.BoxGeometry(1.3, 700, 0.6);
  for (let k = -40; k <= 40; k++) {
    const l = new THREE.Mesh(geoLatte, latte);
    l.position.set(k * 15 + 7, CIMAISE + 350, -259.5);
    scene.add(l);
  }
  const lame = plat(25);
  for (let k = -12; k <= 6; k++) {  // joints du parquet (lignes 25), parallèles au mur
    const j = new THREE.Mesh(new THREE.BoxGeometry(2000, 0.4, 1.6), lame);
    j.position.set(0, SOL_Y + 0.1, k * 22 - 40);
    scene.add(j);
  }

  // --- carrousel ---
  const LANGAGES = [
    { nom: "JAVASCRIPT", ramp: [9, 10, 11] },
    { nom: "PYTHON", ramp: [21, 22, 23] },
    { nom: "JAVA", ramp: [17, 18, 19] },
    { nom: "RUBY", ramp: [29, 30, 31] },
  ];
  const W = 71, H = 39, D = 5, R = 40;  // boîtier (en cubes de texte), distance de l'axe
  const seuils = [0.22, 0.66];
  const creme = rampe(THREE, outils, [7, 8, 8], seuils, L);
  const vert = rampe(THREE, outils, [14, 15, 15], seuils, L);
  const rouge = rampe(THREE, outils, [22, 23, 23], seuils, L);
  const gris = rampe(THREE, outils, [3, 4, 5], seuils, L);

  const carrousel = new THREE.Group();
  scene.add(carrousel);
  const noyau = new THREE.Mesh(new THREE.BoxGeometry(2 * (R - 2), H - 2, 2 * (R - 2)), gris);
  carrousel.add(noyau);
  // axe qui monte au plafond (hors cadre)
  const axe = new THREE.Mesh(new THREE.CylinderGeometry(4, 4, 400, 12), rampe(THREE, outils, [2, 3, 5], seuils, L));
  axe.position.y = H / 2 + 200;
  carrousel.add(axe);
  const chapeau = new THREE.Mesh(new THREE.CylinderGeometry(14, 18, 4, 16), gris);
  chapeau.position.y = H / 2 + 2;
  carrousel.add(chapeau);

  function poserTexte(groupe, texte, couleurDernier, x0, y, mat, matDernier) {
    const t = outils.voxelTexte(texte, { cube: 1, profondeur: 1 });
    // alignement à gauche : le groupe est centré, on retrouve sa largeur en cubes
    const box = new THREE.Box3().setFromObject(t);
    const largeur = box.max.x - box.min.x;
    t.position.set(x0 + largeur / 2, y, D / 2 + 0.7);
    t.children.forEach((lettre, k) => {
      const m = (couleurDernier && k === t.children.length - 1) ? matDernier : mat;
      lettre.children.forEach((cube) => { cube.material = m; });
    });
    groupe.add(t);
    return t;
  }

  const ecrans = LANGAGES.map((lg, i) => {
    const g = new THREE.Group();
    const a = (i * Math.PI) / 2;
    g.position.set(Math.sin(a) * R, 0, Math.cos(a) * R);
    g.rotation.y = a;
    const boitier = new THREE.Mesh(new THREE.BoxGeometry(W, H, D), rampe(THREE, outils, lg.ramp, seuils, L));
    g.add(boitier);
    const cadre = new THREE.Mesh(new THREE.PlaneGeometry(W - 5, H - 5), plat(2));
    cadre.position.z = D / 2 + 0.12;
    g.add(cadre);
    const vitre = new THREE.Mesh(new THREE.PlaneGeometry(W - 7, H - 7), plat(1));
    vitre.position.z = D / 2 + 0.24;
    g.add(vitre);
    // lisière claire en haut du boîtier (comme le décor 2D)
    const liseré = new THREE.Mesh(new THREE.BoxGeometry(W, 0.8, D + 0.1), rampe(THREE, outils, [lg.ramp[1], lg.ramp[2], 8], seuils, L));
    liseré.position.y = H / 2 - 0.4;
    g.add(liseré);
    const X0 = -29.5;  // bord gauche du texte (59 cubes de large au plus)
    poserTexte(g, lg.nom, false, X0, 9.5, creme);
    poserTexte(g, "0.3000000", false, X0, -1.0, vert);
    poserTexte(g, "0000000004", true, X0, -10.0, vert, rouge);
    carrousel.add(g);
    return g;
  });
  void ecrans;

  // angle du carrousel : JAVA (180°) → RUBY (90°) → JAVASCRIPT (0°, posé avec dépassement) → vers PYTHON (−90°)
  const DEP = 1.25;  // force du dépassement (easeOutBack)
  function arrivee(u) {
    u = Math.min(1, Math.max(0, u));
    const v = u - 1;
    return 1 + (DEP + 1) * v * v * v + DEP * v * v;
  }
  function angle(t) {
    let th = Math.PI * (1 - arrivee((t - T0) / (POSE - T0)));  // 180° → 0
    th -= 0.035 * Math.max(0, t - POSE);                          // reptation pendant la pose
    const u = Math.max(0, (t - REPART) / (T1 - REPART));
    th -= (Math.PI / 2) * u * u * (0.6 + 0.4 * u);                 // repart en accélérant
    return th;
  }

  const CIBLE = new THREE.Vector3(0, -24, 0);
  function update(t) {
    carrousel.rotation.y = angle(t);
    // caméra : orbite de −9° à +9° (de face au milieu), légère montée, petit travelling avant
    const u = (t - T0) / (T1 - T0);
    const phi = THREE.MathUtils.degToRad(-9 * Math.cos(Math.PI * Math.min(1, Math.max(0, u))));
    const dist = 290 - 12 * outils.lisse(u);
    const haut = 26 + 6 * Math.sin(Math.PI * u);
    camera.position.set(Math.sin(phi) * dist, haut, Math.cos(phi) * dist);
    camera.lookAt(CIBLE);
    void MILIEU;
  }

  return { scene, camera, update };
}
