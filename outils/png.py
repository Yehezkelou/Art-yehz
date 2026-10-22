#!/usr/bin/env python3
"""Lecteur PNG minimal en Python standard (zlib + struct), sans Pillow.

    import png
    largeur, hauteur, pixels = png.lire("image.png")   # pixels : liste de (r, g, b, a), ligne par ligne
    python3 -I ~/videos/outils/png.py image.png         # affiche la taille et le nombre de couleurs

Formats lus : profondeur 8 bits, types 2 (RGB), 3 (indexé, transparence tRNS), 6 (RGBA),
plus 0 (gris) et 4 (gris + alpha) ; filtres 0 à 4 ; pas d'entrelacement (Adam7).
Un tRNS sur une image RGB ou grise rend transparente la couleur indiquée.
Sert à verifier_pixels.py et à decouper_planche.py.
"""
import struct, sys, zlib

SIGNATURE = b"\x89PNG\r\n\x1a\n"
CANAUX = {0: 1, 2: 3, 3: 1, 4: 2, 6: 4}


class ErreurPNG(ValueError):
    pass


def _morceaux(data):
    if data[:8] != SIGNATURE:
        raise ErreurPNG("signature PNG absente")
    i = 8
    while i + 8 <= len(data):
        n, typ = struct.unpack(">I4s", data[i:i + 8])
        if i + 12 + n > len(data):
            raise ErreurPNG(f"morceau {typ!r} tronqué")
        yield typ, data[i + 8:i + 8 + n]
        if typ == b"IEND":
            return
        i += 12 + n
    raise ErreurPNG("IEND absent (fichier tronqué)")


def _paeth(a, b, c):
    p = a + b - c
    pa, pb, pc = abs(p - a), abs(p - b), abs(p - c)
    if pa <= pb and pa <= pc:
        return a
    return b if pb <= pc else c


def _defiltrer(brut, largeur, hauteur, bpp):
    """Retire les filtres 0–4 ligne par ligne ; renvoie les lignes d'octets bruts."""
    pas = largeur * bpp
    if len(brut) < hauteur * (pas + 1):
        raise ErreurPNG("données d'image trop courtes")
    lignes, prec = [], bytearray(pas)
    for y in range(hauteur):
        o = y * (pas + 1)
        f, ligne = brut[o], bytearray(brut[o + 1:o + 1 + pas])
        if f == 1:
            for x in range(bpp, pas):
                ligne[x] = (ligne[x] + ligne[x - bpp]) & 0xFF
        elif f == 2:
            for x in range(pas):
                ligne[x] = (ligne[x] + prec[x]) & 0xFF
        elif f == 3:
            for x in range(pas):
                g = ligne[x - bpp] if x >= bpp else 0
                ligne[x] = (ligne[x] + ((g + prec[x]) >> 1)) & 0xFF
        elif f == 4:
            for x in range(pas):
                g = ligne[x - bpp] if x >= bpp else 0
                hg = prec[x - bpp] if x >= bpp else 0
                ligne[x] = (ligne[x] + _paeth(g, prec[x], hg)) & 0xFF
        elif f != 0:
            raise ErreurPNG(f"filtre inconnu {f} (ligne {y})")
        lignes.append(ligne)
        prec = ligne
    return lignes


def decoder(data):
    """Octets d'un fichier PNG → (largeur, hauteur, [(r, g, b, a), …])."""
    ihdr, plte, trns, idat = None, None, None, []
    for typ, contenu in _morceaux(data):
        if typ == b"IHDR":
            ihdr = struct.unpack(">IIBBBBB", contenu[:13])
        elif typ == b"PLTE":
            plte = contenu
        elif typ == b"tRNS":
            trns = contenu
        elif typ == b"IDAT":
            idat.append(contenu)
    if ihdr is None:
        raise ErreurPNG("IHDR absent")
    largeur, hauteur, prof, typ, _, _, entrelace = ihdr
    if typ not in CANAUX:
        raise ErreurPNG(f"type de couleur {typ} inconnu")
    if prof != 8:
        raise ErreurPNG(f"profondeur {prof} bits non gérée (8 bits seulement)")
    if entrelace:
        raise ErreurPNG("PNG entrelacé (Adam7) non géré")
    if typ == 3 and plte is None:
        raise ErreurPNG("PNG indexé sans palette PLTE")
    try:
        brut = zlib.decompress(b"".join(idat))
    except zlib.error as e:
        raise ErreurPNG(f"IDAT illisible : {e}") from None
    lignes = _defiltrer(brut, largeur, hauteur, CANAUX[typ])

    pixels = []
    if typ == 3:
        alpha = list(trns or b"") + [255] * 256
        coul = [(plte[3 * i], plte[3 * i + 1], plte[3 * i + 2], alpha[i]) for i in range(len(plte) // 3)]
        for ligne in lignes:
            try:
                pixels += [coul[i] for i in ligne]
            except IndexError:
                raise ErreurPNG("index hors de la palette PLTE") from None
    elif typ == 2:
        cle = struct.unpack(">HHH", trns[:6]) if trns and len(trns) >= 6 else None
        for ligne in lignes:
            for x in range(0, len(ligne), 3):
                r, g, b = ligne[x], ligne[x + 1], ligne[x + 2]
                pixels.append((r, g, b, 0 if (r, g, b) == cle else 255))
    elif typ == 6:
        for ligne in lignes:
            pixels += [tuple(ligne[x:x + 4]) for x in range(0, len(ligne), 4)]
    elif typ == 0:
        cle = struct.unpack(">H", trns[:2])[0] if trns and len(trns) >= 2 else None
        for ligne in lignes:
            pixels += [(v, v, v, 0 if v == cle else 255) for v in ligne]
    else:  # 4 : gris + alpha
        for ligne in lignes:
            pixels += [(ligne[x], ligne[x], ligne[x], ligne[x + 1]) for x in range(0, len(ligne), 2)]
    return largeur, hauteur, pixels


def lire(chemin):
    with open(chemin, "rb") as f:
        return decoder(f.read())


if __name__ == "__main__":
    for c in sys.argv[1:]:
        w, h, px = lire(c)
        print(f"{c} : {w}×{h}, {len(set(px))} couleur(s) RGBA")
