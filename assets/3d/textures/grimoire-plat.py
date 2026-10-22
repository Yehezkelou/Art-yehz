#!/usr/bin/env python3
"""ico-vid : texture 16 × 16 du plat du grimoire (dessin maison, modélisé par Claude, palette ico-pixel-32).

    python3 -I assets/3d/textures/grimoire-plat.py          # → grimoire-plat.png (à côté de ce script)

Motif : la rune ico-vid « 1 dans 0 » (un 1 à empattements qui traverse un 0 ovale), en or 19 avec un éclat 20 en
haut à gauche, un ombré 18 en bas à droite et une ombre portée 29 ; fond de cuir violet 30 à grain 29, bord 29,
couture pointillée 31 et quatre clous 31. Le haut de l'image est le côté du dos opposé au lecteur (fond du livre).
"""
import os, sys

ICI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(ICI, "..", "..", "..", "outils"))
import vox  # noqa: E402

FOND, GRAIN_, COUTURE, OR, ECLAT, OMBRE = 30, 29, 31, 19, 20, 18
GRAIN = {(3, 2), (11, 2), (13, 12), (4, 12), (12, 13), (13, 4), (13, 8)}   # grain 29 du cuir


def rune():
    """Cases de la rune : le 0 (anneau ovale) et le 1 (barre de 2, drapeau, socle)."""
    zero = {(x, 4) for x in range(5, 11)} | {(x, 11) for x in range(5, 11)}
    zero |= {(4, 5), (11, 5), (4, 10), (11, 10)}
    zero |= {(x, y) for y in range(6, 10) for x in (3, 12)}
    un = {(x, y) for y in range(2, 14) for x in (7, 8)} | {(6, 3)} | {(x, 13) for x in range(5, 11)}
    return zero, un


def grille():
    """16 × 16 index de palette (ligne 0 = haut de l'image)."""
    g = [[FOND] * 16 for _ in range(16)]
    for k in range(16):                                  # bord
        g[0][k] = g[15][k] = g[k][0] = g[k][15] = GRAIN_
    for k in range(2, 14, 2):                            # couture pointillée
        g[1][k] = g[14][k] = g[k][1] = g[k][14] = COUTURE
    for x, y in ((1, 1), (14, 1), (1, 14), (14, 14)):    # clous
        g[y][x] = COUTURE
    for x, y in GRAIN:
        g[y][x] = GRAIN_
    zero, un = rune()
    tout = zero | un
    dedans = {(x, y) for y in range(5, 11) for x in range(4, 12)
              if min(a for a, b in zero if b == y) < x < max(a for a, b in zero if b == y)}
    for x, y in tout:                                    # ombre portée (pas dans le creux du 0)
        if (x + 1, y + 1) not in tout and (x + 1, y + 1) not in dedans:
            g[y + 1][x + 1] = GRAIN_
    for x, y in tout:
        c = OR
        if (x, y) in zero and x < 7.5 and y < 7.5:
            c = ECLAT
        elif (x, y) in zero and x > 7.5 and y > 7.5:
            c = OMBRE
        elif (x, y) in un and x == 7:
            c = ECLAT
        g[y][x] = c
    return g


def pixels():
    pal = vox.lire_palette()
    return [pal[i - 1] + (255,) for ligne in grille() for i in ligne]


if __name__ == "__main__":
    sortie = os.path.join(ICI, "grimoire-plat.png")
    vox.ecrire_png(sortie, 16, 16, pixels())
    car = {30: ".", 29: "b", 31: "c", 19: "g", 20: "h", 18: "o"}
    for ligne in grille():
        print("".join(car[i] for i in ligne))
    print(sortie)
