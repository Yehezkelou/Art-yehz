#!/usr/bin/env python3
"""ico-vid : potions voxel (bleue et rouge) + leurs particules, dessin maison (modélisé par Claude, script vox.py).

    python3 -I assets/3d/objets/potion/potion.py            # → potion.vox, potion-particules.vox, apercu.png
    node outils/rendu3d/rendu3d.mjs --scene assets/3d/objets/potion/controle.mjs --out <dossier> --debut 0 --fin 4 --ips 12 \
        [--params '{"couleur": "rouge"}']

Grille 9 × 12 × 9 (x, y en haut, z vers l'avant), axe de la fiole en (4, 4) ; panse octogonale :
- verre = cadre creux (12, fond 11) : fond plein, anneau bas, épaule en deux marches, 4 nervures en diagonale et
  4 fenêtres (une par face) ;
- liquide plein (bleu 10 / éclats 11 / fond 9, rouge 23 / 24 / 22) : il affleure dans les fenêtres du bas, sa
  surface (calque 4) est en retrait d'un voxel, au-dessus les fenêtres sont vides (on voit le verre du fond) ;
- reflet crème 8 en marches sur la nervure avant gauche et l'épaule ; col 3 × 3, lèvre 5 × 5, bouchon 27 / 26.
- bleue retouchée (fonction bleue) : liquide 9 à reflets 10 qui affleure jusqu'à une surface pleine 11, fenêtres du
  haut vitrées sauf la case du milieu de chaque face (plus de « yeux » sombres de face), reflets crème en plus.
Particules : un modèle d'un voxel par particule (6 par couleur) dans potion-particules.vox, que la scène fait flotter.
"""
import argparse, os, sys

ICI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(ICI, "..", "..", "..", "..", "outils"))
import vox  # noqa: E402

VERRE, VERRE_FOND, REFLET, BOUCHON, BOUCHON_SOMBRE = 12, 11, 8, 27, 26
LIQUIDES = {  # nom : (liquide, éclat, ombre)
    "bleue": (9, 10, 9),
    "rouge": (23, 24, 22),
}
PARTICULES = {"bleue": [11, 12, 8, 11, 12, 11], "rouge": [23, 24, 8, 23, 24, 23]}
C = 4                                   # axe de la fiole (x = z = 4)
RAYONS = {0: 2.3, 1: 3.3, 2: 4.4, 3: 4.4, 4: 4.4, 5: 4.4, 6: 3.3, 7: 2.3}   # panse : rayon extérieur par calque
ANNEAUX = (1, 6, 7)                     # calques de verre plein (bas, épaule)
NIVEAU = 4                              # surface du liquide (en retrait d'un voxel ; au-dessus : fenêtres vides)


def dans(dx, dz, r):
    return dx * dx + dz * dz <= r * r


def fiole(nom):
    liq, eclat, ombre = LIQUIDES[nom]
    m = vox.Modele(9, 12, 9, nom=nom)
    for y, r in RAYONS.items():
        for x in range(9):
            for z in range(9):
                dx, dz = x - C, z - C
                if not dans(dx, dz, r):
                    continue
                interieur = dans(dx, dz, r - 1)
                if y == 0:                                       # fond plein
                    m[x, y, z] = VERRE_FOND
                elif not interieur:                              # paroi
                    if y in ANNEAUX or abs(dx) == abs(dz):       # anneaux et 4 nervures en diagonale
                        m[x, y, z] = VERRE
                    elif y < NIVEAU:                             # fenêtre sous la surface : le liquide affleure
                        m[x, y, z] = liq
                elif y <= NIVEAU:                                # liquide
                    m[x, y, z] = liq
    # liquide : éclats en surface, un reflet vertical dans la fenêtre avant
    for x, z in ((3, 3), (5, 5), (2, 4), (6, 3)):
        if m[x, NIVEAU, z] == liq:
            m[x, NIVEAU, z] = eclat
    m[3, 3, 8] = m[3, 4, 8] = eclat
    for x in range(9):                                           # fond du liquide plus sombre (caché par l'anneau bas)
        for z in range(9):
            if m[x, 1, z] == liq:
                m[x, 1, z] = ombre
    # col 3 × 3 creux, lèvre 5 × 5 sans les coins
    m.boite(3, 8, 3, 5, 8, 5, VERRE)
    m.boite(2, 9, 2, 6, 9, 6, VERRE)
    for x, z in ((2, 2), (2, 6), (6, 2), (6, 6)):
        m[x, 9, z] = 0
    # bouchon 3 × 3 : du col jusqu'à 2 voxels au-dessus de la lèvre, entaille sombre
    m[4, 8, 4] = BOUCHON_SOMBRE
    m.boite(3, 9, 3, 5, 11, 5, BOUCHON)
    m.boite(3, 9, 3, 5, 9, 5, BOUCHON_SOMBRE)
    m[5, 11, 5] = m[5, 10, 5] = BOUCHON_SOMBRE
    # reflet crème : en marches sur la nervure avant gauche jusqu'à l'épaule
    for x, y, z in ((1, 3, 7), (1, 4, 7), (1, 5, 7), (2, 6, 6), (3, 7, 5)):
        assert m[x, y, z] == VERRE, (x, y, z)
        m[x, y, z] = REFLET
    if nom == "bleue":
        bleue(m, liq)
    return m


SURFACE_BLEUE = 11
REFLETS_BLEUE = ((7, 3, 1), (7, 4, 1), (6, 6, 2), (1, 2, 7), (3, 1, 7), (3, 9, 6), (2, 9, 5))


def bleue(m, liq):
    """Retouches de la bleue (bleu sur bleu) : liquide 9 qui affleure jusqu'à la surface 11, fenêtres vides du haut
    en partie vitrées (plus de « trous » sombres vus de face), reflets crème en plus sur la nervure arrière droite,
    l'anneau bas et la lèvre."""
    for x in range(9):
        for z in range(9):
            dx, dz = x - C, z - C
            if dans(dx, dz, RAYONS[NIVEAU]) and m[x, NIVEAU, z] in (0, liq, 10):
                m[x, NIVEAU, z] = SURFACE_BLEUE                  # surface pleine, jusqu'au bord des fenêtres
            # calque 5 : on vitre les fenêtres sauf la case du milieu de chaque face
            if dans(dx, dz, RAYONS[5]) and not dans(dx, dz, RAYONS[5] - 1) and not m[x, 5, z]:
                if not (min(abs(dx), abs(dz)) == 0):
                    m[x, 5, z] = VERRE
    for x, y, z in ((3, 3, 8), (3, 2, 8), (8, 3, 3), (0, 3, 5), (5, 3, 0)):   # reflets 10 du liquide, un par fenêtre
        assert m[x, y, z] in (liq, 10), (x, y, z)
        m[x, y, z] = 10
    for x, y, z in REFLETS_BLEUE:
        assert m[x, y, z] == VERRE, (x, y, z)
        m[x, y, z] = REFLET


def particules():
    mods = []
    for nom, couleurs in PARTICULES.items():
        for k, i in enumerate(couleurs, 1):
            p = vox.Modele(1, 1, 1, nom=f"{nom}_{k}")
            p[0, 0, 0] = i
            mods.append(p)
    return mods


def fabriquer(sortie):
    os.makedirs(sortie, exist_ok=True)
    fioles = [fiole(n) for n in LIQUIDES]
    vox.ecrire_vox(os.path.join(sortie, "potion.vox"), fioles)
    vox.ecrire_vox(os.path.join(sortie, "potion-particules.vox"), particules())
    # aperçu : les deux fioles côte à côte, quelques particules au-dessus
    tout = vox.Modele(21, 17, 9, nom="apercu")
    for k, f in enumerate(fioles):
        for x, y, z, i in f.voxels():
            tout[x + 12 * k, y, z] = i
        for j, (dx, dy) in enumerate(((3, 13), (6, 14), (4, 16), (2, 15))):
            tout[dx + 12 * k, dy, 4] = PARTICULES[list(LIQUIDES)[k]][j]
    vox.apercu(os.path.join(sortie, "apercu.png"), tout, vue="trois-quarts", taille=4)
    return fioles


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--sortie", default=ICI)
    for f in fabriquer(ap.parse_args().sortie):
        print(f.nom, f.compter(), "voxels", f.couleurs())
