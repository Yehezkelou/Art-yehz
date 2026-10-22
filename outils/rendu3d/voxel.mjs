// ico-vid : voxels pour rendu3d. Fichiers .vox MagicaVoxel → maillage glouton en couleurs exactes de la palette,
// rigs de parties rigides, TOML simple. Passé aux scènes comme outils.voxel (voir outils.mjs) :
//
//   const [tete] = await outils.voxel.charger("assets/3d/persos/tim/tete.vox")   // → liste de grilles
//   const m = outils.voxel.maillage(tete, { contour: 1, occlusion: true, centre: "bas" })   // → THREE.Mesh
//   const perso = await outils.voxel.chargerRig("assets/3d/persos/tim/tim.rig.toml")    // .vox + rig → THREE.Group
//   perso.poser("marche", t)                      // idle, marche, saut, parle, coucou (12 i/s par défaut)
//
// Chemins : relatifs à la racine du dépôt ("assets/…"), ou à la scène ("./…", dossier du module de scène).
// Axes (comme outils/vox.py) : x → droite, y → haut, z → avant ; le voxel (x, y, z) occupe [x, x+1] × [y, y+1] × [z, z+1].
//
// Ombrage : MeshBasicMaterial (non éclairé) ; chaque face prend une couleur exacte de la palette selon son orientation
// vue de la caméra (eclairage "camera", par défaut) ou dans le repère de l'objet ("fixe") : dessus (normale vers le
// haut), dessous (vers le bas), face (vers l'observateur), cote (tournée à gauche), dessous aussi pour les faces
// tournées à droite (lumière de face, un peu en haut à gauche). Couleurs : rampe(i) = {dessus, face, cote, dessous},
// table par défaut tirée des rampes de la palette (même table que outils/vox.py), surchargeable. Occlusion : un palier
// plus sombre de la même rampe pour les faces coincées (au moins `seuil` voisins pleins autour de la case devant la face).
//
// Le module ne dépend que de THREE (injecté par fabriquerVoxel) ; lireVox, lireToml, rampe… sont purs (testés sous Node).

export const RAMPES = Object.freeze([
  [1, 2, 3, 4, 5, 6, 7, 8], [9, 10, 11, 12], [13, 14, 15, 16], [17, 18, 19, 20],
  [21, 22, 23, 24], [25, 26, 27, 28], [29, 30, 31, 32],
].map((r) => Object.freeze(r)));
const ROLES = ["dessus", "face", "cote", "dessous"];

function verifierIndex(i, quoi = "couleur") {
  if (!Number.isInteger(i) || i < 1 || i > 32) throw new Error(`voxel : ${quoi} ${i} hors palette (index entier 1–32)`);
}

function rampeDe(i) {
  verifierIndex(i);
  const r = RAMPES.find((x) => x.includes(i));
  return [r, r.indexOf(i)];
}

// Couleurs d'un voxel d'index i : face = i ; voisin plus clair → dessus +1, cote −1, dessous −2 ;
// i le plus clair de sa rampe → dessus −1, cote −2, dessous −3 ; on reste dans la rampe.
export function rampe(i) {
  const [r, p] = rampeDe(i);
  const c = (k) => r[Math.min(r.length - 1, Math.max(0, k))];
  if (p < r.length - 1) return { dessus: c(p + 1), face: i, cote: c(p - 1), dessous: c(p - 2) };
  return { dessus: c(p - 1), face: i, cote: c(p - 2), dessous: c(p - 3) };
}

export function plusSombre(i) {
  const [r, p] = rampeDe(i);
  return r[Math.max(0, p - 1)];
}

// ---------- grilles ----------
export class Grille {
  constructor(lx, ly, lz, nom = "") {
    for (const [k, v] of [["lx", lx], ["ly", ly], ["lz", lz]]) {
      if (!Number.isInteger(v) || v < 1 || v > 256) throw new Error(`voxel : ${k} = ${v} (entier 1–256 attendu)`);
    }
    this.lx = lx; this.ly = ly; this.lz = lz; this.nom = String(nom);
    this.donnees = new Uint8Array(lx * ly * lz);  // index x + lx × (y + ly × z), comme vox.py
  }
  dedans(x, y, z) { return x >= 0 && y >= 0 && z >= 0 && x < this.lx && y < this.ly && z < this.lz; }
  get(x, y, z) { return this.dedans(x, y, z) ? this.donnees[x + this.lx * (y + this.ly * z)] : 0; }
  set(x, y, z, i) {
    if (!this.dedans(x, y, z)) throw new Error(`voxel : (${x}, ${y}, ${z}) hors de la grille ${this.lx}×${this.ly}×${this.lz}`);
    if (i !== 0) verifierIndex(i);
    this.donnees[x + this.lx * (y + this.ly * z)] = i;
    return this;
  }
  boite(x0, y0, z0, x1, y1, z1, i) {  // bornes incluses
    const [xa, xb] = [x0, x1].sort((a, b) => a - b), [ya, yb] = [y0, y1].sort((a, b) => a - b);
    const [za, zb] = [z0, z1].sort((a, b) => a - b);
    for (let z = za; z <= zb; z++) for (let y = ya; y <= yb; y++) for (let x = xa; x <= xb; x++) this.set(x, y, z, i);
    return this;
  }
  compter() { let n = 0; for (const v of this.donnees) if (v) n++; return n; }
}

export function grille(lx, ly, lz, nom = "") { return new Grille(lx, ly, lz, nom); }

// ---------- lecture .vox ----------
// Axes MagicaVoxel (z en haut, face avant vue depuis −y) : x = x_vox, y = z_vox, z = sy − 1 − y_vox.
export function lireVox(octets) {
  const u8 = octets instanceof Uint8Array ? octets : new Uint8Array(octets);
  const dv = new DataView(u8.buffer, u8.byteOffset, u8.byteLength);
  const id = (i) => String.fromCharCode(u8[i], u8[i + 1], u8[i + 2], u8[i + 3]);
  if (u8.length < 20 || id(0) !== "VOX ") throw new Error("voxel : pas un fichier .vox (en-tête « VOX » absent)");
  const version = dv.getInt32(4, true);
  if (version !== 150 && version !== 200) throw new Error(`voxel : version .vox ${version} non gérée (150 ou 200)`);
  if (id(8) !== "MAIN") throw new Error("voxel : chunk MAIN absent");
  const debut = 20 + dv.getInt32(12, true), fin = debut + dv.getInt32(16, true);
  if (fin > u8.length) throw new Error("voxel : fichier .vox tronqué");
  const modeles = [], trn = new Map(), shp = new Map();
  let taille = null;
  const lecteur = (o) => {
    const r = {
      o,
      entier() { const v = dv.getInt32(r.o, true); r.o += 4; return v; },
      chaine() { const n = r.entier(); const s = new TextDecoder().decode(u8.subarray(r.o, r.o + n)); r.o += n; return s; },
      dict() { const d = {}; for (let n = r.entier(); n > 0; n--) { const k = r.chaine(); d[k] = r.chaine(); } return d; },
    };
    return r;
  };
  for (let i = debut; i < fin;) {
    if (i + 12 > fin) throw new Error("voxel : chunk tronqué");
    const nom = id(i), nc = dv.getInt32(i + 4, true), ne = dv.getInt32(i + 8, true), c = i + 12;
    if (nc < 0 || ne < 0 || c + nc + ne > fin) throw new Error(`voxel : chunk ${nom} tronqué`);
    if (nom === "SIZE") taille = [dv.getInt32(c, true), dv.getInt32(c + 4, true), dv.getInt32(c + 8, true)];
    else if (nom === "XYZI") {
      if (!taille) throw new Error("voxel : XYZI sans SIZE");
      const [sx, sy, sz] = taille;
      const g = new Grille(sx, sz, sy);
      const n = dv.getInt32(c, true);
      for (let k = 0; k < n; k++) {
        const o = c + 4 + 4 * k, xv = u8[o], yv = u8[o + 1], zv = u8[o + 2], ci = u8[o + 3];
        if (ci > 32) {
          throw new Error(`voxel : modèle ${modeles.length}, voxel (${xv}, ${yv}, ${zv}) d'index ${ci} hors ico-pixel-32 (1–32)`);
        }
        g.set(xv, zv, sy - 1 - yv, ci);
      }
      modeles.push(g);
      taille = null;
    } else if (nom === "nTRN") {
      const r = lecteur(c);
      r.entier();
      const attr = r.dict();
      trn.set(r.entier(), attr._name || "");
    } else if (nom === "nSHP") {
      const r = lecteur(c);
      const nid = r.entier();
      r.dict();
      if (r.entier() >= 1) shp.set(nid, r.entier());
    }
    i = c + nc + ne;
  }
  for (const [nid, k] of shp) if (modeles[k] && trn.get(nid) && !modeles[k].nom) modeles[k].nom = trn.get(nid);
  return modeles;
}

// ---------- TOML simple ----------
// Tables [a.b] et [[a]], clés nues ou entre guillemets (pointées), chaînes "…" et '…', nombres, booléens,
// tableaux (sur plusieurs lignes, virgule finale permise), tables en ligne { a = 1 }, commentaires #.
// Pas de dates ni de chaînes multilignes. Un fichier .json est lu avec JSON.parse (même structure).
export function lireToml(texte) {
  const s = String(texte).replace(/\r\n?/g, "\n");
  let i = 0;
  const ligne = () => s.slice(0, i).split("\n").length;
  const erreur = (m) => { throw new Error(`toml ligne ${ligne()} : ${m}`); };
  const blancs = () => { while (s[i] === " " || s[i] === "\t") i++; };
  const commentaire = () => { if (s[i] === "#") while (i < s.length && s[i] !== "\n") i++; };
  const espaces = () => { for (;;) { blancs(); commentaire(); if (s[i] === "\n") i++; else break; } };
  const finDeLigne = () => {
    blancs(); commentaire();
    if (i < s.length && s[i] !== "\n") erreur(`texte inattendu « ${s.slice(i, i + 12)} »`);
  };
  function chaine() {
    const q = s[i++];
    let r = "";
    while (i < s.length && s[i] !== q) {
      if (s[i] === "\n") erreur("chaîne non fermée");
      if (q === '"' && s[i] === "\\") {
        const e = s[i + 1];
        const t = { n: "\n", t: "\t", r: "\r", '"': '"', "\\": "\\", b: "\b", f: "\f" }[e];
        if (t !== undefined) { r += t; i += 2; continue; }
        if (e === "u" || e === "U") {
          const n = e === "u" ? 4 : 8, h = s.slice(i + 2, i + 2 + n);
          if (!/^[0-9a-fA-F]+$/.test(h) || h.length !== n) erreur("échappement \\u invalide");
          r += String.fromCodePoint(parseInt(h, 16)); i += 2 + n; continue;
        }
        erreur(`échappement « \\${e} » inconnu`);
      }
      r += s[i++];
    }
    if (s[i] !== q) erreur("chaîne non fermée");
    i++;
    return r;
  }
  function cle() {
    const parts = [];
    for (;;) {
      blancs();
      if (s[i] === '"' || s[i] === "'") parts.push(chaine());
      else {
        const m = /^[A-Za-z0-9_-]+/.exec(s.slice(i));
        if (!m) erreur("clé attendue");
        parts.push(m[0]); i += m[0].length;
      }
      blancs();
      if (s[i] === ".") { i++; continue; }
      return parts;
    }
  }
  function valeur() {
    blancs();
    const c = s[i];
    if (c === '"' || c === "'") {
      if (s.startsWith(c.repeat(3), i)) erreur("chaînes multilignes non gérées");
      return chaine();
    }
    if (c === "[") {
      i++;
      const t = [];
      for (;;) {
        espaces();
        if (s[i] === "]") { i++; return t; }
        t.push(valeur());
        espaces();
        if (s[i] === ",") { i++; continue; }
        if (s[i] === "]") { i++; return t; }
        erreur("« , » ou « ] » attendu dans le tableau");
      }
    }
    if (c === "{") {
      i++;
      const t = {};
      blancs();
      if (s[i] === "}") { i++; return t; }
      for (;;) {
        const k = cle();
        if (s[i] !== "=") erreur("« = » attendu");
        i++;
        poser(t, k, valeur());
        blancs();
        if (s[i] === ",") { i++; continue; }
        if (s[i] === "}") { i++; return t; }
        erreur("« , » ou « } » attendu dans la table en ligne");
      }
    }
    const reste = s.slice(i);
    let m = /^(true|false)(?![A-Za-z0-9_])/.exec(reste);
    if (m) { i += m[0].length; return m[0] === "true"; }
    m = /^[+-]?(?:0x[0-9a-fA-F_]+|0o[0-7_]+|0b[01_]+|(?:\d[\d_]*)(?:\.\d[\d_]*)?(?:[eE][+-]?\d[\d_]*)?|inf|nan)(?![A-Za-z0-9_:-])/.exec(reste);
    if (m) {
      i += m[0].length;
      const t = m[0].replace(/_/g, "");
      if (/inf$/.test(t)) return t[0] === "-" ? -Infinity : Infinity;
      if (/nan$/.test(t)) return NaN;
      if (/^[+-]?0[xob]/.test(t)) {
        const sg = t[0] === "-" ? -1 : 1, u = t.replace(/^[+-]/, "");
        return sg * parseInt(u.slice(2), { x: 16, o: 8, b: 2 }[u[1]]);
      }
      return Number(t);
    }
    erreur(`valeur illisible « ${reste.slice(0, 12)} » (dates et chaînes multilignes non gérées)`);
  }
  function poser(t, parts, v) {
    let o = t;
    for (const p of parts.slice(0, -1)) {
      if (o[p] === undefined) o[p] = {};
      else if (typeof o[p] !== "object" || Array.isArray(o[p])) erreur(`clé « ${p} » déjà une valeur`);
      o = o[p];
    }
    const k = parts[parts.length - 1];
    if (Object.prototype.hasOwnProperty.call(o, k)) erreur(`clé « ${parts.join(".")} » en double`);
    o[k] = v;
  }
  const racine = {};
  let courant = racine;
  for (;;) {
    espaces();
    if (i >= s.length) return racine;
    if (s[i] === "[") {
      const double = s[i + 1] === "[";
      i += double ? 2 : 1;
      const parts = cle();
      if (s[i] !== "]" || (double && s[i + 1] !== "]")) erreur("« ] » attendu");
      i += double ? 2 : 1;
      finDeLigne();
      let o = racine;
      for (const p of parts.slice(0, -1)) {
        if (o[p] === undefined) o[p] = {};
        o = Array.isArray(o[p]) ? o[p][o[p].length - 1] : o[p];
      }
      const k = parts[parts.length - 1];
      if (double) {
        if (o[k] === undefined) o[k] = [];
        if (!Array.isArray(o[k])) erreur(`« ${parts.join(".")} » n'est pas un tableau de tables`);
        o[k].push({});
        courant = o[k][o[k].length - 1];
      } else {
        if (o[k] === undefined) o[k] = {};
        else if (typeof o[k] !== "object" || Array.isArray(o[k])) erreur(`table « ${parts.join(".")} » en conflit`);
        courant = o[k];
      }
      continue;
    }
    const k = cle();
    if (s[i] !== "=") erreur("« = » attendu");
    i++;
    poser(courant, k, valeur());
    finDeLigne();
  }
}

// ---------- maillage glouton (pur : tableaux, sans THREE) ----------
// Directions : 0 +x, 1 −x, 2 +y, 3 −y, 4 +z, 5 −z. Renvoie { quads: [{ dir, couleur, occ, p: [4 × [x, y, z]] }] },
// coins dans l'ordre trigonométrique vu de l'extérieur.
export const DIRECTIONS = Object.freeze([[1, 0, 0], [-1, 0, 0], [0, 1, 0], [0, -1, 0], [0, 0, 1], [0, 0, -1]]);

export function faces(g, { occlusion = true } = {}) {
  const seuil = occlusion === true ? 1 : occlusion === false ? 0 : Number(occlusion);
  if (!Number.isInteger(seuil) || seuil < 0 || seuil > 4) throw new Error(`voxel : occlusion ${occlusion} (true, false ou seuil 1–4)`);
  const L = [g.lx, g.ly, g.lz];
  const at = (p) => g.get(p[0], p[1], p[2]);
  const quads = [];
  for (let dir = 0; dir < 6; dir++) {
    const a = dir >> 1, sg = dir & 1 ? -1 : 1, u = (a + 1) % 3, v = (a + 2) % 3;
    const Lu = L[u], Lv = L[v];
    const masque = new Int32Array(Lu * Lv);
    for (let q = 0; q < L[a]; q++) {
      masque.fill(0);
      const p = [0, 0, 0], n = [0, 0, 0];
      for (let j = 0; j < Lv; j++) {
        for (let i = 0; i < Lu; i++) {
          p[a] = q; p[u] = i; p[v] = j;
          const c = at(p);
          if (!c) continue;
          n[0] = p[0]; n[1] = p[1]; n[2] = p[2]; n[a] += sg;
          if (at(n)) continue;
          let occ = 0;
          if (seuil) {
            let k = 0;
            for (const [du, dv] of [[1, 0], [-1, 0], [0, 1], [0, -1]]) {
              const m = [n[0], n[1], n[2]]; m[u] += du; m[v] += dv;
              if (at(m)) k++;
            }
            occ = k >= seuil ? 1 : 0;
          }
          masque[i + Lu * j] = c * 2 + occ;
        }
      }
      for (let j = 0; j < Lv; j++) {
        for (let i = 0; i < Lu;) {
          const cle = masque[i + Lu * j];
          if (!cle) { i++; continue; }
          let w = 1;
          while (i + w < Lu && masque[i + w + Lu * j] === cle) w++;
          let h = 1;
          haut: while (j + h < Lv) {
            for (let k = 0; k < w; k++) if (masque[i + k + Lu * (j + h)] !== cle) break haut;
            h++;
          }
          for (let jj = 0; jj < h; jj++) for (let k = 0; k < w; k++) masque[i + k + Lu * (j + jj)] = 0;
          const plan = q + (sg > 0 ? 1 : 0);
          const coin = (di, dj) => { const r = [0, 0, 0]; r[a] = plan; r[u] = i + di; r[v] = j + dj; return r; };
          const pts = [coin(0, 0), coin(w, 0), coin(w, h), coin(0, h)];
          if (sg < 0) pts.reverse();
          quads.push({ dir, couleur: cle >> 1, occ: cle & 1, p: pts });
          i += w;
        }
      }
    }
  }
  return { quads };
}

// Arêtes vives (convexes ou creuses) du volume, fusionnées en segments : [[x0, y0, z0, x1, y1, z1], …]
export function aretes(g) {
  const L = [g.lx, g.ly, g.lz];
  const at = (p) => (g.get(p[0], p[1], p[2]) ? 1 : 0);
  const segs = [];
  for (let a = 0; a < 3; a++) {
    const u = (a + 1) % 3, v = (a + 2) % 3;
    for (let j = 0; j <= L[u]; j++) {
      for (let k = 0; k <= L[v]; k++) {
        let debut = -1;
        for (let i = 0; i <= L[a]; i++) {
          let vis = false;
          if (i < L[a]) {
            const c = (du, dv) => { const p = [0, 0, 0]; p[a] = i; p[u] = j + du; p[v] = k + dv; return at(p); };
            const b00 = c(-1, -1), b10 = c(0, -1), b01 = c(-1, 0), b11 = c(0, 0), n = b00 + b10 + b01 + b11;
            vis = n === 1 || n === 3 || (n === 2 && b00 === b11);
          }
          if (vis && debut < 0) debut = i;
          if (!vis && debut >= 0) {
            const p0 = [0, 0, 0], p1 = [0, 0, 0];
            p0[a] = debut; p1[a] = i; p0[u] = p1[u] = j; p0[v] = p1[v] = k;
            segs.push([...p0, ...p1]);
            debut = -1;
          }
        }
      }
    }
  }
  return segs;
}

// Rôle d'une face selon sa normale (repère vue ou objet) : lumière de face, un peu en haut à gauche.
export function role(nx, ny, nz) {
  if (ny > 0.5) return "dessus";
  if (ny < -0.5) return "dessous";
  if (nz > 0.6) return "face";
  return nx < 0 ? "cote" : "dessous";
}

// ---------- clips procéduraux ----------
// clip(r, u, o) : r = { roles: { corps, tete, … } (pivots THREE.Group), pose (Group des décalages d'ensemble),
// mesures: { role: { longueur } } }, u = temps du clip (s, déjà cadencé et multiplié par la vitesse),
// o = options ({ amplitude, … }). Les pivots sont remis au repos avant chaque appel.
const lisse = (x) => { x = Math.min(1, Math.max(0, x)); return x * x * (3 - 2 * x); };
const TAU = 2 * Math.PI;

export const CLIPS = Object.freeze({
  idle(r, u, o) {
    const A = o.amplitude, { tete, bras_g, bras_d } = r.roles, f = Math.sin(TAU * u / 2);
    if (tete) { tete.rotation.x += 0.05 * A * f; tete.position.y -= 0.5 * A * (0.5 - 0.5 * Math.cos(TAU * u / 2)); }
    if (bras_g) bras_g.rotation.z += 0.07 * A * f;
    if (bras_d) bras_d.rotation.z -= 0.07 * A * f;
  },
  marche(r, u, o) {
    const A = o.amplitude, { corps, tete, bras_g, bras_d, jambe_g, jambe_d } = r.roles;
    const f = Math.sin(TAU * u / 0.7), th = 0.5 * A * f;
    if (jambe_g) jambe_g.rotation.x += th;
    if (jambe_d) jambe_d.rotation.x -= th;
    if (bras_g) bras_g.rotation.x -= 0.8 * th;
    if (bras_d) bras_d.rotation.x += 0.8 * th;
    if (corps) corps.rotation.y += 0.08 * A * f;
    if (tete) tete.rotation.y -= 0.06 * A * f;
    const L = Math.max(r.mesures.jambe_g?.longueur || 0, r.mesures.jambe_d?.longueur || 0);
    r.pose.position.y -= L * (1 - Math.cos(th));  // les pieds restent au sol
  },
  saut(r, u, o) {
    const A = o.amplitude, { corps, tete, bras_g, bras_d, jambe_g, jambe_d } = r.roles;
    const c = (u % 1.2) / 1.2;  // cycle de 1,2 s : élan, vol, réception
    const elan = lisse(c / 0.18) * (1 - lisse((c - 0.18) / 0.08));
    const vol = c >= 0.18 && c < 0.78 ? (c - 0.18) / 0.6 : -1;
    const bras = lisse((c - 0.14) / 0.12) * (1 - lisse((c - 0.72) / 0.2));
    if (corps) corps.rotation.x += 0.18 * elan;
    if (bras_g) { bras_g.rotation.x += 0.6 * elan; bras_g.rotation.z += 2.5 * A * bras; }
    if (bras_d) { bras_d.rotation.x += 0.6 * elan; bras_d.rotation.z -= 2.5 * A * bras; }
    if (vol >= 0) {
      r.pose.position.y += 6 * A * 4 * vol * (1 - vol);
      if (jambe_g) jambe_g.rotation.x -= 0.35;
      if (jambe_d) jambe_d.rotation.x += 0.35;
      if (tete) tete.rotation.x -= 0.15;
    } else if (c >= 0.78 && tete) tete.rotation.x += 0.15 * Math.sin(Math.PI * (c - 0.78) / 0.22);
  },
  parle(r, u, o) {
    const A = o.amplitude, { tete, bras_d, bouche } = r.roles;
    if (tete) { tete.rotation.x += 0.07 * A * Math.sin(TAU * 3 * u); tete.rotation.z += 0.05 * A * Math.sin(TAU * 0.7 * u); }
    if (bras_d) bras_d.rotation.x -= 0.35 * A * (0.5 + 0.5 * Math.sin(TAU * 0.8 * u));
    if (bouche) bouche.visible = ((Math.floor(u * 8) * 2654435761) >>> 0) % 3 !== 0;
  },
  coucou(r, u, o) {
    const A = o.amplitude, { tete, bras_d, corps } = r.roles;
    if (bras_d) bras_d.rotation.z -= 2.4 + 0.35 * A * Math.sin(TAU * 2.5 * u);
    if (tete) tete.rotation.z += 0.08 * A * Math.sin(TAU * 1.25 * u);
    if (corps) corps.rotation.z += 0.03 * A * Math.sin(TAU * 1.25 * u);
  },
});

// ---------- partie THREE ----------
export function fabriquerVoxel(THREE, { couleur, scene = "/scene/" } = {}) {
  const baseScene = String(scene).replace(/[^/]*$/, "");

  function url(chemin) {
    chemin = String(chemin).replace(/\\/g, "/");
    if (/^[a-z]+:|^\/|(^|\/)\.\.(\/|$)/i.test(chemin)) {
      throw new Error(`voxel : chemin « ${chemin} » refusé (relatif à la racine du dépôt, ou « ./… » relatif à la scène)`);
    }
    const enc = (p) => p.split("/").map(encodeURIComponent).join("/");
    return chemin.startsWith("./") ? baseScene + enc(chemin.slice(2)) : "/depot/" + enc(chemin);
  }

  async function lireFichier(chemin, texte) {
    const r = await fetch(url(chemin));
    if (!r.ok) throw new Error(`voxel : « ${chemin} » introuvable (HTTP ${r.status})`);
    return texte ? r.text() : r.arrayBuffer();
  }

  async function charger(chemin) {
    try {
      return lireVox(await lireFichier(chemin, false));
    } catch (e) {
      throw new Error(`${e.message}${e.message.includes(chemin) ? "" : ` (${chemin})`}`);
    }
  }

  function tableRampe(opt) {
    if (!opt) return rampe;
    if (typeof opt === "function") return (i) => opt(i) || rampe(i);
    return (i) => opt[i] || rampe(i);
  }

  function maillage(modele, { rampe: rp, contour = false, occlusion = true, centre = "bas", eclairage = "camera", taille = 1 } = {}) {
    if (!(modele instanceof Grille)) throw new Error("voxel : maillage(modele) attend une grille (charger() ou grille())");
    if (!["camera", "fixe"].includes(eclairage)) throw new Error(`voxel : eclairage « ${eclairage} » (camera ou fixe)`);
    const R = tableRampe(rp);
    const { lx, ly, lz } = modele;
    let c0;
    if (centre === "bas") c0 = [lx / 2, 0, lz / 2];
    else if (centre === "milieu") c0 = [lx / 2, ly / 2, lz / 2];
    else if (centre === "coin") c0 = [0, 0, 0];
    else if (Array.isArray(centre) && centre.length === 3) c0 = centre.map(Number);
    else throw new Error(`voxel : centre « ${centre} » (bas, milieu, coin ou [x, y, z])`);
    const dec = c0.map((v) => -v);

    const { quads } = faces(modele, { occlusion });
    const cle = (q) => q.dir * 1000 + q.couleur * 2 + q.occ;
    quads.sort((a, b) => cle(a) - cle(b));
    const pos = new Float32Array(quads.length * 12), nor = new Float32Array(quads.length * 12);
    const idx = new (quads.length * 4 > 65535 ? Uint32Array : Uint16Array)(quads.length * 6);
    const geo = new THREE.BufferGeometry();
    const mats = [], entrees = [];
    let courante = -1, debutGroupe = 0;
    quads.forEach((q, k) => {
      const d = DIRECTIONS[q.dir];
      q.p.forEach((p, m) => {
        for (let a = 0; a < 3; a++) { pos[k * 12 + m * 3 + a] = (p[a] + dec[a]) * taille; nor[k * 12 + m * 3 + a] = d[a]; }
      });
      idx.set([k * 4, k * 4 + 1, k * 4 + 2, k * 4, k * 4 + 2, k * 4 + 3], k * 6);
      if (cle(q) !== courante) {
        if (courante >= 0) geo.addGroup(debutGroupe * 6, (k - debutGroupe) * 6, mats.length - 1);
        courante = cle(q); debutGroupe = k;
        const r = R(q.couleur);
        for (const n of ROLES) verifierIndex(r[n], `rampe(${q.couleur}).${n}`);
        mats.push(new THREE.MeshBasicMaterial({
          color: couleur(r.face), polygonOffset: Boolean(contour), polygonOffsetFactor: 1, polygonOffsetUnits: 1,
        }));
        entrees.push({ dir: q.dir, rampe: r, occ: q.occ });
      }
    });
    if (courante >= 0) geo.addGroup(debutGroupe * 6, (quads.length - debutGroupe) * 6, mats.length - 1);
    geo.setAttribute("position", new THREE.BufferAttribute(pos, 3));
    geo.setAttribute("normal", new THREE.BufferAttribute(nor, 3));
    geo.setIndex(new THREE.BufferAttribute(idx, 1));
    geo.computeBoundingBox();
    geo.computeBoundingSphere();

    const mesh = new THREE.Mesh(geo, mats);
    mesh.name = modele.nom || "voxel";
    mesh.userData.voxel = { nom: modele.nom, lx, ly, lz, decalage: dec, taille, faces: quads.length, eclairage };

    // couleurs choisies juste avant chaque dessin (une fois par image et par caméra)
    const cache = new Map();
    const col = (i) => { if (!cache.has(i)) cache.set(i, couleur(i)); return cache.get(i); };
    const q = new THREE.Quaternion(), qc = new THREE.Quaternion(), n = new THREE.Vector3();
    let derniere = null;
    const roles = new Array(6);
    function ombrer(renderer, _scene, camera) {
      const marque = `${renderer.info.render.frame}:${camera.uuid}`;
      if (marque === derniere) return;
      derniere = marque;
      mesh.getWorldQuaternion(q);
      if (eclairage === "camera") q.premultiply(camera.getWorldQuaternion(qc).invert());
      for (let d = 0; d < 6; d++) {
        n.set(...DIRECTIONS[d]).applyQuaternion(q);
        roles[d] = role(n.x, n.y, n.z);
      }
      entrees.forEach((e, k) => {
        let i = e.rampe[roles[e.dir]];
        if (e.occ) i = plusSombre(i);
        mats[k].color.copy(col(i));
      });
    }
    mesh.onBeforeRender = ombrer;
    mesh.userData.ombrer = (camera, renderer = { info: { render: { frame: NaN } } }) => ombrer(renderer, null, camera);

    if (contour) {
      const ci = contour === true ? 1 : contour;
      if (ci !== 1 && ci !== 2) throw new Error(`voxel : contour ${contour} (false, true, 1 ou 2)`);
      const segs = aretes(modele);
      const lp = new Float32Array(segs.length * 6);
      segs.forEach((s, k) => { for (let m = 0; m < 6; m++) lp[k * 6 + m] = (s[m] + dec[m % 3]) * taille; });
      const lg = new THREE.BufferGeometry();
      lg.setAttribute("position", new THREE.BufferAttribute(lp, 3));
      const traits = new THREE.LineSegments(lg, new THREE.LineBasicMaterial({ color: couleur(ci) }));
      traits.name = "contour";
      mesh.add(traits);
      mesh.userData.voxel.aretes = segs.length;
    }
    return mesh;
  }

  // ---------- rig ----------
  function vecteur(v, quoi) {
    if (!Array.isArray(v) || v.length !== 3 || !v.every((x) => Number.isFinite(Number(x)))) {
      throw new Error(`voxel : rig : ${quoi} doit être [x, y, z]`);
    }
    return v.map(Number);
  }

  function rig(parties, rigToml) {
    const def = typeof rigToml === "string" ? lireToml(rigToml) : rigToml;
    if (!def || typeof def.parties !== "object") throw new Error("voxel : rig : table [parties.<nom>] absente");
    const echelle = def.echelle === undefined ? 1 : Number(def.echelle);
    if (!(echelle > 0)) throw new Error(`voxel : rig : echelle ${def.echelle} (nombre > 0)`);
    const noms = Object.keys(def.parties);
    const info = {};
    for (const nom of noms) {
      const p = def.parties[nom];
      const mesh = parties[nom];
      if (!mesh || !mesh.isObject3D) throw new Error(`voxel : rig : partie « ${nom} » sans maillage`);
      if (p.parent !== undefined && !def.parties[p.parent]) throw new Error(`voxel : rig : parent « ${p.parent} » de « ${nom} » inconnu`);
      info[nom] = { p, mesh, origine: vecteur(p.origine ?? [0, 0, 0], `${nom}.origine`), pivot: vecteur(p.pivot ?? [0, 0, 0], `${nom}.pivot`) };
    }
    for (const nom of noms) {  // cycles
      const vus = new Set([nom]);
      for (let x = def.parties[nom].parent; x !== undefined; x = def.parties[x].parent) {
        if (vus.has(x)) throw new Error(`voxel : rig : boucle de parents autour de « ${nom} »`);
        vus.add(x);
      }
    }
    // sol : point de la grille du perso qui devient l'origine du groupe (défaut : milieu du dessous de l'ensemble)
    let sol = def.sol;
    if (sol === undefined) {
      const mn = [Infinity, Infinity, Infinity], mx = [-Infinity, -Infinity, -Infinity];
      for (const nom of noms) {
        const v = info[nom].mesh.userData.voxel;
        const t = v ? [v.lx, v.ly, v.lz] : [0, 0, 0];
        for (let a = 0; a < 3; a++) { mn[a] = Math.min(mn[a], info[nom].origine[a]); mx[a] = Math.max(mx[a], info[nom].origine[a] + t[a]); }
      }
      sol = [(mn[0] + mx[0]) / 2, mn[1], (mn[2] + mx[2]) / 2];
    }
    sol = vecteur(sol, "sol");

    const groupe = new THREE.Group();
    groupe.name = def.nom || "rig";
    groupe.scale.setScalar(echelle);
    const pose = new THREE.Group();
    pose.name = "pose";
    groupe.add(pose);
    const pivots = {}, roles = {}, mesures = {};
    const fabriquer = (nom) => {
      if (pivots[nom]) return pivots[nom];
      const { p, mesh, origine, pivot } = info[nom];
      const g = new THREE.Group();
      g.name = nom;
      const base = p.parent !== undefined ? info[p.parent].pivot : sol;
      g.position.set(pivot[0] - base[0], pivot[1] - base[1], pivot[2] - base[2]);
      g.userData.repos = g.position.clone();
      const v = mesh.userData.voxel || { decalage: [0, 0, 0], taille: 1 };
      mesh.scale.setScalar(1 / (v.taille || 1));
      mesh.position.set(origine[0] - pivot[0] - v.decalage[0], origine[1] - pivot[1] - v.decalage[1], origine[2] - pivot[2] - v.decalage[2]);
      g.add(mesh);
      (p.parent !== undefined ? fabriquer(p.parent) : pose).add(g);
      pivots[nom] = g;
      const r = p.role || nom;
      roles[r] = g;
      mesures[r] = { longueur: pivot[1] - origine[1] };
      return g;
    };
    noms.forEach(fabriquer);

    const clips = { ...CLIPS };
    const defClips = def.clips || {};
    function repos() {
      pose.position.set(0, 0, 0); pose.rotation.set(0, 0, 0);
      for (const g of Object.values(pivots)) {
        g.position.copy(g.userData.repos); g.rotation.set(0, 0, 0); g.scale.set(1, 1, 1); g.visible = true;
      }
    }
    function poser(nomClip, t, options = {}) {
      const dc = defClips[nomClip] || {};
      const base = dc.base || nomClip;
      const clip = clips[nomClip] || clips[base];
      if (typeof clip !== "function") {
        throw new Error(`voxel : clip « ${nomClip} » inconnu (${[...new Set([...Object.keys(clips), ...Object.keys(defClips)])].join(", ")})`);
      }
      const o = { ips: 12, vitesse: 1, amplitude: 1, ...dc, ...options };
      const tc = o.ips ? Math.floor(t * o.ips + 1e-6) / o.ips : t;
      repos();
      clip({ roles, pose, mesures, pivots }, tc * o.vitesse, o);
      return groupe;
    }
    Object.assign(groupe, { parties: pivots, roles, mesures, clips, poser, repos, definition: def });
    return groupe;
  }

  const fichiers = new Map();
  async function chargerRig(cheminToml, options = {}) {
    const texte = await lireFichier(cheminToml, true);
    const def = /\.json$/i.test(cheminToml) ? JSON.parse(texte) : lireToml(texte);
    const dossier = String(cheminToml).replace(/\\/g, "/").replace(/[^/]*$/, "");
    const meshes = {};
    for (const [nom, p] of Object.entries(def.parties || {})) {
      if (!p.fichier) throw new Error(`voxel : rig ${cheminToml} : partie « ${nom} » sans fichier`);
      const f = dossier + String(p.fichier).replace(/^\.\//, "");
      if (!fichiers.has(f)) fichiers.set(f, charger(f));
      const ms = await fichiers.get(f);
      const sel = p.modele ?? 0;
      const m = typeof sel === "number" ? ms[sel] : ms.find((x) => x.nom === sel);
      if (!m) throw new Error(`voxel : rig : modèle « ${sel} » absent de ${f} (${ms.map((x, k) => x.nom || k).join(", ")})`);
      meshes[nom] = maillage(m, { ...options, ...(p.maillage || {}), centre: "coin" });
    }
    return rig(meshes, def);
  }

  return Object.freeze({
    charger, maillage, rig, chargerRig, grille, rampe, plusSombre, RAMPES, CLIPS, lireToml, lireVox, url,
  });
}
