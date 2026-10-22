# Rapport : scènes 3D « chiffres » de pixel-04-binaire3d (equation, quatre, fameux)

- **Date** : 2026-10-22
- **Agent** : artiste 3D (Claude)
- **Spécification** : `pixel-04-binaire3d/scenes3d.md`

## Résultat
Les 3 scènes sont écrites et rendues avec `outils/rendu3d` (RTX 3050, 24 i/s).

| scène | fenêtre (s) | fond | images | temps total |
|---|---|---|---|---|
| `equation` | 0,00–6,60 | transparent | 158 (f_0000–f_0157) | ~4,7 s |
| `quatre` | 12,60–15,30 | transparent | 65 (f_0000–f_0064) | ~1,8 s |
| `fameux` | 68,60–70,85 | opaque (`--fond 1D1B2E`, plus `scene.background` = 2) | 54 (f_0000–f_0053) | ~1,9 s |

`verifier_pixels.py --echelle 1` donne VERT sur les 277 images (2 images par scène vérifiées une par une, puis tout le
lot : « VERT — 277/277 image(s) conforme(s) »). Bande des sous-titres y 312–352 : aucun pixel opaque sur les 223 images
transparentes ; dans `fameux` la bande ne contient que la couleur 2 (`1d1b2e`). Pas de commit.

Commandes (depuis la racine) :
```
node outils/rendu3d/rendu3d.mjs --scene pixel-04-binaire3d/.montage/3d/equation.mjs --out pixel-04-binaire3d/.montage/3d/equation --debut 0 --fin 6.6 --ips 24 --fond transparent
node outils/rendu3d/rendu3d.mjs --scene pixel-04-binaire3d/.montage/3d/quatre.mjs --out pixel-04-binaire3d/.montage/3d/quatre --debut 12.6 --fin 15.3 --ips 24 --fond transparent
node outils/rendu3d/rendu3d.mjs --scene pixel-04-binaire3d/.montage/3d/fameux.mjs --out pixel-04-binaire3d/.montage/3d/fameux --debut 68.6 --fin 70.85 --ips 24 --fond 1D1B2E
```

## Choix techniques
- **Ombrage en couleurs exactes.** Le calcul toon avec deux lumières ne donnait que 2 paliers par rampe (calcul
  hors ligne sur les 32 couleurs) et faisait passer le crème au gris 7 dès que la ligne tournait un peu. Chaque
  lettre porte donc 6 `MeshBasicMaterial` (un par direction de face de cube). À chaque image, la couleur est choisie
  selon la normale vue depuis la caméra, sur une rampe [ombre, côté, face, dessus] : crème [5, 6, 8, 7], or
  [17, 18, 19, 20], rouge [21, 22, 23, 24]. On obtient des faces nettes, sans rien entre deux rampes.
- **Contour sombre (couleur 1)** sur les deux grands « 4 » : une coque en face arrière par cube, élargie seulement
  vers les cases vides, avec les faces intérieures masquées. Le premier essai avec des coques pleines laissait des
  joints sombres entre les cubes. Pas de contour sur `equation`, qui reste lisible sur le mur sombre.
- Les instants viennent de `voix/alignement.json` et sont surchargeables par `params.instants`. Rien d'aléatoire
  hors `outils.hasard(4)` (la poussière de `quatre`).

## Ce que j'ai vu sur les images (planches et zooms ×3, plus de 6 images par scène)
**equation** (images 0, 2–6, 44–54, 91–97, 105, 113–117, 136–140, 145, 150, 157)
- Image 0 : « 0,1 » entre par le haut, incliné. Il touche le sol à l'image 3 (0,14 s), s'écrase, rebondit et se pose
  vers l'image 6.
- Images 44 à 48 : le « + » tombe et s'écrase. Images 48 à 54 : « 0,2 » tombe, s'écrase (net à l'image 52) et se pose.
- Images 91 à 97 (« Facile ! », 3,87 s) : la ligne se tasse puis remonte d'environ 26 px avec un ressort. Le tangage
  ±10° et la rotation en profondeur font voir les côtés (gris 6 et 5) et le dessus (7) : la profondeur de 3 cubes se lit.
- Image 115 (4,81 s) : le « = » or glisse depuis la gauche et claque. Il touche le bord gauche pendant 1 à 2 images.
  Images 138 à 145 : « 0,3 » or (×1,25) jaillit d'en bas, bascule et dépasse, puis se stabilise et reste jusqu'à l'image 157.
- Chiffres : environ 38 px de haut pour la ligne 1 et 48 px pour « 0,3 ». Tout tient entre y 40 et 220.

**quatre** (images 0, 3–9, 17–38, 46–64)
- Image 0 : vide (le 4 est encore au-dessus du cadre). Il entre à l'image 2, étiré, et tombe.
- Impact à l'image 6 (12,83 s) : fort écrasement, poussière grise à ses pieds. Il s'étire puis revient au repos vers
  l'image 9, soit moins de 0,2 s.
- Images 19 à 21 : il se tasse avant le saut. Images 21 à 36 (13,47 s) : il saute (sommet vers y 50), fait un tour
  complet et retombe à sa hauteur de flottement. Vers l'image 27, on le voit de dos (miroir) pendant 2 à 3 images.
- Images 38 à 64 : il flotte (va-et-vient vertical doux) et tourne lentement (±24°). Il mesure environ 145 px de
  haut, entre y 100 et 270.

**fameux** (images 0, 5, 10, 19–23, 25, 27, 30, 35, 45, 53)
- Fond nuit 2, 9 rayons (3) qui tournent et accélèrent d'un coup au « quatre ». Faisceau de poursuite (4) et flaque
  au sol (4 et 5). Plancher 2 sous l'horizon. Le travelling avant fait passer le 4 d'environ 120 px de haut (image 0)
  à environ 200 px (image 53), avec une poussée sèche au « quatre ».
- Image 21 (69,454 s) : le 4 passe de l'or au rouge. Il se tasse (image 20), fait un sursaut et un tour rapide
  (images 22 à 30), puis se repose. La flaque pulse.
- Zoom sur l'image 53 : faces 23, dessus 24, contour 1 net. Le liseré pointillé de la flaque est corrigé (flaque
  agrandie, plan proche reculé).

## Écarts avec la fiche, à valider
1. **`quatre`, instant de l'écrasement : 12,83 s et non 12,71 s.** `composer.py` joue `sifflet_chute` à M(18) =
   12,71 s, puis `impact` et la secousse à M(18) + 0,12 s. J'ai calé l'écrasement sur l'impact et la secousse. Pour
   revenir à 12,71 s : `--params '{"instants":{"impact":12.712}}'`.
2. **`fameux`, « demi-tour rapide » remplacé par un tour complet (360° en 0,42 s).** Un demi-tour laisserait un 4 vu
   de dos, donc en miroir, pendant les 1,4 s restantes. Pour changer, il faut une ligne à modifier dans `update` :
   `2 * Math.PI * tour` → `Math.PI * tour`.
3. Le dessus des faces rouges est en 24 (reflet saumon de la rampe rouge), en plus de 23, 22 et 21. Pour s'en tenir
   à la fiche : `--params '{"rampe":[21,22,23,23]}'` (dans `quatre`) ; dans `fameux`, constante `ROUGE`.
4. Le crème a son dessus en 7 et ses côtés en 6 et 5 : sans cela, la profondeur ne se lisait pas.

## Ce qui reste à améliorer
- Je n'ai pas vu les scènes composées sur la 2D : je n'ai pas lancé `composer.py`, qui écrit dans `.montage/`.
  À vérifier : le « 4 » de `quatre` (x 85–185) et le « ?! » 2D en (205, 150), et le « 0,3 » or par rapport aux
  étiquettes de prix 2D.
- `equation` : le « = » touche le bord gauche pendant 1 à 2 images (glissade de 9 cubes) ; on peut réduire la glissade.
- Pendant les tours (quatre image ~27, fameux images 25 à 27), le 4 vu de profil ou de dos est confus pendant 2 à
  3 images. C'est normal en mouvement rapide, mais à juger en vidéo.
- `fameux` : la moitié basse de l'image est un plancher uni (2). C'est calme pour les sous-titres, mais un peu vide.
  On pourrait y mettre un reflet ou une rampe de scène.
- Les fonctions `voxel` et `ombreur` sont recopiées dans les 3 fichiers, car je ne devais écrire que ces fichiers.
  On pourrait les déplacer vers un module commun, par exemple `outils.voxelOmbre`.
