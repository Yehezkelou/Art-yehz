"""Tests de verifier_pixels.py :  python3 -I -m unittest discover -s ~/videos/outils/tests"""
import contextlib, io, os, sys, tempfile, unittest

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import verifier_pixels as vp  # noqa: E402
from test_png import fabriquer, rgba  # noqa: E402

NUIT, CREME, ROUGE = (29, 27, 46, 255), (242, 237, 228, 255), (229, 83, 61, 255)
VIDE = (0, 0, 0, 0)


def agrandir(lignes_scene, k):
    """Scène (liste de lignes de pixels) → (largeur, hauteur, pixels) agrandie ×k au plus proche voisin."""
    px = [p for ligne in lignes_scene for _ in range(k) for p in ligne for _ in range(k)]
    return len(lignes_scene[0]) * k, len(lignes_scene) * k, px


class Test(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.palette = os.path.join(self.tmp.name, "p.hex")
        with open(self.palette, "w") as f:
            f.write("1d1b2e\nF2EDE4\n#e5533d\n")

    def tearDown(self):
        self.tmp.cleanup()

    def png(self, nom, data):
        chemin = os.path.join(self.tmp.name, nom)
        with open(chemin, "wb") as f:
            f.write(data)
        return chemin

    def lancer(self, *args):
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            code = vp.main([*args, "--palette", self.palette])
        return code, out.getvalue()

    SCENE = [[NUIT, CREME, VIDE], [ROUGE, VIDE, NUIT]]

    def test_vert_x4(self):
        w, h, px = agrandir(self.SCENE, 4)
        code, out = self.lancer(self.png("a.png", rgba(w, h, px, filtres=(4, 1))))
        self.assertEqual(code, 0, out)
        self.assertIn("VERT", out)
        self.assertIn("0 bloc(s) fautif(s) sur 6, 0 couleur(s) hors palette", out)

    def test_bloc_baveux(self):
        w, h, px = agrandir(self.SCENE, 4)
        px[5 * w + 9] = NUIT                     # pixel (9, 5) → bloc de scène (2, 1), qui est NUIT…
        px[1 * w + 6] = ROUGE                    # pixel (6, 1) → bloc (1, 0), CREME
        px[6 * w + 0] = VIDE                     # pixel (0, 6) → bloc (0, 1) : transparent + couleur
        code, out = self.lancer(self.png("b.png", rgba(w, h, px)))
        self.assertEqual(code, 1)
        self.assertIn("2 bloc(s) fautif(s)", out)
        self.assertIn("(1, 0) (0, 1)", out)
        self.assertIn("0 couleur(s) hors palette", out)

    def test_max_et_taille(self):
        w, h, px = agrandir(self.SCENE, 4)
        px = [p if i % 2 else ROUGE for i, p in enumerate(px)]
        code, out = self.lancer(self.png("c.png", rgba(w, h, px)), "--max", "2", "--echelle", "5")
        self.assertEqual(code, 1)
        self.assertIn("taille non multiple de 5 : 12×8", out)
        self.assertIn("2 premières zones (x, y en pixels de scène) : (0, 0) (1, 0)\n", out)

    def test_hors_palette_et_tolerees(self):
        rose, mi = (255, 0, 255, 255), (229, 83, 61, 128)
        w, h, px = agrandir([[NUIT, rose], [mi, rose]], 1)
        chemin = self.png("d.png", rgba(w, h, px))
        code, out = self.lancer(chemin, "--echelle", "1")
        self.assertEqual(code, 1)
        self.assertIn("2 couleur(s) hors palette", out)
        self.assertIn("#ff00ff (2 px), #e5533d alpha 128 (1 px)", out)
        code, out = self.lancer(chemin, "--echelle", "1", "--tolerees", "FF00FF")
        self.assertIn("1 couleur(s) hors palette", out)     # le semi-transparent reste interdit

    def test_png_indexe(self):
        pal = [(0, 0, 0), (29, 27, 46), (242, 237, 228), (1, 2, 3)]
        bon = [bytes([1, 1, 0, 0]), bytes([1, 1, 0, 0]), bytes([2, 2, 1, 1]), bytes([2, 2, 1, 1])]
        code, out = self.lancer(self.png("e.png", fabriquer(4, 4, bon, 3, palette=pal, trns=[0])), "--echelle", "2")
        self.assertEqual(code, 0, out)
        mauvais = [bytes([3, 1, 0, 0])] + bon[1:]
        code, out = self.lancer(self.png("f.png", fabriquer(4, 4, mauvais, 3, palette=pal, trns=[0])),
                                "--echelle", "2")
        self.assertEqual(code, 1)
        self.assertIn("1 bloc(s) fautif(s)", out)
        self.assertIn("#010203 (1 px)", out)

    def test_plusieurs_images_et_illisible(self):
        w, h, px = agrandir(self.SCENE, 4)
        bon = self.png("g.png", rgba(w, h, px))
        code, out = self.lancer(bon, self.png("h.png", b"rien"))
        self.assertEqual(code, 1)
        self.assertIn("illisible", out)
        self.assertIn("ROUGE — 1/2 image(s) conforme(s).", out)


if __name__ == "__main__":
    unittest.main()
