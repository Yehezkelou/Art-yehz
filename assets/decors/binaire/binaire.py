#!/usr/bin/env python3
"""ico-vid : décors et objets de pixel-03-binaire, dessinés par Claude (palette ico-pixel-32).

    python3 -I assets/decors/binaire/binaire.py     # écrit les PNG à côté de ce fichier

Décors 270×480 (comp pixel ; sol à y = 408 comme le modèle ; bande des sous-titres y 316–370 laissée
calme) : boutique.png, atelier.png, classe.png, circuit.png, ecrans.png (1080×480, 4 écrans à traverser).
Objets (fond transparent) : objets-*.png, un objet par fichier (tarte, ciseaux, loupe, fleche, question,
infini, tampon). Pixels entiers, aucune semi-transparence, aucun dégradé (tramage en damier seulement).
"""
import os, struct, zlib

ICI = os.path.dirname(os.path.abspath(__file__))
HEX = ("0E0D18 1D1B2E 2F2C45 4A4663 6E6A80 9A96A6 C9C4C8 F2EDE4 1F2E5C 3E5BA9 5E8FD6 9CC7F0 "
       "1E4D3A 2E7D4F 3FB56B 8FDB86 7A4E1E B9802B F4C542 FBE58C 5A1E2B 9E2F33 E5533D F59A7A "
       "3B2A22 6B4A35 9C7451 C9A57A 3D2550 6B3F87 A066B8 E0A6D9").split()
P = [None] + [tuple(int(h[i:i + 2], 16) for i in (0, 2, 4)) + (255,) for h in HEX]   # P[1..32]
VIDE = (0, 0, 0, 0)


class Toile:
    def __init__(self, l, h, fond=VIDE):
        self.l, self.h = l, h
        self.px = [fond] * (l * h)

    def pt(self, x, y, c):
        if 0 <= x < self.l and 0 <= y < self.h:
            self.px[y * self.l + x] = P[c] if isinstance(c, int) else c

    def rect(self, x0, y0, x1, y1, c):              # bornes incluses
        for y in range(max(0, y0), min(self.h, y1 + 1)):
            for x in range(max(0, x0), min(self.l, x1 + 1)):
                self.px[y * self.l + x] = P[c]

    def cadre(self, x0, y0, x1, y1, c):
        self.rect(x0, y0, x1, y0, c); self.rect(x0, y1, x1, y1, c)
        self.rect(x0, y0, x0, y1, c); self.rect(x1, y0, x1, y1, c)

    def damier(self, x0, y0, x1, y1, c1, c2):       # tramage 1 px
        for y in range(y0, y1 + 1):
            for x in range(x0, x1 + 1):
                self.pt(x, y, c1 if (x + y) % 2 else c2)

    def dessin(self, x0, y0, lignes, couleurs):
        for y, l in enumerate(lignes):
            for x, ch in enumerate(l):
                if ch != ".":
                    self.pt(x0 + x, y0 + y, couleurs[ch])

    def disque(self, cx, cy, r, c):
        for y in range(-r, r + 1):
            for x in range(-r, r + 1):
                if x * x + y * y <= r * r + r:
                    self.pt(cx + x, cy + y, c)

    def ecrire(self, nom):
        brut = b"".join(b"\x00" + bytes(v for p in self.px[y * self.l:(y + 1) * self.l] for v in p) for y in range(self.h))
        def m(t, d):
            return struct.pack(">I", len(d)) + t + d + struct.pack(">I", zlib.crc32(t + d) & 0xFFFFFFFF)
        with open(os.path.join(ICI, nom), "wb") as f:
            f.write(b"\x89PNG\r\n\x1a\n" + m(b"IHDR", struct.pack(">IIBBBBB", self.l, self.h, 8, 6, 0, 0, 0))
                    + m(b"IDAT", zlib.compress(brut, 9)) + m(b"IEND", b""))


SOL = 408


def plancher(t, x0=0, x1=None):
    x1 = t.l - 1 if x1 is None else x1
    t.rect(x0, SOL, x1, t.h - 1, 26)
    t.rect(x0, SOL, x1, SOL, 2)
    for y in range(SOL + 9, t.h, 10):
        t.rect(x0, y, x1, y, 25)
    for y in range(SOL + 1, t.h, 10):
        dec = (y // 10) * 23
        for x in range(x0 + dec % 40, x1 + 1, 40):
            t.rect(x, y, x, y + 8, 25)
    t.rect(x0, SOL + 1, x1, SOL + 1, 27)


def briques(t, y0, y1, fond, joint, eclat):
    t.rect(0, y0, t.l - 1, y1, fond)
    for y in range(y0, y1 + 1, 8):
        t.rect(0, y, t.l - 1, y, joint)
        dec = 8 if (y // 8) % 2 else 0
        for x in range(dec, t.l, 16):
            t.rect(x, y, x, min(y1, y + 7), joint)
            t.pt(x + 2, y + 2, eclat)


def boutique():
    t = Toile(270, 480)
    briques(t, 0, SOL - 1, 3, 2, 4)
    # deux étagères avec des fioles
    couleurs = [(11, 10), (23, 22), (15, 14), (31, 30), (19, 18)]
    for k, y in enumerate((150, 226)):
        t.rect(14, y, 255, y + 3, 27); t.rect(14, y + 4, 255, y + 5, 25); t.rect(14, y, 255, y, 28)
        for i, x in enumerate(range(22, 250, 18)):
            c, o = couleurs[(i + k * 2) % len(couleurs)]
            h = 10 + (i * 7 + k * 3) % 6
            t.rect(x + 2, y - h - 3, x + 4, y - h - 1, 27)              # bouchon
            t.cadre(x, y - h, x + 6, y - 1, 2)
            t.rect(x + 1, y - h + 1, x + 5, y - 2, c)
            t.rect(x + 4, y - h + 3, x + 5, y - 2, o)
            t.pt(x + 2, y - h + 2, 8)
    # lanterne accrochée
    for y in range(0, 52):
        t.pt(41, y, 2)
    t.dessin(36, 52, ["...KKKK...", "..KKKKKK..", ".KYYYYYYK.", "KYWWWWWWYK", "KYWWyyWWYK", "KYWyyyyWYK",
                      "KYWWyyWWYK", "KYWWWWWWYK", ".KYYYYYYK.", "..KKKKKK..", "...KKKK..."],
             {"K": 2, "Y": 18, "W": 20, "y": 19})
    # enseigne dorée au-dessus des étagères (sans texte)
    t.rect(150, 40, 250, 64, 26); t.cadre(150, 40, 250, 64, 2); t.rect(154, 44, 246, 60, 18)
    t.rect(158, 48, 242, 56, 19)
    t.disque(200, 52, 3, 23)
    plancher(t)
    t.ecrire("boutique.png")


def atelier():
    t = Toile(270, 480)
    t.rect(0, 0, 269, SOL - 1, 9)
    for x in range(0, 270, 12):                                         # papier peint à rayures
        t.rect(x, 0, x + 1, SOL - 1, 3)
    # fenêtre de nuit avec la lune
    t.rect(24, 70, 104, 170, 26); t.rect(28, 74, 100, 166, 1)
    t.damier(28, 74, 100, 120, 1, 2)
    t.disque(80, 96, 9, 8); t.disque(84, 93, 7, 1)
    for x, y in ((40, 84), (52, 130), (92, 150), (36, 150)):
        t.pt(x, y, 7)
    t.rect(64, 74, 64, 166, 26); t.rect(28, 120, 100, 120, 26)
    # étagère à livres
    t.rect(150, 100, 250, 103, 27); t.rect(150, 104, 250, 105, 25)
    for i, x in enumerate(range(154, 246, 7)):
        c = (22, 10, 14, 30, 18)[i % 5]
        h = 18 + (i * 5) % 7
        t.rect(x, 100 - h, x + 5, 99, c); t.cadre(x, 100 - h, x + 5, 99, 2); t.rect(x + 1, 100 - h + 3, x + 4, 100 - h + 3, 8)
    # bureau (plateau y 340) et ordinateur posé dessus : écran 80×46 (intérieur x 146–225, y 261–306)
    t.rect(100, 340, 262, 345, 27); t.rect(100, 340, 262, 340, 28); t.rect(100, 346, 262, 347, 25)
    t.rect(108, 348, 113, SOL - 1, 26); t.rect(249, 348, 254, SOL - 1, 26)
    t.rect(132, 247, 239, 320, 7); t.cadre(132, 247, 239, 320, 2); t.rect(134, 249, 237, 250, 8)
    t.rect(142, 257, 229, 310, 2); t.rect(146, 261, 225, 306, 1)
    t.rect(150, 313, 160, 315, 6); t.pt(228, 314, 15)
    t.rect(170, 321, 202, 333, 6); t.cadre(170, 321, 202, 333, 2)                     # pied
    t.rect(150, 334, 222, 339, 7); t.cadre(150, 334, 222, 339, 2)
    plancher(t)
    t.ecrire("atelier.png")


def classe():
    t = Toile(270, 480)
    t.rect(0, 0, 269, SOL - 1, 27)
    t.damier(0, 300, 269, SOL - 1, 27, 26)
    t.rect(0, 300, 269, 302, 26)
    # tableau noir (intérieur x 18–251, y 88–282)
    t.rect(10, 80, 259, 290, 26); t.cadre(10, 80, 259, 290, 2); t.rect(14, 84, 255, 286, 13)
    t.rect(18, 88, 251, 282, 13)
    for x, y in ((40, 100), (200, 120), (120, 260), (230, 250)):
        t.rect(x, y, x + 6, y, 14)
    t.rect(10, 291, 259, 294, 27); t.cadre(10, 291, 259, 294, 2)                      # rebord à craie
    t.rect(40, 289, 48, 290, 8); t.rect(60, 289, 64, 290, 19)
    plancher(t)
    t.ecrire("classe.png")


def circuit():
    t = Toile(270, 480)
    t.rect(0, 0, 269, 479, 13)
    for y in range(4, 480, 16):
        t.rect(0, y, 269, y, 14)
    for x in range(8, 270, 24):
        t.rect(x, 0, x, 479, 14)
    for i, (x, y) in enumerate(((20, 40), (180, 60), (60, 380), (200, 400), (110, 20), (30, 440))):
        t.rect(x, y, x + 34, y + 22, 2); t.cadre(x, y, x + 34, y + 22, 4)
        for k in range(x + 3, x + 33, 5):
            t.rect(k, y - 3, k + 1, y - 1, 6); t.rect(k, y + 23, k + 1, y + 25, 6)
        t.pt(x + 3, y + 3, 18 if i % 2 else 15)
    t.ecrire("circuit.png")


def ecrans():
    """4 écrans côte à côte sur un mur (1080×480), un par langage ; intérieur des écrans 180×70 à
    x = 45 + 270 k, y = 150. Les noms et le résultat sont écrits par le compositeur."""
    t = Toile(1080, 480)
    t.rect(0, 0, 1079, SOL - 1, 4)
    for x in range(0, 1080, 18):
        t.rect(x, 0, x, SOL - 1, 3)
    teintes = (10, 22, 18, 30)
    for k in range(4):
        x0 = 25 + 270 * k
        t.rect(x0, 130, x0 + 219, 239, teintes[k]); t.cadre(x0, 130, x0 + 219, 239, 2)
        t.rect(x0 + 2, 132, x0 + 217, 133, 8)
        t.rect(x0 + 16, 146, x0 + 203, 223, 2); t.rect(x0 + 20, 150, x0 + 199, 219, 1)
        t.rect(x0 + 90, 240, x0 + 129, 262, 6); t.cadre(x0 + 90, 240, x0 + 129, 262, 2)
        t.rect(x0 + 60, 263, x0 + 159, 268, 7); t.cadre(x0 + 60, 263, x0 + 159, 268, 2)
        t.rect(x0 + 10, 270, x0 + 209, 275, 27)
    plancher(t)
    t.ecrire("ecrans.png")


OBJETS = {
    "tarte": (["....KKKKKKKKKKKK....", "..KKYYYYYYYYYYYYKK..", ".KYYyYYYYyYYYYyYYYK.", "KYYYYYYyYYYYYYYyYYYK",
               "KYyYYYYYYYYyYYYYYYYK", "KKYYYYyYYYYYYYYyYYKK", "KRKKKKKKKKKKKKKKKKRK", "KRRRRRRRRRRRRRRRRRRK",
               ".KRrRRRRrRRRRRrRRRK.", "..KKKKKKKKKKKKKKKK.."],
              {"K": 2, "Y": 18, "y": 17, "R": 28, "r": 27}),
    "ciseaux": (["KK..........KK", "KWK........KWK", ".KWK......KWK.", "..KWK....KWK..", "...KWK..KWK...",
                 "....KWKKWK....", ".....KWWK.....", ".....KKKK.....", "....KRKKRK....", "...KRRK.KRRK..",
                 "..KR..K.K..RK.", "..KR..K.K..RK.", "...KRRK..KRRK.", "....KK....KK.."],
                {"K": 2, "W": 7, "R": 23}),
    "loupe": (["....KKKKKK.....", "..KKBBBBBBKK...", ".KBBWBBBBBBBK..", ".KBWBBBBBBBBK..", "KBBBBBBBBBBBBK.",
               "KBBBBBBBBBBBBK.", "KBBBBBBBBBBBBK.", "KBBBBBBBBBBBBK.", ".KBBBBBBBBBBK..", ".KBBBBBBBBBBK..",
               "..KKBBBBBBKKK..", "....KKKKKKKOOK.", "...........KOOK", "............KOK", ".............K."],
              {"K": 2, "B": 12, "W": 8, "O": 26}),
    "fleche": (["....KK....", "...KWWK...", "..KWWWWK..", ".KWWWWWWK.", "KWWWWWWWWK", "KKKWWWWKKK",
                "..KWWWWK..", "..KWWWWK..", "..KWWWWK..", "..KWWWWK..", "..KKKKKK.."],
               {"K": 2, "W": 8}),
    "question": ([".KKKKK.", "KWWWWWK", "KWKKKWK", "KKK.KWK", "...KWWK", "..KWWK.", "..KWK..", "..KKK..",
                  "..KKK..", "..KWK..", "..KKK.."],
                 {"K": 2, "W": 8}),
    "infini": ([".KKK...KKK.", "KWWWK.KWWWK", "KW.KWKWK.WK", "KW..KWK..WK", "KW.KWKWK.WK", "KWWWK.KWWWK",
                ".KKK...KKK."],
               {"K": 2, "W": 19}),
    "tampon": (["....KKKKKK....", "...KRRRRRRK...", "...KRrRRRRK...", "....KKRRKK....", ".....KRRK.....",
                "..KKKKRRKKKK..", ".KRRRRRRRRRRK.", "KRRrRRRRRRrRRK", "KKKKKKKKKKKKKK"],
               {"K": 2, "R": 22, "r": 21}),
}


def objets():
    for nom, (lignes, c) in OBJETS.items():
        assert len(set(map(len, lignes))) == 1, nom
        t = Toile(len(lignes[0]), len(lignes))
        t.dessin(0, 0, lignes, c)
        t.ecrire(f"objet-{nom}.png")


if __name__ == "__main__":
    boutique(); atelier(); classe(); circuit(); ecrans(); objets()
    print("décors : boutique, atelier, classe, circuit, ecrans ; objets :", ", ".join(OBJETS))
