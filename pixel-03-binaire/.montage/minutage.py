"""pixel-03-binaire : instants de la voix (alignement ElevenLabs) et découpage des sous-titres.

`mot(i)` = début du i-ème mot (secondes, voix accélérée ×1,1) ; `fin_mot(i)` = sa fin. Les numéros de
mots sont ceux de la narration (voir `python3 -I minutage.py`). SOUS_TITRES : blocs de 12 caractères au
plus (une ligne Press Start 2P), calés sur les mots ; `chute` = mot-clé en or.
"""
import json, os, re

ICI = os.path.dirname(os.path.abspath(__file__))
EP = os.path.dirname(ICI)
TEMPO = 1.1                      # voix/narration-x1.1.wav = narration.mp3 accélérée (atempo)

with open(os.path.join(EP, "voix", "alignement.json"), encoding="utf-8") as f:
    _A = json.load(f)["alignement"]
_T = "".join(_A["characters"])
MOTS = [(m.group(), _A["character_start_times_seconds"][m.start()] / TEMPO,
         _A["character_end_times_seconds"][m.end() - 1] / TEMPO)
        for m in re.finditer(r"[\wÀ-ÿ'-]+", _T)]
FIN_VOIX = _A["character_end_times_seconds"][-1] / TEMPO


def mot(i):
    return MOTS[i][1]


def fin_mot(i):
    return MOTS[i][2]


# (texte, premier mot, dernier mot, chute)
_BLOCS = [
    ("0,1", 0, 2, False), ("+ 0,2", 3, 6, False), ("ÉGALE...", 7, 7, False), ("0,3 0 0 0...", 8, 13, False),
    ("QUATRE ?!", 14, 14, True), ("TIM VÉRIFIE", 15, 16, False), ("SUR SON ORDI", 17, 19, False),
    ("PAREIL.", 20, 20, True), ("LE MARCHAND", 21, 22, False), ("TRICHE ?", 23, 23, False), ("NON.", 24, 24, True),
    ("JE VAIS", 25, 26, False), ("TE DIRE", 27, 28, False), ("POURQUOI.", 29, 29, True),
    ("PRESQUE TOUS", 30, 31, False), ("LES LANGAGES", 32, 33, False), ("DONNENT CE", 34, 35, False),
    ("RÉSULTAT.", 36, 36, False), ("NOUS, ON", 37, 38, False), ("COMPTE EN", 39, 40, False),
    ("BASE 10.", 41, 42, True), ("ET CERTAINS", 43, 44, False), ("NOMBRES", 45, 45, False),
    ("NE TOMBENT", 46, 47, False), ("JAMAIS JUSTE", 48, 49, False), ("UN TIERS,", 50, 51, False),
    ("C'EST 0,3", 52, 55, False), ("3 3...", 56, 57, False), ("À L'INFINI.", 58, 59, True),
    ("L'ORDI, LUI,", 60, 61, False), ("COMPTE EN", 62, 63, False), ("BASE 2 :", 64, 65, True),
    ("QUE DES 0", 66, 68, False), ("ET DES 1.", 69, 71, False), ("ET EN BASE 2", 72, 75, False),
    ("C'EST 0,1", 76, 79, False), ("QUI NE TOMBE", 80, 82, False), ("JAMAIS JUSTE", 83, 84, False),
    ("0,00011", 85, 89, False), ("0011...", 90, 93, False), ("À L'INFINI.", 94, 95, True),
    ("ALORS L'ORDI", 96, 97, False), ("COUPE :", 98, 98, True), ("IL GARDE", 99, 100, False),
    ("53 CHIFFRES.", 101, 102, True), ("SON 0,1", 103, 106, False), ("VAUT DONC UN", 107, 109, False),
    ("TOUT PETIT", 110, 111, False), ("PEU PLUS.", 112, 113, True), ("ADDITIONNE", 114, 115, False),
    ("LES DEUX", 116, 117, False), ("PETITS", 118, 118, False), ("RESTES...", 119, 119, False),
    ("ET L'ERREUR", 120, 121, False), ("SE VOIT,", 122, 123, False), ("TOUT AU BOUT", 124, 126, False),
    ("LE FAMEUX", 127, 128, False), ("QUATRE.", 129, 129, True), ("ET TIM SAIT", 130, 132, False),
    ("COMMENT LE", 133, 134, False), ("PAYER.", 135, 135, True),
]


def _sous_titres():
    out = []
    for k, (texte, a, b, chute) in enumerate(_BLOCS):
        assert len(texte) <= 12, texte
        debut = mot(a)
        suivant = mot(_BLOCS[k + 1][1]) if k + 1 < len(_BLOCS) else None
        fin = fin_mot(b) + 0.3
        if suivant is not None and suivant - fin_mot(b) < 0.7:
            fin = suivant                         # enchaîné : pas de trou entre deux blocs
        out.append({"texte": texte, "debut": round(debut, 3), "fin": round(min(fin, suivant or fin), 3), "chute": chute})
    return out


SOUS_TITRES = _sous_titres()

if __name__ == "__main__":
    print(" ".join(f"{i}:{m}" for i, (m, _, _) in enumerate(MOTS)))
    print(f"fin de la voix : {FIN_VOIX:.2f} s ; {len(SOUS_TITRES)} sous-titres")
