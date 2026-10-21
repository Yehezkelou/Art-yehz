"""Tests de verifier_licences.py :  python3 -I -m unittest discover -s ~/videos/outils/tests"""
import json, os, sys, tempfile, unittest

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
import verifier_licences as vl  # noqa: E402

PROPRIO = 'fichier = "persos/tim.png"\nlicence = "propriétaire"\nvendable = true\n'


class Test(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.racine = os.path.join(self.tmp.name, "assets")
        os.makedirs(os.path.join(self.racine, "persos"))
        open(os.path.join(self.racine, "persos/tim.png"), "w").close()

    def tearDown(self):
        self.tmp.cleanup()

    def verifier(self, *entrees, projets=()):
        with open(os.path.join(self.racine, "manifeste.toml"), "w", encoding="utf-8") as f:
            f.write("".join("[[asset]]\n" + e for e in entrees))
        return vl.verifier(self.racine, projets=projets)[0]

    def ajouter(self, rel):
        open(os.path.join(self.racine, rel), "w").close()

    def test_vert(self):
        self.assertEqual(self.verifier(PROPRIO), [])

    def test_fichier_sans_entree(self):
        self.ajouter("persos/chat.png")
        self.assertIn("persos/chat.png : fichier sans entrée dans le manifeste", self.verifier(PROPRIO))

    def test_entree_sans_fichier(self):
        err = self.verifier(PROPRIO, 'fichier = "persos/absent.png"\nlicence = "CC0"\n')
        self.assertIn("persos/absent.png : fichier absent du disque", err)

    def test_nc_refuse(self):
        self.ajouter("persos/nc.png")
        err = self.verifier(PROPRIO, 'fichier = "persos/nc.png"\nlicence = "CC-BY-NC-4.0"\ncredit = "x"\n')
        self.assertTrue(any("non commerciale" in e for e in err), err)

    def test_ccby_sans_credit(self):
        self.ajouter("persos/by.png")
        err = self.verifier(PROPRIO, 'fichier = "persos/by.png"\nlicence = "CC-BY-4.0"\ncredit = ""\n')
        self.assertTrue(any("crédit obligatoire" in e for e in err), err)

    def test_cc0_pas_vendable(self):
        self.ajouter("persos/cc0.png")
        err = self.verifier(PROPRIO, 'fichier = "persos/cc0.png"\nlicence = "CC0"\nvendable = true\n')
        self.assertTrue(any("vendable = true interdit" in e for e in err), err)

    def test_projet_media_sans_entree(self):
        self.ajouter("persos/chat.png")
        projet = os.path.join(self.tmp.name, "ep.ecproj")
        items = {"1": {"id": 1, "kind": {"type": "Footage", "path": "assets/persos/chat.png"}},
                 "2": {"id": 2, "kind": {"type": "Footage", "path": "assets/persos/tim.png"}}}
        with open(projet, "w") as f:
            json.dump({"items": items}, f)
        err = self.verifier(PROPRIO, projets=[projet])
        self.assertIn("ep.ecproj utilise persos/chat.png sans entrée valide au manifeste", err)
        self.assertFalse(any("tim.png sans entrée" in e for e in err))


if __name__ == "__main__":
    unittest.main()
