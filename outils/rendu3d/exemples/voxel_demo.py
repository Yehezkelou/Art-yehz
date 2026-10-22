#!/usr/bin/env python3
"""Démo de la chaîne voxel : un petit chibi en 6 parties (tête, corps, bras, jambes) + son rig, à côté de ce script.

    python3 -I outils/rendu3d/exemples/voxel_demo.py                 # → voxel_demo.vox, .rig.toml, .caisse.png, .apercu.png
    python3 -I outils/rendu3d/exemples/voxel_demo.py --sortie <dossier>
    node outils/rendu3d/rendu3d.mjs --scene outils/rendu3d/exemples/voxel_demo.mjs --out <dossier> --debut 0 --fin 2 --ips 12

Démo seulement, pas un asset de chaîne (rien dans assets/). Toutes les parties sont dessinées dans la grille commune du
perso (x 0–9, y 0–16, z 0–7, l'avant vers +z) : chaque partie a sa propre grille, posée par `origine` (coin de la partie
dans la grille du perso) ; `pivot` = point de rotation, dans la même grille. Les 6 modèles vont dans un seul .vox
(noms « tete », « corps »…), que MagicaVoxel ouvre côte à côte.
"""
import argparse, os, sys, tomllib

ICI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(ICI, "..", ".."))
import vox  # noqa: E402

PEAU, CHEVEUX, TUNIQUE, CEINTURE, BOUCLE, PANTALON, CHAUSSURE, OEIL, JOUE, BOUCHE = 28, 18, 11, 19, 20, 4, 26, 1, 24, 22


def tete():
    m = vox.Modele(8, 8, 8, nom="tete")
    m.boite(0, 0, 1, 7, 6, 7, PEAU)
    m.boite(0, 6, 0, 7, 7, 7, CHEVEUX)        # dessus
    m.boite(0, 1, 0, 7, 7, 1, CHEVEUX)        # arrière
    m.boite(0, 3, 0, 0, 7, 4, CHEVEUX)        # côtés
    m.boite(7, 3, 0, 7, 7, 4, CHEVEUX)
    # visage, calque par calque (un calque par hauteur y, une ligne : z = 7, la face avant)
    m.calques([
        ["........"],
        ["...bb..."],
        [".j....j."],
        ["..o..o.."],
        ["..o..o.."],
        ["........"],
        ["cc.c.ccc"],                          # frange
    ], {"o": OEIL, "j": JOUE, "b": BOUCHE, "c": CHEVEUX}, z0=7)
    return m


def corps():
    m = vox.Modele(6, 5, 4, nom="corps")
    m.boite(0, 0, 0, 5, 4, 3, TUNIQUE)
    m.boite(0, 1, 0, 5, 1, 3, CEINTURE)
    m[2, 1, 3] = BOUCLE
    m[3, 1, 3] = BOUCLE
    m.boite(1, 4, 0, 4, 4, 3, PEAU)            # cou
    m.boite(0, 4, 0, 0, 4, 3, TUNIQUE)
    m.boite(5, 4, 0, 5, 4, 3, TUNIQUE)
    return m


def bras_d():
    m = vox.Modele(2, 4, 2, nom="bras_d")
    m.boite(0, 1, 0, 1, 3, 1, TUNIQUE)
    m.boite(0, 0, 0, 1, 0, 1, PEAU)
    m[0, 3, 0] = 10                            # pli de l'épaule, côté extérieur
    return m


def jambe_d():
    m = vox.Modele(2, 4, 3, nom="jambe_d")
    m.boite(0, 1, 0, 1, 3, 1, PANTALON)
    m.boite(0, 0, 0, 1, 0, 2, CHAUSSURE)
    return m


PARTIES = [  # nom, modèle, origine, pivot, parent
    ("corps", corps, (2, 4, 2), (5, 4, 4), None),
    ("tete", tete, (1, 9, 0), (5, 9, 4), "corps"),
    ("bras_d", bras_d, (0, 5, 3), (1, 9, 4), "corps"),
    ("bras_g", lambda: bras_d().miroir_x("bras_g"), (8, 5, 3), (9, 9, 4), "corps"),
    ("jambe_d", jambe_d, (2, 0, 3), (3, 4, 4), "corps"),
    ("jambe_g", lambda: jambe_d().copier("jambe_g"), (6, 0, 3), (7, 4, 4), "corps"),
]


def rig_toml(fichier):
    l = ["# Rig de démonstration (outils/rendu3d/exemples/voxel_demo.py) : coordonnées en voxels, grille du perso.",
         'nom = "chibi-demo"', "echelle = 1", "sol = [5, 0, 4]          # milieu du dessous (origine du groupe)", ""]
    for nom, _, o, p, parent in PARTIES:
        l += [f"[parties.{nom}]", f'fichier = "{fichier}"', f'modele = "{nom}"',
              f"origine = [{o[0]}, {o[1]}, {o[2]}]", f"pivot = [{p[0]}, {p[1]}, {p[2]}]"]
        if parent:
            l.append(f'parent = "{parent}"')
        l.append("")
    l += ["[clips.marche]", "vitesse = 1.0", "", "[clips.balade]", 'base = "marche"', "vitesse = 0.6",
          "amplitude = 0.7", ""]
    return "\n".join(l)


def caisse():
    """Texture 8×8 d'une caisse (planches 27, cadre 26, clous 3)."""
    pal = vox.lire_palette()
    c = lambda i: pal[i - 1] + (255,)  # noqa: E731
    px = []
    for y in range(8):
        for x in range(8):
            if (x, y) in ((1, 1), (6, 1), (1, 6), (6, 6)):
                px.append(c(3))
            elif x in (0, 7) or y in (0, 7) or x == y:
                px.append(c(26))
            else:
                px.append(c(28 if y in (2, 5) else 27))  # planches horizontales
    return px


def fabriquer(sortie):
    os.makedirs(sortie, exist_ok=True)
    modeles = [f() for _, f, *_ in PARTIES]
    for (nom, *_), m in zip(PARTIES, modeles):
        assert m.nom == nom, (m.nom, nom)
    vx = os.path.join(sortie, "voxel_demo.vox")
    vox.ecrire_vox(vx, modeles)
    texte = rig_toml("voxel_demo.vox")
    tomllib.loads(texte)  # le rig doit rester du TOML standard
    with open(os.path.join(sortie, "voxel_demo.rig.toml"), "w", encoding="utf-8", newline="\n") as f:
        f.write(texte)
    vox.ecrire_png(os.path.join(sortie, "voxel_demo.caisse.png"), 8, 8, caisse())
    # aperçu : le perso assemblé dans sa grille commune
    tout = vox.Modele(10, 17, 8, nom="chibi")
    for (nom, _, o, _, _), m in zip(PARTIES, modeles):
        for x, y, z, i in m.voxels():
            tout[o[0] + x, o[1] + y, o[2] + z] = i
    vox.apercu(os.path.join(sortie, "voxel_demo.apercu.png"), tout, vue="trois-quarts", taille=2)
    return vx


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--sortie", default=ICI)
    print(fabriquer(ap.parse_args().sortie))
