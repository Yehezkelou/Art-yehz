# Mission : verifier_pixels.py (contrôle « zéro pixel baveux »)

- **Date** : 2026-10-22 · **Agent** : outilleur (Claude) · **Mode** : écriture · **Étape** : § 6.6, semaine 1 J5

## But
Un outil qui prend des PNG rendus et dit vert/rouge : blocs entiers (à ×N, chaque carré N×N d'une seule couleur) et palette (chaque couleur dans `bible/palette/ico-pixel-32.hex`, plus une liste blanche optionnelle pour les couleurs des polices).

## Contexte à lire
`plans/decisions.md`, `plans/plan-2.3.txt` § 4.1, 4.4, 6.4 et 6.6, `outils/monter.py` (style), `outils/verifier_licences.py` (style de sortie VERT/ROUGE).

## Fichiers autorisés en écriture
- `outils/png.py` (lecteur PNG en Python standard : zlib + struct ; types 2 RGB, 3 indexé avec tRNS, 6 RGBA, 8 bits ; filtres 0–4 ; renvoie largeur, hauteur, liste de pixels RGBA) — il resservira à decouper_planche.py
- `outils/verifier_pixels.py` : `verifier_pixels.py image.png [autres.png] [--echelle 4] [--palette chemin.hex] [--tolerees ff00ff,…] [--max 10]` ; sortie : par image, nombre de blocs fautifs + 10 premières zones (x, y en pixels de scène), couleurs hors palette avec leur nombre de pixels ; code 0 vert / 1 rouge. Les pixels totalement transparents sont ignorés.
- `outils/tests/test_png.py`, `outils/tests/test_verifier_pixels.py` (PNG de test fabriqués dans les tests avec zlib : cas vert ×4, bloc baveux, couleur hors palette, PNG indexé)

## Critère de fin
`python3 -I -m unittest discover -s outils/tests` vert ; l'outil lancé sur `assets/persos/tim/tim-planche.png --echelle 1` (attendu vert : 0 couleur hors palette) et sur `vulga-01-gps/apercu-1.png --echelle 4` (format non pixel : attendu rouge) avec leurs sorties exactes.

## Format du rapport
`agents/rapports/claude/2026-10-22-verifier-pixels.md`.
