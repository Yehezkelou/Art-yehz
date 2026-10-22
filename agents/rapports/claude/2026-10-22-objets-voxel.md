# Rapport : objets voxel (potions bleue et rouge + particules, grimoire en boîte texturée)

- **Date** : 2026-10-22
- **Agent** : artiste 3D voxel (Claude)
- **Spécification** : `plans/3d-premiers-modeles.md` (lignes Potions et Grimoire)

## Résultat
C'est fait. Les deux objets sont modélisés par script, ils ont leur `.vox`, leur aperçu et une scène de contrôle en orbite.
- **Potion** : fiole à panse octogonale, verre en cadre creux (12/11), liquide franc (bleu 10/11/9, rouge 23/24/22),
  reflet crème 8 en marches et bouchon 27/26. 12 voxels de haut. Les 6 particules d'un voxel sont dans un fichier à part.
- **Grimoire** : pavé biseauté (couverture 30/29, coins 31, pages 8/7, signet 23/22, titre doré 19 sur le dos).
  Le plat porte une texture maison de 16 × 16, posée avec un texel par voxel : c'est la rune « 1 dans 0 » en or.
- **Contrôle** : `verifier_pixels --echelle 1` VERT sur les 144 images rendues (48 par scène : potion bleue, potion
  rouge, grimoire), ainsi que sur les 2 aperçus et sur la texture. Rendu en ~16 ms par image.
- Pas de commit. Je n'ai pas touché au manifeste.

## Fichiers produits (à inscrire au manifeste)
Pour tous : dessin maison, auteur @yehz, licence propriétaire, commentaire « modélisé par Claude (script vox.py) ».
- `assets/3d/objets/potion/potion.py` : script source. Il écrit les deux fichiers suivants et l'aperçu.
- `assets/3d/objets/potion/potion.vox` : modèles `bleue` et `rouge`, 9 × 12 × 9, 306 voxels chacun.
- `assets/3d/objets/potion/potion-particules.vox` : 12 modèles d'un voxel (`bleue_1`…`bleue_6`, `rouge_1`…`rouge_6`).
- `assets/3d/objets/potion/apercu.png` : les deux fioles côte à côte en vue iso, avec quelques particules.
- `assets/3d/objets/potion/controle.mjs` : scène de contrôle. Paramètre `{"couleur": "rouge"}` ; `bleue` par défaut.
- `assets/3d/objets/grimoire/grimoire.py` : script source. Il écrit le `.vox` et l'aperçu.
- `assets/3d/objets/grimoire/grimoire.vox` : modèles `corps`, `couvercle` et `signet`, tous dans la grille commune
  19 × 8 × 19. Le couvercle est posé en (0, 5, 0) et sa charnière est sur l'arête x = 0, y = 5.
- `assets/3d/objets/grimoire/apercu.png` : livre fermé. La texture du plat y est recopiée en un calque de voxels, pour
  l'aperçu seulement.
- `assets/3d/objets/grimoire/controle.mjs` : scène de contrôle.
- `assets/3d/textures/grimoire-plat.png` (16 × 16) et son script de dessin `assets/3d/textures/grimoire-plat.py`.

Commandes :
```
python3 -I assets/3d/objets/potion/potion.py
python3 -I assets/3d/textures/grimoire-plat.py && python3 -I assets/3d/objets/grimoire/grimoire.py
node outils/rendu3d/rendu3d.mjs --scene assets/3d/objets/potion/controle.mjs --out <dossier> --debut 0 --fin 4 --ips 12 [--params '{"couleur":"rouge"}']
node outils/rendu3d/rendu3d.mjs --scene assets/3d/objets/grimoire/controle.mjs --out <dossier> --debut 0 --fin 4 --ips 12
python3 -I outils/verifier_pixels.py <dossier>/*.png --echelle 1     → VERT — 144/144 (les trois rendus)
```

## Scènes de contrôle
- **Potion** :
  - **Flottement** : la fiole monte et descend de ±1 voxel (période 2,5 s) et penche très légèrement.
  - **Halo** : disque plein face à la caméra (9 pour la bleue, 21 pour la rouge). Il est dessiné en premier, sans test de
    profondeur, donc il reste toujours derrière la fiole et n'a aucune transparence.
  - **Particules** : elles montent de 8 voxels au-dessus du bouchon en se balançant. Chacune a sa période (2,4 à 3,2 s)
    et elle disparaît en haut.
  - **Cadence** : tout est cadencé à 12 i/s (`pas12`) et les positions sont arrondies au quart de voxel.
  - **Caméra** : un tour en 4 s. La potion fait environ 190 px de haut, bouchon compris.
- **Grimoire** :
  - **Caméra** : orbite d'un tour en 4 s.
  - **Couvercle** : il s'entrouvre de 18° autour de la charnière du dos, reste ouvert, puis se referme avec un petit rebond.
  - **Lueur** : pendant l'ouverture, les pages luisent (deux lames pleines 19 et 20 posées sur les pages) et 5 étincelles
    dorées en sortent.
  - **Taille** : le livre fait environ 230 px de large sur 140 de haut.
  - **Couleurs du cuir** : la rampe du 30 garde 30 sur le dessus, pour que le cuir en voxels et le fond de la texture
    soient de la même couleur. Occlusion : seuil 2.

## Ce que j'ai vu (images lues, rendues dans le scratchpad, dossier `objets/`)
- **Potion bleue** : images 0, 4, 6, 12, 16, 18, 24, 28, 30, 36, 40 et 42 (versions successives et version finale).
  - On lit le cadre de verre : nervures en diagonale, anneau bas et épaule en marches.
  - Le liquide affleure dans les fenêtres du bas. Sa surface est en retrait, et au-dessus les fenêtres restent vides,
    ce qui fait lire du verre et non un bloc.
  - Le reflet crème est vertical sur la nervure avant gauche (images 0, 6 et 42).
  - Les particules montent en douceur ; le halo est net.
- **Potion rouge** : images 3, 8, 9, 15, 20, 21, 27, 32, 33, 39, 44 et 45. C'est la plus lisible des deux : le rouge 23
  tranche franchement sur le verre 12. La surface 24 se voit par les fenêtres vides.
- **Grimoire** : images 0, 3, 6, 9, 14, 15, 20, 21, 26, 27, 32, 33, 38, 44 et 45.
  - Fermé (0, 3, 6) : la rune Φ dorée se lit, avec la couture pointillée et les coins 31 qui dépassent. La tranche
    crème avec sa ligne 7 se lit comme des pages, et le signet rouge pend à l'avant.
  - Ouvert (20, 26, 27, 32) : le couvercle se soulève d'un bloc à la charnière, on voit la lueur dorée et les étincelles.
  - Dos (38, 44) : nerfs 31 et titre doré.
- **Corrections faites en route** :
  - Occlusion au seuil 1 : elle rendait tout le verre en 11, donc j'ai passé l'occlusion à 2.
  - Le halo 10 se confondait avec le liquide bleu : il est maintenant en 9.
  - Le halo en anneau donnait un « donut » gris : il est maintenant plein.
  - Quand le liquide affleurait jusqu'en haut, sa surface débordait comme une jupe : elle est maintenant en retrait.
  - J'ai essayé une panse ronde : c'était trop fouillis et j'en suis revenu à la panse octogonale.
  - J'ai retiré le halo du grimoire, qui faisait un anneau brun terne, et j'ai réduit l'ouverture de 26° à 18°.

## Reprise de la potion bleue (demande de l'orchestrateur, potion rouge et grimoire validés)
- **Liquide** : il est maintenant en 9, avec un reflet 10 par fenêtre. Il affleure jusqu'à une surface pleine en 11.
  La rampe du 11 est surchargée pour la bleue seulement (dessus 11, côtés 10), pour que la surface ne prenne pas le 12
  du verre.
- **Verre** : il garde 12/11. J'ai ajouté des reflets crème 8 sur la nervure arrière droite, sur l'anneau bas, sur
  l'épaule et sur la lèvre (`REFLETS_BLEUE`).
- **« Yeux » vus de face** : les fenêtres vides du calque 5 sont vitrées, sauf la case du milieu de chaque face.
- **Halo** : il est en 3 au lieu de 9 et détache bien la fiole.
- **Rouge inchangée** : son modèle est identique octet pour octet dans le `.vox`, et ses 48 images sont identiques à
  celles d'avant la reprise.
- **Contrôle** : j'ai relu les images 0, 4, 8, 12, 16, 20, 24, 28, 36 et 40 de la bleue. Vues de face (16 et 28), il n'y
  a plus de trous sombres, le liquide sombre tranche sur le verre clair et les reflets crème se voient de plusieurs
  côtés. `verifier_pixels --echelle 1` est VERT sur 48/48 images et sur l'aperçu.
- **Limite** : le haut de la fiole est désormais presque tout en verre. Le liquide forme une bande sombre en bas, avec un
  liseré 11, et le côté « creux » du verre se lit moins que sur la rouge.

## Ce qui reste à améliorer
- **Potion bleue** (corrigée depuis, voir la reprise ci-dessus) : bleu sur bleu, elle restait moins franche que la rouge. Les faces latérales du verre (11) et les éclats
  du liquide (11) partagent la même couleur, puisque la fiche impose verre 12/11 et liquide 11/10.
  - Vue pile de face (images 16 et 28), les deux fenêtres vides du haut font deux « yeux » sombres.
  - Piste : un liquide bleu plus sombre (10 en éclat, 9 en face), ou une teinte de verre distincte, à valider avec @yehz.
- **Silhouette de la fiole** : elle est un peu « lanterne » ou « pion d'échecs » (épaule en deux marches). Une vraie fiole
  ronde demanderait une grille plus grande que 9 × 12 × 9.
- **Signet** : c'est un bloc de 3 × 4 au bout fendu, lisible mais trapu. Le livre est posé à plat, donc le ruban ne peut
  pas pendre plus bas.
- **Texture** : elle est vue en perspective et ses texels n'ont pas tous la même taille à l'écran, comme toute boîte
  texturée. Ses coins sont en partie cachés par les coins 31, ce qui est voulu (bord et couture seulement).
- **MagicaVoxel non vérifié** (pas installé) : les fichiers se relisent avec `vox.py info`.
- **Licences** : `verifier_licences` sera ROUGE tant que les fichiers ci-dessus ne sont pas au manifeste.
