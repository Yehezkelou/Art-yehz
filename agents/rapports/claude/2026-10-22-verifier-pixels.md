# Rapport : verifier_pixels.py (contrôle « zéro pixel baveux »)

- **Date** : 2026-10-22 · **Agent** : outilleur (Claude) · **Mission** : `agents/missions/2026-10-22-verifier-pixels.md`
- **Résultat** : critère de fin atteint (tests verts, Tim vert, aperçu vulga rouge). Pas de commit.

## Fait
- `outils/png.py` : lecteur PNG en Python standard (zlib + struct). 8 bits, types 2 (RGB, tRNS clé de couleur), 3 (indexé + tRNS), 6 (RGBA), plus 0 et 4 (gris) pour presque rien ; filtres 0–4 (Paeth compris) ; `lire(chemin)` / `decoder(octets)` → `(largeur, hauteur, [(r, g, b, a), …])` ; `ErreurPNG` si signature, IHDR, IEND, profondeur ≠ 8, entrelacement Adam7 ou index hors palette. Prêt pour decouper_planche.py.
- `outils/verifier_pixels.py` : `verifier_pixels.py image.png [autres.png] [--echelle 4] [--palette chemin.hex] [--tolerees ff00ff,…] [--max 10]`, style de sortie de `verifier_licences.py`.
  - Blocs : chaque carré N×N aligné sur (0, 0) doit être uniforme ; une taille non multiple de N est rouge aussi (les blocs partiels du bord sont contrôlés).
  - Palette : `.hex` (une couleur par ligne, `#` facultatif) + `--tolerees` ; un pixel semi-transparent est toujours hors palette (« #e5533d alpha 128 »), conformément à la règle « pas de semi-transparence ».
  - Pixels totalement transparents ignorés pour la palette ; pour les blocs ils comptent comme une seule « couleur vide » (un bloc moitié transparent, moitié couleur est fautif : c'est un décalage).
  - Sortie par image : VERT/ROUGE, nombre de blocs fautifs sur le total, `--max` premières zones (x, y en pixels de scène = pixel ÷ N, ordre lecture), couleurs hors palette triées par nombre de pixels ; ligne de bilan si plusieurs images ; code 0/1 ; fichier illisible = rouge.
- Tests (PNG fabriqués avec zlib dans les tests ; l'encodeur de `test_png.py` est réutilisé par `test_verifier_pixels.py`) :
  - `outils/tests/test_png.py` (7) : RGBA avec chacun des filtres 0–4 et filtres mélangés, RGB + tRNS, indexé + tRNS, gris, lecture de fichier, erreurs (non-PNG, tronqué, 16 bits).
  - `outils/tests/test_verifier_pixels.py` (6) : vert ×4, bloc baveux (dont transparent + couleur), `--max` et taille non multiple, hors palette + `--tolerees` + semi-transparent, PNG indexé vert puis rouge, plusieurs images + fichier illisible.

## Fichiers écrits
- `outils/png.py` (nouveau)
- `outils/verifier_pixels.py` (nouveau)
- `outils/tests/test_png.py` (nouveau)
- `outils/tests/test_verifier_pixels.py` (nouveau)
- `agents/rapports/claude/2026-10-22-verifier-pixels.md` (ce rapport)

## Commandes de fin et sorties exactes
```
$ python3 -I -m unittest discover -s outils/tests
....................
----------------------------------------------------------------------
Ran 20 tests in 0.056s

OK
```
```
$ python3 -I outils/verifier_pixels.py assets/persos/tim/tim-planche.png --echelle 1 ; echo code=$?
VERT — assets/persos/tim/tim-planche.png (128×64, ×1) : 0 bloc(s) fautif(s) sur 8192, 0 couleur(s) hors palette
code=0
```
```
$ python3 -I outils/verifier_pixels.py vulga-01-gps/apercu-1.png --echelle 4 ; echo code=$?
ROUGE — vulga-01-gps/apercu-1.png (405×720, ×4) : 7408 bloc(s) fautif(s) sur 18360, 2292 couleur(s) hors palette
  - taille non multiple de 4 : 405×720
  - blocs fautifs, 10 premières zones (x, y en pixels de scène) : (0, 2) (1, 2) (2, 2) (3, 2) (4, 2) (5, 2) (6, 2) (7, 2) (8, 2) (9, 2)
  - hors palette : #1c3152 (89335 px), #243b60 (5265 px), #101d30 (4949 px), #122035 (4937 px), #0f1c2e (4913 px), #16263e (4905 px), #213658 (4898 px), #253c62 (4860 px), #253d63 (4860 px), #0f1b2d (4532 px) … (+2282 autres)
code=1
```
(20 tests = 7 anciens de verifier_licences + 13 nouveaux. Temps sur l'aperçu 405×720 : 2,9 s réel avec la synthèse vocale en fond.)

## Limites restantes
- Pas de « calque probable » (§ 6.6) : le PNG seul ne le dit pas ; il faudra le croiser avec le projet (camera.py / monter.py).
- Blocs alignés sur le coin haut-gauche de l'image : si la comp de sortie décale toute la scène d'un nombre de pixels non multiple de N (secousse mal arrondie), tout sort rouge — c'est voulu, mais le message ne dit pas « décalage global ».
- Non gérés : profondeurs 1/2/4/16 bits, PNG entrelacé (erreur claire). Aseprite exporte en 8 bits indexé (planche de Tim) et EffectCraft en RGB 8 bits (aperçu vulga), donc suffisant aujourd'hui.
- Python pur : environ 1 s par million de pixels hors charge ; une image 1080×1920 prendra quelques secondes (OK pour « quelques images », lent pour toutes les images d'une vidéo).
- `monter.py --rendu` n'appelle pas encore l'outil (refus sauf `--forcer`, § 6.6) : hors périmètre de cette mission.
