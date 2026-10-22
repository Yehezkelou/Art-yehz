#!/usr/bin/env python3
"""Contrôle « zéro pixel baveux » sur des PNG rendus (plan 2.3, § 6.6).

    python3 -I ~/videos/outils/verifier_pixels.py rendu.png [autres.png]          # ×4, palette ico-pixel-32
    python3 -I ~/videos/outils/verifier_pixels.py planche.png --echelle 1         # image à taille réelle
    python3 -I ~/videos/outils/verifier_pixels.py rendu.png --tolerees ff00ff,ffffff --max 20
    python3 -I ~/videos/outils/verifier_pixels.py rendu.png --palette autre.hex

Deux vérifications par image (pas le .mp4 : la compression mélange forcément les couleurs) :
- blocs entiers : à ×N, chaque carré N×N (aligné sur le coin haut-gauche) est d'une seule couleur,
  et la taille de l'image est un multiple de N ;
- palette : chaque couleur est dans le fichier .hex (une couleur par ligne) ou dans --tolerees
  (couleurs des polices). Un pixel semi-transparent est toujours hors palette.
Les pixels totalement transparents sont ignorés (un bloc transparent + une couleur reste fautif).
Sortie : VERT/ROUGE par image, blocs fautifs avec les --max premières zones (x, y en pixels de
scène = pixel ÷ N), couleurs hors palette avec leur nombre de pixels. Code 0 vert, 1 rouge.
"""
import argparse, os, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import png  # noqa: E402

HOME = os.path.expanduser("~")
PALETTE = os.path.join(HOME, "videos/bible/palette/ico-pixel-32.hex")
TRANSPARENT = (0, 0, 0, 0)


def lire_couleur(texte):
    """« #E5533D » ou « e5533d » → (229, 83, 61) ; ValueError sinon."""
    t = texte.strip().lstrip("#")
    if len(t) != 6:
        raise ValueError(f"couleur invalide « {texte.strip()} » (attendu rrggbb)")
    return tuple(int(t[i:i + 2], 16) for i in (0, 2, 4))


def lire_palette(chemin):
    coul = set()
    with open(chemin, encoding="utf-8") as f:
        for ligne in f:
            ligne = ligne.split(";")[0].strip()
            if ligne and not ligne.startswith("//"):
                coul.add(lire_couleur(ligne))
    if not coul:
        raise ValueError(f"palette vide : {chemin}")
    return coul


def nom_couleur(p):
    r, g, b, a = p
    return f"#{r:02x}{g:02x}{b:02x}" + ("" if a == 255 else f" alpha {a}")


def analyser(largeur, hauteur, pixels, echelle, palette):
    """→ dict(taille_ok, blocs (nb total), fautifs [(x, y) scène], hors {pixel: nb})."""
    px = [p if p[3] else TRANSPARENT for p in pixels]
    fautifs = []
    for by in range(0, hauteur, echelle):
        for bx in range(0, largeur, echelle):
            ref = px[by * largeur + bx]
            for y in range(by, min(by + echelle, hauteur)):
                o = y * largeur
                if any(px[o + x] != ref for x in range(bx, min(bx + echelle, largeur))):
                    fautifs.append((bx // echelle, by // echelle))
                    break
    hors = {}
    for p in px:
        if p[3] and (p[3] != 255 or p[:3] not in palette):
            hors[p] = hors.get(p, 0) + 1
    blocs = -(-largeur // echelle) * -(-hauteur // echelle)
    return dict(taille_ok=largeur % echelle == 0 and hauteur % echelle == 0,
                blocs=blocs, fautifs=fautifs, hors=hors)


def verifier_image(chemin, echelle, palette, nmax):
    """Renvoie (vert: bool, lignes de rapport)."""
    try:
        w, h, pixels = png.lire(chemin)
    except (OSError, png.ErreurPNG) as e:
        return False, [f"ROUGE — {chemin} : illisible ({e})"]
    r = analyser(w, h, pixels, echelle, palette)
    nf, nh = len(r["fautifs"]), len(r["hors"])
    vert = r["taille_ok"] and not nf and not nh
    tete = f"{'VERT' if vert else 'ROUGE'} — {chemin} ({w}×{h}, ×{echelle}) : " \
           f"{nf} bloc(s) fautif(s) sur {r['blocs']}, {nh} couleur(s) hors palette"
    lignes = [tete]
    if not r["taille_ok"]:
        lignes.append(f"  - taille non multiple de {echelle} : {w}×{h}")
    if nf:
        zones = " ".join(f"({x}, {y})" for x, y in r["fautifs"][:nmax])
        lignes.append(f"  - blocs fautifs, {min(nf, nmax)} premières zones (x, y en pixels de scène) : {zones}")
    if nh:
        tri = sorted(r["hors"].items(), key=lambda kv: (-kv[1], kv[0]))
        coul = ", ".join(f"{nom_couleur(p)} ({n} px)" for p, n in tri[:nmax])
        suite = f" … (+{nh - nmax} autres)" if nh > nmax else ""
        lignes.append(f"  - hors palette : {coul}{suite}")
    return vert, lignes


def main(argv=None):
    ap = argparse.ArgumentParser(description="Contrôle blocs entiers + palette sur des PNG rendus.")
    ap.add_argument("images", nargs="+")
    ap.add_argument("--echelle", type=int, default=4)
    ap.add_argument("--palette", default=PALETTE)
    ap.add_argument("--tolerees", default="", help="couleurs en plus de la palette : ff00ff,ffffff")
    ap.add_argument("--max", type=int, default=10, help="nombre de zones et de couleurs affichées")
    a = ap.parse_args(argv)
    if a.echelle < 1 or a.max < 1:
        ap.error("--echelle et --max doivent valoir au moins 1")
    try:
        palette = lire_palette(a.palette)
        palette |= {lire_couleur(c) for c in a.tolerees.split(",") if c.strip()}
    except (OSError, ValueError) as e:
        ap.error(str(e))
    rouges = 0
    for chemin in a.images:
        vert, lignes = verifier_image(chemin, a.echelle, palette, a.max)
        rouges += not vert
        print("\n".join(lignes))
    if len(a.images) > 1:
        print(f"{'ROUGE' if rouges else 'VERT'} — {len(a.images) - rouges}/{len(a.images)} image(s) conforme(s).")
    return 1 if rouges else 0


if __name__ == "__main__":
    sys.exit(main())
