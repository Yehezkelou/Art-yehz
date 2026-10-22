// pixel-04-binaire3d : scène 3D « tarte » (31,40–40,30, transparente, posée sur le tableau de classe.png).
// Une tarte aux cerises vue de trois quarts tourne lentement ; « un tiers » (33,89) : elle s'ouvre en 3 parts qui
// s'écartent avec un ressort ; les trois « trois » (36,47 / 37,28 / 37,88) : chaque part saute à son tour ;
// « à l'infini » (39,05) : les parts tournent de plus en plus vite. Zone : tableau x 18–251, y 90–265 ;
// y 270–310 reste libre (texte 2D « 1/3 = 0,333… ») et la bande y 312–352 vide.
//
//   node outils/rendu3d/rendu3d.mjs --scene pixel-04-binaire3d/.montage/3d/tarte.mjs \
//        --out pixel-04-binaire3d/.montage/3d/tarte --debut 31.4 --fin 40.3 --ips 24 --fond transparent
//
// Ombrage : matériau « rampe » maison (3 couleurs exactes de la palette selon l'orientation de la face par rapport
// à une lumière fixe) : pâte 17/18/19, garniture 21/22/23, cerises 21/22/24.
// params (facultatifs) : { "debut": 31.4, "tiers": 33.89, "trois": [36.47, 37.28, 37.88], "infini": 39.05,
//                          "fin": 40.3 }

function rampe(THREE, outils, couleurs, seuils, lumiere) {
  const [a, b, c] = couleurs;
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
    side: THREE.DoubleSide,
  });
}

export default function creer(THREE, outils, params = {}) {
  const T0 = params.debut ?? 31.4, TIERS = params.tiers ?? 33.89, TROIS = params.trois ?? [36.47, 37.28, 37.88];
  const INFINI = params.infini ?? 39.05, T1 = params.fin ?? 40.3;

  const scene = new THREE.Scene();
  const camera = new THREE.PerspectiveCamera(30, outils.largeur / outils.hauteur, 10, 600);
  // décale le cadre : le centre de la tarte tombe vers (144, 184) au lieu de (135, 240), au milieu du tableau
  camera.setViewOffset(outils.largeur, outils.hauteur, -9, 56, outils.largeur, outils.hauteur);

  const L = new THREE.Vector3(-0.4, 0.85, 0.35).normalize();
  const pate = rampe(THREE, outils, [25, 17, 18], [-0.25, 0.5], L);
  const bord = rampe(THREE, outils, [17, 18, 19], [0.1, 0.94], L);
  const garniture = rampe(THREE, outils, [21, 22, 23], [-0.2, 0.5], L);
  const cerise = rampe(THREE, outils, [21, 22, 24], [0.05, 0.78], L);

  const R = 10, RI = 8.6;          // rayon de la pâte, rayon de la garniture
  const FOND = 0.7, PAROI = 2.2, DESSUS = 2.5;
  const PART = (2 * Math.PI) / 3;
  const CG = 5.0;                  // distance du centre de gravité d'une part au centre de la tarte

  function extruder(forme, h, y) {
    const g = new THREE.ExtrudeGeometry(forme, { depth: h, bevelEnabled: false, curveSegments: 14 });
    g.rotateX(-Math.PI / 2);  // forme (x, y) → monde (x, −z), épaisseur vers le haut
    g.translate(0, y, 0);
    return g;
  }
  function secteur(r, a0, a1) {
    const s = new THREE.Shape();
    s.moveTo(0, 0);
    s.lineTo(r * Math.cos(a0), r * Math.sin(a0));
    s.absarc(0, 0, r, a0, a1, false);
    s.lineTo(0, 0);
    return s;
  }
  function anneau(ri, ro, a0, a1) {
    const s = new THREE.Shape();
    s.moveTo(ri * Math.cos(a0), ri * Math.sin(a0));
    s.lineTo(ro * Math.cos(a0), ro * Math.sin(a0));
    s.absarc(0, 0, ro, a0, a1, false);
    s.lineTo(ri * Math.cos(a1), ri * Math.sin(a1));
    s.absarc(0, 0, ri, a1, a0, true);
    return s;
  }

  const tarte = new THREE.Group();
  scene.add(tarte);
  const h = outils.hasard(31);
  const geoCerise = new THREE.IcosahedronGeometry(0.95, 0);
  const parts = [0, 1, 2].map((k) => {
    const a0 = k * PART, a1 = (k + 1) * PART;  // faces de coupe jointives : aucune fente visible tant que la tarte est fermée
    const m = (a0 + a1) / 2;
    const dir = new THREE.Vector3(Math.cos(m), 0, -Math.sin(m));
    const pivot = new THREE.Group();     // placé au centre de gravité de la part : écart radial + saut
    const tour = new THREE.Group();      // pirouette et bascule pendant le saut (autour du centre de la part)
    const ecr = new THREE.Group();       // écrasement au pied de la part
    const corps = new THREE.Group();     // la part, ramenée pour que son centre tombe sur le pivot
    corps.position.copy(dir).multiplyScalar(-CG);
    pivot.add(tour); tour.add(ecr); ecr.add(corps);
    corps.add(new THREE.Mesh(extruder(secteur(R, a0, a1), FOND, 0), pate));
    corps.add(new THREE.Mesh(extruder(anneau(RI, R, a0, a1), PAROI - FOND, FOND), pate));
    corps.add(new THREE.Mesh(extruder(secteur(RI, a0, a1), DESSUS - FOND, FOND), garniture));
    const tore = new THREE.TorusGeometry((RI + R) / 2, 0.85, 6, 16, a1 - a0);
    tore.rotateZ(a0);
    tore.rotateX(-Math.PI / 2);
    const bourrelet = new THREE.Mesh(tore, bord);
    bourrelet.position.y = PAROI + 0.15;
    corps.add(bourrelet);
    for (let c = 0; c < 3; c++) {  // trois cerises par part, placées avec une graine
      const ang = a0 + 0.3 + (a1 - a0 - 0.6) * ((c + 0.2 + 0.6 * h()) / 3);
      const rr = 2.6 + 4.2 * h();
      const ce = new THREE.Mesh(geoCerise, cerise);
      ce.position.set(rr * Math.cos(ang), DESSUS + 0.45, -rr * Math.sin(ang));
      ce.rotation.set(h() * 3, h() * 3, 0);
      corps.add(ce);
    }
    tarte.add(pivot);
    return { pivot, tour, ecr, dir };
  });

  // centre de gravité vertical : la tarte tourne autour de son milieu
  tarte.position.y = -DESSUS / 2;

  const OMEGA = 0.11;          // tours par seconde au repos
  const ACC = 1.0;             // tours/s³ après « à l'infini »
  function angle(t) {
    let tours = OMEGA * (t - T0);
    const u = Math.max(0, t - INFINI);
    tours += (ACC / 3) * u * u * u;
    return 2 * Math.PI * tours;
  }
  const bosse = (u) => (u <= 0 || u >= 1 ? 0 : 4 * u * (1 - u));

  function update(t) {
    // apparition : la tarte grandit avec un ressort (0,45 s)
    const pop = outils.ressort((t - T0) / 0.45);
    tarte.scale.setScalar(Math.max(0.001, pop));
    tarte.rotation.y = angle(t);
    tarte.position.y = -DESSUS / 2 + 0.25 * Math.sin(2 * Math.PI * 0.35 * (t - T0));

    const ouvre = outils.ressort((t - TIERS) / 0.75);
    const centrifuge = 0.6 * outils.entre(t, INFINI, T1);
    parts.forEach((p, k) => {
      const ecart = 2.6 * ouvre + centrifuge;
      const hop = 1.2 * bosse((t - TIERS) / 0.4);              // petit sursaut à l'ouverture
      const tj = TROIS[k];
      const DUREE = 0.42;
      const us = (t - tj) / DUREE;
      const saut = 5.4 * bosse(us);
      p.pivot.position.copy(p.dir).multiplyScalar(ecart + CG);
      p.pivot.position.y = hop + saut;
      // la part saute, puis s'écrase à l'atterrissage
      // pirouette complète sur elle-même (lisse, finit pile à l'atterrissage) + légère bascule vers l'extérieur
      const axe = new THREE.Vector3(-p.dir.z, 0, p.dir.x);
      const q = new THREE.Quaternion().setFromAxisAngle(axe, -0.35 * bosse(us));
      const qy = new THREE.Quaternion().setFromAxisAngle(new THREE.Vector3(0, 1, 0), 2 * Math.PI * outils.lisse(us));
      p.tour.quaternion.copy(q).multiply(qy);
      const ec = (t - (tj + DUREE)) / 0.18;
      const pre = (t - (tj - 0.1)) / 0.1;
      let sy = 1;
      if (ec > 0 && ec < 1) sy = 1 - 0.22 * Math.sin(Math.PI * ec);          // écrasement à l'arrivée
      else if (pre > 0 && pre < 1) sy = 1 - 0.15 * Math.sin(Math.PI * pre);  // prise d'élan
      p.ecr.scale.set(1 + (1 - sy) * 0.5, sy, 1 + (1 - sy) * 0.5);
    });

    // caméra : trois quarts (≈ 36° au-dessus), dérive lente en hauteur et en azimut
    const az = 0.12 * Math.sin(2 * Math.PI * (t - T0) / 9);
    const el = THREE.MathUtils.degToRad(36 + 3 * Math.sin(2 * Math.PI * (t - T0) / 7));
    const dist = 117;
    camera.position.set(Math.sin(az) * Math.cos(el) * dist, Math.sin(el) * dist, Math.cos(az) * Math.cos(el) * dist);
    camera.lookAt(0, 0, 0);
  }

  return { scene, camera, update };
}
