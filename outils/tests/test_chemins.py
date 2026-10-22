"""Tests de chemins.py :  python -I -m unittest discover -s outils/tests"""
import os, subprocess, sys, tempfile, unittest

ICI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(ICI, ".."))
import chemins  # noqa: E402

RACINE_ATTENDUE = os.path.dirname(os.path.dirname(ICI))


class Racine(unittest.TestCase):
    def test_racine_deduite_du_script(self):
        r = chemins.racine(env={})
        self.assertEqual(r, RACINE_ATTENDUE)
        self.assertTrue(os.path.isfile(os.path.join(r, "assets", "manifeste.toml")))
        self.assertTrue(os.path.isfile(os.path.join(r, "bible", "palette", "ico-pixel-32.hex")))

    def test_surcharge_ico_videos(self):
        with tempfile.TemporaryDirectory() as d:
            self.assertEqual(chemins.racine(env={"ICO_VIDEOS": d}), os.path.abspath(d))
            self.assertEqual(chemins.dans_racine("assets", env={"ICO_VIDEOS": d}), os.path.join(os.path.abspath(d), "assets"))

    def test_outils_utilisent_la_racine(self):
        import verifier_licences, verifier_pixels
        self.assertEqual(verifier_licences.RACINE, os.path.join(RACINE_ATTENDUE, "assets"))
        self.assertTrue(os.path.isfile(verifier_pixels.PALETTE))


class EffectCraft(unittest.TestCase):
    def test_exe_sous_windows(self):
        self.assertTrue(chemins.effectcraft_cli(env={}, nt=True).endswith("effectcraft-cli.exe"))
        self.assertTrue(chemins.effectcraft_cli(env={}, nt=False).endswith("effectcraft-cli"))
        p = chemins.effectcraft_cli(env={})
        self.assertTrue(os.path.isabs(p))
        self.assertIn(os.path.join("dev", "vid", "effectcraft", "target", "release"), p)

    def test_surcharge_ico_effectcraft(self):
        with tempfile.TemporaryDirectory() as d:
            b = os.path.join(d, "ec")
            self.assertEqual(chemins.effectcraft_cli(env={"ICO_EFFECTCRAFT": b}), b)

    def test_presets_comme_effectcraft(self):
        self.assertEqual(chemins.presets_effectcraft(env={"EC_PRESETS_DIR": "X"}), "X")
        self.assertEqual(chemins.presets_effectcraft(env={"USERPROFILE": "U"}),
                         os.path.join("U", "Documents", "EffectCraft", "Presets"))
        self.assertEqual(chemins.presets_effectcraft(env={"HOME": "H", "USERPROFILE": "U"}),
                         os.path.join("H", "Documents", "EffectCraft", "Presets"))


class Bureau(unittest.TestCase):
    def test_surcharge_ico_bureau(self):
        with tempfile.TemporaryDirectory() as d:
            self.assertEqual(chemins.bureau(env={"ICO_BUREAU": d}), d)
            self.assertIsNone(chemins.bureau(env={"ICO_BUREAU": os.path.join(d, "absent")}))

    def test_windows_desktop_puis_onedrive(self):
        with tempfile.TemporaryDirectory() as prof:
            c = chemins.candidats_bureau(env={"USERPROFILE": prof}, nt=True)
            self.assertIn(os.path.join(prof, "Desktop"), c)
            self.assertIn(os.path.join(prof, "OneDrive", "Desktop"), c)
            self.assertLess(c.index(os.path.join(prof, "Desktop")), c.index(os.path.join(prof, "OneDrive", "Desktop")))

    def test_wsl_un_seul_compte(self):
        with tempfile.TemporaryDirectory() as users:
            for d in ["Public/Desktop", "Default/Desktop", "toto/OneDrive/Desktop", "toto/Desktop"]:
                os.makedirs(os.path.join(users, d))
            self.assertEqual(chemins.bureau(env={}, nt=False, users_dir=users),
                             os.path.join(users, "toto", "OneDrive", "Desktop"))
            os.makedirs(os.path.join(users, "titi", "Desktop"))
            self.assertIsNone(chemins.bureau(env={}, nt=False, users_dir=users))  # deux comptes : pas de devinette

    def test_wsl_aucun_compte(self):
        with tempfile.TemporaryDirectory() as users:
            self.assertIsNone(chemins.bureau(env={}, nt=False, users_dir=os.path.join(users, "absent")))


class LigneDeCommande(unittest.TestCase):
    def test_affichage(self):
        r = subprocess.run([sys.executable, "-I", os.path.join(ICI, "..", "chemins.py")],
                           capture_output=True, text=True, encoding="utf-8")
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn('"racine"', r.stdout)

    def test_pilote_agy_liste(self):
        r = subprocess.run([sys.executable, "-I", os.path.join(ICI, "..", "pilote_agy.py"), "--liste"],
                           capture_output=True, text=True, encoding="utf-8")
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn('"dossier_usine"', r.stdout)


if __name__ == "__main__":
    unittest.main()
