#!/usr/bin/env python3
"""ico-vid : grimoire en « boîte texturée » (volume en voxels + plat texturé), dessin maison (modélisé par Claude,
script vox.py).

    python3 -I assets/3d/objets/grimoire/grimoire.py         # → grimoire.vox (corps, couvercle, signet), apercu.png
    python3 -I assets/3d/textures/grimoire-plat.py           # → assets/3d/textures/grimoire-plat.png (le plat)
    node outils/rendu3d/rendu3d.mjs --scene assets/3d/objets/grimoire/controle.mjs --out <dossier> --debut 0 --fin 4 --ips 12

Livre posé à plat, dos à gauche (x = 0), tranche avant vers +z ; grille commune 19 × 8 × 19 (x, y en haut, z) :
- « corps » : plat du dessous biseauté (calque 0 en retrait, calque 1 plein, couverture 30 / 29), bloc des pages
  (calques 2–4, crème 8 avec une ligne 7, en retrait d'un voxel sur les trois tranches), dos 30 à nerfs 31 et titre doré 19,
  coins renforcés 31 ;
- « couvercle » (calques 5–7 de la grille commune, posé par ORIGINE_COUVERCLE) : plat 30 plein, puis le plateau
  biseauté 16 × 16 (x 2–17, z 1–16) sur lequel la scène pose la texture 16 × 16 (un texel = un voxel), coins 31
  qui dépassent d'un voxel au-dessus du plat ; charnière = arête (x 0, y 5) ;
- « signet » 23 / 22 : ruban qui sort des pages à l'avant et pend sur la tranche, bout fendu.
"""
import argparse, os, sys

ICI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(ICI, "..", "..", "..", "..", "outils"))
import vox  # noqa: E402

COUV, COUV_SOMBRE, COIN, PAGE, PAGE_LIGNE, SIGNET, SIGNET_SOMBRE, TITRE = 30, 29, 31, 8, 7, 23, 22, 19
LX, LY, LZ = 19, 8, 19
ORIGINE_COUVERCLE = (0, 5, 0)        # coin (0, 0, 0) du couvercle dans la grille commune
CHARNIERE = (0, 5, 0)                # pivot d'ouverture (axe z), grille commune
PLATEAU = (2, 1, 17, 16)             # x0, z0, x1, z1 du plateau texturé (16 × 16)
TEXTURE = os.path.join(ICI, "..", "..", "textures", "grimoire-plat.png")


def coins(m, y, x0, z0, x1, z1, taille=3):
    """Équerres de 31 aux 4 coins du rectangle (x0, z0)–(x1, z1) sur le calque y."""
    for cx, sx in ((x0, 1), (x1, -1)):
        for cz, sz in ((z0, 1), (z1, -1)):
            for k in range(taille):
                m[cx + sx * k, y, cz] = COIN
                m[cx, y, cz + sz * k] = COIN


def corps():
    m = vox.Modele(LX, 5, LZ, nom="corps")
    m.boite(1, 0, 1, 17, 0, 16, COUV_SOMBRE)          # biseau du dessous
    m.boite(0, 1, 0, 18, 1, 17, COUV)                 # plat du dessous
    m.boite(1, 2, 1, 17, 4, 16, PAGE)                 # pages
    m.boite(1, 3, 1, 17, 3, 16, PAGE_LIGNE)
    m.boite(1, 3, 2, 16, 3, 15, PAGE)                 # (la ligne 7 ne se voit que sur les tranches)
    m.boite(0, 2, 0, 0, 4, 17, COUV)                  # dos
    for z in (3, 4, 13, 14):                          # nerfs du dos
        m.boite(0, 1, z, 0, 4, z, COIN)
    for z in (7, 8, 9, 10):                           # titre doré sur le dos (deux traits)
        m[0, 3, z] = TITRE
    m[0, 2, 8] = m[0, 2, 9] = TITRE
    coins(m, 1, 0, 0, 18, 17)
    coins(m, 0, 1, 1, 17, 16, taille=2)
    return m


def couvercle():
    m = vox.Modele(LX, 3, LZ, nom="couvercle")
    m.boite(0, 0, 0, 18, 0, 17, COUV)                 # plat
    x0, z0, x1, z1 = PLATEAU
    m.boite(x0, 1, z0, x1, 1, z1, COUV)               # plateau (sous la texture)
    m.boite(0, 1, 1, 0, 1, 16, COUV)                  # arrondi du dos (x 1 = gorge de la charnière)
    for z in (3, 4, 13, 14):
        m[0, 0, z] = m[0, 1, z] = COIN
    coins(m, 0, 0, 0, 18, 17)
    coins(m, 2, x0, z0, x1, z1, taille=2)             # coins qui dépassent au-dessus du plat
    return m


def signet():
    m = vox.Modele(LX, 5, LZ, nom="signet")
    m.boite(11, 3, 17, 13, 3, 17, SIGNET)             # sort des pages
    m.boite(11, 1, 18, 13, 3, 18, SIGNET)             # pend sur la tranche
    m[11, 0, 18] = m[13, 0, 18] = SIGNET               # bout fendu
    m[12, 1, 18] = SIGNET_SOMBRE
    return m


def fabriquer(sortie):
    os.makedirs(sortie, exist_ok=True)
    mods = [corps(), couvercle(), signet()]
    vox.ecrire_vox(os.path.join(sortie, "grimoire.vox"), mods)
    # aperçu : le livre fermé ; la texture du plat (si elle existe) y est posée en un calque de voxels (aperçu seulement)
    tout = vox.Modele(LX, LY, LZ, nom="grimoire")
    ox, oy, oz = ORIGINE_COUVERCLE
    for m, (dx, dy, dz) in zip(mods, ((0, 0, 0), (ox, oy, oz), (0, 0, 0))):
        for x, y, z, i in m.voxels():
            tout[x + dx, y + dy, z + dz] = i
    if os.path.exists(TEXTURE):
        import png  # noqa: E402  (outils/png.py)
        w, h, px = png.lire(TEXTURE)
        index = {c: k + 1 for k, c in enumerate(vox.lire_palette())}
        x0, z0 = PLATEAU[:2]
        for v in range(h):
            for u in range(w):
                if not tout[x0 + u, LY - 1, z0 + v]:
                    tout[x0 + u, LY - 1, z0 + v] = index[px[v * w + u][:3]]
    vox.apercu(os.path.join(sortie, "apercu.png"), tout, vue="trois-quarts", taille=3)
    return mods


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--sortie", default=ICI)
    for m in fabriquer(ap.parse_args().sortie):
        print(m.nom, m.compter(), "voxels", m.couleurs())
