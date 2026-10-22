"""Tests de vox.py :  python3 -I -m unittest discover -s ~/videos/outils/tests"""
import contextlib, io, os, struct, sys, tempfile, tomllib, unittest

ICI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(ICI, ".."))
sys.path.insert(0, os.path.join(ICI, "..", "rendu3d", "exemples"))
import chemins  # noqa: E402
import png  # noqa: E402
import verifier_pixels  # noqa: E402
import vox  # noqa: E402
import voxel_demo  # noqa: E402

PAL = vox.lire_palette()
PALETTE = set(PAL)


def lire(chemin):
    with open(chemin, "rb") as f:
        return f.read()


def ecrire(chemin, data):
    with open(chemin, "wb") as f:
        f.write(data)


def chunks(data, i, fin):
    out = []
    while i < fin:
        ident = data[i:i + 4]
        nc, ne = struct.unpack_from("<ii", data, i + 4)
        out.append((ident, data[i + 12:i + 12 + nc], (i + 12 + nc, i + 12 + nc + ne)))
        i += 12 + nc + ne
    return out


def exemple():
    m = vox.Modele(5, 3, 4, nom="essai")
    m.boite(0, 0, 0, 4, 0, 3, 14)
    m[1, 1, 2] = 23
    m[4, 2, 3] = 32
    m[0, 2, 0] = 1
    return m


class TestModele(unittest.TestCase):
    def test_acces_et_erreurs(self):
        m = vox.Modele(3, 4, 5)
        m[2, 3, 4] = 32
        self.assertEqual((m[2, 3, 4], m[0, 0, 0], m.lire(-1, 0, 0), m.lire(3, 0, 0)), (32, 0, 0, 0))
        self.assertEqual(m.donnees[2 + 3 * (3 + 4 * 4)], 32)  # x + lx × (y + ly × z)
        with self.assertRaises(IndexError):
            m[3, 0, 0] = 1
        with self.assertRaises(vox.ErreurVox):
            m[0, 0, 0] = 33
        with self.assertRaises(vox.ErreurVox):
            m[0, 0, 0] = True
        with self.assertRaises(TypeError):
            m[0.5, 0, 0] = 1
        for t in ((0, 1, 1), (257, 1, 1), (1.0, 1, 1)):
            with self.assertRaises(vox.ErreurVox):
                vox.Modele(*t)

    def test_boite(self):
        m = vox.Modele(4, 4, 4)
        m.boite(3, 2, 1, 1, 0, 2, 9)  # bornes dans le désordre, incluses
        self.assertEqual(m.compter(), 3 * 3 * 2)
        self.assertEqual({(x, y, z) for x, y, z, _ in m.voxels()},
                         {(x, y, z) for x in range(1, 4) for y in range(3) for z in (1, 2)})
        m.boite(1, 0, 1, 3, 2, 2, 0)
        self.assertEqual(m.compter(), 0)
        with self.assertRaises(IndexError):
            m.boite(0, 0, 0, 4, 0, 0, 1)

    def test_calques(self):
        m = vox.Modele(4, 2, 3)
        m.calques([["#.", " #"], """
            ab
              c
        """], {"#": 8, "a": 19, "b": 20, "c": 23}, x0=1)
        self.assertEqual(sorted(m.voxels()), [(1, 0, 0, 8), (1, 1, 0, 19), (2, 0, 1, 8), (2, 1, 0, 20), (3, 1, 1, 23)])
        with self.assertRaisesRegex(vox.ErreurVox, "« x » absent"):
            m.calques([["x"]], {"#": 1})
        with self.assertRaises(vox.ErreurVox):
            m.calques([["#"]], {"#": 40})

    def test_miroir_copier_symetrie(self):
        m = exemple()
        d = m.miroir_x("d")
        self.assertEqual(m, exemple(), "miroir_x ne doit pas toucher l'original")
        self.assertEqual((d[3, 1, 2], d[0, 2, 3], d[4, 2, 0], d.nom), (23, 32, 1, "d"))
        self.assertEqual(d.miroir_x(), m)
        c = m.copier()
        c[0, 0, 0] = 0
        self.assertEqual(m[0, 0, 0], 14)
        self.assertEqual(c.nom, "essai")
        s = vox.Modele(4, 1, 1)
        s[0, 0, 0], s[1, 0, 0] = 3, 4
        s.symetrie_x()
        self.assertEqual(list(s.donnees), [3, 4, 4, 3])


class TestRampes(unittest.TestCase):
    def test_table(self):
        self.assertEqual(sorted(i for r in vox.RAMPES for i in r), list(range(1, 33)))
        for i in range(1, 33):
            r = vox.rampe(i)
            self.assertEqual(r["face"], i)
            meme = next(x for x in vox.RAMPES if i in x)
            self.assertTrue(set(r.values()) <= set(meme), (i, r))
            self.assertLessEqual(r["dessous"], r["cote"])
            self.assertLessEqual(r["cote"], min(r["face"], r["dessus"]))
            self.assertNotEqual(r["dessus"], r["face"], i)
            self.assertIn(vox.plus_sombre(i), meme)
        self.assertEqual(vox.rampe(8), {"dessus": 7, "face": 8, "cote": 6, "dessous": 5})      # crème des scènes 3D
        self.assertEqual(vox.rampe(19), {"dessus": 20, "face": 19, "cote": 18, "dessous": 17})  # or
        self.assertEqual((vox.plus_sombre(9), vox.plus_sombre(12)), (9, 11))
        with self.assertRaises(vox.ErreurVox):
            vox.rampe(0)


class TestFichierVox(unittest.TestCase):
    def setUp(self):
        self.d = tempfile.TemporaryDirectory()
        self.addCleanup(self.d.cleanup)
        self.f = os.path.join(self.d.name, "x.vox")

    def test_aller_retour(self):
        a = exemple()
        b = vox.Modele(1, 7, 2, nom="tige").boite(0, 0, 0, 0, 6, 1, 26)
        c = vox.Modele(2, 2, 2)  # vide et sans nom
        vox.ecrire_vox(self.f, [a, b, c])
        l = vox.lire_vox(self.f)
        self.assertEqual(l, [a, b, c])
        self.assertEqual([m.nom for m in l], ["essai", "tige", ""])
        vox.ecrire_vox(self.f, a)  # un seul modèle
        self.assertEqual(vox.lire_vox(self.f), [a])

    def test_entete_chunks_et_axes(self):
        a = exemple()
        vox.ecrire_vox(self.f, [a, a.miroir_x("m")])
        data = lire(self.f)
        self.assertEqual(vox.lire_entete(data), (b"VOX ", 150))
        racine = chunks(data, 8, len(data))
        self.assertEqual([c[0] for c in racine], [b"MAIN"])
        self.assertEqual(racine[0][2][1], len(data))
        ids = [c[0] for c in chunks(data, *racine[0][2])]
        self.assertEqual(ids, [b"SIZE", b"XYZI", b"SIZE", b"XYZI", b"nTRN", b"nGRP", b"nTRN", b"nSHP", b"nTRN",
                               b"nSHP", b"LAYR", b"RGBA"])
        enfants = chunks(data, *racine[0][2])
        self.assertEqual(struct.unpack("<iii", enfants[0][1]), (5, 4, 3))  # SIZE = (lx, lz, ly) : z MagicaVoxel en haut
        xyzi = enfants[1][1]
        n = struct.unpack_from("<i", xyzi)[0]
        vs = {tuple(xyzi[4 + 4 * k:8 + 4 * k]) for k in range(n)}
        self.assertEqual(n, a.compter())
        self.assertIn((1, 4 - 1 - 2, 1, 23), vs)  # (x, lz − 1 − z, y, i)
        self.assertIn((4, 0, 2, 32), vs)

    def test_palette_rgba(self):
        vox.ecrire_vox(self.f, exemple())
        rgba = vox.lire_rgba(self.f)
        self.assertEqual(len(rgba), 256)
        self.assertEqual(rgba[:32], [c + (255,) for c in PAL])  # entrée k = index k + 1
        self.assertEqual(rgba[0], (0x0E, 0x0D, 0x18, 255))
        self.assertEqual(set(rgba[32:]), {(0, 0, 0, 255)})

    def test_refus(self):
        vox.ecrire_vox(self.f, exemple())
        data = bytearray(lire(self.f))
        i = data.index(b"XYZI") + 12 + 4 + 3
        data[i] = 40  # index hors palette
        ecrire(self.f, data)
        with self.assertRaisesRegex(vox.ErreurVox, "index 40 hors ico-pixel-32"):
            vox.lire_vox(self.f)
        ecrire(self.f, b"PNG " + bytes(20))
        with self.assertRaisesRegex(vox.ErreurVox, "pas un fichier .vox"):
            vox.lire_vox(self.f)
        with self.assertRaises(vox.ErreurVox):
            vox.ecrire_vox(self.f, [])


class TestImages(unittest.TestCase):
    def test_palette_magicavoxel_et_asset(self):
        with tempfile.TemporaryDirectory() as d:
            f = vox.palette_magicavoxel(os.path.join(d, "p.png"))
            w, h, px = png.lire(f)
            self.assertEqual((w, h), (256, 1))
            self.assertEqual(px[:32], [c + (255,) for c in PAL])
            self.assertEqual(set(px[32:]), {(0, 0, 0, 255)})
            asset = chemins.dans_racine("assets", "3d", "palette", "ico-pixel-32-magicavoxel.png")
            self.assertEqual(lire(asset), lire(f), "asset à régénérer : vox.py palette …")

    def test_apercus(self):
        m = exemple()
        with tempfile.TemporaryDirectory() as d:
            for vue in vox.VUES:
                a, b = os.path.join(d, vue + "a.png"), os.path.join(d, vue + "b.png")
                vox.apercu(a, m, vue=vue, taille=2)
                vox.apercu(b, m, vue=vue, taille=2)
                self.assertEqual(lire(a), lire(b))
                w, h, px = png.lire(a)
                self.assertTrue({p[3] for p in px} <= {0, 255})
                opaques = {p[:3] for p in px if p[3]}
                self.assertTrue(opaques and opaques <= PALETTE, (vue, opaques - PALETTE))
                r = verifier_pixels.analyser(w, h, px, 1, PALETTE)
                self.assertFalse(r["hors"], r)
            w, h, px = png.lire(os.path.join(d, "facea.png"))
            self.assertEqual((w, h), (5 * 4, 3 * 4))
            un = vox.Modele(1, 1, 1)
            un[0, 0, 0] = 19
            vox.apercu(os.path.join(d, "un.png"), un, taille=2)
            w, h, px = png.lire(os.path.join(d, "un.png"))
            self.assertEqual((w, h), (8, 8))
            r = vox.rampe(19)
            self.assertEqual({p[:3] for p in px if p[3]}, {PAL[r[k] - 1] for k in ("dessus", "face", "cote")})
            with self.assertRaises(vox.ErreurVox):
                vox.apercu(os.path.join(d, "x.png"), un, vue="profil")

    def test_ligne_de_commande(self):
        with tempfile.TemporaryDirectory() as d:
            f = os.path.join(d, "x.vox")
            vox.ecrire_vox(f, exemple())
            out, err = io.StringIO(), io.StringIO()
            with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
                self.assertEqual(vox.main(["apercu", f, os.path.join(d, "a.png"), "--modele", "essai"]), 0)
                self.assertEqual(vox.main(["info", f]), 0)
                self.assertEqual(vox.main(["apercu", f, os.path.join(d, "a.png"), "--modele", "autre"]), 1)
                self.assertEqual(vox.main(["info", os.path.join(d, "absent.vox")]), 1)
            self.assertIn("0 essai : 5×3×4, 23 voxel(s), couleurs [1, 14, 23, 32]", out.getvalue())
            self.assertIn("« autre » absent", err.getvalue())


class TestDemo(unittest.TestCase):
    def test_fabriquer(self):
        with tempfile.TemporaryDirectory() as d:
            voxel_demo.fabriquer(d)
            self.assertEqual(sorted(os.listdir(d)), ["voxel_demo.apercu.png", "voxel_demo.caisse.png",
                                                     "voxel_demo.rig.toml", "voxel_demo.vox"])
            ms = vox.lire_vox(os.path.join(d, "voxel_demo.vox"))
            self.assertEqual([m.nom for m in ms], ["corps", "tete", "bras_d", "bras_g", "jambe_d", "jambe_g"])
            with open(os.path.join(d, "voxel_demo.rig.toml"), "rb") as f:
                rig = tomllib.load(f)
            self.assertEqual(set(rig["parties"]), {m.nom for m in ms})
            self.assertTrue(all(p.get("parent", "corps") in rig["parties"] for p in rig["parties"].values()))
            self.assertEqual(ms[3], ms[2].miroir_x())  # bras_g = miroir de bras_d
            for m, (_, _, o, _, _) in zip(ms, voxel_demo.PARTIES):  # chaque partie tient dans la grille 10 × 17 × 8
                self.assertTrue(all(0 <= o[k] and o[k] + m.taille[k] <= (10, 17, 8)[k] for k in range(3)), m)


if __name__ == "__main__":
    unittest.main()
