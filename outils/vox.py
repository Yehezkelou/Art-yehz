#!/usr/bin/env python3
"""Modèles voxel par script : grille, calques ASCII, fichiers .vox MagicaVoxel, aperçu PNG (Python pur).

    import vox
    m = vox.Modele(8, 8, 8, nom="tete")          # axes : x → droite, y → haut, z → avant (vue de face : on regarde vers −z)
    m[3, 0, 4] = 11                              # index de la palette ico-pixel-32 (1–32), 0 = vide
    m.boite(0, 0, 0, 7, 3, 7, 28)                # bornes incluses
    m.calques([                                  # un calque par hauteur y (le 1er = y0), une ligne par z (la 1re = z0,
        ["##", "#."],                            #   le fond), un caractère par x ; « . » et « espace » = vide
        "## \\n.#",                              # un calque peut aussi être un texte multiligne
    ], {"#": 11}, x0=0, y0=4, z0=0)
    d = m.miroir_x()                             # copie retournée gauche ↔ droite ; m.copier() : copie
    vox.ecrire_vox("perso.vox", [m, d])          # un ou plusieurs modèles (noms gardés), palette ico-pixel-32
    modeles = vox.lire_vox("perso.vox")          # → liste de Modele (index > 32 refusés)
    vox.apercu("apercu.png", m, vue="trois-quarts", taille=2)   # vues : trois-quarts, face, dessus, cote
    vox.palette_magicavoxel("ico-pixel-32-magicavoxel.png")     # palette 256×1 à charger dans MagicaVoxel

    python3 -I outils/vox.py info perso.vox                     # modèles, tailles, nombre de voxels, couleurs
    python3 -I outils/vox.py apercu perso.vox apercu.png [--vue face] [--taille 3] [--modele 0]
    python3 -I outils/vox.py palette assets/3d/palette/ico-pixel-32-magicavoxel.png

Fichier .vox (format MagicaVoxel, version 150) : chunks VOX/MAIN/SIZE/XYZI, puis le graphe de scène
(nTRN/nGRP/nSHP, un nœud par modèle avec son nom « _name », modèles côte à côte en x), LAYR 0 et RGBA (couleur
de l'index i à l'entrée i − 1 : nos 32 couleurs aux index 1–32, le reste noir opaque). Axes MagicaVoxel (z en haut,
on regarde la face avant depuis −y) : x_vox = x, y_vox = lz − 1 − z, z_vox = y (rotation, pas de miroir).

Rampes d'ombrage (même table que outils/rendu3d/voxel.mjs) : RAMPES = les rampes de la palette, du plus sombre
au plus clair (gris 1–8 en une rampe continue, puis 9–12, 13–16, 17–20, 21–24, 25–28, 29–32) ;
rampe(i) → {"dessus", "face", "cote", "dessous"} ; plus_sombre(i) → un cran plus sombre dans la même rampe.
"""
import argparse, os, struct, sys, zlib

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import chemins  # noqa: E402

PALETTE_HEX = chemins.dans_racine("bible", "palette", "ico-pixel-32.hex")  # racine : outils/.. ou ICO_VIDEOS
TAILLE_MAX = 256
VERSION = 150
RAMPES = (tuple(range(1, 9)), (9, 10, 11, 12), (13, 14, 15, 16), (17, 18, 19, 20),
          (21, 22, 23, 24), (25, 26, 27, 28), (29, 30, 31, 32))


class ErreurVox(ValueError):
    pass


# ---------- palette et rampes ----------
def lire_palette(chemin=PALETTE_HEX):
    """Les 32 couleurs (r, g, b) du .hex, dans l'ordre (élément 0 = index 1)."""
    coul = []
    with open(chemin, encoding="utf-8") as f:
        for ligne in f:
            ligne = ligne.split(";")[0].strip().lstrip("#")
            if not ligne or ligne.startswith("//"):
                continue
            if len(ligne) != 6:
                raise ErreurVox(f"palette {chemin} : couleur invalide « {ligne} »")
            coul.append(tuple(int(ligne[k:k + 2], 16) for k in (0, 2, 4)))
    if len(coul) != 32:
        raise ErreurVox(f"palette {chemin} : {len(coul)} couleurs (32 attendues)")
    return coul


def _verifier_index(i, vide=False):
    if not isinstance(i, int) or isinstance(i, bool) or not (0 if vide else 1) <= i <= 32:
        raise ErreurVox(f"index de couleur {i!r} hors palette (entier 1–32{', 0 = vide' if vide else ''})")


def _rampe_de(i):
    _verifier_index(i)
    for r in RAMPES:
        if i in r:
            return r, r.index(i)
    raise AssertionError(i)


def rampe(i):
    """Couleurs d'un voxel d'index i selon l'orientation de la face : {dessus, face, cote, dessous}.

    face = i ; si i a un voisin plus clair dans sa rampe : dessus = +1, cote = −1, dessous = −2 ;
    si i est le plus clair : dessus = −1, cote = −2, dessous = −3 (le dessus reste distinct de la face).
    Bornes : on reste dans la rampe (le plus sombre se répète)."""
    r, p = _rampe_de(i)
    n = len(r)
    c = lambda k: r[min(n - 1, max(0, k))]  # noqa: E731
    if p < n - 1:
        return {"dessus": c(p + 1), "face": i, "cote": c(p - 1), "dessous": c(p - 2)}
    return {"dessus": c(p - 1), "face": i, "cote": c(p - 2), "dessous": c(p - 3)}


def plus_sombre(i):
    """Un cran plus sombre dans la même rampe (le plus sombre reste lui-même) : palier d'occlusion."""
    r, p = _rampe_de(i)
    return r[max(0, p - 1)]


# ---------- modèle ----------
class Modele:
    """Grille lx × ly × lz de voxels ; m[x, y, z] = index 1–32 (0 = vide)."""

    def __init__(self, lx, ly, lz, nom=""):
        for k, v in (("lx", lx), ("ly", ly), ("lz", lz)):
            if not isinstance(v, int) or not 1 <= v <= TAILLE_MAX:
                raise ErreurVox(f"{k} = {v!r} : entier de 1 à {TAILLE_MAX} attendu (limite MagicaVoxel)")
        self.lx, self.ly, self.lz, self.nom = lx, ly, lz, str(nom)
        self.donnees = bytearray(lx * ly * lz)  # index x + lx × (y + ly × z)

    @property
    def taille(self):
        return (self.lx, self.ly, self.lz)

    def _k(self, xyz):
        try:
            x, y, z = xyz
        except (TypeError, ValueError):
            raise TypeError("m[x, y, z] attendu") from None
        if not all(isinstance(v, int) for v in (x, y, z)):
            raise TypeError(f"coordonnées entières attendues : {xyz!r}")
        if not (0 <= x < self.lx and 0 <= y < self.ly and 0 <= z < self.lz):
            raise IndexError(f"voxel {xyz} hors du modèle {self.lx}×{self.ly}×{self.lz}")
        return x + self.lx * (y + self.ly * z)

    def __getitem__(self, xyz):
        return self.donnees[self._k(xyz)]

    def __setitem__(self, xyz, i):
        _verifier_index(i, vide=True)
        self.donnees[self._k(xyz)] = i

    def dedans(self, x, y, z):
        return 0 <= x < self.lx and 0 <= y < self.ly and 0 <= z < self.lz

    def lire(self, x, y, z):
        """Comme m[x, y, z] mais 0 hors du modèle."""
        return self.donnees[x + self.lx * (y + self.ly * z)] if self.dedans(x, y, z) else 0

    def __eq__(self, autre):
        return isinstance(autre, Modele) and self.taille == autre.taille and self.donnees == autre.donnees

    def __repr__(self):
        return f"Modele({self.lx}, {self.ly}, {self.lz}, nom={self.nom!r}, voxels={self.compter()})"

    def voxels(self):
        """(x, y, z, i) de chaque voxel plein, z puis y puis x croissants."""
        lx, ly = self.lx, self.ly
        for k, i in enumerate(self.donnees):
            if i:
                yield k % lx, (k // lx) % ly, k // (lx * ly), i

    def compter(self):
        return sum(1 for i in self.donnees if i)

    def couleurs(self):
        return sorted(set(self.donnees) - {0})

    def boite(self, x0, y0, z0, x1, y1, z1, i):
        """Remplit la boîte [x0, x1] × [y0, y1] × [z0, z1] (bornes incluses, dans n'importe quel ordre) ; i = 0 creuse."""
        _verifier_index(i, vide=True)
        xa, xb = sorted((x0, x1))
        ya, yb = sorted((y0, y1))
        za, zb = sorted((z0, z1))
        self._k((xa, ya, za)), self._k((xb, yb, zb))  # bornes dans le modèle
        for z in range(za, zb + 1):
            for y in range(ya, yb + 1):
                base = self.lx * (y + self.ly * z)
                self.donnees[base + xa:base + xb + 1] = bytes([i]) * (xb - xa + 1)
        return self

    def calques(self, lignes_par_y, legende, x0=0, y0=0, z0=0):
        """Dessine par calques ASCII : calque n → y = y0 + n ; ligne k du calque → z = z0 + k ; caractère c → x = x0 + c.

        Un calque = liste de chaînes ou texte multiligne (lignes vides et indentation commune retirées).
        legende : caractère → index (1–32) ; « . » et « espace » = vide (sauf s'ils sont dans la légende) ;
        un caractère inconnu est une erreur. Les cases vides n'effacent rien."""
        for c, i in legende.items():
            if not isinstance(c, str) or len(c) != 1:
                raise ErreurVox(f"légende : clé {c!r} (un seul caractère attendu)")
            _verifier_index(i, vide=True)
        for n, calque in enumerate(lignes_par_y):
            if isinstance(calque, str):
                lignes = [l for l in calque.split("\n") if l.strip()]
                retrait = min((len(l) - len(l.lstrip(" ")) for l in lignes), default=0)
                lignes = [l[retrait:].rstrip() for l in lignes]
            else:
                lignes = list(calque)
            for k, ligne in enumerate(lignes):
                for c, ch in enumerate(ligne):
                    if ch in legende:
                        i = legende[ch]
                    elif ch in ". ":
                        continue
                    else:
                        raise ErreurVox(f"calque {n} (y = {y0 + n}), ligne {k} : caractère « {ch} » absent de la légende")
                    if i:
                        self[x0 + c, y0 + n, z0 + k] = i
        return self

    def copier(self, nom=None):
        m = Modele(self.lx, self.ly, self.lz, self.nom if nom is None else nom)
        m.donnees[:] = self.donnees
        return m

    def miroir_x(self, nom=None):
        """Nouvelle grille retournée gauche ↔ droite (x → lx − 1 − x) ; l'original ne change pas."""
        m = Modele(self.lx, self.ly, self.lz, self.nom if nom is None else nom)
        lx = self.lx
        for base in range(0, len(self.donnees), lx):
            m.donnees[base:base + lx] = self.donnees[base:base + lx][::-1]
        return m

    def symetrie_x(self, depuis="gauche"):
        """Recopie la moitié x < lx/2 (« gauche ») ou x >= lx/2 (« droite ») sur l'autre moitié, sur place."""
        if depuis not in ("gauche", "droite"):
            raise ErreurVox("symetrie_x : depuis = « gauche » ou « droite »")
        lx = self.lx
        for base in range(0, len(self.donnees), lx):
            for x in range(lx // 2):
                a, b = base + x, base + lx - 1 - x
                if depuis == "gauche":
                    self.donnees[b] = self.donnees[a]
                else:
                    self.donnees[a] = self.donnees[b]
        return self


# ---------- écriture .vox ----------
def _chunk(ident, contenu=b"", enfants=b""):
    return ident + struct.pack("<ii", len(contenu), len(enfants)) + contenu + enfants


def _chaine(s):
    b = str(s).encode("utf-8")
    return struct.pack("<i", len(b)) + b


def _dict(d):
    return struct.pack("<i", len(d)) + b"".join(_chaine(k) + _chaine(v) for k, v in d.items())


def ecrire_vox(chemin, modeles, palette=None):
    """Écrit un ou plusieurs Modele dans un .vox MagicaVoxel (version 150), palette ico-pixel-32 aux index 1–32."""
    if isinstance(modeles, Modele):
        modeles = [modeles]
    modeles = list(modeles)
    if not modeles or not all(isinstance(m, Modele) for m in modeles):
        raise ErreurVox("ecrire_vox : un Modele ou une liste non vide de Modele attendu")
    pal = palette or lire_palette()
    corps = b""
    for m in modeles:
        corps += _chunk(b"SIZE", struct.pack("<iii", m.lx, m.lz, m.ly))
        vs = [(x, m.lz - 1 - z, y, i) for x, y, z, i in m.voxels()]
        corps += _chunk(b"XYZI", struct.pack("<i", len(vs)) + b"".join(struct.pack("<4B", *v) for v in vs))
    # graphe de scène : nTRN 0 → nGRP 1 → (nTRN 2 + 2k → nSHP 3 + 2k → modèle k)
    n = len(modeles)
    corps += _chunk(b"nTRN", struct.pack("<i", 0) + _dict({}) + struct.pack("<iiii", 1, -1, -1, 1) + _dict({}))
    corps += _chunk(b"nGRP", struct.pack("<i", 1) + _dict({}) + struct.pack("<i", n)
                    + b"".join(struct.pack("<i", 2 + 2 * k) for k in range(n)))
    x = 0
    for k, m in enumerate(modeles):
        tx = x + m.lx // 2  # MagicaVoxel pose le centre du modèle à la translation : modèles côte à côte
        x += m.lx + 2
        attr = {"_name": m.nom} if m.nom else {}
        corps += _chunk(b"nTRN", struct.pack("<i", 2 + 2 * k) + _dict(attr) + struct.pack("<iiii", 3 + 2 * k, -1, 0, 1)
                        + _dict({"_t": f"{tx} 0 {m.ly // 2}"}))
        corps += _chunk(b"nSHP", struct.pack("<i", 3 + 2 * k) + _dict({}) + struct.pack("<ii", 1, k) + _dict({}))
    corps += _chunk(b"LAYR", struct.pack("<i", 0) + _dict({"_name": "ico"}) + struct.pack("<i", -1))
    rgba = b"".join(struct.pack("<4B", r, g, b, 255) for r, g, b in pal) + struct.pack("<4B", 0, 0, 0, 255) * (256 - len(pal))
    corps += _chunk(b"RGBA", rgba)
    donnees = b"VOX " + struct.pack("<i", VERSION) + _chunk(b"MAIN", b"", corps)
    os.makedirs(os.path.dirname(os.path.abspath(chemin)), exist_ok=True)
    with open(chemin, "wb") as f:
        f.write(donnees)
    return chemin


# ---------- lecture .vox ----------
def _lire_chunks(data, i, fin):
    while i < fin:
        if i + 12 > fin:
            raise ErreurVox("chunk tronqué")
        ident = data[i:i + 4]
        nc, ne = struct.unpack_from("<ii", data, i + 4)
        if nc < 0 or ne < 0 or i + 12 + nc + ne > fin:
            raise ErreurVox(f"chunk {ident!r} tronqué")
        yield ident, data[i + 12:i + 12 + nc], (i + 12 + nc, i + 12 + nc + ne)
        i += 12 + nc + ne


class _Lecteur:
    def __init__(self, b):
        self.b, self.i = b, 0

    def entier(self):
        v = struct.unpack_from("<i", self.b, self.i)[0]
        self.i += 4
        return v

    def chaine(self):
        n = self.entier()
        s = self.b[self.i:self.i + n].decode("utf-8", "replace")
        self.i += n
        return s

    def dict(self):
        return {self.chaine(): self.chaine() for _ in range(self.entier())}


def lire_entete(data):
    """(identifiant, version) des 8 premiers octets."""
    if len(data) < 8:
        raise ErreurVox("fichier trop court")
    return data[:4], struct.unpack_from("<i", data, 4)[0]


def lire_vox(chemin):
    """Liste de Modele (noms lus dans le graphe de scène s'il y en a). Index > 32 → ErreurVox."""
    with open(chemin, "rb") as f:
        data = f.read()
    ident, version = lire_entete(data)
    if ident != b"VOX ":
        raise ErreurVox(f"{chemin} : pas un fichier .vox (en-tête {ident!r})")
    if version not in (150, 200):
        raise ErreurVox(f"{chemin} : version {version} non gérée (150 ou 200)")
    main = list(_lire_chunks(data, 8, len(data)))
    if not main or main[0][0] != b"MAIN":
        raise ErreurVox(f"{chemin} : chunk MAIN absent")
    tailles, modeles, trn, shp = [], [], {}, {}
    for ident, c, (a, b) in _lire_chunks(data, *main[0][2]):
        if ident == b"SIZE":
            tailles.append(struct.unpack_from("<iii", c))
        elif ident == b"XYZI":
            if not tailles or len(tailles) != len(modeles) + 1:
                raise ErreurVox(f"{chemin} : XYZI sans SIZE")
            sx, sy, sz = tailles[-1]
            m = Modele(sx, sz, sy)
            nv = struct.unpack_from("<i", c)[0]
            for k in range(nv):
                xv, yv, zv, i = c[4 + 4 * k:8 + 4 * k]
                if i > 32:
                    raise ErreurVox(f"{chemin} : modèle {len(modeles)}, voxel ({xv}, {yv}, {zv}) d'index {i} hors "
                                    "ico-pixel-32 (1–32) : charger assets/3d/palette/ico-pixel-32-magicavoxel.png")
                m[xv, zv, sy - 1 - yv] = i
            modeles.append(m)
        elif ident == b"nTRN":
            r = _Lecteur(c)
            nid, attr, enfant = r.entier(), r.dict(), r.entier()
            trn[enfant] = attr.get("_name", "")
        elif ident == b"nSHP":
            r = _Lecteur(c)
            nid, _ = r.entier(), r.dict()
            if r.entier() >= 1:
                shp[nid] = r.entier()
    for nid, k in shp.items():
        if 0 <= k < len(modeles) and trn.get(nid) and not modeles[k].nom:
            modeles[k].nom = trn[nid]
    return modeles


def lire_rgba(chemin):
    """Les 256 entrées (r, g, b, a) du chunk RGBA (entrée k = index k + 1), ou None."""
    with open(chemin, "rb") as f:
        data = f.read()
    main = list(_lire_chunks(data, 8, len(data)))
    for ident, c, _ in _lire_chunks(data, *main[0][2]):
        if ident == b"RGBA":
            return [tuple(c[4 * k:4 * k + 4]) for k in range(256)]
    return None


# ---------- PNG ----------
def ecrire_png(chemin, largeur, hauteur, pixels):
    """pixels : liste de (r, g, b, a), ligne par ligne → PNG RGBA 8 bits (filtre 0)."""
    def morceau(t, d):
        return struct.pack(">I", len(d)) + t + d + struct.pack(">I", zlib.crc32(t + d) & 0xFFFFFFFF)
    brut = bytearray()
    for y in range(hauteur):
        brut.append(0)
        for p in pixels[y * largeur:(y + 1) * largeur]:
            brut += bytes(p)
    data = (b"\x89PNG\r\n\x1a\n" + morceau(b"IHDR", struct.pack(">IIBBBBB", largeur, hauteur, 8, 6, 0, 0, 0))
            + morceau(b"IDAT", zlib.compress(bytes(brut), 9)) + morceau(b"IEND", b""))
    os.makedirs(os.path.dirname(os.path.abspath(chemin)), exist_ok=True)
    with open(chemin, "wb") as f:
        f.write(data)
    return chemin


def palette_magicavoxel(chemin_png, palette=None):
    """Palette 256×1 pour MagicaVoxel : pixel x = couleur de l'index x + 1 (nos 32, puis noir opaque)."""
    pal = palette or lire_palette()
    px = [(r, g, b, 255) for r, g, b in pal] + [(0, 0, 0, 255)] * (256 - len(pal))
    return ecrire_png(chemin_png, 256, 1, px)


VUES = ("trois-quarts", "face", "dessus", "cote")


def apercu(chemin_png, modele, vue="trois-quarts", taille=2, palette=None):
    """Image de contrôle : « face » (depuis +z), « dessus » (depuis +y), « cote » (depuis +x) en carrés de 2 × taille px,
    « trois-quarts » en isométrie 2:1 (on voit le dessus, la face +z à gauche, le côté +x à droite ; cube de 4 × taille px).
    Couleurs de la rampe (dessus / face / cote) ; fond transparent ; rien d'autre que la palette."""
    if vue not in VUES:
        raise ErreurVox(f"vue « {vue} » inconnue ({', '.join(VUES)})")
    if not isinstance(taille, int) or taille < 1:
        raise ErreurVox("taille : entier >= 1")
    pal = palette or lire_palette()
    col = lambda i: pal[i - 1] + (255,)  # noqa: E731
    m = modele
    if vue != "trois-quarts":
        s = 2 * taille
        if vue == "face":
            W, H, prof = m.lx, m.ly, m.lz
            cell = lambda u, v, d: (u, v, prof - 1 - d)         # noqa: E731
            role = "face"
        elif vue == "dessus":
            W, H, prof = m.lx, m.lz, m.ly
            cell = lambda u, v, d: (u, prof - 1 - d, v)         # noqa: E731  (haut de l'image = fond z0)
            role = "dessus"
        else:
            W, H, prof = m.lz, m.ly, m.lx
            cell = lambda u, v, d: (prof - 1 - d, v, m.lz - 1 - u)  # noqa: E731  (on regarde vers −x)
            role = "cote"
        img = [(0, 0, 0, 0)] * (W * s * H * s)
        for v in range(H):
            for u in range(W):
                for d in range(prof):
                    x, y, z = cell(u, v, d)
                    i = m.lire(x, y, z)
                    if i:
                        c = col(rampe(i)[role])
                        yy = (H - 1 - v) if vue != "dessus" else v
                        for a in range(s):
                            o = (yy * s + a) * W * s + u * s
                            img[o:o + s] = [c] * s
                        break
        return ecrire_png(chemin_png, W * s, H * s, img)

    p = taille
    W = (m.lx + m.lz) * 2 * p
    H = (m.lx + m.lz) * p + m.ly * 2 * p
    img = [(0, 0, 0, 0)] * (W * H)
    ox, oy = (m.lz - 1) * 2 * p, (m.ly - 1) * 2 * p
    # masque d'un cube 4p × 4p : 1 = dessus, 2 = face (+z, moitié gauche), 3 = côté (+x, moitié droite)
    masque = []
    for v in range(4 * p):
        for u in range(4 * p):
            dc = u if u < 2 * p else 4 * p - 1 - u
            haut, bas = p - 1 - dc // 2, p + dc // 2
            if v < haut:
                masque.append(0)
            elif v <= bas:
                masque.append(1)
            elif v <= bas + 2 * p:
                masque.append(2 if u < 2 * p else 3)
            else:
                masque.append(0)
    ordre = sorted(m.voxels(), key=lambda t: (t[0] + t[1] + t[2], t[1], t[0]))
    for x, y, z, i in ordre:
        r = rampe(i)
        cs = {1: col(r["dessus"]), 2: col(r["face"]), 3: col(r["cote"])}
        sx = ox + (x - z) * 2 * p
        sy = oy + (x + z) * p - y * 2 * p
        for v in range(4 * p):  # peintre : les voxels plus proches (x + y + z plus grand) recouvrent les faces cachées
            o = (sy + v) * W + sx
            for u in range(4 * p):
                k = masque[v * 4 * p + u]
                if k:
                    img[o + u] = cs[k]
    return ecrire_png(chemin_png, W, H, img)


# ---------- ligne de commande ----------
def main(argv=None):
    ap = argparse.ArgumentParser(description="Fichiers .vox MagicaVoxel (palette ico-pixel-32).")
    sp = ap.add_subparsers(dest="cmd", required=True)
    a = sp.add_parser("info", help="modèles d'un .vox")
    a.add_argument("vox")
    a = sp.add_parser("apercu", help="aperçu PNG d'un modèle")
    a.add_argument("vox")
    a.add_argument("png")
    a.add_argument("--vue", default="trois-quarts", choices=VUES)
    a.add_argument("--taille", type=int, default=2)
    a.add_argument("--modele", default="0", help="numéro ou nom du modèle (défaut 0)")
    a = sp.add_parser("palette", help="palette 256×1 pour MagicaVoxel")
    a.add_argument("png")
    o = ap.parse_args(argv)
    try:
        if o.cmd == "palette":
            print(palette_magicavoxel(o.png))
            return 0
        modeles = lire_vox(o.vox)
        if o.cmd == "info":
            for k, m in enumerate(modeles):
                print(f"{k} {m.nom or '-'} : {m.lx}×{m.ly}×{m.lz}, {m.compter()} voxel(s), couleurs {m.couleurs()}")
            return 0
        choix = [m for k, m in enumerate(modeles) if str(k) == o.modele or m.nom == o.modele]
        if not choix:
            raise ErreurVox(f"modèle « {o.modele} » absent ({', '.join(m.nom or str(k) for k, m in enumerate(modeles))})")
        print(apercu(o.png, choix[0], vue=o.vue, taille=o.taille))
        return 0
    except (ErreurVox, OSError) as e:
        print(f"vox : {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
