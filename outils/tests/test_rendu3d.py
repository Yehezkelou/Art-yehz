"""Tests de rendu3d.py et outils/rendu3d/ :  python3 -I -m unittest discover -s ~/videos/outils/tests

Les tests qui rendent vraiment (node + npm ci + Chrome/Edge) sont sautés si l'un manque.
"""
import json, os, pathlib, subprocess, sys, tempfile, unittest

ICI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(ICI, ".."))
sys.path.insert(0, os.path.join(ICI, "..", "..", "assets", "polices"))
import chemins  # noqa: E402
import png  # noqa: E402
import rendu3d  # noqa: E402
import ico5x7  # noqa: E402
import verifier_pixels  # noqa: E402

DEMO = os.path.join(os.path.dirname(rendu3d.OUTIL), "exemples", "demo.mjs")
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
