#!/usr/bin/env python3
"""Ciel couchant ico-vid en cartes pixel superposées (parallaxe), dessiné par script (palette ico-pixel-32).

    python3 -I assets/3d/ciels/couchant/couchant.py              # → les 5 cartes PNG à côté de ce script
    python3 -I assets/3d/ciels/couchant/couchant.py --sortie <dossier>

Cartes (du fond vers l'avant), toutes de 480 px de haut ; profondeurs et glissement dans couchant.toml :
  1. fond.png          270×480  bandes 1 → 29 → 30 → 31 → 22 → 23 → 18 → 19 → 20, bords en marches d'escalier (opaque)
  2. soleil.png        360×480  soleil carré 20, cœur 8, cadre 19 ; deux traits de lumière (le reste transparent)
  3. nuages-hauts.png  360×480  traînées violettes 30 (dessus 31, dessous 29) en marches
  4. nuages-bas.png    360×480  nuages rouge-orangé 22 (dessus 23 / 24, dessous 21) près de l'horizon
  5. mer.png           360×480  mer de nuages en bas : 3 rangs de bosses (31/30, 30/29, 29/1) (opaque en bas)
Transparence tout-ou-rien (alpha 0 ou 255), aucune couleur hors palette, tirages au hasard à graine fixe.
"""
import argparse, os, random, sys

ICI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(ICI, "..", "..", "..", "..", "outils"))
import vox  # noqa: E402

H = 480
L_FOND, L_LARGE = 270, 360


class Carte:
    def __init__(self, l, h=H):
        self.l, self.h = l, h
        self.p = [0] * (l * h)

    def get(self, x, y):
        return self.p[x + self.l * y] if 0 <= x < self.l and 0 <= y < self.h else 0

    def set(self, x, y, i):
        if 0 <= x < self.l and 0 <= y < self.h:
            self.p[x + self.l * y] = i

    def rect(self, x0, y0, x1, y1, i):  # bornes incluses
        for y in range(max(0, y0), min(self.h, y1 + 1)):
            for x in range(max(0, x0), min(self.l, x1 + 1)):
                self.p[x + self.l * y] = i

    def png(self, chemin, pal):
        px = [(0, 0, 0, 0) if i == 0 else pal[i - 1] + (255,) for i in self.p]
        return vox.ecrire_png(chemin, self.l, self.h, px)


def marches(rng, l, base, amp=4, pas=(8, 12, 16, 20)):
    """Profil en marches d'escalier : hauteur par colonne, paliers de largeur multiple de 4, sauts de 2 px."""
    prof, x, y = [], 0, base
    while x < l:
        w = rng.choice(pas)
        prof += [y] * w
        x += w
        y = max(base - amp, min(base + amp, y + rng.choice((-2, 2))))
    return prof[:l]


def fond(pal_l):
    rng = random.Random(1)
    c = Carte(pal_l)
    # (couleur, bas de la bande) du haut vers l'horizon ; sous l'horizon : 20 (cachée par la mer de nuages)
    bandes = [(1, 56), (29, 104), (30, 150), (31, 190), (22, 226), (23, 258), (18, 286), (19, 310), (20, H)]
    haut = [0] * c.l
    for coul, bas in bandes:
        prof = marches(rng, c.l, bas, amp=4) if bas < H else [H] * c.l
        for x in range(c.l):
            for y in range(haut[x], prof[x]):
                c.set(x, y, coul)
        haut = prof
    # quelques étoiles dans le haut (crème et lilas), 1 px
    for _ in range(26):
        x, y = rng.randrange(c.l), rng.randrange(4, 96)
        c.set(x, y, 8 if y < 50 else 32)
    for x, y in ((40, 22), (212, 34)):  # deux étoiles en croix
        for dx, dy in ((0, 0), (1, 0), (-1, 0), (0, 1), (0, -1)):
            c.set(x + dx, y + dy, 8)
    return c


def soleil():
    c = Carte(L_LARGE)
    cx, cy = 244, 76           # centre : haut à droite, au-dessus du toit en plan large
    for r, coul in ((22, 19), (18, 20), (11, 8)):
        c.rect(cx - r, cy - r, cx + r - 1, cy + r - 1, coul)
    # coins du cadre en marches (soleil « arrondi » au pixel)
    for dx, dy in ((0, 0), (1, 0), (0, 1)):
        for sx, sy in ((-22, -22), (21, -22), (-22, 21), (21, 21)):
            x = cx + sx + (dx if sx < 0 else -dx)
            y = cy + sy + (dy if sy < 0 else -dy)
            c.set(x, y, 0)
    # traits de lumière horizontaux (2 px) de part et d'autre
    for y, x0, x1 in ((cy - 4, cx - 60, cx - 28), (cy + 6, cx + 28, cx + 72), (cy + 12, cx - 50, cx - 30)):
        c.rect(x0, y, x1, y + 1, 20)
    return c


def nuage(c, rng, x, y, tiers, corps, dessus, dessous, dessus2=None, centre=False):
    """Nuage en marches : tiers = [(largeur, hauteur)] du bas vers le haut, décalages multiples de 4.
    (x, y) = coin bas-gauche du premier palier. Arête du haut 2 px plus claire (et 2 px dessus2), arête du bas
    2 px dessous (le ventre éclairé par le soleil bas)."""
    masque = set()
    gx, gy = x, y
    for k, (w, h) in enumerate(tiers):
        if k:
            marge = max(0, (tiers[k - 1][0] - w) // 4)
            if centre:
                gx += 4 * max(0, min(marge, marge // 2 + rng.randint(-1, 1)))
            else:
                gx += 4 * rng.randint(0, marge)
        for yy in range(gy - h + 1, gy + 1):
            for xx in range(gx, gx + w):
                masque.add((xx, yy))
        gy -= h
    for (xx, yy) in masque:
        if (xx, yy - 1) not in masque or (xx, yy - 2) not in masque:
            i = dessus
        elif dessus2 and ((xx, yy - 3) not in masque or (xx, yy - 4) not in masque):
            i = dessus2
        elif dessous and ((xx, yy + 1) not in masque or (xx, yy + 2) not in masque):
            i = dessous
        else:
            i = corps
        c.set(xx, yy, i)


def nuages_hauts():
    rng = random.Random(3)
    c = Carte(L_LARGE)
    for x, y, w in ((-8, 74, 112), (168, 58, 92), (252, 112, 124), (36, 140, 88), (176, 170, 100),
                    (-24, 204, 76), (96, 222, 64)):
        tiers = [(w, 6), (w - 20 - 4 * rng.randint(0, 3), 6), (w // 2, 4)]
        if w > 90:
            tiers.append((w // 4, 4))
        nuage(c, rng, x, y, tiers, 30, 31, 23, centre=True)
    return c


def nuages_bas():
    rng = random.Random(5)
    c = Carte(L_LARGE)
    for x, y, w in ((-12, 248, 96), (104, 236, 64), (176, 286, 84), (272, 252, 100), (28, 304, 72), (300, 312, 72)):
        tiers = [(w, 6), (w - 16 - 4 * rng.randint(0, 2), 6), (w // 2, 6), (w // 4, 4)]
        nuage(c, rng, x, y, tiers, 22, 24, 21, dessus2=23, centre=True)
    return c


def mer():
    rng = random.Random(7)
    c = Carte(L_LARGE)
    # 3 rangs de bosses en marches, du fond (haut, clair) vers l'avant (bas, sombre) ; chaque bosse descend jusqu'en bas
    for base, corps, dessus, dessus2, w in ((336, 31, 32, None, 60), (380, 30, 32, 31, 84), (428, 29, 31, 30, 108)):
        x = -4 * rng.randint(4, 8)
        while x < c.l:
            ww = w + 4 * rng.randint(-3, 3)
            b = base + 4 * rng.randint(-2, 2)
            tiers = [(ww, H - b), (ww - 8, 6), (ww - 16, 6), (ww - 28, 6), (ww - 44, 4), (max(8, ww - 64), 4)]
            nuage(c, rng, x, H - 1, tiers, corps, dessus, None, dessus2=dessus2, centre=True)
            x += ww - 4 * rng.randint(4, 7)
    return c


COUCHES = [  # (carte, profondeur) du fond vers l'avant ; profondeur 0 = à l'infini (fixe), 1 = au niveau du sujet
    ("fond", 0.0), ("soleil", 0.08), ("nuages-hauts", 0.22), ("nuages-bas", 0.42), ("mer", 0.75)]
GLISSEMENT = 60   # px par radian d'orbite pour une couche de profondeur 1


def ecrire_toml(chemin):
    l = ["# Ciel couchant ico-vid : cartes pixel en couches (écrit par couchant.py, ne pas retoucher à la main).",
         "# Composition : chaque carte, centrée en x, est décalée de round(-glissement × profondeur × angle) px",
         "# (angle d'orbite de la caméra en radians) puis posée sur les précédentes (alpha tout-ou-rien).",
         "# Le bord d'une carte de largeur L reste hors champ tant que |décalage| <= (L - 270) / 2.",
         'nom = "couchant"', f"largeur = {L_FOND}", f"hauteur = {H}", f"glissement = {GLISSEMENT}", ""]
    for nom, p in COUCHES:
        larg = L_FOND if nom == "fond" else L_LARGE
        l += ["[[couche]]", f'nom = "{nom}"', f'fichier = "{nom}.png"', f"largeur = {larg}", f"profondeur = {p}", ""]
    with open(chemin, "w", encoding="utf-8", newline="\n") as f:
        f.write("\n".join(l))
    return chemin


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--sortie", default=ICI)
    ap.add_argument("--apercu", type=int, default=2, help="échelle de apercu.png (0 = pas d'aperçu)")
    a = ap.parse_args(argv)
    ap_ = a.apercu
    pal = vox.lire_palette()
    cartes = (("fond", fond(L_FOND)), ("soleil", soleil()), ("nuages-hauts", nuages_hauts()),
              ("nuages-bas", nuages_bas()), ("mer", mer()))
    for nom, carte in cartes:
        print(carte.png(os.path.join(a.sortie, f"{nom}.png"), pal))
    print(ecrire_toml(os.path.join(a.sortie, "couchant.toml")))
    if ap_:
        # aperçu : les cartes empilées, centrées (glissement nul), agrandies × ap_
        comp = Carte(L_FOND)
        for _, carte in cartes:
            dx = (carte.l - L_FOND) // 2
            for y in range(H):
                for x in range(L_FOND):
                    i = carte.get(x + dx, y)
                    if i:
                        comp.set(x, y, i)
        big = Carte(L_FOND * ap_, H * ap_)
        for y in range(big.h):
            for x in range(big.l):
                big.p[x + big.l * y] = comp.get(x // ap_, y // ap_)
        print(big.png(os.path.join(a.sortie, "apercu.png"), pal))


if __name__ == "__main__":
    main()
