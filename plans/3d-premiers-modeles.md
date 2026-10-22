# 3D ico-vid : les premiers modèles (fiche des agents artistes)

API : `outils/vox.py` et `outils.voxel` de `outils/rendu3d` (rapport `agents/rapports/claude/2026-10-22-voxel.md`).
Arborescence et règles : `plans/3d-architecture.md`. Palette ico-pixel-32 seulement (index 1–32 :
`bible/palette/ico-pixel-32.hex`). Chaque modèle = un script source `<nom>.py` qui écrit ses `.vox` (et son
`.rig.toml` pour un perso), plus un `apercu.png` (outils/vox.py) ; chaque fichier produit va au manifeste
(dessin maison, auteur @yehz, licence propriétaire, commentaire « modélisé par Claude (script vox.py) »).
Aucune forme reprise d'une référence : on garde le style (chibi voxel, objet iconique, diorama, ciel en bandes,
boîte texturée), on dessine nos propres personnages et objets.

Index utiles : 1 nuit, 2 contour, 3–4 gris bleutés sombres, 5–7 gris, 8 crème ; 9–12 bleus ; 13–16 verts ;
17–20 ors ; 21–24 rouges ; 25–28 terres (bois, peau) ; 29–32 violets.

| Modèle | Dossier | Ce qu'il faut |
|---|---|---|
| **Tim** (héros) | `assets/3d/persos/tim/` | version voxel du Tim d'Aseprite (`assets/persos/tim/tim.lua` : cheveux 17/18, peau 28 et 27, joues 24, yeux crème 8 + pupille 2, foulard rouge 23, tunique verte 15/14, ceinture 26, pantalon bleu 10/9, bottes 25). Chibi : ~16 voxels de haut, tête ≈ 7–8 voxels de haut (la moitié), corps 4, jambes 3–4. Parties séparées : tete, corps, bras_g, bras_d, jambe_g, jambe_d (+ baton en accessoire, gemme bleue 10/11 en haut). Rig : pivots au cou, aux épaules, aux hanches ; clips idle, marche, saut, parle, coucou qui marchent sans que les parties se traversent. |
| **Le marchand** | `assets/3d/persos/marchand/` | gobelin du `assets/persos/marchand/marchand.lua` : capuche violette 30/29/31, peau verte 15/14, grandes oreilles pointues sur les côtés, gros yeux crème, nez vert foncé 14, boutons dorés 19 ; même chibi et mêmes parties que Tim (il peut garder la robe d'un seul bloc et n'avoir que des bras). |
| **Potions** | `assets/3d/objets/potion/` | fiole voxel iconique (variante bleue 11/10 et rouge 23/22) : verre = cadre creux bleu clair 12/11, liquide plein à l'intérieur, reflet crème 8, bouchon 27/26 ; + 6 « particules » d'1 voxel à faire flotter (fichier à part). ~12 voxels de haut. |
| **Grimoire** | `assets/3d/objets/grimoire/` | style boîte texturée : pavé biseauté (couverture 30/29, coins renforcés 31, tranche des pages 8/7, signet 23), une texture pixel 16×16 maison pour le plat (`assets/3d/textures/grimoire-plat.png` : motif « 0 1 » ou rune ico-vid, pas d'emprunt) ; modèle en .vox pour le volume + texture pour la couverture. |
| **Boutique en diorama** | `assets/3d/decors/boutique/` | la boutique du marchand en maquette sur dalle (≈ 48×48 voxels au sol) : façade en briques 3/4 avec joints 2, étage, enseigne à potion dorée 18/19, vitrine éclairée 20, comptoir et étagères de fioles en couleurs, lanterne 19/20, trottoir 6/5, rue 3 avec lignes 8, un lampadaire, un tonneau ; découpée en parties (sol, batiment, mobilier) + `boutique.scene.toml` (placement). Lisible en plan large 270×480 (9:16). |
| **Ciel couchant** | `assets/3d/ciels/couchant/` | 4–5 cartes PNG 270×480 (ou plus larges pour la parallaxe) : bandes orange → violet (20, 19, 18, 23, 22, 31, 30, 29, 1), nuages en marches d'escalier, soleil carré 20/8 ; transparence tout-ou-rien ; `couchant.toml` = profondeur de chaque couche. |

Puis une **vitrine** (`pixel-05-vitrine3d/`, faite par l'orchestrateur) : chaque modèle en orbite + Tim et le
marchand qui jouent leurs clips devant la boutique sous le ciel couchant, pour valider le style avec @yehz.
