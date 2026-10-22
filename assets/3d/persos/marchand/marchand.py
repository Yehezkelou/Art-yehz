#!/usr/bin/env python3
"""Le marchand en voxels (gobelin chibi articulé) : écrit marchand.vox, marchand.rig.toml et apercu.png à côté de ce script.

    python3 -I assets/3d/persos/marchand/marchand.py
    node outils/rendu3d/rendu3d.mjs --scene assets/3d/persos/marchand/controle.mjs --out <dossier> --debut 0 --fin 18 --ips 12

Version voxel du marchand d'Aseprite (assets/persos/marchand/marchand.lua) : capuche et robe violettes 30/29/31, peau
verte 15/14, grandes oreilles pointues, gros yeux crème 8 (pupille 2), nez vert foncé 14, boutons dorés 19.
Dessin maison (modélisé par Claude, script vox.py), palette ico-pixel-32.

Grille commune du perso (en voxels) : x 0–17 (capuche x 4–13, oreilles x 0–3 et 14–17), y 0–16 (sol à y = 0), z −2–9 (pointe de la capuche derrière)
(l'avant vers +z). Chibi de 16 voxels : babouches 1 (y 0, bout relevé à y 1), robe en cloche d'un bloc 7 (y 1–7), tête 8 (y 8–15).
Le visage est en retrait d'un voxel dans l'ouverture de la capuche ; le nez sort de deux voxels.
Parties : corps (robe, ceinture, bourse), tete (capuche + visage), pointe (pointe de la capuche, qui ballotte), oreille_d / oreille_g (enfants de la tête, elles frémissent),
bras_d / bras_g (pivot sur l'arête haute extérieure), jambe_d / jambe_g (les pieds, sous la robe),
bouche (lèvre du bas : cachée = bouche ouverte), paupieres (clin d'œil) et mi_clos (paupières à demi baissées,
air méfiant), cachées dans la tête au repos et avancées de 2 voxels par marchand.clips.mjs.
"""
import argparse, os, sys, tomllib

ICI = os.path.dirname(os.path.abspath(__file__))
RACINE = os.path.normpath(os.path.join(ICI, "..", "..", "..", ".."))
sys.path.insert(0, os.path.join(RACINE, "outils"))
import vox  # noqa: E402

V, v, VC = 30, 29, 31            # capuche et robe, ombre, reflet
G, g = 15, 14                    # peau verte, ombre (nez, oreilles, paupières)
OEIL, PUPILLE, BOUCHE, GORGE = 8, 2, 2, 21
BOUTON = 19
CEINTURE, BOURSE, BOURSE_O, PIECE, PIECE_O = 26, 27, 26, 27, 25
CHAUSSURE, CHAUSSURE_C = 25, 26
HX = 4                           # la capuche commence à x = 4 dans la grille de la tête (les oreilles avant)


def tete():
    m = vox.Modele(18, 8, 10, nom="tete")
    def c(hx, y, z, i):
        m[HX + hx, y, z] = i
    m.boite(HX, 0, 0, HX + 9, 7, 8, V)                  # capuche pleine
    for hx in (0, 9):                                    # dôme : coins arrondis
        for z in (0, 8):
            c(hx, 7, z, 0)
        c(hx, 0, 0, 0)
    m.boite(HX, 7, 0, HX + 9, 7, 0, 0)
    m.boite(HX + 1, 7, 1, HX + 8, 7, 1, V)
    m.boite(HX + 1, 0, 8, HX + 8, 5, 8, 0)              # ouverture du visage (le bord de la capuche reste à z = 8)
    m.boite(HX + 1, 0, 7, HX + 8, 5, 7, G)              # visage en retrait (z = 7)
    m.boite(HX + 1, 0, 6, HX + 8, 5, 6, G)
    m.boite(HX + 1, 6, 8, HX + 8, 6, 8, VC)             # bord de la capuche éclairé
    c(0, 6, 8, V); c(9, 6, 8, V)
    m.boite(HX + 1, 5, 7, HX + 8, 5, 7, g)              # front dans l'ombre de la capuche
    m.boite(HX, 1, 1, HX, 5, 6, v); m.boite(HX + 9, 1, 1, HX + 9, 5, 6, v)   # flancs ombrés
    for hx, y in ((3, 7), (5, 7), (6, 7)):
        c(hx, y, 3, VC)                                  # plis sur le dessus
    # yeux 3×2 : crème, pupille en bas au milieu
    for x0 in (1, 6):
        for dx in range(3):
            c(x0 + dx, 4, 7, OEIL); c(x0 + dx, 3, 7, OEIL)
        c(x0 + 1, 3, 7, PUPILLE)
    # nez : arête entre les yeux, bout qui sort de deux voxels
    for hx in (4, 5):
        c(hx, 3, 7, g); c(hx, 3, 8, g); c(hx, 2, 8, g); c(hx, 2, 9, g)
    # sourire en coin et bouche
    c(2, 2, 7, BOUCHE); c(7, 2, 7, BOUCHE)
    for hx in range(3, 7):
        c(hx, 1, 7, BOUCHE)
    for hx in (3, 4, 5, 6):
        c(hx, 0, 7, 0); c(hx, 0, 6, GORGE)               # creux de la bouche ouverte (couvert par « bouche »)
    return m


def pointe():
    """Pointe molle de la capuche : part du dessus, retombe dans le dos, pompon doré (perso x 8–9, y 13–16, z −2–2)."""
    m = vox.Modele(2, 4, 5, nom="pointe")
    m.boite(0, 3, 2, 1, 3, 4, V); m[0, 3, 3] = VC; m[0, 3, 4] = VC
    m.boite(0, 2, 1, 1, 2, 2, V)
    m.boite(0, 1, 0, 1, 1, 0, v)
    m.boite(0, 0, 0, 1, 0, 0, BOUTON)                    # pompon
    return m


def oreille_d():
    """Oreille côté −x (x 0–3 de la grille de la tête) : triangle qui pointe vers l'extérieur et un peu vers le haut."""
    m = vox.Modele(4, 4, 2, nom="oreille_d")
    m.boite(3, 0, 0, 3, 2, 1, G)                         # base, contre la capuche
    m.boite(2, 1, 0, 2, 2, 1, G)
    m[1, 2, 1] = G; m[1, 2, 0] = G
    m[0, 3, 1] = G                                       # pointe
    m[3, 1, 1] = g; m[2, 1, 1] = g                       # creux de l'oreille, à l'avant
    return m


def oreille_g():
    return oreille_d().miroir_x("oreille_g")


def bouche():
    m = vox.Modele(4, 1, 1, nom="bouche")
    m.boite(0, 0, 0, 3, 0, 0, G)
    return m


def paupieres():
    m = vox.Modele(8, 2, 1, nom="paupieres")
    for x0 in (0, 5):
        for dx in range(3):
            m[x0 + dx, 1, 0] = g; m[x0 + dx, 0, 0] = BOUCHE   # œil fermé : paupière + trait sombre
    return m


def mi_clos():
    m = vox.Modele(8, 1, 1, nom="mi_clos")
    for x0 in (0, 5):
        for dx in range(3):
            m[x0 + dx, 0, 0] = g
    return m


def corps():
    m = vox.Modele(11, 7, 7, nom="corps")                # robe en cloche : y 0–2 (10 de large), y 3 (8), y 4–6 (6) ; x 10 : bourse
    m.boite(0, 0, 0, 9, 2, 6, V)
    m.boite(1, 3, 1, 8, 3, 5, V)
    m.boite(2, 4, 2, 7, 6, 5, V)
    m.boite(0, 0, 0, 9, 0, 6, v)                        # ourlet
    for x in (0, 9):
        m.boite(x, 1, 0, x, 2, 6, v)                     # côtés de la cloche dans l'ombre
    m.boite(2, 4, 2, 2, 5, 5, v); m.boite(7, 4, 2, 7, 5, 5, v)
    m.boite(3, 6, 2, 6, 6, 5, v)                        # col, dans l'ombre de la tête
    for x in (0, 9):
        for z in (0, 6):
            m[x, 2, z] = 0                               # coins arrondis du haut de la cloche
    m[4, 1, 6] = BOUTON; m[4, 5, 5] = BOUTON               # boutons
    m.boite(1, 2, 6, 3, 2, 6, VC)                       # reflet sur la cloche
    m.boite(1, 3, 1, 8, 3, 5, CEINTURE)                 # ceinture
    m[4, 3, 5] = BOUTON                                  # boucle
    m.boite(6, 1, 0, 7, 2, 0, PIECE); m[7, 2, 0] = PIECE_O; m[6, 1, 0] = PIECE_O   # pièce cousue dans le dos
    m.boite(10, 0, 3, 10, 1, 4, BOURSE); m[10, 2, 3] = BOURSE_O; m[10, 2, 4] = BOURSE_O   # bourse pendue à la hanche
    m[10, 0, 4] = BOUTON                                 # une pièce d'or qui dépasse
    return m


def bras_d():
    m = vox.Modele(2, 3, 2, nom="bras_d")
    m.boite(0, 2, 0, 1, 2, 1, V)
    m.boite(0, 1, 0, 1, 1, 1, VC)                       # revers de la manche
    m.boite(0, 0, 0, 1, 0, 1, G)
    m[0, 2, 0] = v; m[0, 2, 1] = v
    return m


def bras_g():
    return bras_d().miroir_x("bras_g")


def jambe_d():
    m = vox.Modele(2, 2, 5, nom="jambe_d")               # babouche : semelle d'un voxel, bout pointu relevé
    m.boite(0, 0, 0, 1, 0, 3, CHAUSSURE)
    m[0, 1, 4] = CHAUSSURE_C; m[1, 1, 4] = CHAUSSURE_C
    m[0, 0, 4] = CHAUSSURE; m[1, 0, 4] = CHAUSSURE
    return m


def jambe_g():
    return jambe_d().miroir_x("jambe_g")


# nom, modèle, origine, pivot, parent
PARTIES = [
    ("corps", corps, (4, 1, 0), (9, 1, 4), None),
    ("tete", tete, (0, 8, 0), (9, 8, 4), "corps"),
    ("pointe", pointe, (8, 13, -2), (9, 16, 3), "tete"),
    ("oreille_d", oreille_d, (0, 11, 5), (4, 14, 6), "tete"),
    ("oreille_g", oreille_g, (14, 11, 5), (14, 14, 6), "tete"),
    ("bouche", bouche, (7, 8, 7), (9, 8, 7), "tete"),
    ("paupieres", paupieres, (5, 11, 6), (9, 12, 6), "tete"),
    ("mi_clos", mi_clos, (5, 12, 6), (9, 12, 6), "tete"),
    ("bras_d", bras_d, (4, 5, 3), (4, 8, 4), "corps"),
    ("bras_g", bras_g, (12, 5, 3), (14, 8, 4), "corps"),
    ("jambe_d", jambe_d, (6, 0, 3), (7, 1, 5.5), "corps"),
    ("jambe_g", jambe_g, (10, 0, 3), (11, 1, 5.5), "corps"),
]
CACHEES = ("paupieres", "mi_clos")


def rig_toml(fichier):
    l = ["# Rig du marchand (assets/3d/persos/marchand/marchand.py) : coordonnées en voxels, grille commune du perso.",
         "# Clips : idle, marche, saut, parle, coucou, non_de_la_tete (marchand.clips.mjs, à installer).",
         'nom = "marchand"', "echelle = 1", "sol = [9, 0, 4]          # sous le milieu de la robe (origine du groupe)", ""]
    for nom, f, o, pv, parent in PARTIES:
        l += [f"[parties.{nom}]", f'fichier = "{fichier}"', f'modele = "{nom}"',
              f"origine = [{o[0]}, {o[1]}, {o[2]}]", f"pivot = [{pv[0]}, {pv[1]}, {pv[2]}]"]
        if parent:
            l.append(f'parent = "{parent}"')
        l.append("")
    return "\n".join(l)


def fabriquer(sortie):
    os.makedirs(sortie, exist_ok=True)
    modeles = [f() for _, f, *_ in PARTIES]
    for (nom, *_), m in zip(PARTIES, modeles):
        assert m.nom == nom, (m.nom, nom)
    vx = os.path.join(sortie, "marchand.vox")
    vox.ecrire_vox(vx, modeles)
    texte = rig_toml("marchand.vox")
    tomllib.loads(texte)
    with open(os.path.join(sortie, "marchand.rig.toml"), "w", encoding="utf-8", newline="\n") as fh:
        fh.write(texte)
    tout = vox.Modele(18, 17, 12, nom="marchand")
    for (nom, _, o, _, _), m in zip(PARTIES, modeles):
        if nom in CACHEES:
            continue
        for x, y, z, i in m.voxels():
            tout[o[0] + x, o[1] + y, o[2] + z + 2] = i      # + 2 en z : la pointe descend à z = −2
    vox.apercu(os.path.join(sortie, "apercu.png"), tout, vue="trois-quarts", taille=4)
    return vx, sum(m.compter() for m in modeles)


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--sortie", default=ICI)
    vx, n = fabriquer(ap.parse_args().sortie)
    print(f"{vx} : {n} voxels")
