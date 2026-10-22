#!/usr/bin/env node
// ico-vid : rend une scène three.js image par image en pixel art (palette ico-pixel-32), en séquence PNG.
//
//   node outils/rendu3d/rendu3d.mjs --scene <fichier.mjs> --out <dossier> --debut <s> --fin <s>
//        [--ips 24] [--largeur 270] [--hauteur 480] [--fond transparent|RRGGBB] [--params '<json>'] [--images 0,5,9]
//
// → <dossier>/f_0000.png … (RGBA 8 bits ; f_0000 = instant --debut, image i = debut + i/ips, fin exclue :
//   round((fin - debut) × ips) images) et un résumé JSON sur stdout (images écrites, temps, GPU…).
// --images : ne rend que ces numéros (les autres fichiers ne sont pas touchés).
//
// Scène (module ESM) : export default function creer(THREE, outils, params) { … return { scene, camera, update(t) } }
// (outils : voir outils.mjs ; t en secondes absolues ; tout doit être déterministe). Fichiers du dépôt lisibles par la
// page sous /depot/ (.vox, .toml, .json, .png, et .mjs sous assets/3d/ : outils.voxel.charger, outils.texturePixel, clips des modèles). Sans lumière dans la scène,
// une ambiance + un soleil sont ajoutés. Le fond --fond s'applique là où la scène n'a pas de scene.background.
//
// Chaque image : WebGLRenderer sans antialiasing, pixelRatio 1, puis couleur de palette la plus proche
// (RGB euclidien) et alpha < 128 → pixel (0,0,0,0), sinon 255. Navigateur : Chrome ou Edge installés, via
// puppeteer-core (surcharge : ICO_CHROME = chemin de l'exécutable). Racine du dépôt (palette, police) :
// outils/.. ou ICO_VIDEOS. Dépendances : `npm ci` dans outils/rendu3d/ (three et puppeteer-core, versions exactes).

import fs from "node:fs";
import http from "node:http";
import path from "node:path";
import zlib from "node:zlib";
import { fileURLToPath } from "node:url";

const ICI = path.dirname(fileURLToPath(import.meta.url));
const RACINE = process.env.ICO_VIDEOS ? path.resolve(process.env.ICO_VIDEOS) : path.resolve(ICI, "..", "..");

class ErreurUsage extends Error {}

// ---------- arguments ----------
const DEFAUTS = { ips: 24, largeur: 270, hauteur: 480, fond: "transparent", params: "{}" };
const CONNUS = new Set(["scene", "out", "debut", "fin", "ips", "largeur", "hauteur", "fond", "params", "images"]);

export function lireArguments(argv) {
  const a = { ...DEFAUTS };
  for (let i = 0; i < argv.length; i++) {
    const m = /^--([a-z]+)(?:=(.*))?$/.exec(argv[i]);
    if (!m || !CONNUS.has(m[1])) throw new ErreurUsage(`option inconnue « ${argv[i]} »`);
    let v = m[2];
    if (v === undefined) {
      if (i + 1 >= argv.length) throw new ErreurUsage(`--${m[1]} sans valeur`);
      v = argv[++i];
    }
    a[m[1]] = v;
  }
  for (const k of ["scene", "out", "debut", "fin"]) if (a[k] === undefined) throw new ErreurUsage(`--${k} obligatoire`);
  const nombre = (k, entier) => {
    const n = Number(a[k]);
    if (!Number.isFinite(n) || (entier && (!Number.isInteger(n) || n <= 0))) {
      throw new ErreurUsage(`--${k} « ${a[k]} » : ${entier ? "entier > 0" : "nombre"} attendu`);
    }
    return n;
  };
  const o = {
    scene: path.resolve(a.scene), out: path.resolve(a.out),
    debut: nombre("debut"), fin: nombre("fin"),
    ips: nombre("ips", true), largeur: nombre("largeur", true), hauteur: nombre("hauteur", true),
  };
  if (o.fin <= o.debut) throw new ErreurUsage(`--fin (${o.fin}) doit être après --debut (${o.debut})`);
  o.n = Math.round((o.fin - o.debut) * o.ips);
  if (o.n < 1) throw new ErreurUsage("aucune image entre --debut et --fin à cette cadence");
  if (a.fond === "transparent") o.fond = "transparent";
  else if (/^#?[0-9a-fA-F]{6}$/.test(a.fond)) o.fond = "#" + a.fond.replace("#", "").toUpperCase();
  else throw new ErreurUsage(`--fond « ${a.fond} » : transparent ou RRGGBB attendu`);
  try { o.params = JSON.parse(a.params); } catch (e) { throw new ErreurUsage(`--params : JSON invalide (${e.message})`); }
  if (a.images === undefined) o.images = [...Array(o.n).keys()];
  else {
    o.images = String(a.images).split(",").filter((s) => s.trim() !== "").map((s) => {
      const k = Number(s);
      if (!Number.isInteger(k) || k < 0 || k >= o.n) throw new ErreurUsage(`--images : « ${s} » hors de 0…${o.n - 1}`);
      return k;
    });
    if (!o.images.length) throw new ErreurUsage("--images vide");
  }
  if (!fs.existsSync(o.scene)) throw new ErreurUsage(`scène introuvable : ${o.scene}`);
  return o;
}

// ---------- palette et police ----------
export function lirePalette(chemin = path.join(RACINE, "bible", "palette", "ico-pixel-32.hex")) {
  const coul = [];
  for (let ligne of fs.readFileSync(chemin, "utf8").split(/\r?\n/)) {
    ligne = ligne.split(";")[0].trim();
    if (!ligne || ligne.startsWith("//")) continue;
    const t = ligne.replace(/^#/, "");
    if (!/^[0-9a-fA-F]{6}$/.test(t)) throw new Error(`palette ${chemin} : couleur invalide « ${ligne} »`);
    coul.push("#" + t.toUpperCase());
  }
  if (coul.length !== 32) throw new Error(`palette ${chemin} : ${coul.length} couleurs (32 attendues)`);
  return coul;
}

// Lit les glyphes directement dans assets/polices/ico5x7.py (une ligne `"c": ["…", …],` par glyphe) : une seule source.
export function lireGlyphes(chemin = path.join(RACINE, "assets", "polices", "ico5x7.py")) {
  const g = {};
  const re = /^\s*"((?:[^"\\]|\\.)+)"\s*:\s*(\[[^\]]*\])\s*,?\s*$/;
  for (const ligne of fs.readFileSync(chemin, "utf8").split(/\r?\n/)) {
    const m = re.exec(ligne);
    if (!m) continue;
    const lignes = JSON.parse(m[2]);
    if (lignes.length !== 7 || lignes.some((l) => !/^[#.]+$/.test(l) || l.length !== lignes[0].length)) {
      throw new Error(`police ${chemin} : glyphe « ${m[1]} » mal formé`);
    }
    g[JSON.parse(`"${m[1]}"`)] = lignes;
  }
  if (!g["0"] || !g["A"]) throw new Error(`police ${chemin} : glyphes introuvables`);
  return g;
}

// ---------- quantification et PNG ----------
export function quantifier(rgba, palette) {
  const pal = palette.map((c) => [1, 3, 5].map((i) => parseInt(c.slice(i, i + 2), 16)));
  const cache = new Map();
  const out = Buffer.alloc(rgba.length);
  for (let i = 0; i < rgba.length; i += 4) {
    if (rgba[i + 3] < 128) continue;  // (0, 0, 0, 0)
    const cle = (rgba[i] << 16) | (rgba[i + 1] << 8) | rgba[i + 2];
    let p = cache.get(cle);
    if (p === undefined) {
      let best = Infinity;
      for (const c of pal) {
        const dr = rgba[i] - c[0], dg = rgba[i + 1] - c[1], db = rgba[i + 2] - c[2];
        const d = dr * dr + dg * dg + db * db;
        if (d < best) { best = d; p = c; }
      }
      cache.set(cle, p);
    }
    out[i] = p[0]; out[i + 1] = p[1]; out[i + 2] = p[2]; out[i + 3] = 255;
  }
  return out;
}

const TABLE_CRC = (() => {
  const t = new Uint32Array(256);
  for (let n = 0; n < 256; n++) {
    let c = n;
    for (let k = 0; k < 8; k++) c = c & 1 ? 0xedb88320 ^ (c >>> 1) : c >>> 1;
    t[n] = c >>> 0;
  }
  return t;
})();

function crc32(buf) {
  let c = 0xffffffff;
  for (let i = 0; i < buf.length; i++) c = TABLE_CRC[(c ^ buf[i]) & 0xff] ^ (c >>> 8);
  return (c ^ 0xffffffff) >>> 0;
}

function morceau(type, data) {
  const t = Buffer.from(type, "ascii");
  const n = Buffer.alloc(4); n.writeUInt32BE(data.length);
  const c = Buffer.alloc(4); c.writeUInt32BE(crc32(Buffer.concat([t, data])));
  return Buffer.concat([n, t, data, c]);
}

export function encoderPNG(largeur, hauteur, rgba) {
  const ihdr = Buffer.alloc(13);
  ihdr.writeUInt32BE(largeur, 0); ihdr.writeUInt32BE(hauteur, 4);
  ihdr[8] = 8; ihdr[9] = 6;  // 8 bits, RGBA
  const pas = largeur * 4, brut = Buffer.alloc(hauteur * (pas + 1));
  for (let y = 0; y < hauteur; y++) {  // filtre 0 : sortie stable et simple à relire
    rgba.copy(brut, y * (pas + 1) + 1, y * pas, (y + 1) * pas);
  }
  return Buffer.concat([
    Buffer.from([0x89, 0x50, 0x4e, 0x47, 0x0d, 0x0a, 0x1a, 0x0a]),
    morceau("IHDR", ihdr), morceau("IDAT", zlib.deflateSync(brut, { level: 6 })), morceau("IEND", Buffer.alloc(0)),
  ]);
}

// ---------- navigateur ----------
export function trouverNavigateur(env = process.env) {
  if (env.ICO_CHROME) {
    if (!fs.existsSync(env.ICO_CHROME)) throw new Error(`ICO_CHROME introuvable : ${env.ICO_CHROME}`);
    return env.ICO_CHROME;
  }
  const c = [];
  if (process.platform === "win32") {
    for (const base of [env.PROGRAMFILES, env["PROGRAMFILES(X86)"], env.LOCALAPPDATA,
      "C:\\Program Files", "C:\\Program Files (x86)"].filter(Boolean)) {
      c.push(path.join(base, "Google", "Chrome", "Application", "chrome.exe"));
    }
    for (const base of [env["PROGRAMFILES(X86)"], env.PROGRAMFILES, "C:\\Program Files (x86)", "C:\\Program Files"].filter(Boolean)) {
      c.push(path.join(base, "Microsoft", "Edge", "Application", "msedge.exe"));
    }
  } else if (process.platform === "darwin") {
    c.push("/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
      "/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge");
  } else {
    for (const d of (env.PATH || "").split(":")) {
      for (const n of ["google-chrome", "google-chrome-stable", "chromium", "chromium-browser", "microsoft-edge"]) c.push(path.join(d, n));
    }
  }
  const t = c.find((p) => fs.existsSync(p));
  if (!t) throw new Error("aucun Chrome ni Edge trouvé (installer l'un des deux ou définir ICO_CHROME)");
  return t;
}

const TYPES = { ".html": "text/html; charset=utf-8", ".js": "text/javascript", ".mjs": "text/javascript",
  ".json": "application/json", ".png": "image/png", ".glb": "model/gltf-binary", ".gltf": "model/gltf+json",
  ".vox": "application/octet-stream", ".toml": "text/plain; charset=utf-8" };
// Fichiers du dépôt lisibles par les scènes (outils.voxel, outils.texturePixel) sous /depot/ : ces extensions seulement,
// jamais dans references/.
export const EXTENSIONS_DEPOT = new Set([".vox", ".toml", ".json", ".png"]);
// Modules de clips des modèles (ex. assets/3d/persos/tim/tim.clips.mjs) : .mjs sous assets/3d/ seulement.
export const DOSSIER_MJS_DEPOT = path.join("assets", "3d");

function servir(racines) {
  // racines : { "/three/": dossier, "/scene/": dossier, "/depot/": dossier, "/": dossier } ; rien hors de ces dossiers ;
  // sous /depot/ (racine du dépôt), seulement les extensions EXTENSIONS_DEPOT
  const serveur = http.createServer((req, res) => {
    const url = decodeURIComponent(new URL(req.url, "http://x").pathname);
    const pref = Object.keys(racines).sort((a, b) => b.length - a.length).find((p) => url.startsWith(p));
    let fichier = null;
    if (pref) {
      const base = racines[pref];
      fichier = path.resolve(base, "." + path.sep + url.slice(pref.length));
      if (url === "/") fichier = path.join(base, "page.html");
      if (fichier !== base && !fichier.startsWith(base + path.sep)) fichier = null;
      const mjsModele = fichier && path.extname(fichier).toLowerCase() === ".mjs"
        && path.relative(base, fichier).startsWith(DOSSIER_MJS_DEPOT + path.sep);
      if (fichier && pref === "/depot/" && ((!EXTENSIONS_DEPOT.has(path.extname(fichier).toLowerCase()) && !mjsModele)
        || path.relative(base, fichier).split(path.sep)[0].toLowerCase() === "references")) fichier = null;  // n'entre jamais dans une vidéo
    }
    if (!fichier || !fs.existsSync(fichier) || !fs.statSync(fichier).isFile()) {
      res.writeHead(404); res.end("introuvable"); return;
    }
    res.writeHead(200, { "Content-Type": TYPES[path.extname(fichier)] || "application/octet-stream", "Cache-Control": "no-store" });
    fs.createReadStream(fichier).pipe(res);
  });
  return new Promise((ok) => serveur.listen(0, "127.0.0.1", () => ok(serveur)));
}

// ---------- rendu ----------
export async function rendre(o) {
  let puppeteer;
  try {
    puppeteer = (await import("puppeteer-core")).default;
  } catch {
    throw new Error(`puppeteer-core absent : lancer « npm ci » dans ${ICI}`);
  }
  if (!fs.existsSync(path.join(ICI, "node_modules", "three", "build", "three.module.js"))) {
    throw new Error(`three absent : lancer « npm ci » dans ${ICI}`);
  }
  const palette = lirePalette(), glyphes = lireGlyphes();
  const navigateur = trouverNavigateur();
  fs.mkdirSync(o.out, { recursive: true });

  const serveur = await servir({ "/three/": path.join(ICI, "node_modules", "three"), "/scene/": path.dirname(o.scene),
    "/depot/": RACINE, "/": ICI });
  const port = serveur.address().port;
  const t0 = performance.now();
  const nav = await puppeteer.launch({
    executablePath: navigateur, headless: true,
    args: ["--ignore-gpu-blocklist", "--force_high_performance_gpu", "--enable-gpu-rasterization", "--no-first-run", "--no-default-browser-check",
      "--disable-extensions", "--mute-audio"],
  });
  const erreurs = [];
  try {
    const page = await nav.newPage();
    page.on("pageerror", (e) => erreurs.push(String(e.message || e)));
    page.on("console", (m) => { if (m.type() === "error" || m.type() === "warn") process.stderr.write(`[page] ${m.text()}\n`); });
    await page.goto(`http://127.0.0.1:${port}/`, { waitUntil: "load" });
    await page.waitForFunction("window.__pret === true", { timeout: 20000 }).catch(() => {
      throw new Error("page de rendu non chargée" + (erreurs.length ? ` : ${erreurs.join(" ; ")}` : ""));
    });
    const info = await page.evaluate((x) => window.__preparer(x), {
      scene: `/scene/${encodeURIComponent(path.basename(o.scene))}`, params: o.params, palette, glyphes,
      largeur: o.largeur, hauteur: o.hauteur, ips: o.ips, fond: o.fond,
    });
    const tPret = performance.now();
    const fichiers = [];
    for (const k of o.images) {
      const t = o.debut + k / o.ips;
      const b64 = await page.evaluate((x) => window.__rendre(x), t);
      const brut = Buffer.from(b64, "base64");
      if (brut.length !== o.largeur * o.hauteur * 4) throw new Error(`image ${k} : ${brut.length} octets lus`);
      const nom = path.join(o.out, `f_${String(k).padStart(4, "0")}.png`);
      fs.writeFileSync(nom, encoderPNG(o.largeur, o.hauteur, quantifier(brut, palette)));
      fichiers.push(nom);
    }
    const tFin = performance.now();
    return {
      ok: true, scene: o.scene, out: o.out, largeur: o.largeur, hauteur: o.hauteur, ips: o.ips,
      debut: o.debut, fin: o.fin, images_total: o.n, images: o.images.length,
      premiere: fichiers[0], derniere: fichiers[fichiers.length - 1], fond: o.fond,
      lumiere_defaut: info.lumiere_defaut, three: info.three, gpu: info.gpu, navigateur,
      secondes_preparation: +((tPret - t0) / 1000).toFixed(3),
      ms_par_image: +((tFin - tPret) / o.images.length).toFixed(1),
      secondes_total: +((tFin - t0) / 1000).toFixed(3),
    };
  } catch (e) {
    const m = String(e && e.message || e).replace(/^Error: /, "").replace(/^rendu3d : /, "");
    throw new Error(m + (erreurs.length && !m.includes(erreurs[0]) ? ` (erreurs de la page : ${erreurs.join(" ; ")})` : ""));
  } finally {
    await nav.close().catch(() => {});
    serveur.close();
  }
}

async function main() {
  let o;
  try {
    o = lireArguments(process.argv.slice(2));
  } catch (e) {
    if (!(e instanceof ErreurUsage)) throw e;
    process.stderr.write(`rendu3d : ${e.message}\nusage : node rendu3d.mjs --scene <fichier.mjs> --out <dossier> --debut <s> --fin <s> `
      + "[--ips 24] [--largeur 270] [--hauteur 480] [--fond transparent|RRGGBB] [--params '<json>'] [--images 0,5,9]\n");
    process.exit(2);
  }
  try {
    process.stdout.write(JSON.stringify(await rendre(o), null, 2) + "\n");
  } catch (e) {
    process.stderr.write(`rendu3d : ${e.message}\n`);
    process.stdout.write(JSON.stringify({ ok: false, erreur: e.message }) + "\n");
    process.exit(1);
  }
}

if (process.argv[1] && path.resolve(process.argv[1]) === fileURLToPath(import.meta.url)) main();
