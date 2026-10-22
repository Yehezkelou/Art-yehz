"""Tests de rendu3d.py et outils/rendu3d/ :  python3 -I -m unittest discover -s ~/videos/outils/tests

Les tests qui rendent vraiment (node + npm ci + Chrome/Edge) sont sautés si l'un manque.
"""
import json, os, pathlib, shutil, subprocess, sys, tempfile, tomllib, unittest

ICI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(ICI, ".."))
sys.path.insert(0, os.path.join(ICI, "..", "..", "assets", "polices"))
import chemins  # noqa: E402
import png  # noqa: E402
import rendu3d  # noqa: E402
import ico5x7  # noqa: E402
import verifier_pixels  # noqa: E402
import vox  # noqa: E402
sys.path.insert(0, os.path.join(ICI, "..", "rendu3d", "exemples"))
import voxel_demo  # noqa: E402

DEMO = os.path.join(os.path.dirname(rendu3d.OUTIL), "exemples", "demo.mjs")
VOXEL_DEMO = os.path.join(os.path.dirname(rendu3d.OUTIL), "exemples", "voxel_demo.mjs")
VOXEL = os.path.join(os.path.dirname(rendu3d.OUTIL), "voxel.mjs")
THREE = os.path.join(os.path.dirname(rendu3d.OUTIL), "node_modules", "three", "build", "three.module.js")
PALETTE = verifier_pixels.lire_palette(verifier_pixels.PALETTE)
NODE = rendu3d.trouver_node()
PRET = bool(NODE) and rendu3d.dependances_presentes()


def lancer_node(code):
    url = pathlib.Path(rendu3d.OUTIL).as_uri()
    r = subprocess.run([NODE, "--input-type=module", "-e", f"import * as R from {json.dumps(url)};\n{code}"],
                       capture_output=True, text=True, encoding="utf-8")
    if r.returncode:
        raise AssertionError(r.stderr)
    return r.stdout


def lancer_voxel(code):
    """Code ESM avec V = voxel.mjs et THREE = three (sous Node) ; renvoie stdout."""
    entete = (f"import * as V from {json.dumps(pathlib.Path(VOXEL).as_uri())};\n"
              f"import * as THREE from {json.dumps(pathlib.Path(THREE).as_uri())};\n")
    r = subprocess.run([NODE, "--input-type=module", "-e", entete + code], capture_output=True, text=True, encoding="utf-8")
    if r.returncode:
        raise AssertionError(r.stderr)
    return r.stdout


class TestCommande(unittest.TestCase):
    def test_arguments(self):
        c = rendu3d.commande("s.mjs", "out", 1, 2.5, fond="#1D1B2E", params={"a": "é"}, images=[0, 5], node="node")
        self.assertEqual(c[:2], ["node", rendu3d.OUTIL])
        a = dict(zip(c[2::2], c[3::2]))
        self.assertEqual(a["--scene"], os.path.abspath("s.mjs"))
        self.assertEqual((a["--debut"], a["--fin"], a["--ips"]), ("1.0", "2.5", "24"))
        self.assertEqual((a["--largeur"], a["--hauteur"], a["--fond"]), ("270", "480", "1D1B2E"))
        self.assertEqual(json.loads(a["--params"]), {"a": "é"})
        self.assertEqual(a["--images"], "0,5")
        self.assertNotIn("--images", rendu3d.commande("s.mjs", "o", 0, 1, node="node"))

    def test_node_surcharge_absente(self):
        self.assertIsNone(rendu3d.trouver_node({"ICO_NODE": os.path.join(ICI, "pas-de-node.exe")}))


@unittest.skipUnless(PRET, "node ou outils/rendu3d/node_modules absent (npm ci)")
class TestModuleNode(unittest.TestCase):
    def test_glyphes_identiques_a_la_police(self):
        g = json.loads(lancer_node("console.log(JSON.stringify(R.lireGlyphes()));"))
        self.assertEqual(g, ico5x7.GLYPHES)

    def test_palette(self):
        p = json.loads(lancer_node("console.log(JSON.stringify(R.lirePalette()));"))
        self.assertEqual(len(p), 32)
        self.assertEqual(p[0], "#0E0D18")
        self.assertEqual({verifier_pixels.lire_couleur(c) for c in p}, PALETTE)

    def test_quantifier_et_png(self):
        # 3 pixels : presque crème opaque, demi-transparent (→ 0), alpha 128 (→ opaque, couleur la plus proche)
        code = ("const q = R.quantifier(Buffer.from([240,236,230,255, 200,10,10,127, 230,80,60,128]), R.lirePalette());"
                "process.stdout.write(R.encoderPNG(3, 1, q).toString('base64'));")
        import base64
        w, h, px = png.decoder(base64.b64decode(lancer_node(code)))
        self.assertEqual((w, h), (3, 1))
        self.assertEqual(px, [(0xF2, 0xED, 0xE4, 255), (0, 0, 0, 0), (0xE5, 0x53, 0x3D, 255)])

    def test_arguments_invalides(self):
        for args in (["--scene", DEMO, "--out", "x", "--debut", "1", "--fin", "1"],
                     ["--scene", DEMO, "--out", "x", "--debut", "0", "--fin", "1", "--images", "24"],
                     ["--scene", DEMO, "--out", "x", "--debut", "0", "--fin", "1", "--fond", "rouge"],
                     ["--scene", DEMO, "--out", "x", "--debut", "0"]):
            r = subprocess.run([NODE, rendu3d.OUTIL] + args, capture_output=True, text=True, encoding="utf-8")
            self.assertEqual(r.returncode, 2, args)
            self.assertIn("usage", r.stderr)


@unittest.skipUnless(PRET, "node ou outils/rendu3d/node_modules absent (npm ci)")
class TestVoxelNode(unittest.TestCase):
    def test_rampes_identiques_a_vox_py(self):
        js = json.loads(lancer_voxel("const t = {}; for (let i = 1; i <= 32; i++) t[i] = [V.rampe(i), V.plusSombre(i)];"
                                     "console.log(JSON.stringify({ r: V.RAMPES, t }));"))
        self.assertEqual([tuple(r) for r in js["r"]], list(vox.RAMPES))
        for i in range(1, 33):
            self.assertEqual(js["t"][str(i)], [vox.rampe(i), vox.plus_sombre(i)], i)

    def test_lire_vox_comme_python(self):
        a = vox.Modele(5, 3, 4, nom="essai").boite(0, 0, 0, 4, 0, 3, 14)
        a[1, 1, 2], a[4, 2, 3] = 23, 32
        b = vox.Modele(1, 7, 2, nom="tige").boite(0, 0, 0, 0, 6, 1, 26)
        with tempfile.TemporaryDirectory() as d:
            f = os.path.join(d, "x.vox")
            vox.ecrire_vox(f, [a, b])
            js = json.loads(lancer_voxel(
                f"import fs from 'node:fs'; const ms = V.lireVox(fs.readFileSync({json.dumps(f)}));"
                "console.log(JSON.stringify(ms.map((m) => ({ nom: m.nom, t: [m.lx, m.ly, m.lz], d: [...m.donnees] }))));"))
        self.assertEqual(js, [{"nom": m.nom, "t": list(m.taille), "d": list(m.donnees)} for m in (a, b)])

    def test_toml_comme_tomllib(self):
        texte = r"""# essai
nom = "chibi"   # commentaire
echelle = 1.5
sol = [5, 0, 4]
"clé avec espace" = 'litt\éral'
drapeau = true
grand = 1_000
neg = -2.5e2
[parties.tete]
fichier = "téte.vox"
pivot = [
  1, 2.5,
  -3,   # fin de ligne
]
maillage = { contour = 2, occlusion = false }
[parties."bras d".sous]
a.b = "x\"y"
[[clips]]
nom = "un"
[[clips]]
nom = "deux"
"""
        js = json.loads(lancer_voxel(f"console.log(JSON.stringify(V.lireToml({json.dumps(texte)})));"))
        self.assertEqual(js, tomllib.loads(texte))
        with tempfile.TemporaryDirectory() as d:
            voxel_demo.fabriquer(d)
            with open(os.path.join(d, "voxel_demo.rig.toml"), encoding="utf-8") as f:
                rig = f.read()
        self.assertEqual(json.loads(lancer_voxel(f"console.log(JSON.stringify(V.lireToml({json.dumps(rig)})));")),
                         tomllib.loads(rig))
        for faux in ("a = ", "a = 1\na = 2", "[t\nb = 1", 'a = "x', "a = 1 b"):
            with self.assertRaisesRegex(AssertionError, "toml ligne"):
                lancer_voxel(f"V.lireToml({json.dumps(faux)});")

    def test_faces_gloutonnes_occlusion_aretes(self):
        js = json.loads(lancer_voxel("""
const plein = V.grille(3, 3, 3).boite(0, 0, 0, 2, 2, 2, 11);
const deux = V.grille(2, 1, 1).set(0, 0, 0, 11).set(1, 0, 0, 23);
const L = V.grille(3, 2, 1).boite(0, 0, 0, 2, 0, 0, 14).set(0, 1, 0, 14);   // sol de 3 + un mur à gauche
const fL = V.faces(L).quads.filter((q) => q.dir === 2);
const sansOcc = V.faces(L, { occlusion: false }).quads.filter((q) => q.occ).length;
const un = V.grille(1, 1, 1).set(0, 0, 0, 1);
const barre = V.grille(2, 1, 1).boite(0, 0, 0, 1, 0, 0, 1);
const coinCreux = V.grille(2, 2, 1).boite(0, 0, 0, 1, 0, 0, 1).set(0, 1, 0, 1);
console.log(JSON.stringify({
  plein: V.faces(plein).quads.length, deux: V.faces(deux).quads.length,
  dessusL: fL.map((q) => [q.p[0][0], q.occ]), sansOcc,
  aretes: [V.aretes(un).length, V.aretes(barre).length, V.aretes(coinCreux).length],
  role: [V.role(0, 1, 0), V.role(0, -1, 0), V.role(0, 0, 1), V.role(-1, 0, 0), V.role(1, 0, 0)],
}));"""))
        self.assertEqual(js["plein"], 6, "cube plein : une face par côté (faces internes retirées, fusion gloutonne)")
        self.assertEqual(js["deux"], 10, "2 couleurs : faces de couleurs différentes non fusionnées")
        # dessus en L : celui du mur (0, 1) et la case x = 2 sont libres, la case x = 1 contre le mur est coincée
        self.assertEqual(sorted(q[1] for q in js["dessusL"]), [0, 0, 1])
        self.assertEqual(js["sansOcc"], 0)
        self.assertEqual(js["aretes"], [12, 12, 18])
        self.assertEqual(js["role"], ["dessus", "dessous", "face", "cote", "dessous"])

    def test_maillage_et_rig_sous_node(self):
        js = json.loads(lancer_voxel(r"""
const couleur = (i) => new THREE.Color(0);
const X = V.fabriquerVoxel(THREE, { couleur });
const g = X.grille(4, 2, 2, "b").boite(0, 0, 0, 3, 1, 1, 19);
const m = X.maillage(g, { contour: 1 });
const bb = m.geometry.boundingBox;
const c = X.maillage(g, { centre: "coin", occlusion: false });
const corps = X.maillage(X.grille(2, 2, 2).boite(0, 0, 0, 1, 1, 1, 11), { centre: "coin" });
const bras = X.maillage(X.grille(1, 2, 1).boite(0, 0, 0, 0, 1, 0, 28), { centre: "coin" });
const r = X.rig({ corps, bras }, `[parties.corps]
origine = [0, 0, 0]
pivot = [1, 0, 1]
[parties.bras]
origine = [2, 0, 0]
pivot = [2.5, 2, 0.5]
parent = "corps"
role = "bras_d"`);
r.updateMatrixWorld(true);
const p = new THREE.Vector3(); bras.getWorldPosition(p);
r.poser("coucou", 0.3);
const rot = r.roles.bras_d.rotation.z;
r.poser("idle", 0);
let erreur = ""; try { r.poser("danse", 0); } catch (e) { erreur = e.message; }
r.clips.danse = (x, u) => { x.roles.bras_d.rotation.x = 1; };
r.poser("danse", 0);
const danse = r.roles.bras_d.rotation.x;
r.poser("idle", 0);
console.log(JSON.stringify({
  groupes: m.geometry.groups.length, mats: m.material.length, basic: m.material.every((x) => x.isMeshBasicMaterial),
  bb: [bb.min.x, bb.min.y, bb.min.z, bb.max.x, bb.max.y, bb.max.z], contour: m.children[0].type, faces: m.userData.voxel.faces,
  bbCoin: [c.geometry.boundingBox.min.x, c.geometry.boundingBox.min.y],
  bras: [p.x, p.y, p.z], sol: [r.parties.corps.position.x, r.parties.corps.position.z], rot, erreur,
  danse, apres: r.roles.bras_d.rotation.x,
}));"""))
        self.assertTrue(js["basic"])
        self.assertEqual(js["groupes"], js["mats"])
        self.assertEqual(js["bb"], [-2, 0, -1, 2, 2, 1])  # centre « bas »
        self.assertEqual(js["bbCoin"], [0, 0])
        self.assertEqual(js["contour"], "LineSegments")
        self.assertEqual(js["faces"], 6)
        # coin du bras dans le groupe = origine − sol (sol par défaut : milieu du dessous de l'ensemble = [1.5, 0, 1])
        self.assertEqual(js["bras"], [0.5, 0, -1])
        self.assertEqual(js["sol"], [-0.5, 0])
        self.assertLess(js["rot"], -2)  # coucou : bras droit levé
        self.assertIn("clip « danse » inconnu", js["erreur"])
        self.assertEqual((js["danse"], js["apres"]), (1, 0))


@unittest.skipUnless(PRET, "node ou outils/rendu3d/node_modules absent (npm ci)")
class TestRenduVoxelDemo(unittest.TestCase):
    def preparer(self, d):
        voxel_demo.fabriquer(d)
        shutil.copy(VOXEL_DEMO, d)
        return os.path.join(d, "voxel_demo.mjs")

    def rendre(self, scene, sortie, **k):
        try:
            return rendu3d.rendre(scene, sortie, 0, 2, ips=12, delai=300, **k)
        except rendu3d.ErreurRendu as e:
            if "aucun Chrome ni Edge" in str(e):
                self.skipTest(str(e))
            raise

    def test_demo_conforme_et_reproductible(self):
        pal = vox.lire_palette()
        with tempfile.TemporaryDirectory() as d:
            scene = self.preparer(d)
            a, b = os.path.join(d, "a"), os.path.join(d, "b")
            info = self.rendre(scene, a, images=[0, 6, 15])
            self.rendre(scene, b, images=[0, 6, 15])
            self.assertEqual((info["images"], info["images_total"]), (3, 24))
            for n in ("f_0000.png", "f_0006.png", "f_0015.png"):
                with open(os.path.join(a, n), "rb") as fa, open(os.path.join(b, n), "rb") as fb:
                    self.assertEqual(fa.read(), fb.read(), f"{n} : deux rendus différents")
                w, h, px = png.lire(os.path.join(a, n))
                self.assertTrue(all(p[3] == 255 for p in px))  # fond opaque (scene.background)
                couleurs = {p[:3] for p in px}
                self.assertTrue(couleurs <= PALETTE, couleurs - PALETTE)
                r = verifier_pixels.analyser(w, h, px, 1, PALETTE)
                self.assertFalse(r["fautifs"] or r["hors"], r)
                attendues = {pal[i - 1] for i in (2, 11, 15, 19, 28)}  # fond, tunique, herbe, or, peau
                self.assertTrue(attendues <= couleurs, attendues - couleurs)
            # sans contour, l'image change : le contour est bien dessiné
            c = os.path.join(d, "c")
            self.rendre(scene, c, images=[0], params={"contour": False})
            with open(os.path.join(a, "f_0000.png"), "rb") as fa, open(os.path.join(c, "f_0000.png"), "rb") as fc:
                self.assertNotEqual(fa.read(), fc.read())

    def test_fichiers_refuses(self):
        with tempfile.TemporaryDirectory() as d:
            scene = os.path.join(d, "s.mjs")
            with open(scene, "w", encoding="utf-8") as f:
                f.write("""export default async function creer(THREE, outils) {
  const st = async (u) => (await fetch(u)).status;
  const s = [await st("/depot/outils/vox.py"), await st("/depot/bible/palette/ico-pixel-32.hex"),
             await st("/depot/assets/3d/palette/ico-pixel-32-magicavoxel.png"), await st("/depot/references/x.png")];
  if (s.join() !== "404,404,200,404") throw new Error("statuts " + s.join());
  let e = ""; try { outils.voxel.url("../x.vox"); } catch (x) { e = x.message; }
  if (!e.includes("refusé")) throw new Error("chemin parent accepté");
  return { scene: new THREE.Scene(), camera: new THREE.PerspectiveCamera() };
}""")
            self.assertTrue(self.rendre(scene, os.path.join(d, "o"), images=[0])["ok"])
            with open(scene, "w", encoding="utf-8") as f:
                f.write("""export default async function creer(THREE, outils) {
  await outils.voxel.charger("./absent.vox");
  return { scene: new THREE.Scene(), camera: new THREE.PerspectiveCamera() };
}""")
            with self.assertRaisesRegex(rendu3d.ErreurRendu, "absent.vox.*introuvable"):
                self.rendre(scene, os.path.join(d, "o"), images=[0])
            with open(scene, "w", encoding="utf-8") as f:
                f.write("""export default function creer(THREE, outils) {
  outils.texturePixel("./absente.png");
  return { scene: new THREE.Scene(), camera: new THREE.PerspectiveCamera() };
}""")
            with self.assertRaisesRegex(rendu3d.ErreurRendu, "texturePixel.*absente.png"):
                self.rendre(scene, os.path.join(d, "o"), images=[0])


@unittest.skipUnless(PRET, "node ou outils/rendu3d/node_modules absent (npm ci)")
class TestRenduDemo(unittest.TestCase):
    def rendre(self, sortie, **k):
        try:
            return rendu3d.rendre(DEMO, sortie, 0, 1, images=[0, 5, 9], delai=300, **k)
        except rendu3d.ErreurRendu as e:
            if "aucun Chrome ni Edge" in str(e):
                self.skipTest(str(e))
            raise

    def test_trois_images_conformes_et_reproductibles(self):
        with tempfile.TemporaryDirectory() as d:
            a, b = os.path.join(d, "a"), os.path.join(d, "b")
            info = self.rendre(a)
            self.rendre(b)
            self.assertEqual((info["images"], info["images_total"], info["largeur"], info["hauteur"]), (3, 24, 270, 480))
            noms = ["f_0000.png", "f_0005.png", "f_0009.png"]
            self.assertEqual(sorted(os.listdir(a)), noms)
            for n in noms:
                with open(os.path.join(a, n), "rb") as fa, open(os.path.join(b, n), "rb") as fb:
                    self.assertEqual(fa.read(), fb.read(), f"{n} : deux rendus différents")
                w, h, px = png.lire(os.path.join(a, n))
                self.assertEqual((w, h), (270, 480))
                self.assertTrue({p[3] for p in px} <= {0, 255})
                opaques = [p[:3] for p in px if p[3] == 255]
                self.assertTrue(set(opaques) <= PALETTE, set(opaques) - PALETTE)
                self.assertGreaterEqual(len(opaques), 0.01 * w * h, f"{n} : moins de 1 % de pixels opaques")
                self.assertTrue(all(p == (0, 0, 0, 0) for p in px if p[3] == 0))
                r = verifier_pixels.analyser(w, h, px, 1, PALETTE)
                self.assertFalse(r["fautifs"] or r["hors"], r)

    def test_fond_et_caractere_absent(self):
        with tempfile.TemporaryDirectory() as d:
            self.rendre(d, fond="1d1b2e", largeur=90, hauteur=160)
            w, h, px = png.lire(os.path.join(d, "f_0000.png"))
            self.assertEqual((w, h), (90, 160))
            self.assertEqual(px[0], (0x1D, 0x1B, 0x2E, 255))
            self.assertTrue(all(p[3] == 255 for p in px))
            with self.assertRaisesRegex(rendu3d.ErreurRendu, "absent.*« b »"):
                self.rendre(d, params={"texte": "0,1b"})


if __name__ == "__main__":
    unittest.main()
