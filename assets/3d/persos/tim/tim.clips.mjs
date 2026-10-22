// ico-vid : clips propres à Tim (tim.rig.toml ou tim-sans-baton.rig.toml), qui remplacent les 5 clips de base
// d'outils.voxel et ajoutent « colere ».
//
//   import { installer } from "./tim.clips.mjs";
//   const tim = installer(await outils.voxel.chargerRig("assets/3d/persos/tim/tim.rig.toml"));
//   tim.poser("marche", t);         // idle, marche, saut, parle, coucou, colere (+ balade = marche lente du rig)
//
// Pourquoi des clips propres : la tête de Tim (10 voxels) est plus large que le corps et couvre le haut des bras ;
// les clips de base la font rouler (rotation z) et descendre d'un demi-voxel, ce qui l'enfonce dans les bras et
// dans le bâton, et la marche de base enfonce le bout des bottes dans le sol. Ici : la tête tourne (y) et hoche
// vers l'avant seulement, les bras ne s'écartent que vers l'extérieur, et la marche garde les pieds posés
// (le point le plus bas des bottes reste à y = 0). Contrôle : aucune interpénétration de plus de 0,25 voxel
// entre parties visibles (voir le rapport agents/rapports/claude/2026-10-22-persos-voxel.md).
//
// Parties d'expression (voir tim.py) : cachées dans la tête au repos, montrées en avançant de 2 voxels en z.
// Pur (pas de THREE ni d'outils) : testable sous Node.

const TAU = 2 * Math.PI;
const lisse = (x) => { x = Math.min(1, Math.max(0, x)); return x * x * (3 - 2 * x); };

function montrer(r, nom) {
  const g = r.pivots[nom];
  if (g) g.position.z = g.userData.repos.z + 2;
}

// clin d'œil : 2 images à 12 i/s toutes les 2,9 s (décalé pour ne pas tomber à t = 0)
export function cligne(u, periode = 2.9, decalage = 1.1) {
  const c = (((u + decalage) % periode) + periode) % periode;
  return c >= periode - 2 / 12 - 1e-6;
}

// Pieds posés : jambes de 4 voxels, bottes de z −1,5 à +1,5 autour du pivot de hanche (voir tim.py).
function poserPieds(r, angles) {
  let bas = Infinity;
  for (const a of angles) for (const z of [-1.5, 1.5]) bas = Math.min(bas, -4 * Math.cos(a) - z * Math.sin(a));
  r.pose.position.y += -4 - bas;
}

export const CLIPS_TIM = {
  idle(r, u, o) {
    const A = o.amplitude, { tete, bras_d, bras_g, bras_baton, corps } = r.roles;
    const f = 0.5 + 0.5 * Math.sin(TAU * u / 2);                 // 0 → 1 → 0 en 2 s
    if (tete) { tete.rotation.x += 0.05 * A * f; tete.rotation.y += 0.06 * A * Math.sin(TAU * u / 4); }
    if (corps) corps.rotation.y += 0.02 * A * Math.sin(TAU * u / 4);
    if (bras_d) bras_d.rotation.z -= 0.07 * A * f;               // les bras respirent vers l'extérieur
    if (bras_g) bras_g.rotation.z += 0.07 * A * f;
    if (bras_baton) bras_baton.rotation.x += 0.04 * A * Math.sin(TAU * u / 2);
  },
  marche(r, u, o) {
    const A = o.amplitude, { corps, tete, bras_d, bras_g, bras_baton, jambe_g, jambe_d } = r.roles;
    const f = Math.sin(TAU * u / 0.7), th = 0.4 * A * f;
    if (jambe_g) jambe_g.rotation.x += th;
    if (jambe_d) jambe_d.rotation.x -= th;
    if (bras_d) bras_d.rotation.x += 0.75 * th;
    if (bras_g) bras_g.rotation.x -= 0.75 * th;
    if (bras_baton) bras_baton.rotation.x -= 0.25 * th;          // le bâton accompagne le pas
    if (corps) corps.rotation.y += 0.07 * A * f;
    if (tete) tete.rotation.y -= 0.06 * A * f;
    poserPieds(r, [th, -th]);
  },
  saut(r, u, o) {
    const A = o.amplitude, { corps, tete, bras_g, bras_d, bras_baton, jambe_g, jambe_d } = r.roles;
    const c = (u % 1.2) / 1.2;                                    // élan 0–0,2 · vol 0,2–0,75 · réception
    const elan = lisse(c / 0.12) * (1 - lisse((c - 0.12) / 0.08));
    const haut = lisse((c - 0.2) / 0.1) * (1 - lisse((c - 0.7) / 0.18));
    const vol = c >= 0.2 && c < 0.75 ? (c - 0.2) / 0.55 : -1;
    if (corps) corps.rotation.x += 0.14 * A * elan;
    if (bras_d) { bras_d.rotation.x += 0.3 * A * elan; bras_d.rotation.z -= 2.4 * A * haut; }
    if (bras_g) { bras_g.rotation.x += 0.3 * A * elan; bras_g.rotation.z += 2.4 * A * haut; }
    if (bras_baton) bras_baton.rotation.x -= 0.25 * A * haut;    // bâton brandi un peu en avant
    if (vol >= 0) {
      r.pose.position.y += 6 * A * 4 * vol * (1 - vol);
      if (jambe_g) jambe_g.rotation.x += 0.3 * A;
      if (jambe_d) jambe_d.rotation.x -= 0.3 * A;
    } else {
      if (c >= 0.75 && tete) tete.rotation.x += 0.14 * A * Math.sin(Math.PI * (c - 0.75) / 0.25);
      if (corps) poserPieds(r, [corps.rotation.x]);
    }
  },
  parle(r, u, o) {
    const A = o.amplitude, { tete, bras_d, bouche } = r.roles;
    if (tete) {
      tete.rotation.x += 0.07 * A * (0.5 + 0.5 * Math.sin(TAU * 3 * u));   // hoche vers l'avant seulement
      tete.rotation.y += 0.08 * A * Math.sin(TAU * 0.7 * u);
    }
    if (bras_d) {
      const g = 0.5 + 0.5 * Math.sin(TAU * 0.8 * u);
      bras_d.rotation.x -= 0.3 * A * g;                             // main qui explique, en avant
      bras_d.rotation.z -= 0.25 * A * g;
    }
    if (bouche) bouche.visible = ((Math.floor(u * 8) * 2654435761) >>> 0) % 3 === 0;   // ouverte 2 fois sur 3
  },
  coucou(r, u, o) {
    const A = o.amplitude, { tete, bras_d, corps } = r.roles;
    const monte = lisse(u / 0.25);
    if (bras_d) bras_d.rotation.z -= monte * (2.45 + 0.3 * A * Math.sin(TAU * 2.5 * u));
    if (tete) { tete.rotation.y += 0.1 * A * Math.sin(TAU * 1.25 * u); tete.rotation.x += 0.03 * A; }
    if (corps) corps.rotation.y += 0.04 * A * Math.sin(TAU * 1.25 * u);
  },
  // colère : sourcils froncés, tête baissée qui tremble, poing qui s'agite, pied qui tape, bouche qui crie
  colere(r, u, o) {
    const A = o.amplitude, { corps, tete, bras_d, bras_g, bras_baton, jambe_d, bouche } = r.roles;
    montrer(r, "sourcils");
    const tape = Math.max(0, Math.sin(TAU * 1.6 * u));            // 1,6 coup de pied par seconde
    if (tete) {
      tete.rotation.x += 0.1 * A;                                  // menton rentré, regard par en dessous
      tete.rotation.y += 0.05 * A * Math.sin(TAU * 6 * u);        // tremblement
    }
    if (bras_d) {
      bras_d.rotation.z -= 0.35 * A + 0.12 * A * Math.sin(TAU * 4 * u);   // poing écarté qui s'agite
      bras_d.rotation.x -= 0.2 * A;
    }
    if (bras_g) bras_g.rotation.z += 0.3 * A + 0.12 * A * Math.sin(TAU * 4 * u + 1);
    if (bras_baton) bras_baton.rotation.x -= 0.12 * A * tape;     // le bâton tape avec le pied
    if (jambe_d) jambe_d.rotation.x -= 0.4 * A * tape;             // pied levé vers l'avant puis frappé
    if (corps) corps.rotation.x += 0.04 * A;
    if (bouche) bouche.visible = Math.floor(u * 12) % 4 === 3;     // bouche ouverte 3 images sur 4
  },
};

export function installer(perso) {
  for (const [nom, clip] of Object.entries(CLIPS_TIM)) {
    perso.clips[nom] = nom === "colere" ? clip : (r, u, o) => {
      clip(r, u, o);
      if (cligne(u)) montrer(r, "paupieres");
    };
  }
  return perso;
}
