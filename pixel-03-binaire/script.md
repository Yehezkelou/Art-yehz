# pixel-03-binaire : « 0,1 + 0,2 » (script v1, à valider)

Référence : Short YouTube « Pourquoi 0.1 + 0.2 = 0.30000000000000004 ? » (48 s), regardé en entier le
22/10/2026 (97 images à 2 i/s + sous-titres). Idée et ordre de l'explication repris ; forme réécrite :
rien de la vidéo (images, voix, mème, tableau, logos) n'entre dans la nôtre.

## Ce que fait la référence (4–5 lignes)
- Accroche en 2 s : un mème détourné (« je comprends pas les hommes » → « nous on comprend pas JavaScript »).
- Preuve tout de suite : la console tape 0.1, 0.2, puis 0.1+0.2 → 0.30000000000000004, une flèche dessus.
- Retournement : « ce n'est pas JavaScript » (logo barré), les autres langages donnent pareil.
- Explication par analogie : 1/3 = 0,333… en décimal ; 0,1 = 0,000110011… en binaire, motif en rouge.
- Fin : l'addition posée, les imprécisions s'accumulent, on voit l'approximation. Une image nouvelle
  toutes les 1–2 s (≈ 30 plans en 48 s), fond sombre texturé, sous-titres mot à mot, zooms et secousses.

## Ce qu'on change
- Notre monde pixel : Tim, le marchand, la boutique de « La potion » (l'épisode devient sa suite).
- Des décors dessinés à chaque scène et une caméra (pan au pixel, zooms par paliers ×1 → ×2 → ×3).
- Des valeurs justes : la référence montre des valeurs « float 32 bits » (0.100000001490…) alors que
  JavaScript calcule en 64 bits ; on montre les vraies (vérifiées avec Python) :
  0,1 → 0,1000000000000000055511… · 0,2 → 0,2000000000000000111022… · somme → 0,3000000000000000444…
- Source primaire citée à l'écran à la fin : documentation Python « Floating Point Arithmetic: Issues and
  Limitations » (docs.python.org/3/tutorial/floatingpoint.html) et norme IEEE 754.

## Fiche d'entrées
- Format : pixel 9:16, comp 270×480 ×4, persos 12 i/s ; durée ≈ 50 s.
- Idée : Tim découvre que le ticket de la boutique a raison, et le monde pixel explique pourquoi.
- Moments forts : 0 s ticket (accroche) · 9 s « NON. » · 29 s le motif 0011 qui défile · 46 s la miette = le 4.
- Fourni : rien. Voix : À DÉCIDER (voir la question en bas).

## Script

| # | Scène et décor | Texte (sous-titre) | Caméra / mouvement | Temps |
|---|---|---|---|---|
| 1 | Boutique (mur de briques, étagères de fioles, lanterne) | 0,1 + 0,2 = 0,30000000000000004 ?! | plan large → coupe zoom ×2 sur le ticket, secousse | 0–3 s |
| 2 | Atelier de Tim, vieil ordinateur pixel | TIM VÉRIFIE… | travelling vers l'écran ; la console s'écrit lettre par lettre : 0.1 + 0.2 → 0.30000000000000004 | 3–7 s |
| 3 | Boutique, le marchand qui sourit | LE MARCHAND TRICHE ? | zoom ×2 sur le marchand | 7–9 s |
| 4 | Plein écran rouge, tampon | NON. | « NON. » tombe ×3, secousse 2 px | 9–10,5 s |
| 5 | Rangée de 4 écrans de couleurs différentes (noms en texte, aucun logo) | TOUS LES LANGAGES DISENT PAREIL | travelling horizontal d'écran en écran | 10,5–14 s |
| 6 | Salle de classe, tableau noir | NOUS, ON COMPTE EN BASE 10 | Tim compte sur ses doigts, chiffres qui poppent | 14–18 s |
| 7 | Tableau, une tarte coupée en 3 | 1/3 = 0,3333… | les 3 sortent sur un ruban sans fin ; pan à droite qui le suit | 18–23 s |
| 8 | Intérieur de l'ordinateur : interrupteurs et lampes | L'ORDI COMPTE EN BASE 2 | plongée ×1 → ×2 dans l'écran (transition) ; lampes 0/1 qui clignotent | 23–28 s |
| 9 | Ruban binaire | 0,1 = 0,000110011001100… | le motif 0011 en rouge ; pan continu vers la droite | 28–33 s |
| 10 | Ciseaux géants | IL GARDE 53 CHIFFRES | les ciseaux coupent le ruban ; un bout tombe | 33–37 s |
| 11 | Ruban coupé, loupe | 0,1 VAUT EN VRAI 0,10000000000000000555 | zoom ×3 par paliers sur l'écart | 37–41 s |
| 12 | L'addition posée à la craie | 0,1000…0555 + 0,2000…1110 = 0,3000…0444 | chaque ligne glisse et se pose, le 4 surligné en rouge | 41–46 s |
| 13 | Retour boutique : Tim tend la miette | ET VOILÀ LE 4. | coupe sur la miette ×3, puis plan large (boucle avec la scène 1) | 46–50 s |
| — | Carton sources + signature | SOURCE : DOC PYTHON · IEEE 754 | — | 50–52 s |

Un plan nouveau toutes les 2,5–5 s, et du mouvement (caméra ou perso) dans chacun.

## Budget de fabrication
- Décors à dessiner (Lua Aseprite, palette ico-pixel-32) : boutique intérieure, atelier + ordinateur,
  salle de classe + tableau, intérieur d'ordinateur, 4 écrans, tampon NON, ciseaux, loupe, tarte.
- Repris : Tim (repos, marche, tend, regarde en haut), le marchand, le ticket, les chiffres 3×5, la miette.
- Outil : la caméra et les changements de scène se font dans composer.py (comme les 2 premières
  vidéos) ; la scène devient opaque et couvre le fond du modèle.
- Rendu : pas de preset lent, ≈ 40 s de rendu.

## Effets (ajoutés le 22/10 à la demande de @yehz : « le plus dynamique, rien ne manque, fluide »)

Tous dessinés et animés par Claude (composer.py), en pixels entiers, palette ico-pixel-32, sans flou ni
semi-transparence. Cadence : caméra, textes et effets à 24 i/s (fluides), persos à 12 i/s (bible § 1).

| Effet | Où | Repris de la référence ? |
|---|---|---|
| Pop des chiffres et mots-clés (×0 → ×3 → ×2 en 3 images, paliers entiers) | partout | oui (pop) |
| Secousse d'écran 2–4 px qui s'amortit | ticket, NON, ciseaux, le 4 | oui |
| Flash blanc d'1 image | impacts | oui |
| Transitions : poussée horizontale, volet en damier pixel, plongée dans l'écran par paliers | entre chaque scène | oui (glissements) |
| Machine à écrire + curseur qui clignote | console (2), addition (12) | oui |
| Flèche qui rebondit vers le résultat | 2, 12 | oui |
| Gros « ? » qui poppent autour de Tim | 2–3 | oui |
| Rayons de lumière qui tournent derrière Tim | « je vais te dire pourquoi » | oui (rayons) |
| Barré rouge en 3 images | « le marchand triche ? » | oui (logo barré) |
| Ruban de chiffres qui défile sans fin + lignes de vitesse | 7, 9 | oui |
| Motif 0011 surligné en rouge, entouré au feutre (cercle qui se dessine) | 9, 12 | oui |
| Tampon qui tombe + poussière | 4 | non (à nous) |
| Interrupteurs et lampes 0/1 qui clignotent | 8 | non |
| Étincelle sur la miette, zoom ×3 par paliers | 13 | non |

## Son
- Voix off ElevenLabs (voix à choisir parmi 3 essais), modèle multilingue, texte du script.
- Bruitages 8 bits synthétisés maison en Python (pop, whoosh, impact, clic de machine à écrire,
  tampon, bip) : aucun fichier d'autrui, un son = un marqueur = un effet.
- Petite boucle chiptune maison en fond, sous la voix.
