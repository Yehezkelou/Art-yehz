#!/usr/bin/env python3
"""pixel-03-binaire : compose « 0,1 + 0,2 » image par image (270×480, 24 i/s, opaque), agrandit ×4 en
pixels nets (ffmpeg, voisin le plus proche) et écrit la séquence 1080×1920 + la liste des bruitages.

    python3 -I pixel-03-binaire/.montage/composer.py [--images 0,120,300]   # sans argument : tout

Sortie : .montage/scene/scene_0000.png … (ignoré par git), .montage/evenements.json (un son = un marqueur
= un effet, lu par sons.py). Caméra, textes et effets à 24 i/s ; persos à 12 i/s (bible). Positions et
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
DUREE = 53.5                                    # la signature du modèle suit (53,5–54,5 s)
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


# ---------------------------------------------------------------- événements (son = marqueur = effet)
EV = []


def ev(t, son):
    EV.append((round(t, 3), son))


PRIX = "0,30000000000000004"

# ---------------------------------------------------------------- la boutique (scènes 1, 3 et 14)
X0, Y0, MX, MY = 124, 379, 160, 370


def boutique(buf, t, tim=None, marchand=0, miette=None, sans_tags=False):
    fond(buf, "boutique")
    poser(buf, OBJ[2], 186, 382)
    poser(buf, MAR[marchand], MX, MY)
    poser(buf, COMPTOIR, 148, 398)
    poser(buf, OBJ[0], 146, 383); poser(buf, OBJ[1], 204, 383)
    if not sans_tags:
        ecrire(buf, "0,10", 140, 366, OR, 2, "3x5"); ecrire(buf, "0,20", 199, 366, OR, 2, "3x5")
    poser(buf, tim or repos(t), X0, Y0)
    if miette:
        mx, my = miette
        if int(t * 12) % 4 < 2:
            poser(buf, ETINCELLE, mx - 7, my - 7)
        pt(buf, mx, my, OR_CLAIR)


CYCLE = [0] * 5 + [1] * 4 + [2] * 5 + [3] * 2


def repos(t):
    return TIM[CYCLE[int(t * 12) % 16]]


def ruban(buf, y_ticket):
    rect(buf, 192, y_ticket + 18, 195, 386, CONTOUR)
    rect(buf, 193, y_ticket + 17, 194, 386, CREME)


# ---- scène 1 : 0,1 + 0,2 = 0,3000…4 ?!
def s1(t):
    buf = neuf()
    imprime = M(10) <= t
    boutique(buf, t, tim=REGARDE if t >= M(8) else None,
             marchand=(1 + int(t * 12 / 3) % 2) if M(10) <= t < M(14) else (3 if t >= M(14) else 0))
    # l'équation monte quand arrive « égale »
    yq = 104 - round(24 * entre(t, M(7), M(7) + 0.2))
    zq = 4
    xs = 135 - largeur("0,1 + 0,2", zq) // 2
    vu = "0,1 + 0,2" if t >= M(4) else ("0,1 +" if t >= M(3) else "0,1")
    if t >= M(0):                                      # la cartouche s'allonge avec l'équation
        w = largeur(vu, zq)
        rect(buf, xs - 9, yq - 23, xs + w + 8, yq + 22, C[4]); rect(buf, xs - 8, yq - 22, xs + w + 7, yq + 21, CONTOUR)
    morceaux = [("0,1", 0, M(0)), ("+", largeur("0,1 ", zq), M(3)), ("0,2", largeur("0,1 + ", zq), M(4))]
    for txt, dx, t0 in morceaux:
        zz = pop(t, t0, zq)
        if zz:
            cx = xs + dx + largeur(txt, zq) // 2
            ecrire_centre(buf, txt, cx, yq, CREME, zz)
    texte_pop(buf, "=", 135, 122, OR, t, M(7), 4, fond_sombre=True)
    if imprime:                                        # le ticket s'imprime au rythme des « zéro »
        n = 3
        for k, i in enumerate((11, 12, 13)):
            if t >= M(i):
                n = 3 + 5 * (k + 1)
        if t >= M(14):
            n = 19
        ruban(buf, 186)
        ticket(buf, PRIX[:n], 236, 186)
    if t >= M(14) + 0.4:
        poser(buf, O["question"], X0 + 22, Y0 - 16 - (int(t * 12) % 2), 2)
    z, cx, cy = 1, 135, 240
    if t >= M(14):                                     # « quatre » : coup de zoom sur le 4
        z, cx, cy = 2, 196, 196
    buf = camera(buf, z, cx, cy)
    return secouer(buf, *secousse(t, M(14), 4, 0.6))


for i in (0, 3, 4):
    ev(M(i), "pop")
ev(M(7), "pop_grave")
ev(M(10), "imprime")
for i in (11, 12, 13):
    ev(M(i), "clic3")
ev(M(14), "impact"); ev(M(14) + 0.4, "pop")


# ---- scène 2 : Tim vérifie sur son ordinateur
T2, T3 = M(15) - 0.07, M(21) - 0.15


def s2(t):
    buf = neuf()
    fond(buf, "atelier")
    marche = t < M(16)
    x = round(20 + 50 * entre(t, T2, M(16))) if marche else 70
    poser(buf, TIM[4 + int(t * 12) % 4] if marche else repos(t), x, Y0)
    # console : écran intérieur x 146–225, y 261–306
    l1 = "> 0.1+0.2"
    n1 = max(0, min(len(l1), int((t - M(17)) / ((M(20) - 0.15 - M(17)) / len(l1))) + 1)) if t >= M(17) else 0
    ecrire(buf, l1[:n1], 150, 266, VERT, 1, "3x5")
    if t >= M(20):
        ecrire(buf, PRIX.replace(",", "."), 150, 276, VERT, 1, "3x5",
               couleur_de=lambda i: ROUGE if i == len(PRIX) - 1 else VERT)
        fleche(buf, 221, 284, t, 1)
    elif int(t * 4) % 2 == 0:                         # curseur
        cx = 150 + largeur(l1[:n1] + " ", 1, "3x5") if n1 else 150
        rect(buf, cx, 266, cx + 2, 270, VERT)
    z, cx, cy = 1, 135, 240
    if t >= M(16):
        u = entre(t, M(16), M(16) + 0.35)
        z, cx, cy = 2, 150 + 36 * u, 300 - 17 * u
    if t >= M(20):
        z, cx, cy = 3, 186, 280
    buf = camera(buf, z, cx, cy)
    return secouer(buf, *secousse(t, M(20), 2, 0.3))


ev(T2, "whoosh"); ev(M(16), "zoom")
for k in range(9):
    ev(M(17) + k * (M(20) - 0.15 - M(17)) / 9, "clic")
ev(M(20), "bip")


# ---- scène 3 : le marchand triche ?
T4 = M(24)


def s3(t):
    buf = neuf()
    boutique(buf, t, marchand=3 if t >= M(23) else 0)
    buf = camera(buf, 3, 176, 372)
    for x, y, i in ((44, 190, 21), (222, 160, 22), (52, 262, 23)):
        zz = pop(t, M(i), 3)
        if zz:
            poser_centre(buf, O["question"], x, y - (int(t * 12) + i) % 2 * 2, zz)
    texte_pop(buf, "TRICHE ?", 135, 110, CREME, t, M(23), 4, fond_sombre=True)
    return buf


for i in (21, 22, 23):
    ev(M(i), "pop")


# ---- scène 4 : NON. (tampon)
T5 = M(25) - 0.12


def s4(t):
    buf = neuf(ROUGE_S)
    for y in range(0, H, 2):
        for x0 in range((y // 2) % 24 - 24, L, 24):
            rect(buf, x0, y, x0 + 11, y + 1, C[21])
    u = (t - T4) * IPS                                  # images depuis le début de la scène
    y_t = -140 + round(min(1, u / 3) * 250)              # le tampon descend en 3 images
    if u >= 9:
        y_t = 110 - round((u - 9) * 40)                  # puis remonte
    if u >= 3:
        ecrire_centre(buf, "NON.", 135, 200, CREME, 8)
        for k in range(14):                              # poussière
            v = (t - T4) - 3 / IPS
            if v < 0.35:
                d = 1 if k % 2 else -1
                px = 135 + d * (70 + round(v * (90 + hache(k) % 120)))
                py = 232 - round(v * (20 + hache(k, 2) % 60)) + round(140 * v * v)
                rect(buf, px, py, px + 2, py + 2, C[7] if k % 3 else CREME)
    poser(buf, O["tampon"], 135 - 7 * 7, y_t, 7)
    if flash(t, T4 + 3 / IPS):
        return neuf(CREME)
    return secouer(buf, *secousse(t, T4 + 3 / IPS, 5, 0.45))


ev(T4, "whoosh_bas"); ev(T4 + 3 / IPS, "tampon")


# ---- scène 5 : je vais te dire pourquoi (rayons)
T6 = M(30) - 0.1


def s5(t):
    buf = neuf(CONTOUR)
    a0 = t * 0.9
    cx, cy = 135, 250
    for y in range(0, H, 2):                            # rayons qui tournent (calculés par carrés de 2 px)
        for x in range(0, L, 2):
            a = math.atan2(y - cy, x - cx) + a0
            if int(a / (math.pi / 8)) % 2 == 0:
                rect(buf, x, y, x + 1, y + 1, OMBRE)
    z = 3 + (1 if (t - T5) * IPS < 2 else 0)
    poser(buf, TEND, 135 - 16 * z, 300 - 28 * z, z)
    texte_pop(buf, "POURQUOI ?", 135, 120, OR, t, M(29), 3)
    return secouer(buf, *secousse(t, M(29), 2, 0.25))


ev(T5, "rayons"); ev(M(29), "pop")


# ---- scène 6 : tous les langages (travelling sur 4 écrans)
T7 = M(37) - 0.12
LANGAGES = ("JAVASCRIPT", "PYTHON", "JAVA", "RUBY")


def s6(t):
    buf = neuf()
    u = entre(t, T6 + 0.15, T7 - 0.25)
    ox = round(810 * u)
    fond(buf, "ecrans", ox)
    for k, nom in enumerate(LANGAGES):
        x0 = 25 + 270 * k - ox
        if -230 < x0 < L:
            ecrire(buf, nom, x0 + 24, 156, CREME, 1)
            t0 = T6 + 0.15 + (k * 270 - 30) / 810 * (T7 - 0.4 - T6) if k else T6 + 0.1
            if t >= t0:
                n = min(len(PRIX), int((t - t0) * 60) + 1)
                ecrire(buf, PRIX.replace(",", ".")[:n], x0 + 32, 190, VERT, 2, "3x5",
                       couleur_de=lambda i: ROUGE if i == len(PRIX) - 1 else VERT)
    v = abs(entre(t + 0.04, T6 + 0.15, T7 - 0.25) - u) * 810
    if v > 4:
        lignes_vitesse(buf, t, min(1.5, v / 12))
    poser(buf, repos(t), 30, Y0)                        # Tim regarde passer les écrans
    return buf


ev(T6 + 0.15, "whoosh")
for k in range(1, 4):
    ev(T6 + 0.15 + (k * 270 - 30) / 810 * (T7 - 0.4 - T6), "bip")


# ---- scène 7 : nous, on compte en base 10
T8 = M(43) - 0.1


def s7(t):
    buf = neuf()
    fond(buf, "classe")
    for k in range(10):
        t0 = M(37) + k * (M(42) - M(37)) / 10
        zz = pop(t, t0, 4)
        if zz:
            ecrire_centre(buf, str(k), 45 + 45 * (k % 5), 130 + 62 * (k // 5), CREME, zz)
    texte_pop(buf, "BASE 10", 135, 255, OR, t, M(41), 3)
    poser(buf, repos(t), 200, Y0)
    return secouer(buf, *secousse(t, M(42), 2, 0.25))


for k in range(10):
    ev(M(37) + k * (M(42) - M(37)) / 10, "craie")
ev(M(41), "pop_grave")


# ---- scène 8 : 1/3 = 0,333… à l'infini
T9 = M(60) - 0.15


def s8(t):
    buf = neuf()
    fond(buf, "classe")
    z = pop(t, M(45), 5)
    if z:
        dx = (2 if int(t * IPS) % 2 else -2) if M(49) <= t < M(49) + 0.3 else 0
        x0 = 135 - O["tarte"][0] * z // 2 + dx
        poser(buf, O["tarte"], x0, 120, z)
        if t >= M(51):                                  # coupée en 3 : deux traits, une part qui glisse
            for k in (1, 2):
                xc = x0 + O["tarte"][0] * z * k // 3
                rect(buf, xc, 120, xc + 1, 120 + O["tarte"][1] * z - 1, CONTOUR)
            if t >= M(51) + 0.15:
                g = round(8 * entre(t, M(51) + 0.15, M(51) + 0.35))
                larg = O["tarte"][0] * z // 3
                for yy in range(120, 120 + O["tarte"][1] * z):
                    a = (yy * L + x0 + 2 * larg + 2) * 3
                    seg = bytes(buf[a:a + (larg - 2) * 3])
                    rect(buf, x0 + 2 * larg + 2, yy, x0 + 2 * larg + 1 + g, yy, C[13])
                    b = (yy * L + x0 + 2 * larg + 2 + g) * 3
                    buf[b:b + len(seg)] = seg[:max(0, (L - (x0 + 2 * larg + 2 + g)) * 3)]
    # 1/3 = 0,333… qui s'allonge, puis défile à l'infini
    if t >= M(52):
        txt = "1/3 = "
        if t >= M(53):
            txt += "0,"
        for i in (55, 56, 57):
            if t >= M(i):
                txt += "3"
        if t >= M(58):
            txt += "3" * int((t - M(58)) * 12)
        w = largeur(txt, 3)
        x = min(30, 240 - w)
        ecrire(buf, txt, x, 222, CREME, 3)
        if t >= M(58):
            lignes_vitesse(buf, t, 1.0)
    zz = pop(t, M(59), 4)
    if zz:
        poser_centre(buf, O["infini"], 135, 283, zz)
    return secouer(buf, *secousse(t, M(51), 2, 0.2))


ev(M(45), "pop"); ev(M(49), "bloup"); ev(M(51), "coupe")
for i in (55, 56, 57):
    ev(M(i), "craie")
ev(M(58), "defile"); ev(M(59), "pop_aigu")


# ---- transition : plongée dans l'écran de l'ordinateur (paliers ×1 → ×5)
T10 = T9 + 0.5


def plongee(t):
    buf = neuf()
    fond(buf, "atelier")
    poser(buf, repos(t), 70, Y0)
    for y in range(261, 307, 5):                        # l'écran s'allume en 0 et 1
        for x in range(148, 224, 6):
            ecrire(buf, "1" if hache(x, y, int(t * 12)) % 2 else "0", x, y, VERT, 1, "3x5")
    z = 1 + min(4, int((t - T9) / 0.1))
    buf = camera(buf, z, 186, 283)
    return neuf(CREME) if flash(t, T10 - 1 / IPS) else buf


ev(T9, "plongee")


# ---- scène 9 : l'ordi compte en base 2 (interrupteurs et lampes)
T11 = M(72) - 0.12


def s9(t):
    buf = neuf()
    fond(buf, "circuit")
    tous = 0 if M(68) <= t < M(71) else (1 if t >= M(71) else None)
    for k in range(8):
        x = 23 + 29 * k
        on = tous if tous is not None else hache(k, int(t * 4)) % 2
        rect(buf, x, 180, x + 21, 201, CONTOUR)
        rect(buf, x + 2, 182, x + 19, 199, OR if on else OMBRE)
        if on:
            rect(buf, x + 4, 184, x + 7, 187, OR_CLAIR)
        ecrire_centre(buf, "1" if on else "0", x + 11, 218, CREME, 2)
    texte_pop(buf, "BASE 2", 135, 110, OR, t, M(65), 4)
    texte_pop(buf, "0", 70, 272, CREME, t, M(68), 6)
    texte_pop(buf, "1", 200, 272, OR, t, M(71), 6)
    return secouer(buf, *secousse(t, M(65), 3, 0.3))


ev(T10, "allume"); ev(M(65), "impact_doux"); ev(M(68), "pop_grave"); ev(M(71), "pop_aigu")

# ---- scènes 10 et 11 : 0,1 en binaire, le ruban, les ciseaux
BIN = "0,0" + "0011" * 30
DIGITS_MOTS = [85, 86, 87, 88, 89, 90, 91, 92, 93]      # « zéro zéro zéro un un zéro zéro un un »
T12 = M(103) - 0.15
COUPE = M(98)


def n_bin(t):
    if t < M(85):
        return 0
    n = 2 + sum(1 for i in DIGITS_MOTS if t >= M(i))
    if t >= M(94):
        n += int((min(t, M(96)) - M(94)) * 16)
    return min(len(BIN), n)


def grille(buf):
    for y in range(4, H, 8):
        for x in range(4, L, 8):
            pt(buf, x, y, OMBRE)


def s10(t):
    buf = neuf(CONTOUR)
    grille(buf)
    if t < M(77):                                       # « et en base deux »
        texte_pop(buf, "BASE 2", 135, 170, OR, t, M(74), 5)
    if t < M(85):
        z = pop(t, M(77), 8)
        if z:
            dx = (3 if int(t * IPS) % 2 else -3) if M(84) <= t < M(84) + 0.35 else 0
            ecrire_centre(buf, "0,1", 135 + dx, 170, CREME, z)
    elif t < M(96):
        ecrire_centre(buf, "0,1 =", 135, 100, CREME, 4)
    n = n_bin(t)
    coupe = t >= COUPE
    if n:
        txt = BIN[:n]
        w = largeur(txt, 3)
        x = min(18, 246 - w) if t < M(96) else min(18, 246 - largeur(BIN[:n_bin(M(96))], 3))
        y = 200
        tombe = 0
        for i, ch in enumerate(txt):                     # chaque groupe 0011 sur fond rouge
            xi = x + (largeur(txt[:i], 3) + 3 if i else 0)
            if coupe and xi > 165:
                v = t - COUPE
                tombe = round(300 * v * v + 40 * v)
            yy = y + (tombe if coupe and xi > 165 else 0)
            if i >= 3:
                rect(buf, xi - 2, yy - 3, xi + 17, yy + 23, ROUGE_S if ((i - 3) // 4) % 2 == 0 else C[21])
            ecrire(buf, ch, xi, yy, CREME, 3)
        if t >= M(89):                                   # le premier 0011 entouré au feutre
            xa, xb = x + largeur(txt[:3], 3) + 3, x + largeur(txt[:7], 3)
            if not coupe or xa < 165:
                ellipse(buf, (xa + xb) // 2, y + 10, (xb - xa) // 2 + 10, 22, ROUGE, entre(t, M(89), M(89) + 0.35))
        if M(94) <= t < M(96):
            lignes_vitesse(buf, t, 1.2)
    zz = pop(t, M(95), 4)
    if zz and t < M(96):
        poser_centre(buf, O["infini"], 135, 270, zz)
    # scène 11 : les ciseaux
    if t >= M(96):
        xs = 300 - round(135 * entre(t, M(96), COUPE - 0.1))     # le milieu des lames arrive en x = 165
        ferme = t >= COUPE
        poser(buf, O["ciseaux"], xs - 35, 168 + (4 if ferme else 0), 5)
        texte_pop(buf, "53", 135, 88, OR, t, M(101), 7)
        texte_pop(buf, "CHIFFRES", 135, 140, CREME, t, M(102), 3)
    if flash(t, COUPE):
        return neuf(CREME)
    dx, dy = secousse(t, COUPE, 4, 0.4)
    if dx == 0:
        dx, dy = secousse(t, M(101), 3, 0.3)
    return secouer(buf, dx, dy)


ev(T11, "whoosh"); ev(M(74), "pop"); ev(M(77), "pop_grave"); ev(M(84), "bloup")
for i in DIGITS_MOTS:
    ev(M(i), "bip_bin")
ev(M(89), "feutre"); ev(M(94), "defile"); ev(M(95), "pop_aigu")
ev(M(96), "glisse"); ev(COUPE, "ciseaux"); ev(M(101), "impact_doux"); ev(M(102), "pop")


# ---- scène 12 : 0,1 vaut en vrai un tout petit peu plus (la loupe)
VRAI = "0,1000000000000000055"
T13 = M(114) - 0.12


def s12(t):
    buf = neuf(CONTOUR)
    grille(buf)
    y_big = 160 - round(70 * entre(t, M(107), M(107) + 0.25))
    z_big = 8 if t < M(107) else 5
    texte_pop(buf, "0,1", 135, y_big, CREME, t, M(104), z_big)
    if t >= M(107):
        n = min(len(VRAI), int((t - M(107)) * 40) + 3)
        ecrire(buf, VRAI[:n], 13, 200, CREME, 2,
               couleur_de=lambda i: ROUGE if i >= len(VRAI) - 2 else CREME)
    z, cx, cy = 1, 135, 240
    x55 = 13 + largeur(VRAI[:-2], 2) + 2                     # début des « 55 »
    if t >= M(110):                                          # la loupe arrive au-dessus des 55 et les grossit
        lx = 330 - round((330 - (x55 + 10)) * entre(t, M(110), M(110) + 0.25))
        ly = 140
        for x, y, c in O["loupe"][2]:
            if c != C[12] and c != C[8]:                         # verre transparent : seul le cadre se pose
                cc = C[6] if c == CONTOUR else c                 # cadre gris clair : visible sur la nuit
                rect(buf, lx - 37 + 5 * x, ly - 37 + 5 * y, lx - 37 + 5 * x + 4, ly - 37 + 5 * y + 4, cc)
        for y in range(-24, 25):
            for x in range(-24, 25):
                if x * x + y * y <= 24 * 24:
                    pt(buf, lx - 3 + x, ly - 7 + y, OMBRE)
        rect(buf, lx - 18, ly - 24, lx - 14, ly - 22, C[5])        # reflet
        ecrire_centre(buf, "55", lx - 3, ly - 7, ROUGE, 4)
        rect(buf, x55 - 1, 198, x55 + 22, 199, ROUGE)                # souligné sous les vrais 55
    if t >= M(111):
        z, cx, cy = 2, x55 + 18, 170
    texte_pop(buf, "+", x55 + 46, 104, ROUGE, t, M(113), 4)
    buf = camera(buf, z, cx, cy)
    return secouer(buf, *secousse(t, M(113), 3, 0.3))


ev(T12, "whoosh"); ev(M(104), "pop_grave"); ev(M(107), "imprime"); ev(M(110), "glisse"); ev(M(111), "zoom"); ev(M(113), "pop_aigu")


# ---- scène 13 : l'addition à la craie
LIGNES = [("0,1000000000000000055", 122), ("+0,2000000000000000111", 142), ("0,3000000000000000166", 166)]
T14 = M(127) - 0.1


def s13(t):
    buf = neuf()
    fond(buf, "classe")
    for k, (txt, y) in enumerate(LIGNES):
        w = largeur(txt, 2, "3x5")
        xd = 240 - w
        if k == 0 and t >= M(115):
            ecrire(buf, txt, xd - round(260 * (1 - entre(t, M(115), M(115) + 0.2))), y, CREME, 2, "3x5")
        if k == 1 and t >= M(117):
            ecrire(buf, txt, xd + round(260 * (1 - entre(t, M(117), M(117) + 0.2))), y, CREME, 2, "3x5")
        if k == 2 and t >= M(120):
            n = min(len(txt), int((t - M(120)) * 50) + 1)
            ecrire(buf, txt[:n], xd, y, CREME, 2, "3x5")
    if t >= M(119):
        rect(buf, 56, 156, 56 + round(186 * entre(t, M(119), M(119) + 0.2)), 157, CREME)
    if t >= M(122):
        ecrire(buf, "ORDI :", 34, 206 - (2 if (t - M(122)) * IPS < 2 else 0), OR, 2)
        ecrire(buf, PRIX, 96, 208, OR, 2, "3x5", couleur_de=lambda i: ROUGE if i == len(PRIX) - 1 else OR)
        x4 = 96 + largeur(PRIX[:-1], 2, "3x5") + 2 + 3          # milieu du dernier « 4 »
        if t >= M(124):
            ellipse(buf, x4, 213, 9, 11, ROUGE, entre(t, M(124), M(124) + 0.3))
        if t >= M(126):
            fleche(buf, x4, 228, t, 2)
    poser(buf, repos(t), 14, Y0)
    return secouer(buf, *secousse(t, M(122), 2, 0.25))


ev(T13, "whoosh"); ev(M(115), "glisse"); ev(M(117), "glisse"); ev(M(119), "craie")
ev(M(120), "imprime"); ev(M(122), "impact_doux"); ev(M(124), "feutre"); ev(M(126), "pop_aigu")


# ---- scène 14 : le fameux 4, et Tim paie
PAYE = M(135)


def s14(t):
    buf = neuf()
    prend = PAYE <= t < PAYE + 0.35
    tim = TEND if M(131) <= t < PAYE + 0.25 else None
    miette = None
    if M(131) <= t < PAYE + 0.25:
        mx, my = X0 + 27, Y0 + 18
        if t >= PAYE:
            u = entre(t, PAYE, PAYE + 0.2)
            mx, my = round(mx + (MX + 1 - mx) * u), round(my + (MY + 24 - my) * u)
        miette = (mx, my)
    marchand = 4 if prend else (3 if M(133) <= t < PAYE else 0)
    boutique(buf, t, tim=tim, marchand=marchand, miette=miette)
    n = len(PRIX)
    if t >= PAYE + 0.4:
        n = max(0, len(PRIX) - int((t - PAYE - 0.4) * 30))
    if n:
        ruban(buf, 186)
        ticket(buf, PRIX[:n], 236, 186)
    z, cx, cy = 1, 135, 240
    if M(129) <= t < M(130):
        z, cx, cy = 3, 222, 196
        if int(t * 8) % 2:                              # le 4 clignote rouge / or
            g = 236 - largeur(PRIX, 2, "3x5") - 6
            ecrire(buf, "4", g + 3 + largeur(PRIX[:-1], 2, "3x5") + 2, 190, OR, 2, "3x5")
    buf = camera(buf, z, cx, cy)
    return secouer(buf, *secousse(t, M(129), 3, 0.4))


ev(T14, "flash"); ev(M(129), "impact"); ev(M(130), "whoosh"); ev(M(131), "scintille"); ev(PAYE, "piece")
ev(PAYE + 0.4, "imprime")

# ---------------------------------------------------------------- montage des scènes et transitions
SCENES = [(0, s1), (T2, s2), (T3, s3), (T4, s4), (T5, s5), (T6, s6), (T7, s7), (T8, s8), (T9, plongee),
          (T10, s9), (T11, s10), (T12, s12), (T13, s13), (T14, s14)]
# transition à l'entrée d'une scène : (type, durée)
TRANS = {T2: ("pousse", 0.25), T5: ("damier", 0.25), T6: ("pousse", 0.25), T7: ("damier", 0.25),
         T11: ("pousse", 0.25), T12: ("damier", 0.25), T13: ("pousse", 0.25)}


def scene_a(t):
    k = max(i for i, (t0, _) in enumerate(SCENES) if t >= t0)
    return k


def rendre(t):
    k = scene_a(t)
    t0, f = SCENES[k]
    buf = f(t)
    if t0 in TRANS:
        typ, d = TRANS[t0]
        u = (t - t0) / d
        if u < 1 and k > 0:
            avant = SCENES[k - 1][1](t)
            if typ == "pousse":                          # la nouvelle scène pousse l'ancienne vers la gauche
                p = round(L * lisse(u))
                out = bytearray()
                for y in range(H):
                    out += avant[(y * L + p) * 3:(y + 1) * L * 3] + buf[y * L * 3:(y * L + p) * 3]
                buf = out
            else:                                        # volet en damier, en diagonale
                for cy in range(0, H, 16):
                    for cx in range(0, L, 15):
                        if (cx / L + cy / H) / 2 > u:
                            for y in range(cy, min(H, cy + 16)):
                                a = (y * L + cx) * 3
                                buf[a:a + 45] = avant[a:a + 45]
    if t0 in (T3, T14) and flash(t, t0):
        buf = neuf(CREME)
    # bande sombre sous le sous-titre actif (Press Start 2P 16 px, centré en x = 135, ligne de base y = 340)
    for s in SOUS_TITRES:                              # mêmes instants que la comp pixel (grille 12 i/s)
        if round(s["debut"] * 12) / 12 <= t < round(s["fin"] * 12) / 12:
            w = 16 * len(s["texte"]) + 16
            rect(buf, 135 - w // 2, 318, 135 + w // 2, 346, CONTOUR)
            break
    return buf


ev(T3, "flash")
for t0, (typ, d) in TRANS.items():
    ev(t0, "whoosh" if typ == "pousse" else "volet")


def main():
    images = None
    if "--images" in sys.argv:
        images = [int(v) for v in sys.argv[sys.argv.index("--images") + 1].split(",")]
    sortie = os.path.join(ICI, "scene")
    os.makedirs(sortie, exist_ok=True)
    with open(os.path.join(ICI, "evenements.json"), "w", encoding="utf-8", newline="\n") as f:
        json.dump(sorted(EV), f, ensure_ascii=False, indent=0)
    if images:
        for n in images:
            buf = rendre(n / IPS)
            p = subprocess.run([FFMPEG, "-loglevel", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{L}x{H}",
                                "-i", "-", "-vf", "scale=iw*2:ih*2:flags=neighbor", os.path.join(ICI, f"controle_{n:04d}.png")],
                               input=bytes(buf))
        print(f"{len(images)} images de contrôle dans {ICI}")
        return
    for vieux in os.listdir(sortie):
        os.remove(os.path.join(sortie, vieux))
    p = subprocess.Popen([FFMPEG, "-loglevel", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{L}x{H}",
                          "-r", str(IPS), "-i", "-", "-vf", "scale=iw*4:ih*4:flags=neighbor",
                          "-start_number", "0", os.path.join(sortie, "scene_%04d.png")], stdin=subprocess.PIPE)
    for n in range(N):
        p.stdin.write(bytes(rendre(n / IPS)))
        if n % 120 == 0:
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
