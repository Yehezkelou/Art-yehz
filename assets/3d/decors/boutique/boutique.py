#!/usr/bin/env python3
"""La boutique du marchand en diorama voxel (palette ico-pixel-32), dessinée par script.

    python3 -I assets/3d/decors/boutique/boutique.py                # → sol.vox, batiment.vox, mobilier.vox, apercu.png
    python3 -I assets/3d/decors/boutique/boutique.py --sortie <dossier> [--taille 2]

Repère du diorama (en voxels) : x de gauche à droite (0–47), y vers le haut, z de l'arrière (0) vers la rue (47) ;
la façade regarde +z. Chaque partie a sa propre grille ; son coin (0, 0, 0) est posé en `origine` dans
boutique.scene.toml (même repère). Les couleurs sont des index 1–32 de ico-pixel-32.

  sol.vox       « sol »        dalle 48×5×48 : socle 2/4, trottoir 6 (joints 5, bordure 5/7), rue 3, lignes 8,
                               flaques de lumière 7/8 devant la vitrine et 26/27 sous la lanterne et le lampadaire
  batiment.vox  « batiment »   façade en briques 3/4 (joints 2), porte, vitrine creuse éclairée (fond 20/19),
                               bandeau-enseigne 29 bordé d'or 18 et fiole dorée 18/19/20, étage à 2 fenêtres
                               (une allumée), volets, jardinière ; briques chaudes 25/26 autour de la lanterne
                «  toit »      toit à deux pans en tuiles violettes 30/29, faîtage 31, cheminée 4
  mobilier.vox  « comptoir », « etageres » (planches 26, fioles en couleurs), « lanterne » (19/20, potence 2),
                « lampadaire » (fût 2, lampe 20), « tonneau » (26, cerclages 4), « caisses », « plante »
"""
import argparse, os, sys

ICI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(ICI, "..", "..", "..", "..", "outils"))
import vox  # noqa: E402

# ---- dimensions (repère du diorama) ----
N = 48                       # dalle 48 × 48
Y_RUE, Y_TROTTOIR = 3, 4     # dessus de la rue, dessus du trottoir
Z_RUE = 36                   # la rue commence ici (z 36–47)
BAT = (4, 5, 4)              # origine de la grille du bâtiment
BX, BZ = 40, 24              # grille du bâtiment : 40 × 56 × 24
FACADE = 21                  # plan de la façade (z local) → z 25 du diorama
MURS = (1, 38)               # murs x 1–38 (local) → x 5–42 du diorama
RDC, BANDEAU, CORNICHE, ETAGE, AVANT_TOIT = (0, 15), (16, 19), (20, 21), (22, 33), 34

PORTE = (3, 8, 2, 12)        # x0, x1, y0, y1 (local)
VITRINE = (12, 35, 3, 14)    # cadre ; ouverture à l'intérieur du cadre
FOND_VITRINE = 14            # mur du fond de la boutique (z local)
LANTERNE = (10, 10)          # x, y (local) du centre de la lanterne, devant la façade

FIOLES = [11, 23, 15, 31, 19, 12, 24, 16, 10, 22, 32, 20]


def hachage(*v):
    h = 2166136261
    for a in v:
        h = ((h ^ (a & 0xFFFF)) * 16777619) & 0xFFFFFFFF
    return h


def brique(x, y, z, chaud=False):
    """Motif de briques 4 × 2 + joint 1, rangs décalés ; u = x + z pour que le motif tourne aux angles."""
    if y % 3 == 2:
        return 2
    u = x + z + (2 if (y // 3) % 2 else 0)
    if u % 5 == 4:
        return 2
    n = hachage(u // 5, y // 3, 7) % 7
    if chaud:
        return 26 if n < 4 else 25
    return 4 if n < 2 else 3


# ------------------------------------------------------------------ sol
def sol():
    m = vox.Modele(N, 5, N, nom="sol")
    m.boite(0, 0, 0, N - 1, 0, N - 1, 2)                 # semelle
    m.boite(0, 1, 0, N - 1, 2, N - 1, 4)                 # tranche du socle
    for x in range(0, N, 6):                             # rainures de la tranche (plaques)
        m.boite(x, 1, N - 1, x, 2, N - 1, 3)
        m.boite(x, 1, 0, x, 2, 0, 3)
        m.boite(0, 1, x, 0, 2, x, 3)
        m.boite(N - 1, 1, x, N - 1, 2, x, 3)
    # rue
    m.boite(0, Y_RUE, Z_RUE, N - 1, Y_RUE, N - 1, 3)
    for x in range(1, N, 8):                             # pointillés
        m.boite(x, Y_RUE, 41, x + 3, Y_RUE, 42, 8)
    m.boite(0, Y_RUE, N - 2, N - 1, Y_RUE, N - 1, 2)     # caniveau au bord de la dalle
    for x, z in ((9, 38), (10, 38), (30, 45), (31, 44), (22, 39)):
        m[x, Y_RUE, z] = 4                               # pavés usés
    # trottoir (z 0–35) : dalles 6 à joints 5, bordure 5 (dessus 7)
    m.boite(0, Y_RUE, 0, N - 1, Y_TROTTOIR, Z_RUE - 1, 5)
    for z in range(0, Z_RUE - 1):
        for x in range(N):
            m[x, Y_TROTTOIR, z] = 5 if (x % 6 == 0 or z % 6 == 2) else 6
    m.boite(0, Y_RUE, Z_RUE - 1, N - 1, Y_TROTTOIR, Z_RUE - 1, 5)   # bordure
    # flaque de lumière de la vitrine : trapèze qui s'élargit vers la rue
    x0, x1 = BAT[0] + VITRINE[0], BAT[0] + VITRINE[1]
    for k, z in enumerate(range(BAT[2] + FACADE + 1, Z_RUE - 1)):
        a, b = x0 + 1 - k // 2, x1 - 1 + k // 2
        for x in range(max(0, a), min(N - 1, b) + 1):
            dedans = a + 2 <= x <= b - 2 and k < 6
            m[x, Y_TROTTOIR, z] = 8 if dedans else 7
    # flaques de lumière : sous la lanterne (28, chaude) et sous le lampadaire (7, cœur 8)
    for (cx, cz, r, ext, coeur) in ((BAT[0] + LANTERNE[0] + 0.5, BAT[2] + FACADE + 3.5, 3.6, 28, 28), (41.5, 34.5, 4.6, 7, 8)):
        for z in range(N):
            for x in range(N):
                d = ((x + 0.5 - cx) ** 2 + (z + 0.5 - cz) ** 2) ** 0.5
                if d > r:
                    continue
                y = Y_TROTTOIR if z < Z_RUE else Y_RUE
                if z == Z_RUE - 1:
                    y = Y_TROTTOIR
                if m[x, y, z] in (8,):
                    continue
                m[x, y, z] = coeur if d < r * 0.55 else ext
    return m


# ------------------------------------------------------------------ bâtiment
def batiment():
    m = vox.Modele(BX, 36, BZ, nom="batiment")
    xa, xb = MURS
    za, zb = 1, FACADE
    lx, ly = LANTERNE
    # volume plein en briques
    for y in range(0, AVANT_TOIT):
        for z in range(za, zb + 1):
            for x in range(xa, xb + 1):
                chaud = z == zb and ((x - lx) ** 2 + ((y - ly) * 1.2) ** 2) <= 20 and y <= RDC[1]
                m[x, y, z] = brique(x, y, z, chaud)
    # soubassement en pierre (y 0–1)
    m.boite(xa, 0, za, xb, 1, zb, 4)
    for x in range(xa, xb + 1, 4):
        m[x, 1, zb] = 3
    # chaînes d'angle en pierre claire (5 / 6 en alternance)
    for y in range(2, AVANT_TOIT):
        c = 5 if (y // 2) % 2 else 6
        for x, z in ((xa, zb), (xb, zb), (xa, za), (xb, za)):
            m[x, y, z] = c
    # corniche (dépasse d'un voxel), dessus clair
    m.boite(xa - 1, CORNICHE[0], za - 1, xb + 1, CORNICHE[1], zb + 1, 5)
    m.boite(xa - 1, CORNICHE[1], za - 1, xb + 1, CORNICHE[1], zb + 1, 6)
    # avant-toit
    m.boite(xa - 1, AVANT_TOIT - 1, za - 1, xb + 1, AVANT_TOIT - 1, zb + 1, 4)

    # --- bandeau-enseigne au-dessus du rez-de-chaussée : violet 29 bordé d'or 18, clous dorés 19
    b0, b1 = BANDEAU
    m.boite(xa + 1, b0, zb + 1, xb - 1, b1, zb + 1, 18)
    m.boite(xa + 2, b0 + 1, zb + 1, xb - 2, b1 - 1, zb + 1, 29)
    for x in range(xa + 4, xb - 2, 4):
        m[x, b0 + 1, zb + 1] = 30
        m[x, b1 - 1, zb + 1] = 30
    # fiole dorée de l'enseigne (au milieu, relief de 2), sur le bandeau et l'étage
    cx = (xa + xb) // 2   # 19 → fiole x 16–23
    fiole = [
        "...cc...",   # y + 10 bouchon
        "...cc...",
        "..oOOo..",   # col
        "...oo...",
        ".oOOOOo.",
        "oOrrRROo",
        "oOrRRrOo",
        "oOrrrrOo",
        "oOOrrOOo",
        ".oOOOOo.",
        "..oooo..",   # y + 0
    ]
    yb = b0 - 1
    for k, ligne in enumerate(reversed(fiole)):
        for c, ch in enumerate(ligne):
            i = {"o": 18, "O": 19, "r": 20, "R": 8, "c": 26}.get(ch)
            if i:
                for z in (zb + 1, zb + 2):
                    m[cx - 4 + c, yb + k, z] = i
    # --- porte (en retrait d'un voxel, panneaux, poignée dorée, imposte éclairée)
    px0, px1, py0, py1 = PORTE
    m.boite(px0, py0, zb, px1, py1 + 1, zb, 25)                 # chambranle
    m.boite(px0 + 1, py0, zb - 1, px1 - 1, py1, zb, 0)           # embrasure
    m.boite(px0 + 1, py0, zb - 1, px1 - 1, py1 - 3, zb - 1, 26)  # vantail
    for y in (py0 + 1, py0 + 5):
        m.boite(px0 + 2, y, zb - 1, px1 - 2, y + 2, zb - 1, 25)  # panneaux
    m[px1 - 2, py0 + 4, zb - 1] = 19                             # poignée
    m.boite(px0 + 1, py1 - 2, zb - 1, px1 - 1, py1, zb - 1, 20)  # imposte éclairée
    m.boite(px0 + 1, py1 - 2, zb - 1, px0 + 1, py1, zb - 1, 25)
    m[(px0 + px1) // 2, py1 - 1, zb - 1] = 19
    m.boite(px0, py0 - 1, zb + 1, px1, py0 - 1, zb + 1, 5)        # marche
    # --- vitrine : cadre bois 26, ouverture creuse jusqu'au mur du fond éclairé
    vx0, vx1, vy0, vy1 = VITRINE
    m.boite(vx0, vy0, zb, vx1, vy1, zb, 26)
    m.boite(vx0 + 1, vy0 + 1, FOND_VITRINE + 1, vx1 - 1, vy1 - 1, zb, 0)   # creux
    m.boite(vx0 + 1, vy0 + 1, FOND_VITRINE, vx1 - 1, vy1 - 1, FOND_VITRINE, 20)  # fond lumineux
    for x in range(vx0 + 1, vx1):                                 # lambris du fond : un rang 19
        m[x, vy0 + 1, FOND_VITRINE] = 19
        m[x, vy0 + 2, FOND_VITRINE] = 19
    m.boite(vx0 + 1, vy0, FOND_VITRINE + 1, vx1 - 1, vy0, zb - 1, 25)    # plancher
    m.boite(vx0 + 1, vy1, FOND_VITRINE + 1, vx1 - 1, vy1, zb - 1, 26)    # plafond
    for x in (vx0 + 8, vx1 - 8):                                  # meneaux
        m.boite(x, vy0 + 1, zb, x, vy1 - 1, zb, 26)
    m.boite(vx0 + 1, vy1 - 4, zb, vx1 - 1, vy1 - 4, zb, 26)       # traverse haute
    m.boite(vx0 - 1, vy0 - 1, zb + 1, vx1 + 1, vy0, zb + 1, 6)    # appui en pierre (dépasse)
    m.boite(vx0 - 1, vy0, zb + 1, vx1 + 1, vy0, zb + 1, 7)
    # --- étage : deux fenêtres à volets (la gauche allumée), jardinière
    e0, e1 = ETAGE
    for fx0, allumee in ((5, True), (28, False)):
        fx1, fy0, fy1 = fx0 + 6, e0 + 3, e0 + 10
        m.boite(fx0 - 1, fy0 - 1, zb, fx1 + 1, fy1 + 1, zb, 5)               # encadrement
        m.boite(fx0, fy0, zb - 1, fx1, fy1, zb, 0)
        m.boite(fx0, fy0, zb - 1, fx1, fy1, zb - 1, 20 if allumee else 9)    # vitre
        if allumee:
            m.boite(fx0, fy0, zb - 1, fx0 + 1, fy1, zb - 1, 23)              # rideaux
            m.boite(fx1 - 1, fy0, zb - 1, fx1, fy1, zb - 1, 23)
            m.boite(fx0, fy1, zb - 1, fx1, fy1, zb - 1, 22)
        else:
            m[fx0 + 1, fy1 - 1, zb - 1] = 10                                  # reflet
            m[fx0 + 2, fy1 - 2, zb - 1] = 10
        m.boite((fx0 + fx1) // 2, fy0, zb - 1, (fx0 + fx1) // 2, fy1, zb - 1, 25)  # croisée
        m.boite(fx0, (fy0 + fy1) // 2, zb - 1, fx1, (fy0 + fy1) // 2, zb - 1, 25)
        for vx in (fx0 - 3, fx1 + 2):                                         # volets ouverts
            m.boite(vx, fy0 - 1, zb + 1, vx + 1, fy1 + 1, zb + 1, 26)
            for y in range(fy0, fy1 + 1, 2):
                m.boite(vx, y, zb + 1, vx + 1, y, zb + 1, 25)
        m.boite(fx0 - 1, fy0 - 2, zb + 1, fx1 + 1, fy0 - 1, zb + 2, 25)      # jardinière
        for k, x in enumerate(range(fx0 - 1, fx1 + 2)):
            m[x, fy0, zb + 1] = 15 if k % 2 else 14
            m[x, fy0, zb + 2] = 14 if k % 3 else 0
            if k % 3 == 1:
                m[x, fy0 + 1, zb + 2] = 24 if k % 2 else 32
    # --- côtés : une petite fenêtre éteinte de chaque côté de l'étage, gouttière
    for x in (xa, xb):
        m.boite(x, e0 + 4, 8, x, e0 + 8, 12, 5)
        m.boite(x, e0 + 5, 9, x, e0 + 7, 11, 9)
        m[x, e0 + 7, 9] = 10
    m.boite(xb + 1, 2, zb - 1, xb + 1, AVANT_TOIT - 2, zb - 1, 4)               # descente d'eau
    return m


def toit():
    """Toit à deux pans (faîtage selon x), tuiles 30/29 en rangs, faîtage 31, pignons en briques, cheminée."""
    xa, xb = MURS
    lz = BZ
    m = vox.Modele(BX, 14, lz, nom="toit")
    za, zb = 0, FACADE + 1                 # débord avant et arrière
    h = (zb - za + 1) // 2                 # 11 marches
    for k in range(h):
        y = k
        z0, z1 = za + k, zb - k
        for x in range(xa - 1, xb + 2):
            for z in (z0, z1):
                m[x, y, z] = 29 if (x + k) % 4 == 0 else 30
            if k:
                m[x, y, z0 + 1 if z0 + 1 <= z1 else z0] = 29
        # pignons : briques entre les deux pans
        for z in range(z0 + 1, z1):
            for x in (xa, xb):
                m[x, y, z] = brique(x, y + 40, z)
            for x in range(xa + 1, xb):
                m[x, y, z] = 2                              # comble (invisible)
    m.boite(xa - 1, h - 1, za + h - 1, xb + 1, h - 1, zb - h + 1, 31)   # faîtage
    # lucarne sur le pan avant (fenêtre allumée, petit toit en marches)
    lx0, lx1, lz1 = 16, 23, zb - 1
    m.boite(lx0, 0, lz1 - 6, lx1, 6, lz1, 4)
    for y in range(0, 7):
        for x in range(lx0, lx1 + 1):
            m[x, y, lz1] = brique(x, y + 1, lz1)
    m.boite(lx0, 0, lz1, lx0, 6, lz1, 5)
    m.boite(lx1, 0, lz1, lx1, 6, lz1, 5)
    m.boite(lx0 + 2, 2, lz1, lx1 - 2, 5, lz1, 20)
    m.boite(lx0 + 2, 2, lz1, lx0 + 2, 5, lz1, 23)
    m.boite(lx1 - 2, 2, lz1, lx1 - 2, 5, lz1, 23)
    m.boite(lx0 + 1, 1, lz1 + 1, lx1 - 1, 1, lz1 + 1, 25)        # appui
    for k, (a, b) in enumerate(((lx0 - 1, lx1 + 1), (lx0, lx1), (lx0 + 2, lx1 - 2), (lx0 + 3, lx1 - 3))):
        m.boite(a, 7 + k, lz1 - 7, b, 7 + k, lz1 + 1, 30)
        m.boite(a, 7 + k, lz1 + 1, b, 7 + k, lz1 + 1, 29)
    m.boite(lx0 + 3, 10, lz1 - 7, lx1 - 3, 10, lz1 + 1, 31)
    # œil-de-bœuf éclairé dans le pignon droit
    m.boite(xb, 3, 9, xb, 5, 13, 5)
    m.boite(xb, 4, 10, xb, 4, 12, 20)
    # cheminée (traverse le pan arrière)
    m.boite(29, 0, 5, 32, 13, 8, 4)
    for y in range(0, 13):
        for x in range(29, 33):
            for z in (5, 8):
                m[x, y, z] = brique(x, y, z)
    m.boite(28, 12, 4, 33, 12, 9, 5)
    m.boite(29, 13, 5, 32, 13, 8, 2)
    m.boite(30, 13, 6, 31, 13, 7, 1)
    return m


# ------------------------------------------------------------------ mobilier
def comptoir():
    m = vox.Modele(16, 4, 3, nom="comptoir")
    m.boite(0, 0, 0, 15, 2, 2, 25)
    m.boite(0, 3, 0, 15, 3, 2, 27)
    for x in range(1, 15, 3):
        m.boite(x, 1, 2, x + 1, 1, 2, 26)      # tiroirs
    return m


def etageres(larg=22):
    m = vox.Modele(larg, 8, 2, nom="etageres")
    for y in (0, 4):
        m.boite(0, y, 0, larg - 1, y, 1, 26)
        k = 0
        for x in range(1, larg - 1, 2):
            c = FIOLES[(k + y) % len(FIOLES)]
            hfiole = 3 if (k + y) % 3 == 0 else 2
            for yy in range(1, hfiole):
                m[x, y + yy, 1] = c
            m[x, y + hfiole, 1] = 8 if c not in (8, 20) else 27         # reflet / bouchon
            if (k + y) % 4 == 1 and x + 1 < larg - 1:
                m[x + 1, y + 1, 1] = 27                                  # petit pot
            k += 1
    m.boite(0, 1, 0, 0, 7, 0, 26)
    m.boite(larg - 1, 1, 0, larg - 1, 7, 0, 26)
    return m


def lanterne():
    """Lanterne murale : potence 2 depuis la façade, lanterne 3×4×3 (verre 20, cadre 2, chapeau 1)."""
    m = vox.Modele(3, 7, 4, nom="lanterne")
    m.boite(1, 6, 0, 1, 6, 2, 2)              # potence
    m[1, 5, 2] = 2
    m.boite(0, 0, 1, 2, 0, 3, 2)              # culot
    m.boite(0, 1, 1, 2, 3, 3, 20)             # verre
    m.boite(1, 1, 1, 1, 3, 3, 19)             # flamme (croix plus chaude)
    m.boite(0, 2, 2, 2, 2, 2, 19)
    m[1, 2, 3] = 8
    m.boite(0, 4, 1, 2, 4, 3, 1)              # chapeau
    return m


def lampadaire():
    m = vox.Modele(6, 30, 3, nom="lampadaire")
    m.boite(4, 0, 0, 5, 1, 1, 3)              # socle (x 4–5, z 0–1)
    m.boite(4, 2, 0, 5, 2, 1, 2)
    m.boite(4, 3, 0, 4, 26, 0, 2)             # fût
    m.boite(4, 10, 0, 4, 10, 0, 4)
    m.boite(1, 26, 0, 4, 26, 0, 2)            # bras vers la boutique (−x)
    m[4, 25, 0] = 2
    m.boite(0, 25, 0, 2, 25, 2, 1)            # chapeau
    m.boite(0, 22, 0, 2, 24, 2, 20)           # lampe
    m.boite(1, 22, 0, 1, 24, 2, 8)
    m.boite(0, 21, 0, 2, 21, 2, 2)
    m[1, 27, 0] = 2
    return m


def tonneau():
    m = vox.Modele(4, 5, 4, nom="tonneau")
    for y in range(5):
        r = 4 if 1 <= y <= 3 else 3
        if r == 4:
            m.boite(0, y, 0, 3, y, 3, 26)
            for x, z in ((0, 0), (3, 0), (0, 3), (3, 3)):
                m[x, y, z] = 0
        else:
            m.boite(0, y, 0, 3, y, 3, 26)
            for x, z in ((0, 0), (3, 0), (0, 3), (3, 3)):
                m[x, y, z] = 0
    for y in (1, 3):
        for x in range(4):
            for z in range(4):
                if m[x, y, z] and (x in (0, 3) or z in (0, 3)):
                    m[x, y, z] = 4
    m.boite(1, 4, 1, 2, 4, 2, 25)
    return m


def caisses():
    m = vox.Modele(4, 6, 4, nom="caisses")
    m.boite(0, 0, 0, 3, 2, 3, 27)
    for (x, z) in ((0, 0), (3, 0), (0, 3), (3, 3)):
        m.boite(x, 0, z, x, 2, z, 26)
    m.boite(0, 1, 0, 3, 1, 3, 26)
    m.boite(1, 3, 1, 3, 5, 3, 27)             # petite caisse dessus
    m.boite(1, 4, 1, 3, 4, 3, 26)
    m[2, 5, 3] = 23                           # fiole qui dépasse
    m[2, 5, 2] = 0
    return m


def plante():
    m = vox.Modele(3, 6, 3, nom="plante")
    m.boite(0, 0, 0, 2, 1, 2, 26)             # pot
    m.boite(0, 1, 0, 2, 1, 2, 27)
    m.boite(0, 2, 0, 2, 3, 2, 14)
    m.boite(1, 2, 1, 1, 5, 1, 15)
    m[0, 4, 1] = 15
    m[2, 3, 0] = 16
    m[1, 5, 1] = 24
    return m


# ------------------------------------------------------------------ placement (repère du diorama)
def placements():
    bx, by, bz = BAT
    vx0, vx1, vy0, _ = VITRINE
    return [
        ("sol.vox", "sol", (0, 0, 0)),
        ("batiment.vox", "batiment", BAT),
        ("batiment.vox", "toit", (bx, by + AVANT_TOIT, bz)),
        ("mobilier.vox", "etageres", (bx + vx0 + 1, by + vy0 + 3, bz + FOND_VITRINE + 1)),
        ("mobilier.vox", "comptoir", (bx + vx0 + 4, by + vy0 + 1, bz + FACADE - 4)),
        ("mobilier.vox", "lanterne", (bx + LANTERNE[0] - 1, by + LANTERNE[1] - 3, bz + FACADE + 1)),
        ("mobilier.vox", "lampadaire", (40, Y_TROTTOIR + 1, 33)),
        ("mobilier.vox", "tonneau", (0, Y_TROTTOIR + 1, 27)),
        ("mobilier.vox", "caisses", (0, Y_TROTTOIR + 1, 21)),
        ("mobilier.vox", "plante", (bx + PORTE[1] + 1, Y_TROTTOIR + 1, bz + FACADE + 1)),
    ]


def lumieres():
    """Centres des lumières (repère du diorama) : halo pixel en anneaux pleins, face à la caméra."""
    pl = {n: o for _, n, o in placements()}
    lo, la = pl["lanterne"], pl["lampadaire"]
    return [
        # le halo est posé un peu derrière la lampe (côté façade) pour que les voxels passent devant
        ("lanterne", (lo[0] + 1.5, lo[1] + 2.5, lo[2] + 1.0), 3.6, [19, 18], 2.4),
        ("lampadaire", (la[0] + 1.5, la[1] + 23, la[2] - 0.5), 4.2, [19, 18], 2.6),
    ]


def scene_toml(chemin, hauteur):
    l = ["# Diorama « boutique du marchand » : placement des parties (écrit par boutique.py, ne pas retoucher à la main).",
         "# Repère en voxels : x gauche → droite, y vers le haut, z arrière → rue ; origine = coin (0, 0, 0) de la partie.",
         "# Chargement : outils.voxel.charger(fichier) → modèle nommé, maillage(…, { centre: \"coin\", occlusion: 2 }),",
         "# position = origine − centre. Voir controle.mjs.",
         'nom = "boutique"',
         f"taille = [{N}, {hauteur}, {N}]",
         f"centre = [{N // 2}, {Y_TROTTOIR + 1}, {N // 2}]   # point du diorama posé à l'origine de la scène (sol du trottoir, milieu)",
         "occlusion = 2                 # vrais coins seulement (conseillé sur les dioramas)",
         ""]
    for f, n, o in placements():
        l += ["[[partie]]", f'nom = "{n}"', f'fichier = "{f}"', f'modele = "{n}"', f"origine = [{o[0]}, {o[1]}, {o[2]}]", ""]
    for n, p, r, c, inter in lumieres():
        l += ["[[lumiere]]", f'nom = "{n}"', f"position = [{p[0]}, {p[1]}, {p[2]}]",
              f"halo = {{ rayon = {r}, couleurs = [{', '.join(map(str, c))}], interieur = {inter} }}", ""]
    l += ["# Cadrages conseillés (cible et distance en voxels, champ vertical 24°, image 270 × 480)",
          "[cadrage.large]", "cible = [0, 21, 0]", "distance = 250", "hauteur = 80", "",
          "[cadrage.rapproche]", "cible = [4, 14, 4]", "distance = 145", "hauteur = 26", ""]
    with open(chemin, "w", encoding="utf-8", newline="\n") as fd:
        fd.write("\n".join(l))
    return chemin


def assembler(modeles):
    """Tout le diorama dans une seule grille (pour l'aperçu)."""
    par_nom = {m.nom: m for m in modeles}
    ly = max(o[1] + par_nom[n].ly for _, n, o in placements())
    g = vox.Modele(N, ly, N, nom="boutique")
    for _, nom, (ox, oy, oz) in placements():
        for x, y, z, i in par_nom[nom].voxels():
            if g.dedans(ox + x, oy + y, oz + z):
                g[ox + x, oy + y, oz + z] = i
    return g


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--sortie", default=ICI)
    ap.add_argument("--taille", type=int, default=2, help="taille de l'aperçu")
    a = ap.parse_args(argv)
    s, b, t = sol(), batiment(), toit()
    mob = [comptoir(), etageres(VITRINE[1] - VITRINE[0] - 1), lanterne(), lampadaire(), tonneau(), caisses(), plante()]
    vox.ecrire_vox(os.path.join(a.sortie, "sol.vox"), [s])
    vox.ecrire_vox(os.path.join(a.sortie, "batiment.vox"), [b, t])
    vox.ecrire_vox(os.path.join(a.sortie, "mobilier.vox"), mob)
    g = assembler([s, b, t] + mob)
    vox.apercu(os.path.join(a.sortie, "apercu.png"), g, vue="trois-quarts", taille=a.taille)
    print(scene_toml(os.path.join(a.sortie, "boutique.scene.toml"), g.ly))
    print(f"diorama {g.lx}×{g.ly}×{g.lz}, {g.compter()} voxels")


if __name__ == "__main__":
    main()
