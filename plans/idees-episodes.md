# Idées d'épisodes ico-vid tirées de « awesome-opus5-5-videos »

- Source : github.com/yihui-dev/awesome-opus5-5-videos, copie locale `a-trier/awesome-opus/` (hors git) (commit 92aee2f, compilation MIT de yihui-dev ; chaque prompt et chaque vidéo appartiennent à leur auteur, `README.md:111`).
- Tri du 22/10/2026 (mission `agents/missions/2026-10-22-awesome-opus-videos.md`), rapport : `agents/rapports/claude/2026-10-22-awesome-opus-videos.md`.
- Règle : on reprend une **idée**, on réécrit toute la **forme** (histoire, décor, chute, titre). Aucun prompt n'est recopié ici ; l'auteur est cité par son slug et son compte.
- Rien de ceci n'est validé : chaque idée passe par l'étape 2 de sa recette (script présenté à @yehz).

## Les 3 à faire en premier

1. **V4 · « Ton QR code se répare tout seul »** : le QR code est déjà du pixel art ; les rapides existants suffisent.
2. **P1 · « LE SORT RATÉ »** : gag pixel pur, sans voix, avec le héros d'Aseprite, `pixel-saut`, `pixel-degats` et `secousse`.
3. **V3 · « Point Nemo »** : l'accroche contre-intuitive tient en une phrase, et il ne faut que deux jauges à l'écran.

---

## Pixel art (9:16, comp 270×480 ×4, 12 i/s, sans voix)

### P1 · LE SORT RATÉ
- **Source** : `zacxbt-944604` (@zacxbt ; le même prompt figure aussi sous `majidmanzarpour-927543`, @majidmanzarpour). Il décrit un mage pixel en boucle repos, charge, lancer, retour.
- **Accroche (0–1 s)** : le mage lève son bâton, des étincelles tournent autour de la gemme.
- **Déroulé** : repos (2 images de balancement) → charge (étincelles, gemme qui clignote) → silence 0,5 s → le sort part… et retombe en une poule pixel sur sa tête (secousse de 1 px, `pixel-degats`).
- **Sous-titres** (≤ 12 car./ligne) : « BOULE DE FEU » → « … » → « COT. »
- **Boucle** : la poule reprend la pose de repos du mage (la dernière image renvoie à la première).
- **Neuf** : sprite du mage dessiné par @yehz (D3), étincelles en animation Aseprite (planche), poule CC0 ou dessinée. Aucun code.

### P2 · BATTERIE 1 %
- **Source** : `byaiden-vu-755862` (@byaiden_vu). L'original est un bonhomme à l'encre, dans une icône de batterie, contre la ligne rouge qui baisse ; ici, on passe au pixel et on change la chute.
- **Accroche** : le héros est coincé dans une icône de batterie, la barre descend vers lui.
- **Déroulé** : la barre baisse par crans (12 i/s) → le héros saute par-dessus (`pixel-saut`) → il branche un câble → mauvais embout → la batterie s'éteint (`pixel-degats`).
- **Sous-titres** : « 1 % » → « J'AI LE CÂBLE » → « PAS CELUI-LÀ ».
- **Neuf** : icône de batterie et câble dans Aseprite ; la barre qui baisse par crans correspond à la « jauge en escaliers » de D15 (conditionnelle) : en attendant, 4 calques posés l'un après l'autre.

### P3 · BOSS : L'INFLATION
- **Source** : `0xpai-eth-635565` (@0xpai_eth, prompt partiel). L'idée est un jeu rétro où les écueils de l'épargne deviennent des niveaux.
- **Accroche** : « NIVEAU 1 : ÉPARGNER ».
- **Déroulé** : le héros saute par-dessus un trou « ACHAT IMPULSIF » → un monstre « INFLATION » grossit derrière lui → il ramasse des pièces qui rapetissent → « GAME OVER ? NON : PATIENCE +1 ».
- **Lien science (D10)** : sert de bande-annonce à une vidéo de science sur les intérêts composés.
- **Neuf** : décor de niveau et monstre dans Aseprite ; `pixel-scintillement` pour les pièces. Aucun code.

### P4 · DE LA GROTTE AU WI-FI
- **Sources** : `xodud-rkd-160324` (@xodud_rkd, « tout le progrès humain » en pixel) et `songkeys-384673` (@songkeys, histoire de l'humanité sans langue parlée, compréhensible partout).
- **Accroche** : un homme des cavernes allume un feu.
- **Déroulé** : 5 époques en 20 s (feu, roue, imprimerie, ordinateur, téléphone), le héros vieillit d'une case à chaque saut → le Wi-Fi coupe → il se retrouve devant le feu, comme au début (boucle).
- **Sous-titres** : presque aucun (« -40 000 », « 2026 », « WIFI ? »). Le gag se lit sans texte, donc partout.
- **Neuf** : 5 petits décors Aseprite. C'est le plus cher en dessin, à garder pour plus tard.

## Sketch (9:16, perso rond, 15–45 s)

### S1 · LA RÉCURSION
- **Source** : `emollick-019567` (@emollick) : une explication de la récursion où chaque explication change de style.
- **Accroche** : « C'EST QUOI LA RÉCURSION ? »
- **Déroulé** : Moi commence « Pour comprendre la récursion… » → zoom dans l'écran derrière lui : le même perso, plus petit, recommence la phrase → 3 niveaux, chaque fois plus vite → silence → le plus petit : « …demande à ta mère. »
- **Neuf** : la comp du sketch imbriquée en elle-même, réduite (précomp), avec `zoom` au marqueur. A priori 0 code, mais l'imbrication est à tester.

### S2 · LES VOISINS (le son raconte la moitié)
- **Source** : `kamstudiolabs-100086` (@KamStudioLabs) : film muet où le son porte la moitié de l'histoire.
- **Accroche** : « 3 H DU MATIN ».
- **Déroulé** : Moi essaie de dormir ; à travers le mur, une perceuse, puis un piano, puis une fanfare : seule l'image de Moi réagit → silence → Moi frappe au mur → le mur frappe en retour, plus fort.
- **Garde-fou** : le gag doit rester lisible sans le son (comme la règle pixel, `.claude/skills/video-pixel/SKILL.md:10`) ; les sous-titres nomment le bruit (« *PERCEUSE* »).
- **Neuf** : bruitages CC0 ou jsfxr au manifeste, posés aux marqueurs (à la main dans l'app : `monter.py` ne place pas de sons).

### S3 · RECETTE D'UN LUNDI
- **Sources** : `ror-fly-880547` (@Ror_Fly) et `sarut0bisasuke-069973` (@Sarut0biSasuke) : une recette de cocktail, du verre vide au verre plein, avec les doses.
- **Accroche** : « RECETTE DU LUNDI ».
- **Déroulé** : un verre se remplit couche par couche, chaque dose s'affiche (« 2 cl de sommeil », « 40 cl de café », « 1 pincée de mails ») → la dernière dose « 1 réunion à 8 h » → le verre déborde → secousse.
- **Neuf** : un calque de forme dont la hauteur monte à chaque marqueur (expression, ou 4 calques). Aucun rapide « remplir » n'existe : à faire à la main d'abord, puis en rapide si ça se reproduit.

## Vulgarisation (9:16, 45–90 s, voix D4 bis)

### V1 · SI CHAQUE BILLE ÉTAIT 1 MILLION DE GENS
- **Source** : `rneayan-417829` (@rneayan) : la population de chaque pays tombe en billes (1 bille = 1 million de personnes), avec un bruit à chaque choc.
- **Question** : « La France en billes ? »
- **3 points** : France ≈ 68 billes · Inde ≈ 1 400 (le cadre déborde) · la Terre entière ≈ 8 000.
- **À vérifier** : chiffres de population (ONU, World Population Prospects, dernière révision).
- **Neuf** : une chute de billes demande une simulation. C'est **le meilleur candidat** pour la voie Canvas (voir le rapport), sinon on se contente de grilles de billes posées par paliers.

### V2 · 100 000 ANS POUR SORTIR DU SOLEIL
- **Source** : `astrothewizard-618782` (@AstroTheWizard) : le voyage d'un photon, avec une vraie marche aléatoire et l'aveu des incertitudes.
- **Question** : « Ta lumière a quel âge ? »
- **3 points** : le photon rebondit au hasard dans le Soleil · il met des dizaines de milliers d'années à en sortir · puis 8 min 20 s jusqu'à toi.
- **À vérifier** : la fourchette publiée va de ~10 000 à ~170 000 ans selon les modèles (NASA). Dire « des dizaines de milliers d'années », pas un chiffre unique.
- **Neuf** : un chemin en zigzag qui se trace (calque de forme + tracé progressif, à tester) ou une marche aléatoire (candidat Canvas).

### V3 · POINT NEMO
- **Source** : `haribuilds-007643` (@hariBuilds_) : le point le plus isolé de la Terre, l'altitude de l'orbite comparée à la distance au sol, et le cimetière des engins spatiaux.
- **Question** : « Plus seul qu'un astronaute ? »
- **3 points** : la terre la plus proche est à ~2 700 km · la station spatiale passe à ~400 km · les satellites en fin de vie y sont coulés.
- **À vérifier** : distance du point Nemo à la côte la plus proche (~2 688 km) ; altitude de l'ISS (~400–420 km) ; choix du site pour les rentrées contrôlées (ESA ou NASA).
- **Neuf** : deux jauges horizontales (aucune n'existe dans le modèle ; c'est la « jauge » de D15) et une carte très simple dessinée dans Aseprite. Ça remplit le cadre « schéma » (journal n° 26).

### V4 · TON QR CODE SE RÉPARE TOUT SEUL
- **Source** : `eyadnour-172216` (@eyadnour) : comment un QR code garde un message et le répare.
- **Question** : « QR code abîmé, il marche ? »
- **Analogie** : un message répété en morceaux, comme une phrase dont on peut deviner les lettres manquantes.
- **3 points** : le code est une grille de cases · une partie sert de « réserve » (correction d'erreurs) · jusqu'à ~30 % peut manquer (niveau H).
- **À vérifier** : niveaux L/M/Q/H ≈ 7/15/25/30 % (norme ISO/IEC 18004). « QR Code » est une marque de Denso Wave : employer le mot sans logo.
- **Neuf** : un QR code factice dessiné à la main dans Aseprite (ne renvoyant vers rien), des « dégâts » par `pixel-degats`. Rien d'autre.

### V5 · « TROP DE REQUÊTES » : LE SEAU À JETONS
- **Source** : `parkerrex-701462` (@ParkerRex) : expliquer le limiteur de débit « token bucket ».
- **Question** : « Pourquoi le site te bloque ? »
- **Analogie** : un seau qui se remplit d'un jeton par seconde ; chaque clic en prend un ; seau vide = « réessaie plus tard ».
- **3 points** : le seau se remplit à vitesse fixe · il a une taille maximum (rafale permise) · seau vide = erreur 429.
- **Neuf** : la jauge en escaliers de D15 (le seau), un compteur (D15). C'est la 2ᵉ vidéo qui en aurait besoin après V3, donc le seuil de la règle d'or serait atteint si on fait les deux.

## Fantasy (16:9, 60–120 s, série de Tim)

### F1 · LA FRESQUE QUI TOURNE
- **Source** : `perezalexa23-414045` (@perezalexa23) : une légende antique racontée en peinture autour d'un vase qui tourne.
- **Pitch** : Tim trouve dans la forêt une colonne de pierre gravée ; en en faisant le tour, il lit la légende de la forêt qui parle (la caméra suit la frise), et la dernière gravure… c'est lui.
- **Cliffhanger** : « Prochain épisode : qui l'a gravée ? »
- **Neuf** : une frise longue dessinée dans Aseprite, défilée en parallaxe horizontale (le modèle fantasy le fait déjà).

### F2 · LA VILLE QUI S'ALLUME À CHAQUE NOTE
- **Sources** : `kopert0x-098349` (@kopert0x) et `0xcodez-474136` (@0xCodez) : un personnage joue d'un piano, chaque note allume quelque chose et une seule chronologie règle le son et l'image.
- **Pitch** : Tim trouve une flûte dans un village abandonné ; chaque note rallume une fenêtre ; à la dernière, une fenêtre s'allume toute seule… quelqu'un est là.
- **Neuf** : une mélodie dans SoundCraft (à nous), une liste de marqueurs = une note = une fenêtre (calques allumés au marqueur). Pas de piano, pas de chat, pas de robot : on ne garde que le mécanisme « une note, une lumière ».

### F3 · UNE SEULE LIGNE
- **Source** : `paripune-657175` (@paripune) : une ligne continue dessine toute l'histoire.
- **Pitch** : prologue de saison : un fil d'or trace le village, la forêt, la grotte, puis le visage de Tim, sans jamais se couper ; il finit sur la carte de la saison.
- **Neuf** : un tracé progressif sur un calque de forme dans EffectCraft (existence de l'équivalent « Trim Paths » à vérifier). Les bords doivent rester nets en 16:9 (pas une règle pixel, mais la DA fantasy).

---

## Écartées (et pourquoi)
- Jeux interactifs (`froessell-562325`, `niegramotny-197521`, `aisongman-461057`…) : ce ne sont pas des vidéos.
- Jeux, films ou marques d'autrui (`opener-ai-843891` « Romance of the Three Kingdoms », `gandamu-ml-124280` Another World et Kavinsky, `taylorbereiter-189192` Cuphead, `aisongman-461057` Hearthstone, `kurahu-capten-054506` Evangelion, `airobertdaily-416945` Apple) : propriété d'autrui.
- Clips musicaux et vidéos de promo de produits (la majorité des 369 « motion ») : hors de nos 4 formats.
- Zoom continu jusqu'à l'atome (`acoramaa-053577`, `irinatoxi-962937`) : en Three.js, contraire au zoom pixel par paliers entiers et très cher en dessin.
- Parodie d'une pub célèbre (`johnmckeownn-511049`) : « forme reprise ».
