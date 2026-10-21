"""Essai de style « portrait monochrome » : gros plan de chat, 96x96, une seule famille de teintes.

Sujet, pose, palette et signature sont les nôtres ; la référence n'a servi qu'à relever la technique
(cadrage serré, une teinte en 14 valeurs, pas de contour noir, fourrure en traits d'1 px).

    python chat.py <dossier>   → chat.png (96x96) et chat-x6.png
"""
import math, os, random, sys

from PIL import Image

L = 96
random.seed(11)


def h(x):
    return tuple(int(x[i:i + 2], 16) for i in (0, 2, 4))


# rampe « ambre » : 14 valeurs, de l'ombre violacée au crème
RAMPE = [h(c) for c in (
    "1A1222", "2A1A28", "3B2A22", "4E3528", "63422C", "7A4E1E", "946028",
    "B9802B", "D09A3C", "E8B44E", "F4C542", "F8D470", "FBE58C", "FFF3C6",
)]
FOND = h("14101E")
ROSE = h("9C5A5A")          # intérieur des oreilles et nez (toujours la même famille chaude)
ACCENT, ACCENT2 = h("9CC7F0"), h("5E8FD6")
NIV = len(RAMPE) - 1

niv = [[None] * L for _ in range(L)]        # niveau dans la rampe, couleur directe, ou None


def pose(x, y, v):
    if 0 <= x < L and 0 <= y < L:
        niv[y][x] = v


def eclaircir(x, y, d):
    if 0 <= x < L and 0 <= y < L and isinstance(niv[y][x], int):
        niv[y][x] = max(0, min(NIV, niv[y][x] + d))


# ---------------------------------------------------------------- silhouette
CX, CY, RX, RY = 48, 57, 34, 31

# bruit de contour : la fourrure déborde de l'ovale, par touffes
TOUFFE = [1.0 + 0.055 * math.sin(a * 7.0 + 1.3) + 0.040 * math.sin(a * 17.0)
          + 0.030 * math.sin(a * 29.0 + 2.1) for a in [i * math.pi / 180 for i in range(360)]]


def rayon(ang):
    return TOUFFE[int(math.degrees(ang) % 360)]


def dans_tete(x, y):
    ang = math.atan2((y - CY) / RY, (x - CX) / RX)
    d = math.hypot((x - CX) / RX, (y - CY) / RY)
    return d <= rayon(ang), d


OREILLES = (  # pointe, base intérieure, base extérieure
    ((15, 5), (37, 27), (12, 33)),
    ((81, 5), (59, 27), (84, 33)),
)


def dans_triangle(x, y, p, a, b):
    def cote(u, v):
        return (v[0] - u[0]) * (y - u[1]) - (v[1] - u[1]) * (x - u[0])
    s = (cote(p, a), cote(a, b), cote(b, p))
    return all(v >= 0 for v in s) or all(v <= 0 for v in s)


def retreci(p, a, b, k):
    cx = ((p[0] + a[0] + b[0]) / 3, (p[1] + a[1] + b[1]) / 3)
    return tuple((cx[0] + (q[0] - cx[0]) * k, cx[1] + (q[1] - cx[1]) * k) for q in (p, a, b))


# ---------------------------------------------------------------- volume
for y in range(L):
    for x in range(L):
        tete, d = dans_tete(x, y)
        oreille = any(dans_triangle(x, y, *o) for o in OREILLES)
        if oreille and not tete:                       # pointe adoucie
            for (p, a, b) in OREILLES:
                if dans_triangle(x, y, p, a, b) and math.hypot(x - p[0], y - p[1]) < 3.2:
                    oreille = False
        if not (tete or oreille):
            continue

        lx, ly = (x - CX) / RX, (y - CY) / RY
        dirlum = -(lx * 0.60 + ly * 0.74)              # lumière en haut à gauche
        if tete:
            v = 5.6 + 4.6 * max(0.0, 1.0 - d) + 3.0 * dirlum
        else:
            v = 4.4 + 2.4 * dirlum                     # oreilles plus sombres, moins modelées
        niv[y][x] = max(0, min(NIV, int(round(v))))

# intérieur des oreilles
for o in OREILLES:
    p, a, b = retreci(*o, 0.42)
    for y in range(0, 40):
        for x in range(L):
            if dans_triangle(x, y, p, a, b):
                if math.hypot(x - p[0], y - p[1]) < 2.6:
                    continue                           # pointe intérieure adoucie
                niv[y][x] = ROSE

# bord des oreilles : un liseré sombre, et des touffes à la base
for (p, a, b) in OREILLES:
    for t in range(60):
        k = t / 59.0
        for (u, v) in ((p, a), (p, b)):
            x = int(round(u[0] + (v[0] - u[0]) * k))
            y = int(round(u[1] + (v[1] - u[1]) * k))
            eclaircir(x, y, -2)
    for t in range(14):                                # touffes de la base
        k = t / 13.0
        x = int(round(a[0] + (b[0] - a[0]) * k)) + random.choice((-1, 0, 1))
        y = int(round(a[1] + (b[1] - a[1]) * k)) + random.choice((0, 1, 2))
        eclaircir(x, y, 2)

# ---------------------------------------------------------------- fourrure
# traits courts d'1 px, surtout sur le pourtour : la fourrure se voit au bord,
# pas au milieu du visage (sinon le volume disparaît)
for _ in range(900):
    ang = random.uniform(0, 2 * math.pi)
    r = 0.52 + 0.50 * math.sqrt(random.random())      # concentrés vers l'extérieur
    x0 = CX + math.cos(ang) * r * RX
    y0 = CY + math.sin(ang) * r * RY
    lg = random.choice((2, 2, 3))
    delta = random.choice((-1, -1, 1)) * (1 if r < 0.9 else 2)
    dx, dy = math.cos(ang + random.uniform(-0.35, 0.35)), math.sin(ang + random.uniform(-0.35, 0.35))
    for k in range(lg):
        eclaircir(int(round(x0 + dx * k)), int(round(y0 + dy * k)), delta)

# structure du visage : arcades plus sombres, arête du nez et pommettes plus claires
for y in range(L):
    for x in range(L):
        if not isinstance(niv[y][x], int):
            continue
        for ox in (29, 67):                            # arcade au-dessus de chaque œil
            if ((x - ox) / 13.0) ** 2 + ((y - 41) / 6.0) ** 2 < 1.0:
                eclaircir(x, y, -2)
        # arête du nez : étroite, marquée entre les yeux puis s'éteint vers le museau
        if 38 <= y <= 66:
            larg = 3.4 - 1.6 * (y - 38) / 28.0
            if abs(x - 48) < larg:
                eclaircir(x, y, 2 if y < 52 else 1)
        for ox in (20, 76):                            # pommettes, dans l'ombre
            if ((x - ox) / 9.0) ** 2 + ((y - 62) / 11.0) ** 2 < 1.0:
                eclaircir(x, y, -2)

# rayures du front, en arc
for i, (xc, lg, prof) in enumerate(((48, 12, 4), (36, 10, 3), (60, 10, 3), (27, 7, 2), (69, 7, 2))):
    for k in range(lg):
        y = 20 + k
        x = int(xc + math.sin(k * 0.22 + i * 1.7) * 2.0 + (k * (xc - 48)) * 0.035)
        for ddx in (0, 1):
            eclaircir(x + ddx, y, -prof)

# ---------------------------------------------------------------- yeux
def oeil(ox, oy, sens):
    RXE, RYE = 11.0, 9.5
    for y in range(oy - 14, oy + 14):
        for x in range(ox - 14, ox + 14):
            if not (0 <= x < L and 0 <= y < L) or niv[y][x] is None:
                continue
            nx, ny = (x - ox) / RXE, (y - oy) / RYE
            if ny < 0:
                ny *= 1.18                              # amande : paupière plus plate en haut
            d = nx * nx + ny * ny
            if d > 1.0:
                continue
            if d > 0.80:
                niv[y][x] = 1 if ny < 0.15 else 2       # cerne, plus marqué en haut
                continue
            dd = d / 0.80
            niv[y][x] = max(3, min(NIV, int(round(11.2 - 6.4 * dd - 1.3 * ny))))
    # pupille fendue
    for y in range(oy - 9, oy + 10):
        t = abs(y - oy) / 9.0
        larg = max(0, int(round(2.4 * (1.0 - t ** 1.7))))
        for x in range(ox - larg, ox + larg + 1):
            if isinstance(niv[y][x], int):
                niv[y][x] = 0
    # reflet froid
    rx = ox + sens * -4
    for ddx, ddy, c in ((0, -5, ACCENT), (1, -5, ACCENT), (0, -4, ACCENT),
                        (1, -4, ACCENT2), (0, -6, ACCENT2)):
        pose(rx + ddx, oy + ddy, c)
    pose(ox + sens * 5, oy + 4, RAMPE[12])              # petit rebond de lumière en bas


oeil(29, 54, 1)
oeil(67, 54, 1)

# ---------------------------------------------------------------- museau
for y in range(64, 88):
    for x in range(30, 67):
        if not isinstance(niv[y][x], int):
            continue
        for cx2 in (41, 55):                            # deux bajoues
            if ((x - cx2) / 11.0) ** 2 + ((y - 75) / 8.0) ** 2 < 1.0:
                eclaircir(x, y, 2)
                break

for k, lg in enumerate((3, 2, 1)):                      # nez
    for x in range(48 - lg, 48 + lg + 1):
        pose(x, 68 + k, ROSE)
for k in range(2):
    pose(48, 71 + k, 2)
for sens in (-1, 1):                                    # bouche
    for k in range(4):
        x, y = 48 + sens * (1 + k), 73 + (1 if k > 1 else 0)
        eclaircir(x, y, -3)

# points des moustaches
for sens in (-1, 1):
    for i in range(3):
        for j in range(2):
            eclaircir(48 + sens * (6 + j * 4), 72 + i * 3, -2)

# ---------------------------------------------------------------- moustaches
for sens in (-1, 1):
    for i, (y0, courbe, lg) in enumerate(((-4, -0.016, 24), (0, 0.004, 26), (5, 0.022, 21))):
        for k in range(lg):
            x = 48 + sens * (13 + k)
            y = 74 + y0 + courbe * k * k + (-0.18 if i == 0 else 0.10) * k
            yy = int(round(y))
            if not (0 <= x < L and 0 <= yy < L) or isinstance(niv[yy][x], tuple):
                continue
            clair = 12 if k < lg * 0.55 else 10         # la pointe s'éteint
            if niv[yy][x] is None:
                if k % 5 != 4:                          # trait discontinu sur le fond
                    niv[yy][x] = clair - 2
            elif niv[yy][x] < clair:
                niv[yy][x] = clair

# ---------------------------------------------------------------- rendu
img = Image.new("RGB", (L, L), FOND)
px = img.load()
for y in range(L):
    for x in range(L):
        v = niv[y][x]
        if v is not None:
            px[x, y] = v if isinstance(v, tuple) else RAMPE[v]

out = sys.argv[1] if len(sys.argv) > 1 else "."
os.makedirs(out, exist_ok=True)
img.save(os.path.join(out, "chat.png"))
img.resize((L * 6, L * 6), Image.NEAREST).save(os.path.join(out, "chat-x6.png"))
print("ok", L, "x", L, "·", len(img.getcolors(9999)), "couleurs")
