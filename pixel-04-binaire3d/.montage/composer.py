#!/usr/bin/env python3
"""pixel-04-binaire3d : compose « 0,1 + 0,2 » (version 3D) image par image (270×480, 24 i/s, opaque), agrandit ×4 en
pixels nets (ffmpeg, voisin le plus proche) et écrit la séquence 1080×1920 + la liste des bruitages.

    python3 -I pixel-04-binaire3d/.montage/composer.py [--images 0,120,300]   # sans argument : tout

Sortie : .montage/scene/scene_0000.png … (ignoré par git), .montage/evenements.json (un son = un marqueur
= un effet, lu par sons.py). Les 7 séquences 3D (.montage/3d/<nom>/, outils/rendu3d) sont superposées à leur
instant. Caméra, textes et effets à 24 i/s ; persos à 12 i/s (bible). Positions et
agrandissements entiers, palette ico-pixel-32, ni flou ni semi-transparence. Les instants viennent des
mots de la voix (minutage.py). Décors et objets : assets/decors/binaire/ ; persos : assets/persos/.
"""
import json, math, os, subprocess, sys

sys.dont_write_bytecode = True                   # pas de __pycache__ dans assets/ (manifeste)

ICI = os.path.dirname(os.path.abspath(__file__))
EP = os.path.dirname(ICI)
RACINE = os.path.dirname(EP)
sys.path[:0] = [ICI, os.path.join(RACINE, "outils"), os.path.join(RACINE, "assets", "polices")]
import png, ico5x7  # noqa: E402
from minutage import mot as M, SOUS_TITRES  # noqa: E402

L, H, IPS = 270, 480, 24
DUREE = 75.9                                    # la signature du modèle suit (75,9–76,9 s)
N = round(DUREE * IPS)

HEX = ("0E0D18 1D1B2E 2F2C45 4A4663 6E6A80 9A96A6 C9C4C8 F2EDE4 1F2E5C 3E5BA9 5E8FD6 9CC7F0 "
       "1E4D3A 2E7D4F 3FB56B 8FDB86 7A4E1E B9802B F4C542 FBE58C 5A1E2B 9E2F33 E5533D F59A7A "
       "3B2A22 6B4A35 9C7451 C9A57A 3D2550 6B3F87 A066B8 E0A6D9").split()
C = [None] + [bytes.fromhex(h) for h in HEX]
NUIT, CONTOUR, OMBRE, CREME, VERT, OR, OR_CLAIR, ROUGE, ROUGE_S = C[1], C[2], C[3], C[8], C[15], C[19], C[20], C[23], C[22]

# ---------------------------------------------------------------- chargement des images
A = os.path.join(RACINE, "assets")


def charger(chemin):
    w, h, px = png.lire(chemin)
    return w, h, px


def decor(nom):
    w, h, px = charger(os.path.join(A, "decors", "binaire", nom))
    return w, [b"".join(bytes(p[:3]) for p in px[y * w:(y + 1) * w]) for y in range(h)]


def sprite(px, w, x0, y0, cw, ch):
    return (cw, ch, [(x, y, bytes(px[(y0 + y) * w + x0 + x][:3])) for y in range(ch) for x in range(cw)
                     if px[(y0 + y) * w + x0 + x][3]])


def planche(chemin, cw, ch):
    w, h, px = charger(chemin)
    return [sprite(px, w, i * cw, r * ch, cw, ch) for r in range(h // ch) for i in range(w // cw)]


def objet(nom):
    w, h, px = charger(os.path.join(A, "decors", "binaire", f"objet-{nom}.png"))
    return sprite(px, w, 0, 0, w, h)


D = {n: decor(n + ".png") for n in ("boutique", "atelier", "classe", "circuit", "ecrans")}
TIM = planche(os.path.join(A, "persos", "tim", "tim-planche.png"), 32, 32)            # 0-3 repos, 4-7 marche
FOUILLE_A, FOUILLE_B, TEND, REGARDE = planche(os.path.join(A, "persos", "tim", "tim-potion-planche.png"), 32, 32)
MAR = planche(os.path.join(A, "persos", "marchand", "marchand-planche.png"), 32, 32)  # repos, caisse ×2, yeux, prend
OBJ = planche(os.path.join(A, "objets", "potion", "potion-planche.png"), 16, 16)      # bleue, rouge, caisse, pièce
COMPTOIR = planche(os.path.join(A, "objets", "potion", "comptoir.png"), 80, 10)[0]
ETINCELLE = planche(os.path.join(A, "objets", "sort", "sort-planche.png"), 16, 16)[1]
O = {n: objet(n) for n in ("tarte", "ciseaux", "loupe", "fleche", "question", "infini", "tampon")}

# petite police 3×5 (chiffres de potion.lua + signes de la console)
P35 = {
    "0": ["###", "#.#", "#.#", "#.#", "###"], "1": [".#.", "##.", ".#.", ".#.", "###"],
    "2": ["###", "..#", "###", "#..", "###"], "3": ["###", "..#", ".##", "..#", "###"],
    "4": ["#.#", "#.#", "###", "..#", "..#"], "5": ["###", "#..", "###", "..#", "###"],
    "6": ["###", "#..", "###", "#.#", "###"], "7": ["###", "..#", "..#", ".#.", ".#."],
    "8": ["###", "#.#", "###", "#.#", "###"], "9": ["###", "#.#", "###", "..#", "###"],
    ",": [".", ".", ".", "#", "#"], ".": [".", ".", ".", ".", "#"], "+": ["...", ".#.", "###", ".#.", "..."],
    "=": ["...", "###", "...", "###", "..."], ">": ["#..", ".#.", "..#", ".#.", "#.."], " ": ["..", "..", "..", "..", ".."],
}
POLICES = {"5x7": ico5x7.G, "3x5": P35}

# ---------------------------------------------------------------- dessin
def neuf(c=NUIT):
    return bytearray(c * (L * H))


def fond(buf, nom, ox=0, oy=0):
    w, rows = D[nom]
    for y in range(H):
        sy = y + oy
        if 0 <= sy < len(rows):
            buf[y * L * 3:(y + 1) * L * 3] = rows[sy][ox * 3:(ox + L) * 3]


def rect(buf, x0, y0, x1, y1, c):
    x0, x1 = max(0, x0), min(L - 1, x1)
    if x1 < x0:
        return
    ligne = c * (x1 - x0 + 1)
    for y in range(max(0, y0), min(H - 1, y1) + 1):
        buf[(y * L + x0) * 3:(y * L + x1 + 1) * 3] = ligne


def pt(buf, x, y, c):
    if 0 <= x < L and 0 <= y < H:
        buf[(y * L + x) * 3:(y * L + x) * 3 + 3] = c


def poser(buf, spr, x0, y0, z=1, teinte=None):
    for x, y, c in spr[2]:
        if z == 1:
            pt(buf, x0 + x, y0 + y, teinte or c)
        else:
            rect(buf, x0 + z * x, y0 + z * y, x0 + z * x + z - 1, y0 + z * y + z - 1, teinte or c)


def poser_centre(buf, spr, cx, cy, z):
    poser(buf, spr, cx - spr[0] * z // 2, cy - spr[1] * z // 2, z)


def largeur(texte, z, police="5x7"):
    g = POLICES[police]
    return z * (sum(len(g[c][0]) + 1 for c in texte) - 1) if texte else 0


def ecrire(buf, texte, x, y, c, z=1, police="5x7", couleur_de=None):
    """Écrit `texte` à (x, y) coin haut gauche ; couleur_de(i) peut changer la couleur du i-ème caractère."""
    g = POLICES[police]
    for i, ch in enumerate(texte):
        cc = couleur_de(i) if couleur_de else c
        for yy, l in enumerate(g[ch]):
            for xx, v in enumerate(l):
                if v == "#":
                    rect(buf, x + z * xx, y + z * yy, x + z * xx + z - 1, y + z * yy + z - 1, cc)
        x += z * (len(g[ch][0]) + 1)


def ecrire_centre(buf, texte, cx, cy, c, z, police="5x7", couleur_de=None):
    h = len(POLICES[police]["0"]) * z
    ecrire(buf, texte, cx - largeur(texte, z, police) // 2, cy - h // 2, c, z, police, couleur_de)


def pop(t, t0, z):
    """Agrandissement d'un élément qui « poppe » à t0 : invisible avant, z+1 deux images, puis z."""
    f = (t - t0) * IPS
    if f < 0:
        return 0
    return z + 1 if f < 2 else z


def cartouche(buf, texte, cx, cy, z, police="5x7", marge=None):
    """Fond sombre derrière un texte posé sur un décor chargé (bord d'1 px plus clair)."""
    m = marge if marge is not None else 2 * z
    w, h = largeur(texte, z, police), len(POLICES[police]["0"]) * z
    x0, y0 = cx - w // 2 - m, cy - h // 2 - m
    rect(buf, x0 - 1, y0 - 1, x0 + w + 2 * m, y0 + h + 2 * m, C[4])
    rect(buf, x0, y0, x0 + w + 2 * m - 1, y0 + h + 2 * m - 1, CONTOUR)


def texte_pop(buf, texte, cx, cy, c, t, t0, z, police="5x7", couleur_de=None, fond_sombre=False):
    zz = pop(t, t0, z)
    if zz:
        if fond_sombre:
            cartouche(buf, texte, cx, cy, zz, police)
        ecrire_centre(buf, texte, cx, cy, c, zz, police, couleur_de)


def lisse(u):
    u = min(1.0, max(0.0, u))
    return u * u * (3 - 2 * u)


def entre(t, t0, t1):
    return lisse((t - t0) / (t1 - t0)) if t1 > t0 else float(t >= t0)


def camera(buf, z, cx, cy):
    """Zoom entier z centré sur (cx, cy), recadré dans l'image (voisin le plus proche)."""
    if z == 1:
        return buf
    w, h = L // z, H // z
    x0, y0 = min(max(0, round(cx) - w // 2), L - w), min(max(0, round(cy) - h // 2), H - h)
    out = bytearray()
    for y in range(h):
        base = ((y0 + y) * L + x0) * 3
        ligne = b"".join(bytes(buf[base + 3 * i:base + 3 * i + 3]) * z for i in range(w))
        ligne += ligne[-3:] * (L - w * z)
        out += ligne * z
    out += out[-L * 3:] * (H - h * z)
    return out


def secouer(buf, dx, dy):
    if not dx and not dy:
        return buf
    out = neuf(CONTOUR)
    for y in range(H):
        sy = y - dy
        if 0 <= sy < H:
            src = buf[sy * L * 3:(sy + 1) * L * 3]
            if dx > 0:
                out[(y * L + dx) * 3:(y + 1) * L * 3] = src[:(L - dx) * 3]
            elif dx < 0:
                out[y * L * 3:((y + 1) * L + dx) * 3] = src[-dx * 3:]
            else:
                out[y * L * 3:(y + 1) * L * 3] = src
    return out


def secousse(t, t0, amp, duree=0.4):
    """Décalage (dx, dy) d'une secousse qui s'amortit, en pixels entiers."""
    u = t - t0
    if not 0 <= u < duree:
        return 0, 0
    a = max(1, round(amp * (1 - u / duree)))
    f = int(u * IPS)
    return (a if f % 2 else -a), ((a + 1) // 2 if f % 4 < 2 else -((a + 1) // 2))


def flash(t, t0):
    return 0 <= (t - t0) * IPS < 1


def hache(*v):                                      # pseudo-hasard déterministe
    x = 0
    for k in v:
        x = (x * 1103515245 + int(k) + 12345) & 0x7FFFFFFF
    return x


def lignes_vitesse(buf, t, force, c=CREME):
    """Traits horizontaux qui filent vers la gauche (vitesse de caméra)."""
    f = int(t * IPS)
    for k in range(int(10 * force)):
        y = 40 + hache(k, 7) % 260
        lg = 12 + hache(k, 3) % 30
        x = L - ((hache(k, 11) + f * (18 + hache(k) % 14)) % (L + lg))
        rect(buf, x, y, x + lg, y, c)


def ellipse(buf, cx, cy, rx, ry, c, part=1.0):
    """Cercle au feutre (2 px), dessiné jusqu'à la fraction `part` du tour."""
    n = int(160 * part)
    for i in range(n):
        a = -math.pi / 2 + 2 * math.pi * i / 160
        x, y = round(cx + rx * math.cos(a)), round(cy + ry * math.sin(a))
        rect(buf, x, y, x + 1, y + 1, c)


def fleche(buf, cx, y0, t, z=2):
    """La flèche (pointe en haut) qui rebondit sous ce qu'elle montre (12 i/s)."""
    rebond = (0, 2, 3, 2)[int(t * 12) % 4] * z // 2
    poser(buf, O["fleche"], cx - O["fleche"][0] * z // 2, y0 + rebond, z)


def ticket(buf, texte, droite, y, z=2):
    """Ticket crème, chiffres 3×5 ×z, le dernier « 4 » en rouge."""
    if not texte:
        return
    w = largeur(texte, z, "3x5")
    g = droite - w - 6
    rect(buf, g, y, droite, y + 5 * z + 7, CONTOUR)
    rect(buf, g + 1, y + 1, droite - 1, y + 5 * z + 6, CREME)
    n = len(texte)
    ecrire(buf, texte, g + 3, y + 4, CONTOUR, z, "3x5",
           couleur_de=lambda i: ROUGE_S if (i == n - 1 and texte.endswith("4") and n >= 19) else CONTOUR)


# ---------------------------------------------------------------- calques 3D (outils/rendu3d)
TROIS_D = {}                                     # nom → (début, liste des images RGBA, largeur)
FENETRES_3D = {"equation": (0.00, 6.60), "quatre": (12.60, 15.30), "ecrans": (26.90, 29.40), "tarte": (31.40, 40.30),
               "circuit": (40.30, 44.60), "ruban": (44.60, 54.90), "fameux": (68.60, 70.85)}


def calque3d(nom):
    if nom not in TROIS_D:
        dossier = os.path.join(ICI, "3d", nom)
        imgs = sorted(f for f in os.listdir(dossier) if f.startswith("f_") and f.endswith(".png")) if os.path.isdir(dossier) else []
        TROIS_D[nom] = (FENETRES_3D[nom][0], [os.path.join(dossier, f) for f in imgs], {})
    return TROIS_D[nom]


def poser3d(buf, nom, t, dx=0):
    """Superpose l'image 3D de l'instant t (pixels opaques seulement ; alpha déjà tout-ou-rien), décalée de dx px."""
    debut, images, cache = calque3d(nom)
    if not images:
        return False
    n = min(len(images) - 1, max(0, round((t - debut) * IPS)))
    if n not in cache:
        cache.clear()
        w, h, px = png.lire(images[n])
        cache[n] = [(i, bytes(p[:3])) for i, p in enumerate(px) if p[3]]
    for i, c in cache[n]:
        if dx:
            x = i % L + dx
            if not 0 <= x < L:
                continue
            i += dx
        buf[i * 3:i * 3 + 3] = c
    return True


# ---------------------------------------------------------------- motion design : texte cinétique, sauts, colère
def texte_cinetique(buf, texte, cx, cy, c, t, t0, z, ecart=0.035, police="5x7", fond_sombre=False):
    """Chaque lettre tombe de 36 px et rebondit (ease-out-back), l'une après l'autre."""
    if t < t0:
        return
    g = POLICES[police]
    x = cx - largeur(texte, z, police) // 2
    h = len(g["0"]) * z
    if fond_sombre:
        cartouche(buf, texte, cx, cy, z, police)
    for i, ch in enumerate(texte):
        u = (t - t0 - i * ecart) / 0.22
        if u >= 0:
            u = min(1.0, u)
            s = 1.70158
            dos = 1 + (s + 1) * (u - 1) ** 3 + s * (u - 1) ** 2            # ease-out-back
            ecrire(buf, ch, x, cy - h // 2 - round(36 * (1 - dos)), c, z, police)
        x += z * (len(g[ch][0]) + 1)


def saut(t, t0, haut=14, duree=0.42):
    u = (t - t0) / duree
    return -round(haut * 4 * u * (1 - u)) if 0 <= u < 1 else 0


def colere(buf, x, y, t, z=2):
    """Symbole de colère (croix rouge qui pulse) au-dessus d'une tête."""
    k = 1 if int(t * 12) % 2 else 0
    for dx, dy in ((0, 0), (3 + k, 0), (0, 3 + k), (3 + k, 3 + k)):
        rect(buf, x + dx * z, y + dy * z, x + dx * z + z, y + dy * z + z, ROUGE)


def gouttes(buf, x, y, t, t0, z=2):
    """Gouttes de sueur qui glissent (bleu 11/12)."""
    if t < t0:
        return
    for k in range(2):
        v = ((t - t0) * 1.6 + k * 0.5) % 1.0
        yy = y + round(v * 18) * z // 2
        rect(buf, x + k * 9 * z, yy, x + k * 9 * z + z, yy + 2 * z, C[11])
        pt(buf, x + k * 9 * z, yy, C[12])


# ---------------------------------------------------------------- événements (son = marqueur = effet)
EV = []


def ev(t, son):
    EV.append((round(t, 3), son))


PRIX = "0,30000000000000004"
X0, Y0, MX, MY = 124, 379, 160, 370
CYCLE = [0] * 5 + [1] * 4 + [2] * 5 + [3] * 2


def repos(t):
    return TIM[CYCLE[int(t * 12) % 16]]


def boutique(buf, t, tim=None, marchand=0, miette=None, dy_tim=0, dx_m=0):
    fond(buf, "boutique")
    poser(buf, OBJ[2], 186, 382)
    poser(buf, MAR[marchand], MX + dx_m, MY)
    poser(buf, COMPTOIR, 148, 398)
    poser(buf, OBJ[0], 146, 383); poser(buf, OBJ[1], 204, 383)
    ecrire(buf, "0,10", 140, 366, OR, 2, "3x5"); ecrire(buf, "0,20", 199, 366, OR, 2, "3x5")
    poser(buf, tim or repos(t), X0, Y0 + dy_tim)
    if miette:
        mx, my = miette
        if int(t * 12) % 4 < 2:
            poser(buf, ETINCELLE, mx - 7, my - 7)
        pt(buf, mx, my, OR_CLAIR)


def ruban(buf, y_ticket):
    rect(buf, 192, y_ticket + 18, 195, 386, CONTOUR)
    rect(buf, 193, y_ticket + 17, 194, 386, CREME)


# ---- 1. boutique : 0,1 + 0,2 (équation 3D) ; Tim : « Facile ! 0,3 ! »
T_TICKET = M(11) - 0.1


def s_ouverture(t):
    buf = neuf()
    boutique(buf, t, tim=TEND if M(8) <= t < M(11) else None, dy_tim=saut(t, M(7)))
    if not poser3d(buf, "equation", t):                      # repli 2D si la 3D n'est pas rendue
        texte_pop(buf, "0,1 + 0,2", 135, 104, CREME, t, M(0), 4, fond_sombre=True)
    if M(7) <= t < M(7) + 0.6:
        poser(buf, O["question"], X0 + 24, Y0 - 18 + saut(t, M(7)), 1)
    return buf


ev(M(0), "chute3d"); ev(M(3), "chute3d"); ev(M(4), "chute3d"); ev(M(7), "saut"); ev(M(9), "pop_grave"); ev(M(10), "ressort")


# ---- 2. le ticket s'imprime ; le 4 (3D) s'écrase ; « Quatre ?! » de Tim en gros plan
T_ATELIER = M(20) - 0.12


def s_ticket(t):
    buf = neuf()
    boutique(buf, t, tim=REGARDE if t < M(19) else None,
             marchand=(1 + int(t * 4) % 2) if M(13) <= t < M(18) else 0, dy_tim=saut(t, M(19), 18, 0.5))
    n = 3 if t >= M(13) else 0
    for k, i in enumerate((14, 15, 16, 17)):
        if t >= M(i):
            n = 3 + (4, 8, 12, 15)[k]
    if t >= M(18):
        n = 19
    if t >= M(11):
        ruban(buf, 186)
        ticket(buf, PRIX[:max(1, n)], 236, 186)
    z, cx, cy = 1, 135, 240
    if M(18) <= t < M(19):
        z, cx, cy = 2, 196, 196
    elif t >= M(19):                                          # gros plan sur Tim qui saute
        z, cx, cy = 3, X0 + 36, Y0 + 30                       # Tim à gauche, au-dessus des sous-titres ; le 4 à droite
    buf = camera(buf, z, cx, cy)
    if t >= M(19):
        texte_cinetique(buf, "?!", 84, 112, ROUGE, t, M(19), 5, 0.06)
    if t >= FENETRES_3D["quatre"][0]:
        poser3d(buf, "quatre", t, 62 if t >= M(19) else 0)
    dx, dy = secousse(t, M(18) + 0.12, 5, 0.5)
    if not dx:
        dx, dy = secousse(t, M(19), 3, 0.3)
    return secouer(buf, dx, dy)


ev(M(11), "imprime")
for i in (14, 15, 16, 17):
    ev(M(i), "clic3")
ev(M(18), "sifflet_chute"); ev(M(18) + 0.12, "impact"); ev(M(19), "saut"); ev(M(19) + 0.05, "pop_aigu")


# ---- 3. l'atelier : Tim vérifie… pareil
T_ACCUSE = M(26) - 0.12


def s_atelier(t):
    buf = neuf()
    fond(buf, "atelier")
    marche = t < M(21)
    x = round(20 + 50 * entre(t, T_ATELIER, M(21))) if marche else 70
    poser(buf, TIM[4 + int(t * 12) % 4] if marche else repos(t), x, Y0)
    l1 = "> 0.1+0.2"
    t_l1, t_res = M(22), M(25)
    n1 = max(0, min(len(l1), int((t - t_l1) / ((t_res - 0.1 - t_l1) / len(l1))) + 1)) if t >= t_l1 else 0
    ecrire(buf, l1[:n1], 150, 266, VERT, 1, "3x5")
    if t >= t_res:
        ecrire(buf, PRIX.replace(",", "."), 150, 276, VERT, 1, "3x5",
               couleur_de=lambda i: ROUGE if i == len(PRIX) - 1 else VERT)
        fleche(buf, 221, 284, t, 1)
    elif int(t * 4) % 2 == 0:
        cx = 150 + largeur(l1[:n1] + " ", 1, "3x5") if n1 else 150
        rect(buf, cx, 266, cx + 2, 270, VERT)
    z, cx, cy = 1, 135, 240
    if t >= M(21):
        u = entre(t, M(21), M(21) + 0.4)
        z, cx, cy = 2, 150 + 36 * u, 300 - 17 * u
    if t >= t_res:
        z, cx, cy = 3, 186, 280
    buf = camera(buf, z, cx, cy)
    return secouer(buf, *secousse(t, t_res, 2, 0.3))


ev(T_ATELIER, "whoosh"); ev(M(21), "zoom")
for k in range(9):
    ev(M(22) + k * (M(25) - 0.1 - M(22)) / 9, "clic")
ev(M(25), "bip")


# ---- 4. champ / contrechamp : Tim accuse, le marchand s'offusque
T_MARCHAND = M(29) - 0.1
T_NON = M(34) - 0.05


def s_accuse(t):
    buf = neuf()
    boutique(buf, t, tim=TEND, dy_tim=saut(t, M(28), 8, 0.3))
    buf = camera(buf, 3, X0 + 16, Y0 + 30)
    colere(buf, 104, 150 + (int(t * 12) % 2) * 2, t, 6)
    texte_cinetique(buf, "TRICHEUR !", 135, 110, ROUGE, t, M(28), 3, fond_sombre=True)
    return secouer(buf, *secousse(t, M(28), 4, 0.4))


def s_marchand(t):
    buf = neuf()
    non = 0
    if t >= M(30):                                            # il secoue la tête : « Jamais de la vie ! »
        non = (2, 0, -2, 0)[int(t * 12) % 4]
    boutique(buf, t, marchand=3 if t >= M(29) else 0, dx_m=non)
    buf = camera(buf, 3, MX + 16, MY + 10)
    gouttes(buf, 196, 120, t, M(29), 3)
    texte_pop(buf, "MOI ?", 135, 100, CREME, t, M(29), 4, fond_sombre=True)
    texte_cinetique(buf, "JAMAIS !", 135, 160, OR, t, M(30), 3, fond_sombre=True)
    return buf


ev(T_ACCUSE, "flash"); ev(M(28), "colere"); ev(T_MARCHAND, "volet"); ev(M(29), "pop"); ev(M(30), "sueur")


# ---- 5. NON. (tampon) puis « personne ne triche… je vais te dire pourquoi » (rayons)
T_POURQUOI = M(35) - 0.05


def s_non(t):
    buf = neuf(ROUGE_S)
    for y in range(0, H, 2):
        for x0 in range((y // 2) % 24 - 24, L, 24):
            rect(buf, x0, y, x0 + 11, y + 1, C[21])
    u = (t - T_NON) * IPS
    y_t = -140 + round(min(1, u / 3) * 250)
    if u >= 9:
        y_t = 110 - round((u - 9) * 40)
    if u >= 3:
        ecrire_centre(buf, "NON.", 135, 200, CREME, 8)
        for k in range(14):
            v = (t - T_NON) - 3 / IPS
            if v < 0.35:
                d = 1 if k % 2 else -1
                px = 135 + d * (70 + round(v * (90 + hache(k) % 120)))
                py = 232 - round(v * (20 + hache(k, 2) % 60)) + round(140 * v * v)
                rect(buf, px, py, px + 2, py + 2, C[7] if k % 3 else CREME)
    poser(buf, O["tampon"], 135 - 7 * 7, y_t, 7)
    if flash(t, T_NON + 3 / IPS):
        return neuf(CREME)
    return secouer(buf, *secousse(t, T_NON + 3 / IPS, 5, 0.45))


T_ECRANS = 26.90


def s_pourquoi(t):
    buf = neuf(CONTOUR)
    a0 = t * 1.1
    cx, cy = 135, 250
    for y in range(0, H, 2):
        for x in range(0, L, 2):
            if int((math.atan2(y - cy, x - cx) + a0) / (math.pi / 8)) % 2 == 0:
                rect(buf, x, y, x + 1, y + 1, OMBRE)
    z = 3
    poser(buf, TEND if t >= M(38) else repos(t), 135 - 16 * z, 300 - 28 * z + saut(t, M(42), 10, 0.35), z)
    if t < M(38):
        texte_cinetique(buf, "PERSONNE", 135, 92, CREME, t, M(35), 3)
        texte_cinetique(buf, "NE TRICHE.", 135, 124, CREME, t, M(36), 3)
    else:
        texte_cinetique(buf, "POURQUOI ?", 135, 110, OR, t, M(42), 3)
    return secouer(buf, *secousse(t, M(42), 2, 0.25))


ev(T_NON, "whoosh_bas"); ev(T_NON + 3 / IPS, "tampon"); ev(T_POURQUOI, "rayons"); ev(M(35), "lettres")
ev(M(36), "lettres"); ev(M(42), "lettres"); ev(M(42) + 0.25, "pop_aigu")


# ---- 6. écrans (3D)
T_BASE10 = M(50) - 0.1


def s_ecrans(t):
    buf = neuf(C[4])
    if not poser3d(buf, "ecrans", t):
        texte_pop(buf, "JS PYTHON JAVA", 135, 200, CREME, t, T_ECRANS, 2)
    return buf


ev(T_ECRANS, "whoosh"); ev(T_ECRANS + 0.6, "bip"); ev(T_ECRANS + 1.2, "bip"); ev(T_ECRANS + 1.8, "bip")


# ---- 7. base 10 (classe)
T_TARTE = M(56) - 0.1


def s_base10(t):
    buf = neuf()
    fond(buf, "classe")
    for k in range(10):
        t0 = M(50) + k * (M(55) - M(50)) / 10
        zz = pop(t, t0, 4)
        if zz:
            ecrire_centre(buf, str(k), 45 + 45 * (k % 5), 130 + 62 * (k // 5) + saut(t, t0, 6, 0.25), CREME, zz)
    texte_cinetique(buf, "BASE 10", 135, 255, OR, t, M(54), 3)
    poser(buf, repos(t), 200, Y0 + saut(t, M(55), 10, 0.35))
    return secouer(buf, *secousse(t, M(55), 2, 0.25))


for k in range(10):
    ev(M(50) + k * (M(55) - M(50)) / 10, "craie")
ev(M(54), "lettres"); ev(M(55), "saut")


# ---- 8. la tarte (3D) et 1/3 = 0,333… à l'infini
T_CIRCUIT = M(72) - 0.1


def s_tarte(t):
    buf = neuf()
    fond(buf, "classe")
    poser3d(buf, "tarte", t)
    if t >= M(64):
        txt = "1/3 = "
        if t >= M(65):
            txt += "0,"
        for i in (67, 68, 69):
            if t >= M(i):
                txt += "3"
        if t >= M(70):
            txt += "3" * int((t - M(70)) * 14)
        w = largeur(txt, 3)
        x = min(30, 226 - w)
        ecrire(buf, txt, x, 280, CREME, 3)
        if t >= M(70):
            lignes_vitesse(buf, t, 1.0)
            zz = pop(t, M(71), 3)
            rect(buf, 228, 276, 262, 306, CONTOUR)
            if zz:
                poser_centre(buf, O["infini"], 245, 291, zz)
    return buf


ev(M(62), "coupe"); ev(M(63), "ressort")
for i in (67, 68, 69):
    ev(M(i), "craie")
ev(M(70), "defile"); ev(M(71), "pop_aigu")


# ---- 9. le circuit (3D) : base 2
T_RUBAN = M(84) - 0.1


def s_circuit(t):
    buf = neuf(C[13])
    if not poser3d(buf, "circuit", t):
        fond(buf, "circuit")
    texte_cinetique(buf, "BASE 2", 135, 72, OR, t, M(77), 4, fond_sombre=True)
    if flash(t, T_CIRCUIT):
        return neuf(CREME)
    return secouer(buf, *secousse(t, M(77), 3, 0.3))


ev(T_CIRCUIT, "plongee"); ev(M(76), "allume"); ev(M(77), "impact_doux"); ev(M(80), "bits"); ev(M(83), "bits")


# ---- 10. le ruban binaire (3D)
T_CISEAUX = M(104) - 0.1


def s_ruban(t):
    buf = neuf(NUIT)
    poser3d(buf, "ruban", t)
    if t >= M(87):
        cartouche(buf, "0,1 = ?", 135, 40, 3)
        ecrire_centre(buf, "0,1 = ?", 135, 40, CREME, 3)
    texte_cinetique(buf, "COINCE !", 135, 84, ROUGE, t, M(92), 3, fond_sombre=True) if M(92) <= t < M(93) + 0.6 else None
    return secouer(buf, *secousse(t, M(92), 2, 0.25))


ev(T_RUBAN, "whoosh"); ev(M(88), "pop_grave"); ev(M(92), "bloup")
for i in range(93, 102):
    ev(M(i), "bip_bin")
ev(M(102), "defile"); ev(M(103), "pop_aigu")


# ---- 11. les ciseaux : il garde 53 chiffres
BIN = "0,0" + "0011" * 30
COUPE = M(106)
T_LOUPE = M(115) - 0.1


def grille(buf):
    for y in range(4, H, 8):
        for x in range(4, L, 8):
            pt(buf, x, y, OMBRE)


def s_ciseaux(t):
    buf = neuf(CONTOUR)
    grille(buf)
    txt = BIN[:31]
    x = 246 - largeur(txt, 3)
    y = 200
    for i, ch in enumerate(txt):
        xi = x + (largeur(txt[:i], 3) + 3 if i else 0)
        yy = y
        if t >= COUPE and xi > 165:
            v = t - COUPE
            yy += round(300 * v * v + 40 * v)
        if i >= 3:
            rect(buf, xi - 2, yy - 3, xi + 17, yy + 23, ROUGE_S if ((i - 3) // 4) % 2 == 0 else C[21])
        ecrire(buf, ch, xi, yy, CREME, 3)
    xs = 300 - round(135 * entre(t, T_CISEAUX, COUPE - 0.1))
    ferme = t >= COUPE
    poser(buf, O["ciseaux"], xs - 35, 168 + (4 if ferme else 0), 5)
    texte_pop(buf, "53", 135, 88, OR, t, M(109), 7)
    texte_cinetique(buf, "CHIFFRES", 135, 140, CREME, t, M(110), 3)
    texte_cinetique(buf, "PAS UN DE PLUS", 135, 270, ROUGE, t, M(111), 2, 0.025)
    if flash(t, COUPE):
        return neuf(CREME)
    dx, dy = secousse(t, COUPE, 4, 0.4)
    if not dx:
        dx, dy = secousse(t, M(109), 3, 0.3)
    return secouer(buf, dx, dy)


ev(T_CISEAUX, "glisse"); ev(COUPE, "ciseaux"); ev(M(109), "impact_doux"); ev(M(110), "lettres"); ev(M(111), "lettres")


# ---- 12. la loupe : 0,1 vaut un tout petit peu plus
VRAI = "0,1000000000000000055"
T_ADDITION = M(126) - 0.1


def s_loupe(t):
    buf = neuf(CONTOUR)
    grille(buf)
    y_big = 160 - round(70 * entre(t, M(119), M(119) + 0.25))
    texte_pop(buf, "0,1", 135, y_big, CREME, t, M(116), 8 if t < M(119) else 5)
    if t >= M(119):
        n = min(len(VRAI), int((t - M(119)) * 40) + 3)
        ecrire(buf, VRAI[:n], 13, 200, CREME, 2, couleur_de=lambda i: ROUGE if i >= len(VRAI) - 2 else CREME)
    z, cx, cy = 1, 135, 240
    x55 = 13 + largeur(VRAI[:-2], 2) + 2
    if t >= M(122):
        lx = 330 - round((330 - (x55 + 10)) * entre(t, M(122), M(122) + 0.25))
        ly = 140
        for x, y, c in O["loupe"][2]:
            if c != C[12] and c != C[8]:
                cc = C[6] if c == CONTOUR else c
                rect(buf, lx - 37 + 5 * x, ly - 37 + 5 * y, lx - 37 + 5 * x + 4, ly - 37 + 5 * y + 4, cc)
        for y in range(-24, 25):
            for x in range(-24, 25):
                if x * x + y * y <= 24 * 24:
                    pt(buf, lx - 3 + x, ly - 7 + y, OMBRE)
        rect(buf, lx - 18, ly - 24, lx - 14, ly - 22, C[5])
        ecrire_centre(buf, "55", lx - 3, ly - 7, ROUGE, 4)
        rect(buf, x55 - 1, 198, x55 + 22, 199, ROUGE)
    if t >= M(123):
        z, cx, cy = 2, x55 + 18, 170
    texte_pop(buf, "+", x55 + 46, 104, ROUGE, t, M(125), 4)
    buf = camera(buf, z, cx, cy)
    return secouer(buf, *secousse(t, M(125), 3, 0.3))


ev(T_LOUPE, "whoosh"); ev(M(116), "pop_grave"); ev(M(119), "imprime"); ev(M(122), "glisse"); ev(M(123), "zoom"); ev(M(125), "pop_aigu")


# ---- 13. l'addition à la craie
LIGNES = [("0,1000000000000000055", 122), ("+0,2000000000000000111", 142), ("0,3000000000000000166", 166)]
T_FAMEUX = 68.60


def s_addition(t):
    buf = neuf()
    fond(buf, "classe")
    for k, (txt, y) in enumerate(LIGNES):
        xd = 240 - largeur(txt, 2, "3x5")
        if k == 0 and t >= M(127):
            ecrire(buf, txt, xd - round(260 * (1 - entre(t, M(127), M(127) + 0.2))), y, CREME, 2, "3x5")
        if k == 1 and t >= M(129):
            ecrire(buf, txt, xd + round(260 * (1 - entre(t, M(129), M(129) + 0.2))), y, CREME, 2, "3x5")
        if k == 2 and t >= M(132):
            n = min(len(txt), int((t - M(132)) * 50) + 1)
            ecrire(buf, txt[:n], xd, y, CREME, 2, "3x5")
    if t >= M(131):
        rect(buf, 56, 156, 56 + round(186 * entre(t, M(131), M(131) + 0.2)), 157, CREME)
    if t >= M(133):
        ecrire(buf, "ORDI :", 34, 206 - (2 if (t - M(133)) * IPS < 2 else 0), OR, 2)
        ecrire(buf, PRIX, 96, 208, OR, 2, "3x5", couleur_de=lambda i: ROUGE if i == len(PRIX) - 1 else OR)
        x4 = 96 + largeur(PRIX[:-1], 2, "3x5") + 2 + 3
        if t >= M(136):
            ellipse(buf, x4, 213, 9, 11, ROUGE, entre(t, M(136), M(136) + 0.3))
        if t >= M(138):
            fleche(buf, x4, 228, t, 2)
    poser(buf, repos(t), 14, Y0 + saut(t, M(138), 10, 0.35))
    return secouer(buf, *secousse(t, M(133), 2, 0.25))


ev(T_ADDITION, "whoosh"); ev(M(127), "glisse"); ev(M(129), "glisse"); ev(M(131), "craie")
ev(M(132), "imprime"); ev(M(133), "impact_doux"); ev(M(136), "feutre"); ev(M(138), "pop_aigu")


# ---- 14. le fameux quatre (3D)
T_FINAL = M(142) - 0.1


def s_fameux(t):
    buf = neuf(CONTOUR)
    if not poser3d(buf, "fameux", t):
        texte_pop(buf, "4", 135, 200, OR, t, T_FAMEUX, 12)
    return secouer(buf, *secousse(t, M(141), 3, 0.35))


ev(T_FAMEUX, "gong"); ev(M(141), "impact")


# ---- 15. final : Tim paie avec une miette, le marchand n'en revient pas
PAYE = M(151) + 0.55


def s_final(t):
    buf = neuf()
    tend = M(145) <= t < PAYE + 0.25
    miette = None
    if tend:
        mx, my = X0 + 27, Y0 + 18
        if t >= PAYE:
            u = entre(t, PAYE, PAYE + 0.2)
            mx, my = round(mx + (MX + 1 - mx) * u), round(my + (MY + 24 - my) * u)
        miette = (mx, my)
    marchand = 4 if PAYE <= t < PAYE + 0.35 else (3 if M(149) <= t < PAYE else 0)
    boutique(buf, t, tim=TEND if tend else None, marchand=marchand, miette=miette, dy_tim=saut(t, M(142), 10, 0.35))
    n = len(PRIX)
    if t >= PAYE + 0.4:
        n = max(0, len(PRIX) - int((t - PAYE - 0.4) * 30))
    if n:
        ruban(buf, 186)
        ticket(buf, PRIX[:n], 236, 186)
    z, cx, cy = 1, 135, 240
    if M(149) <= t < PAYE:                                   # gros plan : « Avec… une miette ?! »
        z, cx, cy = 3, MX + 6, MY + 4
    buf = camera(buf, z, cx, cy)
    if M(151) <= t < PAYE:
        texte_cinetique(buf, "?!", 215, 150, OR, t, M(151), 6, 0.06)
        gouttes(buf, 200, 120, t, M(151), 3)
    return secouer(buf, *secousse(t, M(151), 3, 0.35))


ev(T_FINAL, "flash"); ev(M(142), "saut"); ev(M(145), "scintille"); ev(M(149), "zoom"); ev(M(151), "pop_aigu")
ev(PAYE, "piece"); ev(PAYE + 0.4, "imprime")

# ---------------------------------------------------------------- montage
SCENES = [(0, s_ouverture), (T_TICKET, s_ticket), (T_ATELIER, s_atelier), (T_ACCUSE, s_accuse), (T_MARCHAND, s_marchand),
          (T_NON, s_non), (T_POURQUOI, s_pourquoi), (T_ECRANS, s_ecrans), (T_BASE10, s_base10), (T_TARTE, s_tarte),
          (T_CIRCUIT, s_circuit), (T_RUBAN, s_ruban), (T_CISEAUX, s_ciseaux), (T_LOUPE, s_loupe),
          (T_ADDITION, s_addition), (T_FAMEUX, s_fameux), (T_FINAL, s_final)]
TRANS = {T_ATELIER: ("pousse", 0.25), T_MARCHAND: ("pousse", 0.2), T_POURQUOI: ("damier", 0.25),
         T_ECRANS: ("pousse", 0.25), T_BASE10: ("damier", 0.25), T_TARTE: ("pousse", 0.25), T_RUBAN: ("damier", 0.3),
         T_CISEAUX: ("pousse", 0.25), T_LOUPE: ("damier", 0.25), T_ADDITION: ("pousse", 0.25)}
for t0, (typ, d) in TRANS.items():
    ev(t0, "whoosh" if typ == "pousse" else "volet")


def rendre(t):
    k = max(i for i, (t0, _) in enumerate(SCENES) if t >= t0)
    t0, f = SCENES[k]
    buf = f(t)
    if t0 in TRANS:
        typ, d = TRANS[t0]
        u = (t - t0) / d
        if u < 1 and k > 0:
            avant = SCENES[k - 1][1](t)
            if typ == "pousse":
                p = round(L * lisse(u))
                out = bytearray()
                for y in range(H):
                    out += avant[(y * L + p) * 3:(y + 1) * L * 3] + buf[y * L * 3:(y * L + p) * 3]
                buf = out
            else:
                for cy in range(0, H, 16):
                    for cx in range(0, L, 15):
                        if (cx / L + cy / H) / 2 > u:
                            for y in range(cy, min(H, cy + 16)):
                                a = (y * L + cx) * 3
                                buf[a:a + 45] = avant[a:a + 45]
    if t0 in (T_ACCUSE, T_FINAL, T_FAMEUX) and flash(t, t0):
        buf = neuf(CREME)
    for s in SOUS_TITRES:                                   # bande sombre sous le sous-titre (grille 12 i/s)
        if round(s["debut"] * 12) / 12 <= t < round(s["fin"] * 12) / 12:
            w = 16 * len(s["texte"]) + 16
            rect(buf, 135 - w // 2, 318, 135 + w // 2, 346, CONTOUR)
            break
    return buf


def main():
    images = None
    if "--images" in sys.argv:
        images = [int(v) for v in sys.argv[sys.argv.index("--images") + 1].split(",")]
    sortie = os.path.join(ICI, "scene")
    os.makedirs(sortie, exist_ok=True)
    with open(os.path.join(ICI, "evenements.json"), "w", encoding="utf-8", newline="\n") as f:
        json.dump(sorted(EV), f, ensure_ascii=False, indent=0)
    manque = [n for n in FENETRES_3D if not calque3d(n)[1]]
    if manque:
        print("séquences 3D absentes (repli 2D) :", ", ".join(manque))
    if images:
        for n in images:
            subprocess.run([FFMPEG, "-loglevel", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{L}x{H}",
                            "-i", "-", "-vf", "scale=iw*2:ih*2:flags=neighbor", os.path.join(ICI, f"controle_{n:04d}.png")],
                           input=bytes(rendre(n / IPS)))
        print(f"{len(images)} images de contrôle dans {ICI}")
        return
    for vieux in os.listdir(sortie):
        os.remove(os.path.join(sortie, vieux))
    p = subprocess.Popen([FFMPEG, "-loglevel", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{L}x{H}",
                          "-r", str(IPS), "-i", "-", "-vf", "scale=iw*4:ih*4:flags=neighbor",
                          "-start_number", "0", os.path.join(sortie, "scene_%04d.png")], stdin=subprocess.PIPE)
    for n in range(N):
        p.stdin.write(bytes(rendre(n / IPS)))
        if n % 240 == 0:
            print(f"  {n}/{N}", flush=True)
    p.stdin.close()
    p.wait()
    print(f"{N} images 1080×1920 à {IPS} i/s dans {sortie} ; {len(EV)} événements sonores")


def _ffmpeg():
    import glob, shutil
    v = os.environ.get("ICO_FFMPEG") or shutil.which("ffmpeg")
    if not v:
        v = (glob.glob(os.path.join(os.environ.get("LOCALAPPDATA", ""), "Microsoft", "WinGet", "Packages", "Gyan.FFmpeg*", "*", "bin", "ffmpeg.exe")) or ["ffmpeg"])[0]
    return v


FFMPEG = _ffmpeg()

if __name__ == "__main__":
    main()
