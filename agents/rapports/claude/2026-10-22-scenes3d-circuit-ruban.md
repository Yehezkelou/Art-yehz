# Rapport : scènes 3D « circuit » et « ruban » (pixel-04-binaire3d)

- **Date** : 2026-10-22
- **Agent** : artiste 3D (Claude)
- **Spécification** : `pixel-04-binaire3d/scenes3d.md`

## Résultat
Les deux scènes sont écrites et rendues. `verifier_pixels.py --echelle 1` donne VERT sur toutes les images
(103/103 pour circuit, 247/247 pour ruban). Rien n'est commité.

| scène | fichier | rendu | commande |
|---|---|---|---|
| circuit | `pixel-04-binaire3d/.montage/3d/circuit.mjs` | `.montage/3d/circuit/f_0000–f_0102.png` (103 images, ~21 ms/image) | `--debut 40.3 --fin 44.6 --ips 24 --fond 1E4D3A` |
| ruban | `pixel-04-binaire3d/.montage/3d/ruban.mjs` | `.montage/3d/ruban/f_0000–f_0246.png` (247 images, ~19 ms/image) | `--debut 44.6 --fin 54.9 --ips 24 --fond 0E0D18` |

Les deux scènes posent leur propre `scene.background` (13 et 1), donc `--fond` ne change rien. Les instants viennent
de la fiche, avec des valeurs par défaut qu'on peut changer par `params` (noms en tête de chaque fichier). Toutes les
couleurs sont « cuites » par face avec `MeshBasicMaterial` et des couleurs d'instance exactes de la palette. Il n'y a
pas d'éclairage, donc aucun dégradé ne bave à la quantification. L'aléatoire vient seulement de `outils.hasard(2026)`
(implantation de la carte).

### circuit (40,30–44,60)
- **Caméra** : elle plonge à 40,27 (bruitage « plongée ») de y 95 à y 42, file latéralement en rase-mottes de x −105 à 0
  (départ rapide, freinage en douceur), puis se pose face à la rangée vers 41,95 et dérive lentement jusqu'à la fin.
- **Carte** : plan 13, environ 320 pistes en L (14, quelques-unes en 15) avec pastilles 15/16, environ 70 puces
  (dessus 2, côtés 3, pattes 6, repère 4). La brume et le ciel sont de la couleur 13, donc la carte se fond dans un
  fond uni au-dessus de y ≈ 160.
- **Les 8 bits** : 8 dalles (corps 3, dessus 4) posées sur des socles, chacune avec un chiffre voxel en relief sur la
  face avant et un autre, à l'envers, sur la face arrière. Un retournement dure 0,42 s : recul d'anticipation de 10 %,
  demi-tour avec `ressort` (dépassement amorti), petit saut, écrasement au départ. Une impulsion 16 remonte la piste
  d'alimentation et touche le socle à chaque retournement.
- **Déroulé** :
  - motif de départ 10110010 ;
  - vague 1 à 40,85 (+0,05 s par bit), vague 2 à 41,40 ;
  - à 41,835 (« allume »), les pistes d'alimentation passent de 14 à 15 en remontant vers les bits ;
  - à 42,14 (« deux »), les 8 bits se retournent ensemble ;
  - à 43,23 (« zéros »), tous montrent 0 en gris 5 (côtés 4) ;
  - à 44,12 (« uns »), tous montrent 1 en or 19 (côtés 18).
- **Zones** : la bande vue en y 312–352 correspond à une bande de carte (z calculé depuis la caméra posée) sans piste
  ni puce. Elle est **vide (100 % couleur 13) de l'image 15 à la fin**. La zone y 40–110 est au fond uni 13 sur
  **toutes** les images.
- **Taille des chiffres** : environ 30 px de haut, la rangée tient dans la largeur (environ 4 px de marge par côté).

### ruban (44,60–54,90)
- **Le ruban** : une spirale logarithmique dans le sens horaire, 0,6 fois plus petite à chaque tour et un peu plus
  profonde à chaque tour (cône), sur 9 tours. Bande 2 avec liserés 4.
- **Les cases** : une `InstancedMesh` de 1000 cases. Elles attendent en fantôme (3 pour « 0, » et le premier 0, 21
  pour les groupes « 0011 »). Quand le chiffre s'y pose, elles passent à 4 ou au rouge 22 avec un pop `ressort`.
  Un petit écart sépare chaque groupe « 0011 », et la case de la virgule est étroite.
- **Les chiffres** : voxels crème 8 (côtés 6/7/5). Chacun tombe vers le ruban depuis la caméra, touche sa case
  **à l'instant du mot**, puis fait un petit rebond écrasé.
- **Suite affichée** : « 0 » à 45,85, « , » à 46,01, puis d1…d9 = 0 0 0 1 1 0 0 1 1 aux 9 instants de la fiche, puis
  un chiffre par 0,1 s à partir de 53,97. À la fin, la suite affichée est
  « 0,0 0011 0011 0011 0011 0011 00 », soit 0,0001100110011… avec le motif « 0011 » répété.
- **Caméra** : elle glisse sur le ruban vide, suit le dernier chiffre posé (somme de pas lissés, fonction pure de t)
  et tourne avec la vraie tangente de la spirale pour garder le chiffre droit.
- **Recul final** : à 53,97, la caméra recule en 0,85 s en ouvrant le champ de 40° à 62° (effet vertigo) et vise le
  centre de la spirale. Image finale : la spirale entière en y ≈ 85–290, avec les chiffres posés sur le tour
  extérieur et les quartets rouges qui filent vers le centre.
- **Taille du chiffre suivi** : environ 35 px de haut.
- **Zones** :
  - y 20–60 est au fond uni 1 sur **toutes** les images ;
  - y 312–352 est vide sur toutes les images **sauf 227–241** (54,06–54,64), pendant le recul, quand le grand tour
    extérieur balaie l'écran ; elle est de nouveau vide aux images 242–246.

## Ce que j'ai vu sur les images (Read, planches à ×1 et ×2 avec repères des zones)
- **circuit**
  - **Première version** (images 0, 8, 14, 20, 28, 37, 44, 47, 50, 60, 70, 72, 76, 92, 96, 102) : la caméra était trop
    basse, la carte écrasée et vide. J'ai relevé la caméra (y 42) et doublé la densité des pistes et des puces.
  - **Deuxième version** : une puce et des pistes se trouvaient dans la bande y 312–352. Le comptage par rangée (79 à
    210 px non-fond par rangée sur l'image 100) a montré que les bornes en z de la bande étaient inversées. Après
    correction, la bande compte 0 px non-fond sur les images 30, 60 et 100.
  - **Version finale** :
    - images 0, 10, 20 : plongée de biais, les puces défilent au premier plan ;
    - image 30 : le bit 1 est en plein retournement, la rangée est coupée à gauche (la caméra arrive encore) ;
    - images 37 et 39 : les pistes d'alimentation s'allument (discret, derrière la rangée) ;
    - image 42 : rangée posée, motif 10110010 ;
    - images 44, 46, 48 : retournement d'ensemble, chiffres en biais au milieu du demi-tour puis 01001101 ;
    - images 68, 70, 72 : passage aux 0 gris ;
    - images 90, 92, 94 : passage aux 1 or, rebond visible ;
    - image 102 : 11111111 en or, net.
  - Les images 37, 71, 93 et 102 ont été relues agrandies ×2 : chiffres francs, côtés en relief d'un cran plus sombre.
- **ruban**
  - **Première version** : la spirale rentre, si bien que le ruban penchait d'environ 5° au chiffre suivi (images 30
    à 116). J'ai aligné le roulis, les chiffres et les cases sur la vraie tangente. On ne voyait aussi que 4 à 5
    chiffres : j'ai reculé la caméra (35 px par chiffre) et décalé le suivi d'une case vers l'arrière. Enfin, l'extrémité
    du ruban était visible au début (image 0) : j'ai raccourci la queue et le glissé d'entrée.
  - **Version finale** :
    - image 0 : ruban vide, cases fantômes ;
    - images 28, 30, 32 : « 0 » qui tombe puis « 0, » ;
    - images 77, 79, 81 : premier 0 posé, écrasement visible à l'image 79 ;
    - image 116 : « 0 001 », le 1 en chute ;
    - images 199, 201, 203 : « 0011 0011 » ;
    - images 223, 225, 227 : départ des 10 chiffres par seconde, le recul commence ;
    - images 236, 240, 246 : la spirale entière (relue ×2), centre vers y ≈ 205, plus de 6 tours visibles qui
      convergent.
- **verifier_pixels.py --echelle 1** : VERT sur circuit/f_0044 et f_0100, ruban/f_0116 et f_0246, puis sur toutes les
  images des deux dossiers.

## Ce qui reste à améliorer
- **circuit, images 0–14 (0,6 s de plongée)** : la bande y 312–352 n'est pas encore calme (puces et pistes qui
  passent, jusqu'à 1 700 px). Pour la vider aussi pendant la plongée, il faudrait une zone libre qui suive la caméra
  pendant la descente.
- **ruban, images 227–241** : pendant le recul, le tour extérieur traverse la bande des sous-titres. C'est
  inévitable avec un recul plein cadre, sauf à monter la spirale plus haut pendant la transition ou à couper.
- **circuit** : les 0 gris (5 sur un corps 3) sont lisibles mais peu contrastés ; c'est la couleur imposée par la
  fiche. L'allumage des pistes à 41,835 se voit peu, car il est comprimé derrière la rangée par la perspective. Les
  impulsions 16 sont petites.
- **ruban** : la queue du ruban (début de la spirale) s'arrête net, à gauche de l'image finale. Les chiffres du
  recul final font environ 6 px : c'est voulu (image d'ensemble), le sens est porté avant.
- Les planches contact et le comptage des zones ont été faits avec deux petits scripts Node du scratchpad
  (`planche.mjs`, `rangs.mjs`). Ils ne sont pas dans le dépôt ; un outil de planche contact pourrait servir aux
  autres scènes.
