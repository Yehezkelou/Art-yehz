"""pixel-04-binaire3d : instants du dialogue (voix/alignement.json, écrit par voix.py) et sous-titres.

`mot(i)` = début du i-ème mot (s), `fin_mot(i)` = sa fin, `voix(i)` = N, T ou M. Numéros : `python3 -I minutage.py`.
SOUS_TITRES : blocs ≤ 12 caractères (une ligne Press Start 2P) calés sur les mots ; `chute` = mot-clé en or.
"""
import json, os

ICI = os.path.dirname(os.path.abspath(__file__))
EP = os.path.dirname(ICI)
with open(os.path.join(EP, "voix", "alignement.json"), encoding="utf-8") as f:
    _D = json.load(f)
MOTS = _D["mots"]
FIN_VOIX = _D["duree"]


def mot(i):
    return MOTS[i]["debut"]


def fin_mot(i):
    return MOTS[i]["fin"]


def voix(i):
    return MOTS[i]["voix"]


# (texte, premier mot, dernier mot, chute)
_BLOCS = [
    ("0,1", 0, 2, False), ("+ 0,2...", 3, 6, False), ("FACILE !", 7, 7, True), ("0,3 !", 8, 10, False),
    ("0,3...", 11, 13, False), ("0 0 0 0...", 14, 17, False), ("QUATRE ?!", 18, 18, True), ("QUATRE ?!", 19, 19, True),
    ("TIM VÉRIFIE", 20, 21, False), ("SUR SON ORDI", 22, 24, False), ("PAREIL.", 25, 25, True),
    ("C'EST UN", 26, 27, False), ("TRICHEUR !", 28, 28, True), ("MOI ?", 29, 29, False), ("JAMAIS", 30, 30, False),
    ("DE LA VIE !", 31, 33, True), ("NON.", 34, 34, True), ("PERSONNE", 35, 35, False), ("NE TRICHE.", 36, 37, False),
    ("JE VAIS TE", 38, 40, False), ("DIRE", 41, 41, False), ("POURQUOI.", 42, 42, True),
    ("PRESQUE TOUS", 43, 44, False), ("LES LANGAGES", 45, 46, False), ("DONNENT ÇA.", 47, 49, False),
    ("NOUS, ON", 50, 51, False), ("COMPTE EN", 52, 53, False), ("BASE 10.", 54, 55, True),
    ("CERTAINS", 56, 56, False), ("NOMBRES NE", 57, 58, False), ("TOMBENT", 59, 59, False),
    ("JAMAIS JUSTE", 60, 61, False), ("UN TIERS,", 62, 63, False), ("C'EST 0,3", 64, 67, False),
    ("3, 3...", 68, 69, False), ("À L'INFINI.", 70, 71, True), ("L'ORDI, LUI,", 72, 73, False),
    ("COMPTE EN", 74, 75, False), ("BASE 2 :", 76, 77, True), ("QUE DES 0", 78, 80, False), ("ET DES 1.", 81, 83, False),
    ("EN BASE 2,", 84, 86, False), ("C'EST 0,1", 87, 90, False), ("QUI COINCE :", 91, 92, True),
    ("0 0 0", 93, 95, False), ("1 1", 96, 97, False), ("0 0", 98, 99, False), ("1 1...", 100, 101, False),
    ("À L'INFINI.", 102, 103, True), ("ALORS L'ORDI", 104, 105, False), ("COUPE :", 106, 106, True),
    ("IL GARDE", 107, 108, False), ("53 CHIFFRES.", 109, 110, True), ("PAS UN", 111, 112, False),
    ("DE PLUS.", 113, 114, False), ("SON 0,1", 115, 118, False), ("VAUT DONC UN", 119, 121, False),
    ("TOUT PETIT", 122, 123, False), ("PEU PLUS.", 124, 125, True), ("ADDITIONNE", 126, 127, False),
    ("LES DEUX", 128, 129, False), ("PETITS", 130, 130, False), ("RESTES...", 131, 131, False),
    ("ET L'ERREUR", 132, 133, False), ("SE VOIT,", 134, 135, False), ("TOUT AU BOUT", 136, 138, True),
    ("LE FAMEUX...", 139, 140, False), ("QUATRE.", 141, 141, True), ("PAS DE SOUCI", 142, 144, False),
    ("JE PAIE", 145, 146, False), ("LE QUATRE !", 147, 148, True), ("AVEC... UNE", 149, 150, False),
    ("MIETTE ?!", 151, 151, True),
]


def _sous_titres():
    out = []
    for k, (texte, a, b, chute) in enumerate(_BLOCS):
        assert len(texte) <= 12, texte
        suivant = mot(_BLOCS[k + 1][1]) if k + 1 < len(_BLOCS) else None
        fin = fin_mot(b) + 0.3
        if suivant is not None and suivant - fin_mot(b) < 0.7:
            fin = suivant
        if suivant is not None:
            fin = min(fin, suivant)
        out.append({"texte": texte, "debut": round(mot(a), 3), "fin": round(fin, 3), "chute": chute, "voix": voix(a)})
    return out


SOUS_TITRES = _sous_titres()

if __name__ == "__main__":
    print(" ".join(f"{i}:{m['mot']}" for i, m in enumerate(MOTS)))
    print(f"fin du dialogue : {FIN_VOIX:.2f} s ; {len(SOUS_TITRES)} sous-titres")
