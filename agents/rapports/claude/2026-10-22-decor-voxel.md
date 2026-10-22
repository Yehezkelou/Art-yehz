# Rapport : boutique du marchand en diorama voxel + ciel couchant en couches

- **Date** : 2026-10-22
- **Agent** : artiste 3D voxel (Claude)
- **Spécification** : `plans/3d-premiers-modeles.md` (lignes Boutique et Ciel)

## Résultat
C'est fait. Le diorama se lit en plan large 270×480 et en plan rapproché. La scène de contrôle compose le ciel et le
diorama : orbite lente de ±0,55 rad pendant 6 s, puis rapprochement en 1 s sur la vitrine, jusqu'à 10 s.
- **Pixels** : `verifier_pixels --echelle 1` VERT sur les 120/120 images de contrôle, sur les 5 cartes du ciel et sur
  `apercu.png`.
- **Reproductible** : deux rendus des images 0, 50 et 105 sont identiques octet pour octet.
- **Temps** : ~21 ms par image (RTX 3050).
- Pas de commit. Je n'ai pas touché au manifeste.

## Fichiers produits (à inscrire au manifeste : dessin maison, @yehz, propriétaire, « modélisé par Claude (script vox.py) »)
`assets/3d/decors/boutique/` :
- `boutique.py` : script source. Il écrit les 3 `.vox`, `boutique.scene.toml` et `apercu.png`.
- `sol.vox` : modèle « sol », 48×5×48. Il contient :
  - le socle 2/4 rainuré et le trottoir 6 avec ses joints 5 et sa bordure ;
  - la rue 3, ses pointillés 8 et son caniveau 2 ;
  - les flaques de lumière : 7/8 devant la vitrine, 28 sous la lanterne, 7/8 sous le lampadaire.
- `batiment.vox` : deux modèles.
  - « batiment » (40×36×24) :
    - façade en briques 3/4 avec joints 2 (motif 4×2 décalé qui tourne aux angles), chaînes d'angle 5/6, soubassement 4 ;
    - porte en retrait avec imposte éclairée 20 ;
    - vitrine creuse de 6 voxels de profondeur, fond lumineux 20/19, avec meneaux et appui en pierre ;
    - bandeau-enseigne 29 bordé d'or 18 et fiole dorée en relief 18/19/20 ;
    - étage à deux fenêtres, la gauche allumée avec rideaux 23, la droite éteinte 9 avec un reflet 10 ;
    - volets 26, jardinières fleuries, fenêtres latérales, descente d'eau ;
    - briques chaudes 25/26 autour de la lanterne.
  - « toit » (40×14×24) : deux pans en tuiles 30/29 avec faîtage 31. Il a une lucarne allumée, un œil-de-bœuf éclairé
    dans le pignon droit et une cheminée en briques.
- `mobilier.vox` : comptoir, étagères (planches 26 et 22 fioles en couleurs), lanterne (19/20 sur une potence 2),
  lampadaire (lampe 20), tonneau, caisses (avec une fiole) et plante.
- `boutique.scene.toml` (généré par le script) :
  - `centre` et `occlusion = 2` ;
  - 10 `[[partie]]` (fichier, modèle, origine en voxels) ;
  - 2 `[[lumiere]]` (position et halo : rayon, couleurs, intérieur) ;
  - `[cadrage.large]` et `[cadrage.rapproche]` (cible, distance, hauteur).
- `apercu.png` : vue iso du diorama assemblé.
- `controle.mjs` : la scène de contrôle.

`assets/3d/ciels/couchant/` :
- `couchant.py` : script de dessin. Il écrit les cartes, `couchant.toml` et `apercu.png`.
- Les 5 cartes, du fond vers l'avant :
  - `fond.png` (270×480, opaque) : bandes 1 → 29 → 30 → 31 → 22 → 23 → 18 → 19 → 20 en marches, avec des étoiles 8/32 ;
  - `soleil.png` (360) : soleil carré 19/20/8 aux coins en marches, avec des traits de lumière ;
  - `nuages-hauts.png` (360) : traînées 30, dessus 31, ventre 23 éclairé ;
  - `nuages-bas.png` (360) : nuages 22, dessus 24/23, dessous 21 ;
  - `mer.png` (360) : mer de nuages en 3 rangs de bosses en marches (31, 30, 29).
- `couchant.toml` : `glissement = 60` px par radian, et pour chaque couche, sa profondeur (0 ; 0,08 ; 0,22 ; 0,42 ;
  0,75). Décalage d'une couche = round(−glissement × profondeur × angle).
- `apercu.png` : composition des cartes ×2.
- Les cartes n'ont que de l'alpha 0 ou 255 et aucune couleur hors palette.

Rapport : `agents/rapports/claude/2026-10-22-decor-voxel.md`.

## Commandes
```
python3 -I assets/3d/decors/boutique/boutique.py      # → diorama 48×53×48, 43 855 voxels
python3 -I assets/3d/ciels/couchant/couchant.py
node outils/rendu3d/rendu3d.mjs --scene assets/3d/decors/boutique/controle.mjs --out <tmp> --debut 0 --fin 10 --ips 12
  → ok, 120 images, 20,7 ms/image
python3 -I outils/verifier_pixels.py <tmp>/*.png --echelle 1                     → VERT 120/120
python3 -I outils/verifier_pixels.py assets/3d/ciels/couchant/{fond,soleil,nuages-hauts,nuages-bas,mer}.png --echelle 1 → VERT 5/5
```
Params de la scène : `{ duree, orbite, bascule, plan: "les-deux" | "large" | "rapproche", ciel }`. Pour une seule
couche de ciel, prendre `ciel: false` (fond uni 1).

## Technique de la scène de contrôle
- **Ciel** : les cartes sont peintes à chaque image dans un canevas de 270×480 (`imageSmoothingEnabled = false`,
  décalages entiers), qui sert de `scene.background` (CanvasTexture, NearestFilter). Le ciel garde donc des pixels
  exacts et ne passe pas par la perspective.
- **Diorama** : `outils.voxel.maillage(…, { centre: "coin", occlusion: 2 })` sur chaque partie.
- **Lumières** : `outils.halo` face à la caméra, en anneaux pleins 19/18. Le halo est posé un peu derrière la lampe
  pour que les voxels passent devant. La lanterne vacille (rayon −0,5) une image sur cinq, à 6 i/s.

## Ce que j'ai vu (images lues)
- **Premiers essais** :
  - ctl1/0, 30, 100 : caméra trop proche, diorama coupé ; halos en gros disques pleins ; soleil caché derrière le
    bâtiment. J'ai corrigé la distance (250), les halos (anneaux fins, derrière la lampe) et le soleil (monté en haut à
    droite, au-dessus du toit).
  - ctl2/0, 30, 60, 100 : plan large juste, vitrine bien éclairée, étagères et fioles lisibles en rapproché.
  - ctl3/0 : soleil visible.
- **ctl4/20, 45, 75, 90, 110** :
  - j'ai ajouté la lucarne, sinon le toit faisait un grand aplat violet ;
  - la flaque du lampadaire en 26/27 ressemblait à de la terre, elle est passée en 7/8 sous la lampe ;
  - le pot de la plante, rouge, ressemblait à un petit personnage : il est passé en terre cuite 26/27.
- **ctl5/40, 78, 119 et ctl6/10, 105 (finales)** :
  - En plan large, le diorama entier est centré avec le ciel autour, le soleil à droite au-dessus du toit et la mer
    de nuages en bas.
  - La vitrine dorée, la lanterne et le lampadaire avec leurs halos, l'enseigne-fiole et la fenêtre allumée se lisent.
  - La parallaxe est visible : la mer glisse d'environ 30 px entre les images 20 et 45, le soleil de 3 px.
  - La 78 fait un très bon plan moyen.
  - 105 et 119 sont des plans rapprochés : façade du rez-de-chaussée et étage, avec les fioles du fond de vitrine.

## Ce qui reste à améliorer
- **Plan rapproché** : on n'y voit plus de ciel (seul le toit en haut). Si la vitrine en a besoin, viser plus bas ou
  remonter la caméra.
- **Lampadaire** : sous certains angles, son halo passe devant l'enseigne (image 10). On peut l'écarter d'un voxel vers
  la rue ou réduire le halo.
- **Mer de nuages** : les bosses du rang du fond font encore des « pics » un peu réguliers. On pourrait varier davantage
  la largeur des paliers et ajouter un contour sombre sur les côtés des bosses.
- **Ciel** : il ne glisse qu'en x. Le toml pourrait recevoir un décalage vertical si une caméra monte ou descend.
- **Arrière** du bâtiment et du toit : il est fait (briques, pan, cheminée) mais simple, car l'orbite ne montre que
  ±31°. Pour un tour complet, il faudrait une porte de service et une fenêtre arrière.
- **MagicaVoxel** : les `.vox` n'y ont pas été ouverts (logiciel non installé), comme pour la chaîne voxel.
- **Manifeste** : `verifier_licences` sera ROUGE tant que ces fichiers n'y sont pas inscrits (ils sont listés plus
  haut). Il signale aussi des fichiers 3D d'autres agents (tim, grimoire).
