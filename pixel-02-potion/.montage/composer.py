#!/usr/bin/env python3
"""pixel-02-potion : compose la scène « La potion » en séquence PNG 270×480 à 12 i/s (180 images).

    python3 -I pixel-02-potion/.montage/composer.py     # écrit pixel-02-potion/.montage/scene/scene_0000.png …

Sprites : assets/persos/tim/tim-planche.png et tim-potion-planche.png (cases 32×32),
assets/persos/marchand/marchand-planche.png (32×32), assets/objets/potion/{potion-planche (16×16),
chiffres-planche (4×6), comptoir (80×10)}.png et l'étincelle de assets/objets/sort/sort-planche.png.
Toutes les positions sont entières et calculées image par image (« posées sur la grille »). Le fond, le
sol, la lune, le titre et les sous-titres restent ceux du modèle pixel (EffectCraft) ; la séquence est
transparente. Instants (script validé, pixel-02-potion/validations.md) : ticket 4,4 s · silence 7,0 s ·
fouille 8,4 s · miette 10,6 s · le marchand la prend 12,6 s.
"""
import os, struct, sys, zlib

ICI = os.path.dirname(os.path.abspath(__file__))
RACINE = os.path.normpath(os.path.join(ICI, "..", ".."))
sys.path.insert(0, os.path.join(RACINE, "outils"))
import png  # noqa: E402

L, H, IPS, N = 270, 480, 12, 180          # comp pixel, cadence des persos, 15 s
X0, Y0 = 124, 379                          # case de Tim arrêté devant le comptoir, pieds (ligne 28) sur y = 407
MX, MY = 160, 370                          # case du marchand : ligne 28 = haut du comptoir (y = 398)
COMPTOIR, CAISSE = (148, 398), (186, 382)
POTIONS = [(146, 383), (204, 383)]         # cases 16×16 posées sur le comptoir
ETIQUETTES = [("0,10", 140, 366), ("0,20", 199, 366)]   # chiffres ×2, sous les sous-titres, à côté de la tête du marchand
PRIX = "0,30000000000000004"
TICKET_D, TICKET_Y, RUBAN_X = 200, 286, 192   # bord droit et haut du ticket ; ruban qui sort de la caisse
PIECES = [(106, 160), (112, 170), (118, 175)]  # (image du lancer, x d'arrivée sur le comptoir)

I_ARRET, I_CAISSE, I_FIN_CAISSE, I_TICKET, I_FIN_TICKET = 12, 31, 53, 53, 81
I_REGARDE, I_FOUILLE, I_TEND, I_YEUX, I_PREND, I_PRIS, I_FIN_PREND = 82, 101, 127, 129, 152, 156, 158

# repos de Tim : 0,40 / 0,30 / 0,40 / 0,15 s à 12 i/s = 5, 4, 5, 2 images (cycle de 16)
CYCLE_REPOS = [0] * 5 + [1] * 4 + [2] * 5 + [3] * 2
OR_CLAIR, CONTOUR, CREME, OR = (0xFB, 0xE5, 0x8C, 255), (0x1D, 0x1B, 0x2E, 255), (0xF2, 0xED, 0xE4, 255), (0xF4, 0xC5, 0x42, 255)


def cases(chemin, cw, ch):
    w, h, px = png.lire(chemin)
    return [[[px[(r * ch + y) * w + i * cw + x] for x in range(cw)] for y in range(ch)]
            for r in range(h // ch) for i in range(w // cw)]


A = os.path.join(RACINE, "assets")
TIM = cases(os.path.join(A, "persos", "tim", "tim-planche.png"), 32, 32)          # 0-3 repos, 4-7 marche
TIMP = cases(os.path.join(A, "persos", "tim", "tim-potion-planche.png"), 32, 32)  # fouille ×2, tend, regarde-haut
MAR = cases(os.path.join(A, "persos", "marchand", "marchand-planche.png"), 32, 32)
OBJ = cases(os.path.join(A, "objets", "potion", "potion-planche.png"), 16, 16)   # bleue, rouge, caisse, pièce
CHIFFRES = cases(os.path.join(A, "objets", "potion", "chiffres-planche.png"), 4, 6)
BOIS = cases(os.path.join(A, "objets", "potion", "comptoir.png"), 80, 10)[0]
ETINCELLE = cases(os.path.join(A, "objets", "sort", "sort-planche.png"), 16, 16)[1]  # étincelle moyenne
FOUILLE_A, FOUILLE_B, TEND, REGARDE = TIMP
REPOS_M, CAISSE_A, CAISSE_B, YEUX_RONDS, PREND = MAR


def coller(img, sprite, x0, y0, teinte=None, z=1):
    """Pose un sprite ; z = agrandissement entier (chaque pixel devient un carré de z × z)."""
    for y, ligne in enumerate(sprite):
        for x, c in enumerate(ligne):
            if c[3]:
                for yy in range(y0 + z * y, y0 + z * y + z):
                    for xx in range(x0 + z * x, x0 + z * x + z):
                        if 0 <= yy < H and 0 <= xx < L:
                            img[yy * L + xx] = teinte or c


def rect(img, x0, y0, x1, y1, c):          # bornes incluses
    for y in range(y0, y1 + 1):
        for x in range(x0, x1 + 1):
            img[y * L + x] = c


def largeur(texte, z=2):
    return z * (sum(2 if ch == "," else 4 for ch in texte) - 1)


def ecrire(img, texte, x, y, c, z=2):
    """Chiffres 3×5 agrandis ×z (×2 : le prix doit se lire sur un téléphone)."""
    for ch in texte:
        coller(img, CHIFFRES[10 if ch == "," else int(ch)], x, y, c, z)
        x += z * (2 if ch == "," else 4)


def ticket(img, k):
    """Le ticket avec ses k premiers caractères, qui sort vers la gauche au-dessus de la caisse."""
    if k <= 0:
        return
    texte = PRIX[:k]
    g = TICKET_D - largeur(texte) - 5
    rect(img, g, TICKET_Y, TICKET_D, TICKET_Y + 17, CONTOUR)
    rect(img, g + 1, TICKET_Y + 1, TICKET_D - 1, TICKET_Y + 16, CREME)
    rect(img, RUBAN_X, TICKET_Y + 18, RUBAN_X + 3, CAISSE[1] + 4, CONTOUR)   # ruban jusqu'à la fente
    rect(img, RUBAN_X + 1, TICKET_Y + 17, RUBAN_X + 2, CAISSE[1] + 4, CREME)
    ecrire(img, texte, g + 3, TICKET_Y + 3, CONTOUR)


def image(n):
    """Ce que montre l'image n (t = n / 12 s)."""
    px = [(0, 0, 0, 0)] * (L * H)
    x, dx = X0, 0
    tim = TIM[CYCLE_REPOS[(n - I_ARRET) % 16]]
    if n < I_ARRET:                                     # 0–1,0 s : Tim arrive en marchant (4 px par image)
        x, tim = X0 - 4 * (I_ARRET - n), TIM[4 + n % 4]
    elif I_REGARDE <= n < I_FOUILLE:                    # 6,8–8,4 s : il regarde le ticket, silence
        tim = REGARDE
    elif I_FOUILLE <= n < I_TEND - 2:                   # 8,4–10,4 s : il fouille sa poche en tremblant
        tim, dx = (FOUILLE_A, FOUILLE_B)[(n // 2) % 2], n % 2
    elif I_TEND <= n < I_PRIS:                          # 10,6–13,0 s : il tend la miette
        tim = TEND

    marchand = REPOS_M
    if I_CAISSE <= n < I_FIN_CAISSE:                    # 2,6–4,4 s : il tape sur la caisse
        marchand = (CAISSE_A, CAISSE_B)[(n // 3) % 2]
    elif I_YEUX <= n < I_PREND:
        marchand = YEUX_RONDS
    elif I_PREND <= n < I_FIN_PREND:
        marchand = PREND

    coller(px, OBJ[2], *CAISSE)
    coller(px, marchand, MX, MY)
    coller(px, BOIS, *COMPTOIR)
    for k, (px0, py0) in enumerate(POTIONS):
        coller(px, OBJ[k], px0, py0)
    if n >= I_ARRET:                                    # 1,0 s : les étiquettes de prix
        for texte, ex, ey in ETIQUETTES:
            ecrire(px, texte, ex, ey, OR)
    if I_FOUILLE <= n < I_PRIS:                         # trois pièces sautent de la poche au comptoir
        for i0, xa in PIECES:
            t = min(1.0, max(0.0, (n - i0) / 6))
            if n >= i0:
                xs, ys, ya = X0 + 20, Y0 + 18, COMPTOIR[1] - 5
                coller(px, OBJ[3], round(xs + (xa - xs) * t), round(ys + (ya - ys) * t - 12 * t * (1 - t) * 4))
    coller(px, tim, x + dx, Y0)

    if I_TEND <= n < I_PRIS:                            # la miette d'un pixel, puis dans la main du marchand
        mx, my = X0 + 27, Y0 + 18
        if n >= I_PREND:
            t = (n - I_PREND + 1) / (I_PRIS - I_PREND)
            mx, my = round(mx + (MX + 1 - mx) * t), round(my + (MY + 24 - my) * t)
        else:
            if (n // 3) % 2 == 0:
                coller(px, ETINCELLE, mx - 7, my - 7)
        px[my * L + mx] = OR_CLAIR

    k = 0
    if I_TICKET <= n < I_PREND:                         # 4,4–6,8 s : le ticket s'imprime, chiffre par chiffre
        k = min(len(PRIX), (n - I_TICKET) * len(PRIX) // (I_FIN_TICKET - I_TICKET) + 1)
    elif I_PREND <= n < I_PREND + 12:                   # 12,6–13,6 s : il rentre dans la caisse
        k = len(PRIX) - (n - I_PREND + 1) * len(PRIX) // 12
    ticket(px, k)
    return px


def ecrire_png(chemin, px):
    brut = b"".join(b"\x00" + bytes(v for c in px[y * L:(y + 1) * L] for v in c) for y in range(H))
    def morceau(t, d):
        return struct.pack(">I", len(d)) + t + d + struct.pack(">I", zlib.crc32(t + d) & 0xFFFFFFFF)
    with open(chemin, "wb") as f:
        f.write(b"\x89PNG\r\n\x1a\n" + morceau(b"IHDR", struct.pack(">IIBBBBB", L, H, 8, 6, 0, 0, 0))
                + morceau(b"IDAT", zlib.compress(brut, 9)) + morceau(b"IEND", b""))


def main():
    sortie = os.path.join(ICI, "scene")
    os.makedirs(sortie, exist_ok=True)
    for n in range(N):
        ecrire_png(os.path.join(sortie, f"scene_{n:04d}.png"), image(n))
    print(f"{N} images {L}×{H} dans {sortie}")


if __name__ == "__main__":
    main()
