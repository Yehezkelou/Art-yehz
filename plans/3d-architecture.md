# 3D ico-vid : analyse des références et architecture (22/10/2026)

Demande de @yehz (22/10) : « passons à un niveau supérieur… avec le skill 3D on va créer le nôtre, même
texture, animation et mouvement : architecture modèle personnage, modèle paysage, modèles objet et autre ».
Références téléchargées dans `references/3d/` (ignoré par git, n'entrent jamais dans une vidéo ; idées
reprises, formes redessinées).

## Ce que montrent les références

| # | Référence | Ce qu'on en retient (idée, pas la forme) |
|---|---|---|
| 1, 4 | Valkyrie voxel, « 3D pixel series » de Bitgem (Sketchfab) et son test d'animation (Matthias Andre) | Perso **chibi voxel** : tête ≈ la moitié du corps, membres de 2–3 voxels, silhouette lisible de loin ; accessoires qui dépassent (ailes du casque, bouclier) ; quelques voxels **émissifs** (or) ; ombre de contact au sol ; animation par **parties rigides** (tête, corps, bras, jambes) : rebond, balancement, pas de déformation. |
| 2 | « Potion 3D », Diogo Ferreira (ArtStation) | **Objet voxel iconique** vu de trois quarts : verre = cadre de voxels creux, liquide = bloc plein, reflet en voxels blancs, bouchon, **particules cubes** qui flottent ; fond nuit uni, 3 teintes par matière. |
| 3 | Café voxel en diorama (Behance) | **Diorama** sur un socle (trottoir, route, voiture, panneau) : bâtiment en étages, fenêtres éclairées de l'intérieur, enseigne lumineuse, nuit bleue + lumières chaudes. Un décor = une maquette posée sur sa dalle, qu'on filme en orbite. |
| 5 | Ciel de coucher de soleil pixel (Pinterest, style bloc) | **Paysage de ciel** en bandes de couleur (orange → violet), nuages en marches d'escalier, soleil carré ; à faire en **cartes 2D superposées** (parallaxe) derrière la 3D. |
| 6 | Livre enchanté pixel (Pinterest, style Minecraft) | **Boîte texturée en pixels** : géométrie simple (pavé biseauté, coins renforcés), texture 16×16 à texels nets (NearestFilter) ; second style à côté du voxel pur. On ne reprend ni le dessin ni l'objet (marque Minecraft). |

Ce qu'on adapte à la bible : leurs rendus ont flou lumineux (bloom), occlusion douce et dégradés ; chez
nous tout est ramené à la palette ico-pixel-32 sans semi-transparence. Équivalents pixel : **lueur = halo
en anneaux de couleurs de la palette**, **occlusion = un palier plus sombre de la rampe** sur les voxels
coincés, ombre de contact = taches pleines.

## Architecture

```
assets/3d/
  palette/ico-pixel-32-magicavoxel.png   palette 256×1 pour MagicaVoxel (index 1–32 = nos couleurs)
  persos/<nom>/  <nom>.py → parties .vox (tete, corps, bras_g, bras_d, jambe_g, jambe_d, accessoires)
                 <nom>.rig.toml (pivot de chaque partie, parent, échelle), apercu.png
  objets/<nom>/  <nom>.py → <nom>.vox (+ parties si animé), apercu.png
  decors/<nom>/  <nom>.py → dalles .vox du diorama (sol, bâtiment, mobilier), <nom>.scene.toml (placement)
  ciels/<nom>/   cartes PNG en couches (parallaxe) + <nom>.toml (profondeur de chaque couche)
  textures/<nom>.png   textures pixel 16×16 / 32×32 pour les boîtes texturées (style n° 6)
outils/vox.py              écrire / lire des .vox MagicaVoxel (palette ico-pixel-32), voxeliser des
                           calques ASCII, aperçu PNG ; tests
outils/rendu3d/voxel.mjs   charger un .vox → maillage glouton, couleur de face par rampe (dessus / face /
                           côté / dessous), occlusion en paliers, contour optionnel ; rig (parties + pivots) ;
                           texture pixel (NearestFilter) ; halo pixel ; éclairages types (nuit, diorama, studio)
```

- **Source = script**, comme nos sprites Lua : chaque modèle est écrit par un script (calques ASCII, boîtes),
  qui produit le `.vox`. Le `.vox` s'ouvre dans MagicaVoxel (gratuit) si @yehz veut retoucher à la main.
- **Animation** : procédurale par parties rigides (idle, marche, saut, parle, coup), au rythme de la bible
  (persos à 12 i/s, caméra et effets à 24) ; clips nommés dans le `.rig.toml`.
- **Licences** : tout est dessin maison, au manifeste ; aucune forme, texture ou couleur relevée d'une référence.
- **Ordre** : 1) outils (vox.py + voxel.mjs + tests), 2) premiers modèles (Tim voxel avec rig, le marchand,
  potion, livre, boutique en diorama, ciel couchant), 3) vitrine en vidéo (orbite + animations) pour valider le
  style avec @yehz, 4) première vraie vidéo qui s'en sert.
