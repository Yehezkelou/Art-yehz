# Rapport : bibliothèque « awesome-opus5-5-videos »

- **Mission** : `agents/missions/2026-10-22-awesome-opus-videos.md`
- **Agent** : Claude `general-purpose`, 2026-10-22, Windows 11
- **Source** : copie locale `a-trier/awesome-opus/` (commit 92aee2f du 13/10/2026, `SOURCE.txt`), soit 703 fiches. Le tri se fait sur `data/videos.json` avec un script Python lancé en `-I` depuis le dossier temporaire de la session, hors du dépôt. J'ai lu en entier environ 45 fiches retenues. Je n'ai ouvert aucun lien x.com ni skillry.dev, je n'ai lancé aucun prompt et je n'ai rien installé ni commité.
- **Écrit** : ce rapport et `a-trier/awesome-opus/idees-ico-vid.md` (15 idées détaillées, hors git par `.gitignore:16`).

## Résultat

### En 6 lignes
1. **15 idées transposables** (4 pixel, 3 sketch, 5 vulga, 3 fantasy). Quatorze se font avec les modèles et les rapides actuels, plus des dessins Aseprite. La quinzième (V1, les billes) demande une simulation.
2. **Les 3 meilleures** : V4 « Ton QR code se répare tout seul », P1 « LE SORT RATÉ » et V3 « Point Nemo ».
3. **9 régularités de prompts à reprendre**, toutes sans code, dans les recettes `video-*`. Trois autres sont **à ne pas reprendre**.
4. **Voie Canvas : techniquement saine, mais pas maintenant.** Un Canvas 2D sans lissage, rendu image par image et importé dans EffectCraft en séquence PNG, donnerait du pixel exact. Aucune gêne du journal ne la réclame deux fois. On la garde comme voie de secours, avec un déclencheur écrit.
5. **Droits** : on peut s'inspirer et citer. On ne copie aucun prompt dans le dépôt public, on ne refait aucune vidéo à l'identique et on ne reprend rien de la propriété d'autrui que certains prompts citent (jeux, marques, musiques).
6. Point à corriger dans la mission : D15 ne dit pas « DOM/CSS refusé ». Elle dit « Hyperframes non installé » (`plans/decisions.md:17`). Le refus du rendu navigateur lissé vient du rapport motion design (`agents/rapports/claude/2026-10-22-motion-design-opus.md:37`).

### Tri de la bibliothèque (mesuré)
| Mesure | Valeur |
|---|---|
| Fiches | 703 : motion 369, 3d 117, explainer 116, interactive 101 |
| Prompts partiels (seul le message de l'auteur est donné) | 207 ; il reste **496 prompts complets** |
| Étiquette technique `pixel` | 15 fiches, dont 11 jeux ou démos jouables |
| Mots-clés pixel, rétro, 8/16-bit, sprite, fantasy, dessiné à la main, bonhomme… | ≈ 50 fiches utiles une fois le bruit retiré |
| Explainers sans mot-clé de style | ≈ 95 : surtout des promos de produits et des démos 3D interactives |
| Doublons exacts (prompt de plus de 150 car.) | 7, dont `zacxbt-944604` = `majidmanzarpour-927543` (même prompt, même date) |
| Longueur des prompts | médiane 221 caractères, 90ᵉ centile 1 077 |

Le gros de la bibliothèque (promos de produits, interfaces Dribbble, Three.js/shaders, jeux jouables) ne sert pas ico-vid.

### Q1 : les 15 idées
Le détail de chacune (accroche, déroulé, sous-titres, faits à vérifier) est dans `a-trier/awesome-opus/idees-ico-vid.md`.

| # | Format | Idée ico-vid réécrite | Source (slug · compte) | Ce qu'il faudrait de neuf |
|---|---|---|---|---|
| P1 ★ | Pixel | **LE SORT RATÉ** : le mage charge une boule de feu, étincelles, silence, le sort retombe en poule sur sa tête ; la poule reprend la pose de départ (boucle) | `zacxbt-944604` · @zacxbt (même prompt sous @majidmanzarpour) | Sprite du mage par @yehz (D3), étincelles en planche Aseprite ; `pixel-saut`, `pixel-degats`, `secousse` existent |
| P2 | Pixel | **BATTERIE 1 %** : le héros, coincé dans une icône de batterie, fuit la barre qui baisse par crans, branche un câble… le mauvais | `byaiden-vu-755862` · @byaiden_vu | Icône et câble Aseprite ; barre par crans = « jauge en escaliers » de D15 (sinon 4 calques successifs) |
| P3 | Pixel | **BOSS : L'INFLATION** : niveau rétro où l'achat impulsif est un trou à sauter et l'inflation un monstre qui grossit ; bande-annonce d'une vidéo de science (D10) | `0xpai-eth-635565` · @0xpai_eth (partiel) | Décor de niveau et monstre Aseprite ; `pixel-scintillement` pour les pièces |
| P4 | Pixel | **DE LA GROTTE AU WI-FI** : 5 époques en 20 s, presque sans texte ; le Wi-Fi coupe et on revient au feu | `xodud-rkd-160324` · @xodud_rkd ; `songkeys-384673` · @songkeys | 5 petits décors (le plus cher en dessin) |
| S1 | Sketch | **LA RÉCURSION** : Moi commence à expliquer, zoom dans l'écran derrière lui, son double recommence, 3 niveaux, chute | `emollick-019567` · @emollick | Comp du sketch imbriquée en elle-même + `zoom` au marqueur (à tester) |
| S2 | Sketch | **LES VOISINS** : 3 h du matin, seuls les bruits du mur racontent l'escalade ; Moi frappe, le mur répond plus fort | `kamstudiolabs-100086` · @KamStudioLabs | Bruitages CC0/jsfxr au manifeste, posés à la main (`monter.py` ne place pas de sons) ; le gag reste lisible sans le son (sous-titres qui nomment le bruit), comme la règle pixel `.claude/skills/video-pixel/SKILL.md:10` |
| S3 | Sketch | **RECETTE D'UN LUNDI** : un verre se remplit de doses absurdes (« 40 cl de café ») jusqu'à déborder | `ror-fly-880547` · @Ror_Fly ; `sarut0bisasuke-069973` · @Sarut0biSasuke | Niveau de liquide monté par marqueur (expression ou 4 calques) ; aucun rapide « remplir » |
| V1 | Vulga | **SI CHAQUE BILLE ÉTAIT 1 MILLION DE GENS** : France ≈ 68, Inde ≈ 1 400, Terre ≈ 8 000 | `rneayan-417829` · @rneayan | Chute de billes = simulation : **premier candidat de la voie Canvas** ; sinon grilles posées par paliers |
| V2 | Vulga | **100 000 ANS POUR SORTIR DU SOLEIL** : marche au hasard du photon, puis 8 min 20 s jusqu'à toi | `astrothewizard-618782` · @AstroTheWizard | Tracé en zigzag (à tester) ; fourchette de durée très large : dire « des dizaines de milliers d'années » |
| V3 ★ | Vulga | **POINT NEMO** : la terre la plus proche à ~2 700 km, la station spatiale à ~400 km, le cimetière des satellites | `haribuilds-007643` · @hariBuilds_ | 2 jauges (D15) + carte Aseprite : remplit le cadre « schéma » (journal n° 26) |
| V4 ★ | Vulga | **TON QR CODE SE RÉPARE TOUT SEUL** : grille, réserve de correction, jusqu'à ~30 % peut manquer | `eyadnour-172216` · @eyadnour | QR factice dessiné dans Aseprite, dégâts par `pixel-degats` ; rien d'autre |
| V5 | Vulga | **« TROP DE REQUÊTES » : LE SEAU À JETONS** : un jeton par seconde, chaque clic en prend un, seau vide = erreur 429 | `parkerrex-701462` · @ParkerRex | Jauge en escaliers + compteur (D15) : avec V3, ce serait la 2ᵉ vidéo qui les demande |
| F1 | Fantasy | **LA FRESQUE QUI TOURNE** : Tim fait le tour d'une colonne gravée qui raconte la légende de la forêt ; la dernière gravure, c'est lui | `perezalexa23-414045` · @perezalexa23 | Frise longue Aseprite défilée en parallaxe (le modèle le fait) |
| F2 | Fantasy | **LA VILLE QUI S'ALLUME À CHAQUE NOTE** : chaque note de flûte de Tim rallume une fenêtre ; à la fin, une fenêtre s'allume toute seule | `kopert0x-098349` · @kopert0x ; `0xcodez-474136` · @0xCodez | Mélodie SoundCraft ; une note = un marqueur = un calque allumé |
| F3 | Fantasy | **UNE SEULE LIGNE** : prologue de saison tracé par un fil d'or continu, jusqu'à la carte | `paripune-657175` · @paripune | Tracé progressif d'un calque de forme (équivalent « Trim Paths » à vérifier dans EffectCraft) |

Pourquoi ces 3 en tête :
- **V4** : le sujet est pixel par nature, le gag est intégré (on abîme le code et il marche encore), le fait est vérifiable dans une norme et il ne faut aucun outil neuf.
- **P1** : il ne demande que des rapides existants et le héros dessiné par @yehz.
- **V3** : l'accroche est contre-intuitive et sourçable, et elle remplit le cadre « schéma » qui restait vide (gêne n° 26).

### Q2 : régularités des prompts qui marchent
Comptages sur les 496 prompts complets. Ce sont des expressions régulières grossières, donc des ordres de grandeur. Fichiers unitaires « single / self-contained » : 64. Rendu « fonction pure du temps / seek(t) » : 35. Image par seconde donnée : 63. Durée en secondes : 94. Résolution : 58. Blocs balisés `<inputs>`, `<direction>`… : 31. Son calé sur le temps ou le tempo : 64. Playwright, Puppeteer ou ffmpeg : 44. `?t=` : **2 seulement**. `imageSmoothingEnabled` : 2 (le même prompt en double).

**À reprendre** (aucune ligne de code, seulement les recettes) :

| # | Régularité | Exemples | Où la mettre (fichier : section) |
|---|---|---|---|
| R1 | **Des chiffres, pas des adjectifs** : secondes, pixels, couleurs de la palette par leur nom ou hex | `flxrnc-251921` (le prompt le demande en toutes lettres) | `.claude/skills/video-*/SKILL.md` : « Mise en scène », puce « Chaque demande d'effet en 5 éléments » (ajouter : « chaque élément en valeur : s, px, couleur de la palette ») |
| R2 | **Liste des moments forts sur une grille de temps, validée avant de construire** | `flxrnc-251921`, `twoclipping-402193`, `woojinrad-455731`, `henrygsing-050247` | `.claude/skills/video-*/SKILL.md` : « Méthode », étape 2 (le tableau existe ; ajouter que les `temps` des `[[effets]]` en sont recopiés tels quels) |
| R3 | **Liste d'interdits explicite par format** | `twoclipping-402193` (« Banned »), `zacxbt-944604` (« no sub-pixel, anti-aliasing, gradients, shadowBlur ») | `.claude/skills/video-pixel/SKILL.md` : « Règles d'écriture », puce « Règle d'or du pixel art » (ajouter dégradé, ombre douce, sous-pixel, texte hors multiples de 8) |
| R4 | **Mouvement lisse, puis posé sur la grille** : on calcule la pose en continu, puis on arrondit chaque image pour garder une sensation de 8 à 12 i/s | `zacxbt-944604` | `.claude/skills/video-pixel/SKILL.md` : « Règles d'écriture » ; aussi la consigne de la DA Gemini (`.agents/skills/ico-da`, hors de cette mission) |
| R5 | **La dernière image = la première**, vérifiée en comparant | `flxrnc-251921`, `twoclipping-402193`, `0xkarmi-129839` (contrôle « image 0 contre image 720 ») | `.claude/skills/video-*/SKILL.md` : « Méthode », étape 6 (aperçus) : « regarder si la dernière image renvoie à la première » (`bible.md:47`) |
| R6 | **Contrôler des images autour de chaque moment fort avant le rendu complet** | `flxrnc-251921` (5 images autour de chaque temps fort), `twoclipping-402193` (1 image par temps fort), `astrothewizard-618782` | `.claude/skills/video-*/SKILL.md` : « Méthode », étape 6 ; c'est la planche contact déjà prévue (journal n° 3), sans code tant qu'il n'y a pas de 2ᵉ gêne |
| R7 | **Faits sourcés à la source primaire, incertitude dite** | `cryptoxorz-359201` (articles originaux, institutions, manuels ; pas de comptes secondaires), `astrothewizard-618782` | `.claude/skills/video-vulga/SKILL.md` : « Règles d'écriture », 2ᵉ puce (préciser « source primaire : article, institution, manuel ») |
| R8 | **Accroche = écart de curiosité contre-intuitif relié au réel** | `michaelraspuzzi-740595`, `cryptoxorz-359201` | `.claude/skills/video-vulga/SKILL.md` : « Règles d'écriture », 1re puce (exemple : « L'ISS est plus proche que la terre ferme ») |
| R9 | **Une seule chronologie pour le son et l'image** : un son = un marqueur = un effet | `kopert0x-098349`, `0xcodez-474136`, `rneayan-417829`, `koushikde-937635` | `.claude/skills/video-pixel/SKILL.md` et `video-fantasy/SKILL.md` : « Mise en scène » (nouvelle puce) |
| R10 | **Bloc « entrées » avec valeurs par défaut** : ce que l'agent demande, et ce qu'il prend s'il ne l'a pas | `flxrnc-251921`, `twoclipping-402193`, `gkxspace-923139` | Façon de demander un `episode.toml` : `.claude/skills/video-*/SKILL.md` : « Méthode », étape 2 (fiche : format, idée en 1 phrase, durée, 3–4 moments forts avec instants, ce qui est fourni ou non : voix, sprites) |

**À ne pas reprendre** :
- **« Travaille seul, ne me pose pas de questions »** (`astrothewizard-618782`). C'est contraire à la validation du script par @yehz (étape 2 des recettes) et aux portes.
- **Flou de mouvement par sous-images** (`twoclipping-402193`, `yankis0x-174321`, `flxrnc-251921`) et **60 i/s**. C'est contraire à « pas de flou ni de semi-transparence » (`CLAUDE.md:26`) et aux cadences de la bible.
- **Morceaux « libres de droits » de Mixkit ou d'ailleurs** (`twoclipping-402193`). Tout fichier passe au manifeste (`CLAUDE.md:25`).

`?t=` (`flxrnc-251921`, `0xcodez-474136`) : chez nous, `render_frame` d'EffectCraft fait déjà « une image à n'importe quel instant ». Ça ne sert que pour la voie Canvas. La règle derrière reste bonne à écrire pour toute nouvelle expression : pas d'aléatoire sans graine fixe, rien qui dépende de l'image précédente.

### Q3 : voie « Canvas 2D → vidéo » : verdict
**Techniquement saine pour du pixel exact, mais pas maintenant.** On la garde en voie de secours avec un déclencheur précis.

- **Ce qui marche sur le papier** :
  - On dessine dans un Canvas de 270×480 en coordonnées entières, avec une palette fixe, sans `drawImage` agrandi ni texte. Les sprites d'Aseprite sont collés à l'échelle ×1 (`zacxbt-944604` décrit exactement ce protocole).
  - On rend chaque image depuis une fonction pure du temps, à 12 i/s.
  - On importe le résultat en **séquence PNG dans la comp pixel d'EffectCraft** : `file.import {"paths": […], "sequence": true, "frameRate": 12}` (`~/dev/vid/effectcraft/docs/footage.md:54`). Sous-titres, signature, ×4 et export restent dans EffectCraft, et `verifier_pixels.py` contrôle la palette.
  - **Il ne faut pas ffmpeg** sur ce chemin. Il est absent du PATH de Git Bash sur cette machine, et `INSTALLATION.md:39` le dit facultatif.
- **Capture sans rien installer** :
  - Chrome et Edge sont présents (`C:\Program Files\Google\Chrome\Application\chrome.exe`, `msedge.exe`), et Node v24.22.1 aussi.
  - Le mode `--headless --screenshot` avec `--force-device-scale-factor=1` et `?t=` permet une capture par image : un processus par image, soit 360 lancements pour 30 s. C'est lent, et **non testé**.
  - Playwright ou Puppeteer iraient plus vite, mais ce serait une installation npm, et Playwright télécharge ses navigateurs (sortie réseau).
- **Coûts** :
  - Chaque clip est un programme JS sur mesure (300 à 1 000 lignes d'après les prompts lus), à écrire, relire et vérifier, sans réutilisation comme les rapides ou les modèles.
  - Il y aurait deux chaînes à entretenir.
  - Le texte de Canvas (`fillText`) est lissé : il resterait dans EffectCraft.
- **Conflits** :
  - **D3** : les héros sont dessinés par @yehz, donc pas de personnage procédural en code. Le Canvas ne servirait qu'à la « machinerie » (billes, particules, marche au hasard, grilles de données), avec des sprites Aseprite collés.
  - **D15 / rapport motion design** : l'objection technique (rendu navigateur lissé) tombe pour un Canvas sans lissage. L'objection de méthode reste : la décision du rapport motion design dit de rouvrir un moteur navigateur seulement si EffectCraft échoue 2 fois sur un même type d'élément (`agents/rapports/claude/2026-10-22-motion-design-opus.md:28`).
  - **Règle d'or** (`CLAUDE.md:24`) : aucune gêne du journal ne réclame une simulation. La n° 26 (`ce-qui-m-a-gene.md:35`) demande des icônes, et Aseprite y répond.
- **Déclencheur proposé** : si deux vraies vidéos ont besoin d'un élément qu'EffectCraft ne sait pas faire en pixel exact (simulation, dizaines d'objets pilotés par des données), V1 et V2 étant les candidates, alors ouvrir une mission test : un clip de 3 s, séquence PNG 270×480 à 12 i/s, import dans la comp pixel, `verifier_pixels.py` vert, temps passé comparé à EffectCraft.

### Q4 : droits
- **La licence MIT** (`LICENSE:3`, « Copyright (c) 2026 yihui-dev ») couvre la compilation : la liste, la mise en forme, les fichiers. Le `README.md:111` dit que chaque vidéo et chaque prompt appartiennent à leur créateur.
- **Permis** : s'inspirer d'une idée (une idée n'est pas protégée), la réécrire entièrement (histoire, décor, chute, titre, dessin), citer l'auteur (slug + @compte) dans nos notes. Mettre « idée inspirée de @… » dans la description est une courtoisie à décider par @yehz. Garder la copie locale dans `a-trier/` est permis : elle est hors git (`.gitignore:16`).
- **Interdit** :
  - copier un prompt entier, ou un long passage, dans un fichier suivi par git (dépôt public) ;
  - refaire une vidéo à l'identique, avec la même suite de scènes, le même titre (« The 99th Spell », « the last piano ») ou la même chute ;
  - reprendre leurs images, aperçus ou sons (`media.skillry.dev`) ;
  - reprendre la propriété d'autrui que certains prompts citent : Another World et Kavinsky (`gandamu-ml-124280`), Hearthstone (`aisongman-461057`), Cuphead (`taylorbereiter-189192`), Evangelion (`kurahu-capten-054506`), logos de marques ;
  - présenter une idée reprise comme entièrement nôtre si on nous le demande.
- Le mot « QR Code » est une marque de Denso Wave. On peut l'employer comme nom commun, mais sans logo (V4).

## Preuves
- Comptages : script `filtre.py`, `f2.py` et `f3.py` dans `C:\Users\HP\AppData\Local\Temp\claude\C--Users-HP-Documents-yehz-Art-yehz\214e438e-9381-4471-a999-20405c2e9cba\scratchpad\filtre\`, lancés en `python3 -I` sur `a-trier/awesome-opus/data/videos.json`. Sorties résumées dans le tableau « Tri ».
- Fiches lues en entier : les 15 sources du tableau, plus `flxrnc-251921`, `twoclipping-402193`, `0xkarmi-129839`, `koushikde-937635`, `yankis0x-174321`, `cryptoxorz-359201`, `woojinrad-455731`, `alex-prompter-997524`, `michaelraspuzzi-740595`, `gkxspace-923139` (fiche tronquée dans la source), `anjmaxx-459455`, `songkeys-384673` et une dizaine d'autres explainers et prompts « motion ».
- Règles ico-vid citées : `CLAUDE.md:24-28` ; `bible.md:44,47` ; `plans/decisions.md:17` (D15) ; `ce-qui-m-a-gene.md:11` (n° 3) et `:35` (n° 26) ; `.claude/skills/video-pixel/SKILL.md:10,16,23-26,34-36,42-56`.
- EffectCraft : `~/dev/vid/effectcraft/docs/footage.md:17-54` (import de séquences d'images).

## Ce qui reste incertain
- **Rien n'a été testé** : ni la capture Chrome headless image par image, ni l'exactitude au pixel d'une capture (facteur d'échelle Windows, profil de couleur PNG), ni l'imbrication de comp (S1), ni le tracé progressif (F2, F3) dans EffectCraft.
- Le texte des fiches est un **déclaratif d'auteur**. Je n'ai pas vu les vidéos (aucun lien ouvert). Une idée peut être meilleure ou pire à l'écran que sur le papier.
- Paternité de `zacxbt-944604` et `majidmanzarpour-927543` : même prompt, même date. Je ne sais pas qui l'a écrit le premier, et je cite les deux.
- Les faits des idées vulga (population, durée du photon, Point Nemo, niveaux du QR code) viennent de ma mémoire. Ils sont **à vérifier** à la source primaire avant tout script.
- Les comptages par expressions régulières sont approximatifs (faux positifs et faux négatifs possibles).
- Gemini (essaim) donne un avis indépendant en parallèle. Je ne l'ai pas attendu, il est à comparer avant d'intégrer quoi que ce soit.
