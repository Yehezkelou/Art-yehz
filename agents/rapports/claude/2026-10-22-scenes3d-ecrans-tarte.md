# Rapport : scènes 3D `ecrans` et `tarte` (pixel-04-binaire3d)

- **Date** : 2026-10-22
- **Agent** : artiste 3D (Claude)
- **Spécification** : `pixel-04-binaire3d/scenes3d.md`

## Résultat
Les deux scènes sont écrites et rendues. `verifier_pixels.py --echelle 1` est VERT sur toutes les images :
60/60 pour `ecrans` et 214/214 pour `tarte`. Aucun commit.

| scène | fichier | images | commande |
|---|---|---|---|
| `ecrans` | `pixel-04-binaire3d/.montage/3d/ecrans.mjs` → `ecrans/f_0000…f_0059.png` | 60 (26,90–29,40) | `--debut 26.9 --fin 29.4 --ips 24 --fond 4A4663` |
| `tarte` | `pixel-04-binaire3d/.montage/3d/tarte.mjs` → `tarte/f_0000…f_0213.png` | 214 (31,40–40,30) | `--debut 31.4 --fin 40.3 --ips 24 --fond transparent` |

Le rendu prend environ 20 ms par image. Rien n'est aléatoire, sauf la place des cerises, tirée par `outils.hasard(31)`.

**Ombrage** : chaque scène a un petit matériau « rampe » (ShaderMaterial avec `colorspace_fragment`). Il choisit
l'une de 3 couleurs **exactes** de la palette selon l'angle entre la face et une lumière fixe. Il n'y a donc aucune
teinte intermédiaire et rien ne bave à la quantification. Le toon de `outils` n'est pas utilisé. Le matériau est
recopié dans les deux fichiers, parce qu'un import vers un dossier parent est interdit. Si d'autres scènes
l'adoptent, ce serait un candidat pour `outils`.

### `ecrans`
- **Carrousel** : 4 moniteurs sur un noyau gris (3/4/5) suspendu à un axe qui monte hors cadre. Boîtiers
  JAVASCRIPT 9/10/11, PYTHON 21/22/23, JAVA 17/18/19 et RUBY 29/30/31, selon l'ordre de la fiche (10, 22, 18, 30).
  Chaque boîtier a un liseré clair en haut, un cadre 2 et une vitre 1.
- **Textes** : voxels de 1 cube, en relief, alignés à gauche comme dans un terminal.
  - Le nom est en crème 8, avec les côtés en 7.
  - Le résultat est sur **2 lignes**, « 0.3000000 » puis « 0000000004 », en vert 15 avec les côtés en 14. Le 4 final
    est en rouge 23.
  - Sur une seule ligne, il aurait fallu 113 cubes de large, soit environ 2,3 px par cube et des glyphes de 16 px.
    Avec 2 lignes, on a environ 3,6 px par cube : le glyphe fait **25 px de haut** sur l'écran de face.
- **Mouvement** :
  - Départ lancé : JAVA est de face à 26,90, puis RUBY passe (images 3–5).
  - JAVASCRIPT se pose de face avec un dépassement amorti (easeOutBack, environ +12°). Il reste immobile, à une
    lente reptation près, de **28,0 à 28,75** (« langages donnent »).
  - Le carrousel repart ensuite en accélérant vers PYTHON, qui arrive de face sur la dernière image.
  - La caméra orbite de −9° à +9° : elle est de face au milieu (28,15), avec un léger travelling avant et une petite
    montée.
- **Décor** : mur 4 avec des lattes verticales 3 (comme `ecrans.png`) au-dessus d'une cimaise vers y ≈ 290. En
  dessous, le mur est uni jusqu'au parquet 26/25, qui commence vers y ≈ 355 : la bande 312–352 reste un aplat de 4.

### `tarte`
- **La tarte** : 3 parts extrudées et jointives (aucune fente visible quand la tarte est fermée). Chaque part a :
  - un fond et une paroi de pâte 18, avec les côtés en 17 et l'ombre en 25 ;
  - un bourrelet (tore) en 17/18 avec un reflet 19 ;
  - une garniture 23, dont la face de coupe est en 22/21 ;
  - 3 cerises en icosaèdres 22, avec un reflet 24 et l'ombre en 21.
- **Vue** : trois quarts, environ 36° au-dessus. Le cadre est décalé par `setViewOffset` pour que la tarte soit
  centrée sur le tableau.
- **Mouvement** :
  - La tarte apparaît d'un coup de ressort (0,45 s), puis tourne lentement (0,11 tour/s), flotte un peu (±0,25), et la
    caméra dérive en hauteur et en azimut.
  - À 33,89, elle s'ouvre : `ressort` sur 0,75 s, plus un petit sursaut.
  - Aux trois « trois », chaque part à son tour se ramasse pour prendre son élan, saute en faisant une pirouette
    complète sur son propre centre avec une légère bascule, puis s'écrase à l'atterrissage.
  - À partir de 39,05, la rotation accélère en t³, jusqu'à environ 1,7 tour/s sur la dernière image, et les parts
    s'écartent un peu plus.
- **Zone** : mesurée sur les 214 images, l'opaque reste dans **x 19–246, y 93–260**. Le tableau va de x 18 à 251 et
  de y 88 à 282. La zone y 270–310 et la bande 312–352 sont donc entièrement transparentes. L'image 0 est vide, car
  la tarte y est à l'échelle 0.

## Ce que j'ai vu sur les images
Les images de `tarte` ont été contrôlées posées sur `classe.png`.

**`ecrans`**
- f_0000 : JAVA de face, un peu de biais. Le texte est lisible, le bord gauche de RUBY est visible.
- f_0001 à f_0005 : RUBY entre puis passe. Le défilement se lit bien, à environ 20° par image.
- f_0008, f_0010 et f_0012 : JAVASCRIPT arrive et dépasse sa place.
- f_0024, f_0028, f_0030 et f_0032 : JAVASCRIPT est de face et très net. « 0.3000000 / 0000000004 » se lit et le 4
  rouge saute aux yeux.
- f_0044 et f_0052 : le carrousel repart, et PYTHON apparaît de profil à droite.
- f_0059 : PYTHON est de face.
- Les lignes du parquet sont droites et inclinées par l'orbite, ce qui est normal. La bande 312–352 est un aplat de 4
  sur toutes les images contrôlées.

**`tarte`**
- f_0001 : petite tarte qui surgit. f_0003 : dépassement du ressort. f_0006 : taille normale.
- f_0040 et f_0058–f_0060 : la tarte est entière et sans fente. En f_0060, les traits de coupe apparaissent.
- f_0062, f_0064 et f_0068 : les 3 parts s'écartent ; on voit nettement la coupe, avec la garniture 22 sur la pâte.
- f_0122 à f_0136 : premier saut (la part de devant), avec la pirouette et l'atterrissage.
- f_0144 et f_0147 : deuxième saut (la part du fond), le plus haut, vers y 93.
- f_0156 et f_0159 : troisième saut (la part de gauche).
- f_0182 à f_0213 : la rotation accélère et les parts restent dans le tableau.

**Corrections faites en cours de route**
- J'ai remonté le carrousel (cible caméra −24) et descendu le sol (y −150) : au premier jet, le parquet tombait dans
  la bande des sous-titres.
- J'ai supprimé les fentes de 0,02 rad entre les parts : elles faisaient des pointillés quand la tarte était fermée.
- J'ai baissé le reflet 19 du bourrelet : il rendait la pâte trop jaune.
- Le saut de la part de devant se lisait mal en vue plongeante. Je l'ai remplacé par saut + pirouette autour du centre
  de la part.
- J'ai recentré la tarte (décalage x −9) et éloigné la caméra (117), et j'ai réduit l'écart pendant les sauts et
  l'écart centrifuge final. Avant ces réglages, le troisième saut sortait du tableau par la gauche (x 0) et le
  deuxième dépassait en haut (y 83).

## Ce qui reste à améliorer
- **`ecrans`** :
  - Le résultat est coupé sur 2 lignes. C'est un choix de lisibilité, que @yehz doit valider ; l'autre solution serait
    une ligne unique de 16 px.
  - Le bas du cadre (y 250–355) est un mur vide : c'est calme, mais un peu nu.
  - Le tout début tourne très vite (environ 29° par image sur les 2 premières images).
- **`tarte`** :
  - Quand la part de devant fait sa pirouette, elle passe devant ses voisines (images 124–129). C'est juste en 3D,
    mais un peu chargé.
  - Les cerises (icosaèdres) ressemblent un peu à des gemmes ; on pourrait ajouter une queue.
- Les instants sont dans `params`, avec la fiche pour valeurs par défaut. Si le minutage change, il faut relancer les
  deux commandes ci-dessus.
