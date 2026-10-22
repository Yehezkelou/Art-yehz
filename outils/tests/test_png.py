"""Tests de png.py :  python3 -I -m unittest discover -s ~/videos/outils/tests"""
import os, struct, sys, tempfile, unittest, zlib

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
import png  # noqa: E402


def _morceau(typ, data):
    return struct.pack(">I", len(data)) + typ + data + struct.pack(">I", zlib.crc32(typ + data))


def _paeth(a, b, c):
    p = a + b - c
    pa, pb, pc = abs(p - a), abs(p - b), abs(p - c)
    return a if pa <= pb and pa <= pc else (b if pb <= pc else c)


def _filtrer(ligne, prec, bpp, f):
    out = bytearray([f])
    for x, v in enumerate(ligne):
        a = ligne[x - bpp] if x >= bpp else 0
        b = prec[x]
        c = prec[x - bpp] if x >= bpp else 0
        pred = [0, a, b, (a + b) >> 1, _paeth(a, b, c)][f]
        out.append((v - pred) & 0xFF)
    return out


def fabriquer(largeur, hauteur, lignes, typ=6, palette=None, trns=None, filtres=(0,)):
    """PNG 8 bits à partir de lignes d'octets bruts ; la ligne y utilise filtres[y % len]."""
    bpp = png.CANAUX[typ]
    brut, prec = bytearray(), bytes(largeur * bpp)
    for y, ligne in enumerate(lignes):
        brut += _filtrer(bytes(ligne), prec, bpp, filtres[y % len(filtres)])
        prec = bytes(ligne)
    data = png.SIGNATURE + _morceau(b"IHDR", struct.pack(">IIBBBBB", largeur, hauteur, 8, typ, 0, 0, 0))
    if palette:
        data += _morceau(b"PLTE", bytes(c for rgb in palette for c in rgb))
    if trns is not None:
        data += _morceau(b"tRNS", bytes(trns))
    return data + _morceau(b"IDAT", zlib.compress(bytes(brut))) + _morceau(b"IEND", b"")


def rgba(largeur, hauteur, pixels, filtres=(0,)):
    """PNG RGBA à partir d'une liste de (r, g, b, a)."""
    lignes = [bytes(c for p in pixels[y * largeur:(y + 1) * largeur] for c in p) for y in range(hauteur)]
    return fabriquer(largeur, hauteur, lignes, 6, filtres=filtres)


class Test(unittest.TestCase):
    PX = [((x * 37 + y * 11) % 256, (x * y * 5) % 256, (200 - x * 3) % 256, (y * 60) % 256)
          for y in range(5) for x in range(7)]

    def test_rgba_tous_les_filtres(self):
        for f in range(5):
            w, h, px = png.decoder(rgba(7, 5, self.PX, filtres=(f,)))
            self.assertEqual((w, h, px), (7, 5, self.PX), f"filtre {f}")

    def test_filtres_melanges(self):
        self.assertEqual(png.decoder(rgba(7, 5, self.PX, filtres=(4, 3, 1, 2, 0)))[2], self.PX)

    def test_rgb_et_trns(self):
        lignes = [bytes([10, 20, 30, 1, 2, 3]), bytes([1, 2, 3, 255, 255, 255])]
        _, _, px = png.decoder(fabriquer(2, 2, lignes, 2, trns=struct.pack(">HHH", 1, 2, 3), filtres=(1, 4)))
        self.assertEqual(px, [(10, 20, 30, 255), (1, 2, 3, 0), (1, 2, 3, 0), (255, 255, 255, 255)])

    def test_indexe_avec_trns(self):
        pal = [(0, 0, 0), (229, 83, 61), (63, 181, 107)]
        lignes = [bytes([0, 1, 2]), bytes([2, 2, 1])]
        _, _, px = png.decoder(fabriquer(3, 2, lignes, 3, palette=pal, trns=[0], filtres=(2,)))
        self.assertEqual(px, [(0, 0, 0, 0), (229, 83, 61, 255), (63, 181, 107, 255),
                              (63, 181, 107, 255), (63, 181, 107, 255), (229, 83, 61, 255)])

    def test_gris(self):
        _, _, px = png.decoder(fabriquer(2, 1, [bytes([7, 200])], 0))
        self.assertEqual(px, [(7, 7, 7, 255), (200, 200, 200, 255)])

    def test_lire_fichier(self):
        with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as f:
            f.write(rgba(7, 5, self.PX))
        try:
            self.assertEqual(png.lire(f.name)[2], self.PX)
        finally:
            os.unlink(f.name)

    def test_erreurs(self):
        with self.assertRaises(png.ErreurPNG):
            png.decoder(b"pas un png")
        bon = rgba(2, 2, [(1, 2, 3, 255)] * 4)
        with self.assertRaises(png.ErreurPNG):
            png.decoder(bon[:-20])                        # tronqué
        seize = bon[:24] + b"\x10" + bon[25:]            # profondeur 16 bits
        with self.assertRaises(png.ErreurPNG):
            png.decoder(seize)


if __name__ == "__main__":
    unittest.main()
