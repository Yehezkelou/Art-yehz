// ico-vid : clips propres au marchand (marchand.rig.toml), qui remplacent les 5 clips de base d'outils.voxel et
// ajoutent « non_de_la_tete ».
//
//   import { installer } from "./marchand.clips.mjs";
//   const m = installer(await outils.voxel.chargerRig("assets/3d/persos/marchand/marchand.rig.toml"));
//   m.poser("non_de_la_tete", t);   // idle, marche, saut, parle, coucou, non_de_la_tete
//
// Pourquoi des clips propres : sous sa robe d'un bloc, le marchand n'a que des pieds ; ils glissent d'avant en arrière
// (petit pas de gobelin qui se dandine) au lieu de pivoter comme des jambes. La tête (capuche + oreilles, 18 voxels
// de large) ne roule pas : elle tourne et hoche vers l'avant, les bras ne s'écartent que vers l'extérieur.
// Les oreilles frémissent (rotation autour de leur base, dans la capuche).
// Parties d'expression (voir marchand.py) : cachées dans la tête au repos, montrées en avançant de 2 voxels en z.
// Pur (pas de THREE ni d'outils) : testable sous Node.

const TAU = 2 * Math.PI;
const lisse = (x) => { x = Math.min(1, Math.max(0, x)); return x * x * (3 - 2 * x); };

function montrer(r, nom) {
  const g = r.pivots[nom];
  if (g) g.position.z = g.userData.repos.z + 2;
}

export function cligne(u, periode = 3.3, decalage = 0.4) {
  const c = (((u + decalage) % periode) + periode) % periode;
  return c >= periode - 2 / 12 - 1e-6;
}

// frémissement d'oreilles : un petit coup vers le haut, toutes les `periode` s
function oreilles(r, u, force = 1, periode = 1.7) {
  const { oreille_d, oreille_g } = r.roles;
  const c = (u % periode) / periode;
  const f = c < 0.12 ? Math.sin(Math.PI * c / 0.12) : 0;
  if (oreille_d) oreille_d.rotation.z -= 0.25 * force * f;
  if (oreille_g) oreille_g.rotation.z += 0.25 * force * f;
}

// pointe de la capuche : ne bascule que vers l'arrière (rotation x positive), jamais vers la capuche
function pointe(r, a) {
  if (r.roles.pointe) r.roles.pointe.rotation.x += Math.max(0, a);
}

export const CLIPS_MARCHAND = {
  idle(r, u, o) {
    const A = o.amplitude, { tete, corps, bras_d, bras_g } = r.roles;
    const f = 0.5 + 0.5 * Math.sin(TAU * u / 2);
    if (tete) { tete.rotation.x += 0.05 * A * f; tete.rotation.y += 0.08 * A * Math.sin(TAU * u / 4); }
    if (corps) corps.rotation.y += 0.03 * A * Math.sin(TAU * u / 4);
    if (bras_d) bras_d.rotation.z -= 0.06 * A * f;
    if (bras_g) bras_g.rotation.z += 0.06 * A * f;
    oreilles(r, u, A);
    pointe(r, 0.06 * A * f);
  },
  marche(r, u, o) {
    const A = o.amplitude, { corps, tete, bras_d, bras_g, jambe_d, jambe_g } = r.roles;
    const ph = TAU * u / 0.6, f = Math.sin(ph);
    // pieds : glissent de ±1,2 voxel et se lèvent d'un demi-voxel quand ils avancent ; le corps rebondit à chaque
    // pas, le pied posé reste au sol (les pieds sont enfants du corps : on retire le rebond)
    const rebond = 0.4 * A * Math.abs(Math.cos(ph));
    r.pose.position.y += rebond;
    if (jambe_d) { jambe_d.position.z += 1.2 * A * f; jambe_d.position.y += 0.5 * A * Math.max(0, Math.cos(ph)) - rebond; }
    if (jambe_g) { jambe_g.position.z -= 1.2 * A * f; jambe_g.position.y += 0.5 * A * Math.max(0, -Math.cos(ph)) - rebond; }
    if (bras_d) bras_d.rotation.x -= 0.3 * A * f;
    if (bras_g) bras_g.rotation.x += 0.3 * A * f;
    if (corps) corps.rotation.y += 0.1 * A * f;               // se dandine
    if (tete) tete.rotation.y -= 0.07 * A * f;
    oreilles(r, u, A, 0.6);
    pointe(r, 0.25 * A * Math.abs(f));
  },
  saut(r, u, o) {
    const A = o.amplitude, { corps, tete, bras_g, bras_d, jambe_d, jambe_g } = r.roles;
    const c = (u % 1.2) / 1.2;
    const elan = lisse(c / 0.12) * (1 - lisse((c - 0.12) / 0.08));
    const haut = lisse((c - 0.2) / 0.1) * (1 - lisse((c - 0.7) / 0.18));
    const vol = c >= 0.2 && c < 0.75 ? (c - 0.2) / 0.55 : -1;
    if (tete) tete.rotation.x += 0.08 * A * elan;
    if (bras_d) { bras_d.rotation.x += 0.3 * A * elan; bras_d.rotation.z -= 1.9 * A * haut; }
    if (bras_g) { bras_g.rotation.x += 0.3 * A * elan; bras_g.rotation.z += 1.9 * A * haut; }
    if (vol >= 0) {
      r.pose.position.y += 5 * A * 4 * vol * (1 - vol);
      if (jambe_d) jambe_d.position.z += 0.8 * A;
      if (jambe_g) jambe_g.position.z -= 0.8 * A;
      oreilles(r, 0, 1.2 * A * Math.sin(Math.PI * vol), 1);   // oreilles levées pendant le vol
      pointe(r, 0.5 * A * vol);                                 // la pointe traîne derrière
    } else if (c >= 0.75 && tete) {
      tete.rotation.x += 0.12 * A * Math.sin(Math.PI * (c - 0.75) / 0.25);
      pointe(r, 0.5 * A * (1 - (c - 0.75) / 0.25));             // et retombe
    }
  },
  parle(r, u, o) {
    const A = o.amplitude, { tete, bras_d, bouche } = r.roles;
    if (tete) {
      tete.rotation.x += 0.07 * A * (0.5 + 0.5 * Math.sin(TAU * 2.6 * u));
      tete.rotation.y += 0.1 * A * Math.sin(TAU * 0.6 * u);
    }
    if (bras_d) {
      const g = 0.5 + 0.5 * Math.sin(TAU * 0.9 * u);
      bras_d.rotation.x -= 0.3 * A * g;
      bras_d.rotation.z -= 0.3 * A * g;                       // main ouverte, « voyez-vous »
    }
    if (bouche) bouche.visible = ((Math.floor(u * 8) * 2654435761) >>> 0) % 3 === 0;
    oreilles(r, u, A, 1.3);
    pointe(r, 0.08 * A * (0.5 + 0.5 * Math.sin(TAU * 2.6 * u - 1)));
  },
  coucou(r, u, o) {
    const A = o.amplitude, { tete, bras_d, corps } = r.roles;
    const monte = lisse(u / 0.25);
    if (bras_d) bras_d.rotation.z -= monte * (1.85 + 0.3 * A * Math.sin(TAU * 2.5 * u));
    if (tete) { tete.rotation.y += 0.1 * A * Math.sin(TAU * 1.25 * u); tete.rotation.x += 0.04 * A; }
    if (corps) corps.rotation.y += 0.04 * A * Math.sin(TAU * 1.25 * u);
    oreilles(r, u, A, 0.8);
  },
  // « non » : la tête tourne de gauche à droite, paupières mi-closes (méfiant), index levé qui s'agite
  non_de_la_tete(r, u, o) {
    const A = o.amplitude, { tete, bras_g, corps } = r.roles;
    montrer(r, "mi_clos");
    if (tete) { tete.rotation.y += 0.4 * A * Math.sin(TAU * 2 * u); tete.rotation.x += 0.05 * A; }
    if (bras_g) {
      bras_g.rotation.z += 1.5 * lisse(u / 0.25);               // bras levé sur le côté, index en l'air
      bras_g.rotation.x -= 0.2 * A * Math.sin(TAU * 4 * u);    // qui s'agite
    }
    if (corps) corps.rotation.y -= 0.05 * A * Math.sin(TAU * 2 * u);
    oreilles(r, u, 0.6 * A, 0.5);
    pointe(r, 0.2 * A * Math.abs(Math.sin(TAU * 2 * u)));        // la pointe suit la tête
  },
};

export function installer(perso) {
  for (const [nom, clip] of Object.entries(CLIPS_MARCHAND)) {
    perso.clips[nom] = nom === "non_de_la_tete" ? clip : (r, u, o) => {
      clip(r, u, o);
      if (cligne(u)) montrer(r, "paupieres");
    };
  }
  return perso;
}
