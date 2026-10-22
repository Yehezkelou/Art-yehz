#!/usr/bin/env python3
"""Tim en voxels (chibi articulé) : écrit tim.vox, tim.rig.toml, tim-sans-baton.rig.toml et apercu.png à côté de ce script.

    python3 -I assets/3d/persos/tim/tim.py
    node outils/rendu3d/rendu3d.mjs --scene assets/3d/persos/tim/controle.mjs --out <dossier> --debut 0 --fin 12 --ips 12

Version voxel du Tim d'Aseprite (assets/persos/tim/tim.lua) : cheveux 17/18, peau 28/27, joues 24, yeux crème 8 +
pupille 2, foulard rouge 23, tunique verte 15/14, ceinture 26, pantalon bleu 10/9, bottes 25 ; bâton à gemme bleue.
Dessin maison (modélisé par Claude, script vox.py), palette ico-pixel-32.

Grille commune du perso (en voxels) : x 0–12 (le manche du bâton à x = 11, un voxel d'écart avec la tête), y 0–18 (sol à y = 0), z 0–9, l'avant vers +z.
Chibi de 16 voxels : jambes 4 (y 0–3), corps 4 (y 4–7), tête 8 (y 8–15) ; le bâton monte jusqu'à y = 18.
Chaque partie a sa grille propre posée par `origine` (coin de la partie dans la grille du perso) ; `pivot` = point de
rotation. Épaules : pivot sur l'arête haute EXTÉRIEURE du bras (le bras levé s'écarte de la tête au lieu d'y entrer).

Parties d'expression (enfants de la tête) : « paupieres » (clin d'œil), « sourcils » (colère). Au repos, elles sont
cachées DANS la tête (une couche derrière la face) ; tim.clips.mjs les avance de 2 voxels pour les montrer (elles
dépassent alors d'un voxel, sous la frange qui dépasse aussi). « bouche » = la lèvre du bas : visible = bouche fermée ;
le clip « parle » de base la cache par moments → bouche ouverte (fond rouge sombre 21).

Deux rigs : tim.rig.toml (bâton dans la main gauche ; ce bras a le rôle « bras_baton », que les clips de base
n'animent pas : le bâton reste tenu sans traverser la tête) et tim-sans-baton.rig.toml (deux bras libres).
"""
import argparse, os, sys, tomllib

ICI = os.path.dirname(os.path.abspath(__file__))
RACINE = os.path.normpath(os.path.join(ICI, "..", "..", "..", ".."))
sys.path.insert(0, os.path.join(RACINE, "outils"))
import vox  # noqa: E402

H, h = 17, 18                    # cheveux, reflet
S, s, JOUE = 28, 27, 24          # peau, ombre, joues
OEIL, PUPILLE, BOUCHE, GORGE = 8, 2, 2, 21
FOULARD, FOULARD_O = 23, 22
T, t = 15, 14                    # tunique, ombre
CEINT, BOUCLE = 26, 18
P, p = 10, 9                     # pantalon, ombre
BOTTE, BOTTE_H = 25, 26
SOURCIL = 25                     # sourcils froncés (plus sombres que la frange)
BOIS, BOIS_O, BOIS_C = 26, 25, 27
GEMME, GEMME_O, GEMME_C = 11, 10, 12



def tete():
    m = vox.Modele(10, 9, 9, nom="tete")             # y 8 : l'épi
    m.boite(0, 0, 1, 9, 6, 7, S)                       # bloc de peau (face avant à z = 7)
    m.boite(0, 6, 0, 9, 7, 7, H)                       # calotte
    m.boite(0, 1, 0, 9, 7, 1, H)                       # arrière
    m.boite(0, 1, 0, 0, 7, 4, H)                       # côtés (la peau ne revient qu'à l'avant)
    m.boite(9, 1, 0, 9, 7, 4, H)
    m.boite(0, 5, 5, 0, 7, 6, H)                       # pattes au-dessus des oreilles
    m.boite(9, 5, 5, 9, 7, 6, H)
    for x, c in enumerate("H..HHHH..H"):                # frange, rangée y = 5, sur la face
        m[x, 5, 7] = H if c != "." else S
    m.boite(0, 6, 8, 9, 6, 8, H)                       # frange qui dépasse d'un voxel (z = 8)
    for x, c in enumerate("H..HHHH..H"):
        if c != ".":
            m[x, 5, 8] = H
    m[3, 6, 8] = h; m[4, 6, 8] = h; m[4, 5, 8] = h       # reflets de la frange
    m[2, 7, 6] = h; m[3, 7, 6] = h; m[3, 7, 5] = h       # reflet sur le dessus
    for x, y, z in [(0, 7, 0), (9, 7, 0), (0, 7, 7), (9, 7, 7), (0, 1, 0), (9, 1, 0)]:
        m[x, y, z] = 0                                 # coins arrondis
    m.boite(0, 0, 0, 9, 0, 0, 0)
    m[4, 8, 3] = H; m[5, 8, 3] = h; m[5, 8, 2] = H       # épi sur le dessus
    for x in (1, 4, 7):
        m[x, 1, 0] = 0                                   # pointes de la nuque
    for x, y in ((2, 5), (3, 5), (6, 4), (7, 6), (4, 3)):
        m[x, y, 0] = h                                   # mèches à l'arrière
    # visage (z = 7) : yeux 2×2 (crème côté extérieur, pupille côté intérieur), joues, bouche
    for x0, pup in ((1, 2), (7, 7)):
        for y in (3, 4):
            m[x0, y, 7] = OEIL; m[x0 + 1, y, 7] = OEIL
            m[pup, y, 7] = PUPILLE
    m[1, 2, 7] = JOUE; m[8, 2, 7] = JOUE
    m[4, 1, 7] = BOUCHE; m[5, 1, 7] = BOUCHE
    m[4, 0, 7] = 0; m[5, 0, 7] = 0                       # creux de la bouche ouverte (couvert par « bouche »)
    m[4, 0, 6] = GORGE; m[5, 0, 6] = GORGE
    m[0, 0, 7] = s; m[9, 0, 7] = s                       # menton ombré
    return m


def bouche():
    m = vox.Modele(2, 1, 1, nom="bouche")
    m.boite(0, 0, 0, 1, 0, 0, S)
    return m


def paupieres():
    m = vox.Modele(8, 2, 1, nom="paupieres")
    for x0 in (0, 6):
        m[x0, 1, 0] = S; m[x0 + 1, 1, 0] = S               # paupière
        m[x0, 0, 0] = BOUCHE; m[x0 + 1, 0, 0] = BOUCHE     # cils (œil fermé = trait sombre)
    return m


def sourcils():
    m = vox.Modele(8, 2, 1, nom="sourcils")
    m[0, 1, 0] = SOURCIL; m[1, 0, 0] = SOURCIL                     # « \ » au-dessus de l'œil droit (côté −x)
    m[6, 0, 0] = SOURCIL; m[7, 1, 0] = SOURCIL                     # « / » au-dessus de l'œil gauche
    return m


def corps():
    m = vox.Modele(6, 4, 5, nom="corps")                 # z 1–4 : le corps ; z 0 : pan du foulard dans le dos
    m.boite(0, 0, 1, 5, 3, 4, T)
    m.boite(0, 0, 1, 0, 2, 4, t); m.boite(5, 0, 1, 5, 2, 4, t)
    m.boite(0, 1, 1, 5, 1, 4, CEINT)
    m[2, 1, 4] = BOUCLE; m[3, 1, 4] = BOUCLE
    m.boite(0, 3, 1, 5, 3, 4, FOULARD)
    m[2, 3, 4] = FOULARD_O; m[3, 3, 4] = FOULARD_O       # nœud
    m[3, 3, 0] = FOULARD; m[3, 2, 0] = FOULARD; m[2, 1, 0] = FOULARD_O   # pan qui pend dans le dos
    return m


def bras_d():
    m = vox.Modele(2, 3, 2, nom="bras_d")
    m.boite(0, 1, 0, 1, 2, 1, T)
    m.boite(0, 2, 0, 0, 2, 1, t)                         # épaule, côté extérieur
    m.boite(0, 0, 0, 1, 0, 1, S)
    m[0, 0, 0] = s
    return m


def bras_g():
    return bras_d().miroir_x("bras_g")


def bras_g_baton():
    m = vox.Modele(4, 3, 3, nom="bras_g_baton")          # x 0–1 = le bras ; x 2–3 = le poing autour du manche
    b = bras_g()
    for x, y, z, i in b.voxels():
        m[x, y, z] = i
    m.boite(2, 0, 0, 2, 0, 2, S)                         # poing (perso x 10)
    m[3, 0, 0] = s; m[3, 0, 2] = S                       # doigts devant et derrière le manche (perso x 11, z 4)
    return m


def baton():
    m = vox.Modele(3, 18, 3, nom="baton")                # manche à x = 1, z = 1 (perso : x 11, z 4)
    m.boite(1, 0, 1, 1, 14, 1, BOIS)
    for y in (0, 7, 14):
        m[1, y, 1] = BOIS_O
    m[1, 10, 1] = BOIS_C; m[1, 2, 1] = BOIS_C
    m[1, 15, 1] = GEMME_O                                # gemme en losange de 3 voxels de haut
    for dx, dz in ((0, 1), (2, 1), (1, 0), (1, 2), (1, 1)):
        m[dx, 16, dz] = GEMME
    m[1, 17, 1] = GEMME_C
    return m


def jambe_d():
    m = vox.Modele(2, 4, 3, nom="jambe_d")
    m.boite(0, 2, 0, 1, 3, 1, P)
    m.boite(0, 2, 0, 0, 2, 1, p)
    m.boite(0, 0, 0, 1, 1, 1, BOTTE)
    m.boite(0, 0, 2, 1, 0, 2, BOTTE)                     # bout de la botte
    m[0, 1, 1] = BOTTE_H; m[1, 1, 1] = BOTTE_H           # revers
    return m


def jambe_g():
    return jambe_d().miroir_x("jambe_g")


# nom, modèle, origine, pivot, parent, rôle
COMMUN = [
    ("corps", corps, (2, 4, 1), (5, 4, 4), None, None),
    ("tete", tete, (0, 8, 0), (5, 8, 4), "corps", None),
    ("bouche", bouche, (4, 8, 7), (5, 8, 7), "tete", None),
    ("paupieres", paupieres, (1, 11, 6), (5, 12, 6), "tete", None),
    ("sourcils", sourcils, (1, 12, 6), (5, 13, 6), "tete", None),
    ("bras_d", bras_d, (0, 5, 3), (0, 8, 4), "corps", None),
    ("jambe_d", jambe_d, (3, 0, 3), (4, 4, 4.5), "corps", None),
    ("jambe_g", jambe_g, (5, 0, 3), (6, 4, 4.5), "corps", None),
]
AVEC_BATON = COMMUN + [
    ("bras_g", bras_g_baton, (8, 5, 3), (10, 8, 4), "corps", "bras_baton"),
    ("baton", baton, (10, 1, 3), (11, 5, 4), "bras_g", None),
]
SANS_BATON = COMMUN + [
    ("bras_g", bras_g, (8, 5, 3), (10, 8, 4), "corps", None),
]


def rig_toml(parties, fichier, titre):
    l = [f"# {titre} (assets/3d/persos/tim/tim.py) : coordonnées en voxels, grille commune du perso.",
         "# Clips de base : idle, marche, saut, parle, coucou ; tim.clips.mjs ajoute colere et le clin d'œil.",
         'nom = "tim"', "echelle = 1", "sol = [5, 0, 4]          # milieu des pieds (origine du groupe)", ""]
    for nom, f, o, pv, parent, role in parties:
        l += [f"[parties.{nom}]", f'fichier = "{fichier}"', f'modele = "{f().nom}"',
              f"origine = [{o[0]}, {o[1]}, {o[2]}]", f"pivot = [{pv[0]}, {pv[1]}, {pv[2]}]"]
        if parent:
            l.append(f'parent = "{parent}"')
        if role:
            l.append(f'role = "{role}"')
        l.append("")
    l += ["[clips.balade]", 'base = "marche"', "vitesse = 0.7", "amplitude = 0.7", ""]
    return "\n".join(l)


def assembler(parties, nom):
    tout = vox.Modele(13, 19, 10, nom=nom)
    for _, f, o, _, _, _ in parties:
        m = f()
        if m.nom in ("paupieres", "sourcils"):
            continue                                      # cachées dans la tête au repos
        for x, y, z, i in m.voxels():
            tout[o[0] + x, o[1] + y, o[2] + z] = i
    return tout


def fabriquer(sortie):
    os.makedirs(sortie, exist_ok=True)
    vus, modeles = set(), []
    for _, f, *_ in AVEC_BATON + SANS_BATON:
        m = f()
        if m.nom not in vus:
            vus.add(m.nom); modeles.append(m)
    vx = os.path.join(sortie, "tim.vox")
    vox.ecrire_vox(vx, modeles)
    for parties, fic, titre in ((AVEC_BATON, "tim.rig.toml", "Rig de Tim avec son bâton"),
                                (SANS_BATON, "tim-sans-baton.rig.toml", "Rig de Tim sans bâton")):
        texte = rig_toml(parties, "tim.vox", titre)
        tomllib.loads(texte)
        with open(os.path.join(sortie, fic), "w", encoding="utf-8", newline="\n") as fh:
            fh.write(texte)
    vox.apercu(os.path.join(sortie, "apercu.png"), assembler(AVEC_BATON, "tim"), vue="trois-quarts", taille=4)
    return vx, sum(m.compter() for m in modeles), sum(f().compter() for _, f, *_ in AVEC_BATON)


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--sortie", default=ICI)
    vx, n_fichier, n_rig = fabriquer(ap.parse_args().sortie)
    print(f"{vx} : {n_fichier} voxels dans le fichier, {n_rig} dans le rig avec bâton")
