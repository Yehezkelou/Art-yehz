# pixel-04-binaire3d : les 7 scènes 3D (fiche commune aux agents)

Rendu : `node outils/rendu3d/rendu3d.mjs --scene pixel-04-binaire3d/.montage/3d/<nom>.mjs --out
pixel-04-binaire3d/.montage/3d/<nom>/ --debut <début> --fin <fin> --ips 24 --fond <fond>` (contrat :
`agents/missions/2026-10-22-rendu3d.md`, rapport de l'outilleur : `agents/rapports/claude/2026-10-22-rendu3d.md`).
Le compositeur Python (`pixel-04-binaire3d/.montage/composer.py`, écrit par l'orchestrateur) superpose chaque séquence
à son instant : image n = temps `début + n/24`. Les instants ci-dessous sont **absolus** (secondes depuis le début de la
vidéo, mots du dialogue : `python3 -I pixel-04-binaire3d/.montage/minutage.py`) ; les passer en `params` plutôt que
de les recopier dans le code quand c'est commode.

Règles communes (bible) :
- Toile 270×480 (9:16), l'image finale est agrandie ×4 en pixels nets. Lisible à cette taille : un chiffre voxel
  (glyphe 5×7) doit faire au moins ~25 px de haut à l'écran quand il porte le sens.
- Palette ico-pixel-32 seulement (l'outil ramène chaque pixel à la couleur la plus proche) : choisir des couleurs
  et des lumières qui tombent **nettement** sur les rampes de la palette (index 1–32, `outils.palette`), éclairage
  simple (1 directionnelle + ambiante), faces bien distinctes ; pas de dégradé qui « bave » entre deux rampes.
- Transparence tout-ou-rien (fond `transparent` = la scène 2D du compositeur reste derrière).
- Ne rien mettre dans la bande des sous-titres : **y 312–352** (de la toile 270×480) reste vide pour les scènes
  transparentes, et calme (fond uni) pour les scènes opaques.
- Mouvement fluide à 24 i/s : courbes lisses (`outils.lisse`, `outils.ressort` pour les rebonds), aucune saccade,
  caméra qui bouge toujours un peu (dérive lente) ; déterministe (fonction de t seulement).
- Rapport visuel obligatoire : lire au moins 6 images de la séquence (début, chaque instant clé ±2 images, fin),
  corriger tant qu'un chiffre est illisible, qu'un objet sort du cadre sans le vouloir ou qu'une couleur bave.

| nom | début–fin (s) | fond | où à l'écran | ce qui se passe (instants absolus) |
|---|---|---|---|---|
| `equation` | 0,00–6,60 | transparent | haut, y 50–250 | « 0,1 » en voxels crème (8) tombe du ciel et rebondit à 0,02 ; « + » à 1,84 ; « 0,2 » à 2,10 ; la ligne tangue doucement (±10°), la caméra dérive. À 3,87 (« Facile ! ») la ligne remonte d'un cran ; « = » or (19) à 4,81 ; « 0,3 » or (19) jaillit avec un ressort à 5,77 et reste. |
| `quatre` | 12,60–15,30 | transparent | centre, y 60–300 | un « 4 » géant en voxels rouges (23, faces 22/21) tombe et s'écrase à 12,71 (écrasement puis rebond, < 0,2 s) ; à 13,47 (Tim : « Quatre ?! ») il saute et fait un tour complet sur lui-même ; puis il flotte en tournant lentement. |
| `fameux` | 68,60–70,85 | opaque (fond nuit 2 + rayons 3) | plein cadre | travelling avant lent et dramatique vers un « 4 » voxel or (19) éclairé par une poursuite ; rayons qui tournent derrière ; à 69,45 (« quatre ») le 4 passe au rouge (23), petit sursaut et demi-tour rapide. |
| `ecrans` | 26,90–29,40 | opaque (mur 4) | plein cadre | carrousel de 4 écrans (boîtiers 10, 22, 18, 30, écran noir 1) qui tourne ; sur chaque écran, en voxels plats crème : le nom (JAVASCRIPT, PYTHON, JAVA, RUBY) et en vert (15) « 0.30000000000000004 » (le 4 final rouge 23) ; caméra en orbite, un écran passe bien de face au milieu de la scène. |
| `tarte` | 31,40–40,30 | transparent | tableau, y 90–300 | une tarte (pâte 18/17, dessus 23/22 cerises ou 28/27) tourne lentement, vue de trois quarts ; à 33,89 (« un tiers ») elle s'ouvre en 3 parts qui s'écartent avec un ressort ; aux trois « trois » (36,47 / 37,28 / 37,88) chaque part fait un petit saut à tour de rôle ; à 39,05 (« à l'infini ») les parts tournent de plus en plus vite. |
| `circuit` | 40,30–44,60 | opaque | plein cadre | la caméra file en rase-mottes au-dessus d'une carte électronique (plan 13, pistes 14/15, puces 2/4) ; une rangée de 8 bits voxel (cubes qui montrent « 0 » ou « 1 ») se retournent en vague ; à 42,14 (« deux ») tous se retournent ensemble ; à 43,23 (« zéros ») tous montrent 0 (gris 5) ; à 44,12 (« uns ») tous montrent 1 (or 19). Laisser y 40–110 calme (titre « BASE 2 » en 2D par-dessus). |
| `ruban` | 44,60–54,90 | opaque (nuit 1/2) | plein cadre | un ruban plat qui s'enroule en spirale vers le lointain ; les chiffres voxel crème de « 0,0001100110011… » s'y posent un à un : « 0, » à 45,85 puis un chiffre à chacun de ces instants 47,88 · 48,26 · 48,77 · 49,45 · 50,00 · 50,74 · 51,57 · 52,28 · 52,95 (les mots « zéro zéro zéro un un zéro zéro un un »), puis à partir de 53,97 (« à l'infini ») 10 chiffres par seconde ; chaque groupe « 0011 » sur des tuiles rouges (22). La caméra suit le dernier chiffre posé, puis à 53,97 recule pour montrer la spirale qui file à l'infini. |
