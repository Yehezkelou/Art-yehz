# Rapport : Tim et le marchand en voxels (chibi articulés, animés)

- **Date** : 2026-10-22
- **Agent** : artiste 3D voxel (Claude)
- **Spécification** : `plans/3d-premiers-modeles.md` (lignes Tim et marchand)

## Résultat
C'est fait : les deux persos sont modélisés, rigés et animés. Leurs clips se jouent sans interpénétration visible.
- **Rendu** : `verifier_pixels --echelle 1` est VERT sur les images demandées, et aussi sur les 432 images des deux scènes de contrôle.
- **Commit** : aucun. **Manifeste** : non modifié, les fichiers à inscrire sont listés plus bas.

| | Tim | Le marchand |
|---|---|---|
| Voxels | 850 dans `tim.vox` (11 modèles) ; 838 dans le rig avec bâton | 1094 dans `marchand.vox` (12 modèles) |
| Taille | 16 de haut (jambes 4, corps 4, tête 8, + épi) ; bâton jusqu'à y = 18 | 16 de haut (babouches 1, robe en cloche 7, tête 8) ; 18 de large avec les oreilles |
| Parties | corps, tete, bras_d, bras_g, jambe_d, jambe_g, baton ; bouche, paupieres, sourcils | corps (robe, ceinture, bourse), tete, pointe (de la capuche), oreille_d, oreille_g, bras_d, bras_g, jambe_d, jambe_g (babouches) ; bouche, paupieres, mi_clos |
| Clips | idle, marche, saut, parle, coucou, **colere**, balade (marche lente, définie dans le rig) | idle, marche, saut, parle, coucou, **non_de_la_tete** |
| Rigs | `tim.rig.toml` (bâton dans la main gauche) et `tim-sans-baton.rig.toml` | `marchand.rig.toml` |

À 12 i/s, le rendu prend environ 16 ms par image (RTX 3050).

### Fichiers produits (à inscrire au manifeste)
Pour tous : dessin maison, auteur @yehz, licence propriétaire, commentaire « modélisé par Claude (script vox.py) ».
- `assets/3d/persos/tim/` :
  - `tim.py` (source) ;
  - `tim.vox`, `tim.rig.toml`, `tim-sans-baton.rig.toml` et `apercu.png` (générés) ;
  - `tim.clips.mjs` (clips) ;
  - `controle.mjs` (scène de contrôle).
- `assets/3d/persos/marchand/` :
  - `marchand.py` (source) ;
  - `marchand.vox`, `marchand.rig.toml` et `apercu.png` (générés) ;
  - `marchand.clips.mjs` (clips) ;
  - `controle.mjs` (scène de contrôle).

Commandes :
```
python3 -I assets/3d/persos/tim/tim.py           # → tim.vox, les 2 rigs, apercu.png
python3 -I assets/3d/persos/marchand/marchand.py
node outils/rendu3d/rendu3d.mjs --scene assets/3d/persos/tim/controle.mjs --out <dossier> --debut 0 --fin 18 --ips 12
#   params : {"angle": 0.4} caméra fixe ; {"clip": "colere"} un seul clip ; {"rig": "./tim-sans-baton.rig.toml"}
```
Dans la scène de contrôle, chaque clip dure 3 s, dans l'ordre :

| Intervalle | 0–3 s | 3–6 s | 6–9 s | 9–12 s | 12–15 s | 15–18 s |
|---|---|---|---|---|---|---|
| Images | 0–35 | 36–71 | 72–107 | 108–143 | 144–179 | 180–215 |
| Tim | idle | marche | saut | parle | coucou | colere |
| Marchand | idle | marche | saut | parle | coucou | non_de_la_tete |

La caméra fait un tour complet en 18 s.

## Point à trancher : où vivent les clips propres
Les clips propres à chaque perso sont dans `<nom>.clips.mjs` (`installer(perso)` après `chargerRig`). Ils remplacent les
5 clips de base, pour les raisons données dans la section « Choix ».

La route `/depot/` de `rendu3d.mjs` ne sert que les `.vox .toml .json .png`. Une scène placée ailleurs, comme la vitrine
`pixel-05-vitrine3d/`, ne peut donc pas importer `assets/3d/persos/tim/tim.clips.mjs`. La scène de contrôle, elle, y
arrive, parce qu'elle est dans le même dossier.

Deux solutions :
- ajouter `.mjs` aux extensions de `/depot/`, limité à `assets/3d/` (hors de ma mission) ;
- copier le module à côté de la vitrine.

**Sans `installer`, les rigs marchent quand même avec les clips de base, mais moins bien.**
- Sans le module, les pieds de Tim s'enfoncent de 0,7 voxel dans le sol pendant la marche.
- La tête descend de 0,5 voxel dans le corps (idle).
- Le roulis de la tête touche le bâton (parle, coucou).
- Il n'y a ni clin d'œil, ni colère, ni « non ».

## Choix
- **Épaules** : le pivot est sur l'arête haute *extérieure* du bras, et le bord extérieur du bras est aligné sur celui de
  la tête. Le bras qui se lève (coucou, saut) s'écarte donc de la tête au lieu d'y entrer. J'ai vérifié cette géométrie
  au calcul, puis au contrôle automatique.
- **Expressions par les yeux** : les paupières et sourcils sont des parties cachées *dans* la tête au repos, une couche
  derrière la face. Le clip les avance de 2 voxels pour les montrer : tant que rien ne les active, aucune couche
  coplanaire ni scintillement.
  - Tim : la paupière dépasse d'un voxel, sous sa frange qui dépasse aussi.
  - Le marchand : son visage est en retrait dans la capuche, si bien que les paupières arrivent au ras du bord.
  - La bouche s'ouvre quand on cache la partie `bouche` (la lèvre du bas) : on voit alors le creux rouge sombre 21.
    Le clip `parle` de base s'en sert déjà.
- **Bâton** : le bras qui le tient a le rôle `bras_baton`, que les clips de base n'animent pas. Ainsi `saut` ne fait pas
  passer le bâton à travers la tête. Le manche est à x = 11, un voxel à l'écart de la tête. Pour deux bras libres, il
  y a le rig `tim-sans-baton.rig.toml`.
- **Clips propres** (`tim.clips.mjs`, `marchand.clips.mjs`) :
  - **Tête** : elle tourne (y) et hoche vers l'avant ; elle ne roule pas, car sa largeur l'enfoncerait dans les bras.
  - **Bras** : ils ne s'écartent que vers l'extérieur.
  - **Marche de Tim** : elle garde les pieds posés (le point le plus bas des bottes est recalculé à chaque image).
  - **Marchand** : ses babouches glissent sous la robe en se dandinant.
  - **Mouvement secondaire** :
    - les oreilles du marchand frémissent (pivot en haut de leur base, pour qu'elles s'écartent de la capuche) ;
    - la pointe de sa capuche ne bascule que vers l'arrière.
  - **Clins d'œil** : 2 images toutes les 2,9 s (Tim) ou 3,3 s (marchand).
- **Couleurs** : celles de la spécification, plus quelques ajouts.
  - Tim :
    - pupilles vers l'intérieur ;
    - frange qui dépasse, avec reflets 18 ;
    - épi ;
    - mèches et pointes de nuque à l'arrière ;
    - pan du foulard dans le dos ;
    - boucle de ceinture 18 ;
    - sourcils de colère en 25, parce qu'en 17 ils se fondaient dans la frange.
  - Le marchand :
    - bord de capuche éclairé 31 ;
    - front dans l'ombre (14) ;
    - nez qui sort de 2 voxels ;
    - sourire en coin ;
    - au dos : ceinture 26, pièce cousue 27/25, bourse avec une pièce d'or 19, pompon doré au bout de la capuche.

## Ce que j'ai vu sur les images
Les images ont été rendues dans le dossier temporaire, puis regardées en planches. Les numéros renvoient à la scène de
contrôle.

**Tim**
- **Premier rendu** (caméra en orbite, images 0, 40, 80, 110, 150 et 190) :
  - Le perso est lisible à environ 200 px de haut : gros yeux, joues 24, foulard rouge, tunique, ceinture, bâton à gemme.
  - Le dos de la tête était un bloc brun plat. J'ai ajouté des mèches 18, des pointes de nuque et un épi.
- **Caméra fixe** (angle 0,4) :

  | Images | Clip | Ce que j'ai vu |
  |---|---|---|
  | 20 | idle | le clin d'œil se lit en deux traits sombres |
  | 45 | marche | les pieds restent sur la dalle |
  | 76, 82 et 90 | saut | les bras levés passent à côté de la tête |
  | 110 et 115 | parle | la bouche s'ouvre en rouge |
  | 146 et 152 | coucou | la main salue au-dessus de l'épaule, sans toucher la tête |
  | 182 et 186 | colere | les sourcils en 17 ne se voyaient pas, d'où le passage en 25 |

- **Colère, après correction** (images 182, 186 et 190, agrandies ×2) : le « \ / » des sourcils est sombre et lisible, la
  bouche est ouverte et le poing écarté.
- **Petite taille**, à environ 110 px de haut (images 30, 50, 80, 115, 150 et 195) : yeux, bouche ouverte, sourcils de
  colère et bâton restent lisibles.
- **Orbite** : à certains angles (image 20 en orbite), la face entière prend sa couleur « côté » (26). C'est l'éclairage
  `camera` d'`outils.voxel`, qui est voulu, pas un défaut du modèle.

**Le marchand**
- **Premier jet** (images 0, 45, 80, 112, 150 et 190) :
  - Le visage marchait déjà : gros yeux, nez, sourire, paupières mi-closes sur « non » (image 190).
  - Trois défauts :
    - la robe était étroite au-dessus d'une « jupe » ;
    - les pieds faisaient de gros blocs bruns ;
    - les oreilles ressemblaient à des moufles.
  - Corrections :
    - robe en cloche de 10 de large, comme la robe large du sprite ;
    - babouches d'un voxel à bout relevé ;
    - oreilles en triangle pointu.
- **Orbite** (images 10, 45, 70, 100, 140 et 200) : le dos était une boîte violette sans rien. J'ai ajouté la pointe de
  capuche à pompon, la ceinture, la pièce cousue et la bourse ; j'ai revu le résultat aux mêmes images.
- **Caméra fixe** (angle 0,3) :

  | Images | Clip | Ce que j'ai vu |
  |---|---|---|
  | 21 | idle | rien à signaler |
  | 46 | marche | rien à signaler |
  | 82 | saut | les oreilles et le pompon se lèvent pendant le vol |
  | 112 | parle | la bouche est ouverte |
  | 150 | coucou | le bras levé passe sous l'oreille |
  | 190 | non_de_la_tete | la tête est tournée, les paupières mi-closes |

- **Petite taille**, à environ 110 px de haut (mêmes numéros que Tim) : la silhouette tient grâce aux oreilles, au
  violet, aux yeux crème et aux boutons dorés.

## Contrôles
**Interpénétration** : j'ai écrit un script Node, hors dépôt, dans le scratchpad. Il pose le vrai rig avec `outils.voxel`
et les clips, à 12 i/s sur 3 s par clip. Il place 8 points dans chaque voxel, à 0,25 voxel des faces, et compte ceux qui
tombent dans un voxel plein d'une autre partie, ainsi que ceux qui passent sous le sol.

Ce que le script trouve sur les clips finaux, pour les trois rigs :
- **Rien du tout** : idle, coucou, colere et non_de_la_tete.
- **Sous le sol** : 0 point partout.
- **Contacts restants** : tous cachés à l'intérieur d'un volume.
  - Le haut des jambes de Tim rentre dans le corps (marche, saut). Le corps est plus profond que les jambes, donc
    l'intérieur ne se voit pas.
  - Les babouches du marchand glissent sous la cloche de la robe (marche, saut).
  - Le haut des bras touche le dessous de la tête, sous le surplomb, sur 0,25 à 0,35 voxel, quand le bras balance en
    marchant :
    - Tim : 21 points sur 36 images ;
    - le marchand : 24 points sur 36 images.
  - Le marchand, clip parle : le bas de la manche frôle l'épaulement de la robe, sur 0,3 voxel au plus (38 points).

**Pixels** : `python3 -I outils/verifier_pixels.py <image> --echelle 1` est VERT, avec 0 bloc fautif et 0 couleur hors
palette, sur :
- Tim : images 20 et 186 ;
- le marchand : images 46 et 190.

Il est aussi VERT, par lots, sur les 216 images de chacune des deux scènes de contrôle.

## Ce qui reste à améliorer
- **Clips hors du dossier des persos** : voir le point à trancher plus haut.
- **Contacts restants** :
  - Les bras touchent un peu le dessous de la tête en marchant, de façon cachée. Pour les supprimer tout à fait, il
    faudrait un cou d'un voxel, au prix de la compacité chibi.
  - La marche « pieds posés » de Tim fait monter le corps de 0,3 voxel au milieu du pas. C'est l'inverse d'une marche
    réelle, mais avec des jambes rigides et des bottes longues, il n'y a pas d'autre moyen d'éviter le sol.
- **Colère de Tim** : elle se lit, mais elle est sage. On pourrait ajouter des joues rouges (23) ou une bouche en
  grimace (dents 8), si @yehz le veut.
- **Marchand derrière son comptoir** : pour pixel-02, il pourrait avoir un clip « caisse » (la main qui tape), et le clip
  `prend` du sprite (bras tendu en avant). Le bras tendu en avant passerait sous le surplomb de la capuche : à vérifier.
- **MagicaVoxel** : non testé ici. Les fichiers suivent la même chaîne que la démo.
- **Avis à demander** : Gemini n'a pas été consulté (mission en lecture seule). Un avis de direction artistique sur les
  apercus serait utile avant la vitrine.
