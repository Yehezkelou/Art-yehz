#!/usr/bin/env python3
"""pixel-01-sort : compose la scène « Le sort raté » en séquence PNG 270×480 à 12 i/s (144 images).

    python3 -I pixel-01-sort/.montage/composer.py     # écrit pixel-01-sort/.montage/scene/scene_0000.png …

Sprites : assets/persos/tim/tim-sort-planche.png (cases 32×32) et assets/objets/sort/sort-planche.png
(cases 16×16), dessinés par tim-sort.lua et sort.lua. Toutes les positions sont entières et calculées
image par image : la séquence est déjà « posée sur la grille ». Le fond, le sol, la lune, le titre et
les sous-titres restent ceux du modèle pixel (EffectCraft) ; la séquence est transparente.
Instants (script validé, pixel-01-sort/validations.md) : charge 0,6 s · lancer 4,8 s · poule 6,2 s.
"""
import math, os, struct, sys, zlib

ICI = os.path.dirname(os.path.abspath(__file__))
RACINE = os.path.normpath(os.path.join(ICI, "..", ".."))
sys.path.insert(0, os.path.join(RACINE, "outils"))
import png  # noqa: E402

L, H, IPS, N = 270, 480, 12, 144          # comp pixel, cadence des persos, 12 s
X0, Y0 = 119, 379                          # case de Tim : centrée sur x = 135, pieds (ligne 28) sur y = 407
I_CHARGE, I_TREMBLE, I_LANCER, I_REGARDE, I_POULE, I_FIN_DEGATS, I_REPOS = 7, 36, 58, 65, 74, 96, 96

# repos de Tim : 0,40 / 0,30 / 0,40 / 0,15 s à 12 i/s = 5, 4, 5, 2 images (cycle de 16)
CYCLE_REPOS = [0] * 5 + [1] * 4 + [2] * 5 + [3] * 2
RESPIRE = {1: 1}                           # image 1 du repos : buste (et tête) 1 px plus bas


def planche(chemin, case):
    w, h, px = png.lire(chemin)
    return [[[px[y * w + i * case + x] for x in range(case)] for y in range(case)] for i in range(w // case)]


TIM = planche(os.path.join(RACINE, "assets", "persos", "tim", "tim-sort-planche.png"), 32)
FX = planche(os.path.join(RACINE, "assets", "objets", "sort", "sort-planche.png"), 16)
ETINCELLES, BOULE, POULE_CHUTE, POULE_ASSISE = [0, 1, 2], [3, 4], 5, 6


def coller(img, sprite, x0, y0):
    for y, ligne in enumerate(sprite):
        yy = y0 + y
        if 0 <= yy < H:
            for x, c in enumerate(ligne):
                xx = x0 + x
                if c[3] and 0 <= xx < L:
                    img[yy * L + xx] = c


def ecrire_png(chemin, px):
    brut = b"".join(b"\x00" + bytes(v for c in px[y * L:(y + 1) * L] for v in c) for y in range(H))
    def morceau(t, d):
        return struct.pack(">I", len(d)) + t + d + struct.pack(">I", zlib.crc32(t + d) & 0xFFFFFFFF)
    with open(chemin, "wb") as f:
        f.write(b"\x89PNG\r\n\x1a\n" + morceau(b"IHDR", struct.pack(">IIBBBBB", L, H, 8, 6, 0, 0, 0))
                + morceau(b"IDAT", zlib.compress(brut, 9)) + morceau(b"IEND", b""))


def image(n):
    """Ce que montre l'image n (t = n / 12 s)."""
    px = [(0, 0, 0, 0)] * (L * H)
    dx = dy = 0
    tim, visible, poule = CYCLE_REPOS[n % 16], True, None

    if I_CHARGE <= n < I_LANCER:                       # 0,6–4,8 s : bâton levé, gemme qui clignote
        tim = 4 + (n // 2) % 2
        if n >= I_TREMBLE:                             # 3,0–4,8 s : Tim tremble d'1 px
            dx = n % 2
    elif I_LANCER <= n < I_REGARDE:                    # 4,8–5,4 s : lancer
        tim = 6
    elif I_REGARDE <= n < I_POULE:                     # 5,4–6,2 s : regarde en l'air, silence
        tim = 7
        if n >= I_POULE - 4:                           # la poule tombe (4 images)
            poule = (POULE_CHUTE, -16 + 96 * (n - (I_POULE - 4)))
    elif I_POULE <= n < I_FIN_DEGATS:                  # 6,2–8,0 s : sonné, dégâts, secousse
        tim = 8
        visible = not (n < I_POULE + 8 and (n - I_POULE) % 2)   # clignote 0,67 s (pixel-degats)
        dx = [1, -1, 1, -1, 0][n - I_POULE] if n - I_POULE < 5 else 0
    if n >= I_POULE:                                   # la poule assise sur la tête, jusqu'à la fin
        poule = (POULE_ASSISE, Y0 - 12 + RESPIRE.get(tim if n >= I_REPOS else -1, 0))

    if I_CHARGE <= n < I_LANCER:                       # 3 étincelles autour de la gemme (22–23, 1–2)
        cx, cy = X0 + 23 + dx, Y0 + 2
        r = 9 if n < I_TREMBLE else 9 - 6 * (n - I_TREMBLE) / (I_LANCER - I_TREMBLE)
        for k in range(3):
            a = 2 * math.pi * k / 3 + n * 0.55
            coller(px, FX[ETINCELLES[(n // 2 + k) % 3]], round(cx + r * math.cos(a)) - 7, round(cy + r * math.sin(a)) - 7)
    if visible:
        coller(px, TIM[tim], X0 + dx, Y0 + dy)
    if I_LANCER <= n < I_REGARDE:                      # la boule part de la gemme (29–30, 14–15) et sort en haut
        coller(px, FX[BOULE[n % 2]], X0 + 30 - 8, Y0 + 15 - 8 - 70 * (n - I_LANCER))
    if poule:
        coller(px, FX[poule[0]], X0 + 8 + dx, poule[1] + dy)
    return px


def main():
    sortie = os.path.join(ICI, "scene")
    os.makedirs(sortie, exist_ok=True)
    for n in range(N):
        ecrire_png(os.path.join(sortie, f"scene_{n:04d}.png"), image(n))
    print(f"{N} images {L}×{H} dans {sortie}")


if __name__ == "__main__":
    main()
