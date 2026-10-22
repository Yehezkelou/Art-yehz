# Ce qui m'a gêné

Journal de l'étape 1 du plan (`EffectCraft_Plan_Videos_Animees.docx`).
Ce fichier décide des étapes 4 à 7 : **on ne code une fonction que si elle a manqué sur au moins
2 vraies vidéos.** Une ligne par gêne, avec la vidéo où ça s'est produit.

| # | Gêne | Vu sur | Contournement utilisé | Piste |
|---|---|---|---|---|
| 1 | Pas de commande pour régler le point d'entrée/sortie d'un calque (seulement *Time Stretch* et *Split*) | sketch-01 | script `run_script` (`layer.inPoint = …`) | commande `layer.setTimeSpan` (= trim) ; très utile pour les sous-titres |
| 2 | Pas d'import de sous-titres `.srt` ni de « sous-titres depuis un texte » | sketch-01 | 4 calques texte créés un par un à la main | `captions.import` / `captions_from_transcript` — **le plus gros coût manuel de la vidéo** |
| 3 | Pour vérifier une animation : une image PNG par appel | sketch-01 | 4 rendus séparés (0,25 s / 2,5 s / 13,9 s / 15 s) | `contact_sheet` (grille 4×4 horodatée) — déjà listé dans `docs/claude-montage.md` |
| 4 | `get_comp` renvoie tout l'arbre : savoir « quel calque est où » coûte cher | sketch-01 | `run_script` qui liste juste les noms | `timeline_summary` (vue compacte façon EDL) |
| 5 | `transform/scale` est un vec3 : passer `[126,126]` met l'échelle Z à 0 | sketch-01 | toujours écrire `[x, y, 100]` | valeur par défaut Z = 100 quand on passe 2 composantes |
| 6 | Aucune animation prête à l'emploi pour rebond / pop / secousse comique / clignement | sketch-01 | expressions écrites à la main (pop, wiggle temporisé, clignement par liste de temps) | étape 4 du plan : en faire des `.ecpreset` |
| 7 | Pas de voix : aucune synthèse vocale française sur la machine (`flite` ne parle qu'anglais) | sketch-01 | vidéo muette + sous-titres ; texte à enregistrer dans `voix-a-enregistrer.txt` | enregistrer au téléphone, ou TTS externe (clé API perso) |
| 8 | Lip-sync : la bouche est pilotée par une sinusoïde, pas par la voix | sketch-01 | expression `sin(time*13)` pendant les répliques | `keys.audioToKeyframes` **fonctionne** (testé : null « Audio Amplitude », 3 curseurs × 408 clés) → brancher la bouche dessus dès qu'il y a une voix |
| 9 | Seulement 10 familles de polices installées, aucune police « display » / cartoon | sketch-01 | Inter Bold (fournie avec le logiciel) | étape 2 : installer 2 Google Fonts (licence OFL) |
| 10 | En headless, le rendu est CPU (pas de `--gpu`) : 408 images 1080×1920 en 50 s (~8 i/s) | sketch-01 | acceptable en 17 s de vidéo | prévisualiser en demi-résolution ; tester `--gpu` |
| 10b | Sous WSLg, le « GPU » est llvmpipe (Vulkan logiciel) : 885 ms par image dans la fenêtre, même en qualité Quart | sketch-01 | prévisualiser en Quart, travailler surtout en headless | tester une build Windows native (accès direct à l'Intel UHD 620) |
| 11 | Le serveur MCP met plus de 30 s à démarrer si le binaire n'est pas déjà compilé | étape 0 | `cargo build --release -p effectcraft-cli` avant de lancer Claude | déjà noté dans le plan (§ étape 0) |
| 12 | Les sous-titres du sketch 01 débordent de la zone sûre (≈ x 115–970) et mordent sur la colonne des boutons | étape 2 (contrôle) | — | à corriger en calant la voix : passer en 72 px, ≤ 20 car./ligne (bible § 5) |
| 13 | `layer.newSolid` n'a pas de paramètre `position` (il faut un `layer.setTransform` derrière) | étape 2 | `layers: ["#1"]` juste après la création | ajouter `position` comme pour `layer.newShape` / `layer.newText` |
| 14 | `renderQueue.saveTemplate` renvoie tout le catalogue de modèles (~15 000 caractères) au lieu du seul modèle créé | étape 2 | — | réponse courte pour les agents |
| 15 | Le headless (CLI / MCP) ne peut pas enregistrer de modèle : `templates.saveAs` → « no settings store » | étape 3 | 2ᵉ instance de l'app sur un autre port avec `EFFECTCRAFT_CONFIG_DIR` jetable, puis copie des `.ectemplate` | option `--config-dir` pour la CLI |
| 16 | `layer.settings` qui change la taille d'un solide garde l'ancien point d'ancrage : le calque saute hors champ (la brume avait disparu) | étape 3 | recentrer l'ancrage à la main | recentrer l'ancrage comme AE |
| 17 | Fractal Noise en 1920×1080 : 630 ms par image sur le CPU | étape 3 | calculer en 480×270 et agrandir ×4 (42 ms) | à garder en tête pour toute texture « douce » |
| 18 | Le texte dans la comp pixel 270×480 est anticrénelé (15 teintes autour du titre au lieu de 2) | étape 3 | acceptable pour l'instant | option « texte sans lissage » pour le pixel art — à revoir sur une vraie vidéo pixel |
| 19 | La fenêtre de l'app a cessé de répondre au canal de contrôle (2 timeouts de 60 s) pendant qu'elle était ouverte avec une modif non enregistrée | étape 3 | travail en headless + instance temporaire | à observer : boîte de dialogue ouverte ? lecture en cours ? |
| 20 | Pas de commande pour renommer un effet ; `list_effects` filtré renvoie tous les paramètres (énorme) | étape 3 | script `run_script` (`effect.name = …`) | `effect.rename` ; liste courte par défaut |
| 21 | `anim.applyPreset` remplace la valeur fixe des propriétés du calque par celle du preset : un preset de secousse sur la position téléporte le calque, l'échelle 126 % repasse à 100 % | étape 4 | tous les presets passent par leurs propres effets (*Transform*), jamais par les propriétés du calque | ne pas écraser la valeur quand le preset n'apporte qu'une expression |
| 22 | Un `.ecpreset` ne transporte pas les animateurs de texte ; le menu *Fichier ▸ Scripts* ne liste que les `.jsx/.js`, pas les scripts de commandes `.jsonl` | étape 4 | karaoké en `.jsonl` lancé par *Exécuter un fichier de script* | presets avec animateurs ; `.jsonl` installables |
| 23 | `prop.select` refuse le chemin d'un groupe d'effet (`effects/#1`), il faut son uid ; `anim.savePreset` passe forcément par la sélection | étape 4 | génération des `.ecpreset` en Python à partir d'un preset enregistré par le logiciel | `anim.savePreset {layer, effects:[…]}` sans sélection |
| 24 | Sur un calque de forme, l'effet *Transform* coûte ~360 ms par image et même un simple *Slider Control* ~200 ms (CPU) : un seul preset fait passer une image de 235 à 1 270 ms | étape 5 (test) | mouvements « rapides » en expressions sur la transformation du calque (0 ms) ; `monter.py` les utilise par défaut | un contrôle d'expression ne devrait rien coûter au rendu |
| 25 | Dans une expression, `value` d'une position/échelle d'un calque 2D n'a que 2 composantes alors que la propriété est en 3D : `value[2]` est indéfini → « expression result array must contain numbers » | étape 5 | `value.slice()` puis modifier [0] et [1] | `value` de même longueur que la propriété, ou message plus clair |
| 26 | Modèle vulga : le cadre « schéma » reste vide pendant l'analogie (orage, 7–17 s) : aucune illustration ni icône disponible | vulga-01-gps | — | bibliothèque d'icônes / pictos simples (éclair, satellite, horloge) dans le modèle |
| 27 | Une question de 27 caractères en 88 px débordait des bords sûrs | vulga-01-gps | `monter.py` réduit la taille au-delà de 22 car. (72 px ici) | — corrigé dans l'outil |
| 28 | Le récap dure 7 s sans voix (fixé à « fin − 8 s ») : peut-être trop long | vulga-01-gps | à juger en regardant la vidéo | durée du récap réglable dans l'épisode |
| 29 | Aseprite (Windows) ne peut ni lire ni écrire dans les dossiers WSL (`\\wsl.localhost\…` → « File not found » / « Cannot save file ») | étape « usine 2.2 » (essai Tim) | dossier de travail Aseprite côté Windows (`C:\Users\Yehezkelou\ico-pixel\`), copie vers `~/videos/assets/` après chaque export | garder les sources `.aseprite` côté Windows ; le dépôt git reçoit la copie |
| 30 | monter.py contrôle la longueur de la question (> 22 car.) mais pas celle de la conclusion de la flèche (vulga) : « réglées au sol ! » sortait du cadre et de la zone sûre | vulga-01-gps (v2, 22/10) | vu sur apercu-2.png, conclusion raccourcie à « réglées ! » | alerte (ou réduction de taille) au-delà de ~12 car., comme pour la question |
| 30 | Word (COM) refuse `ExportAsFixedFormat` et `SaveAs2` en PDF sur un document déjà ouvert dans la même session : il faut rouvrir le `.docx` dans une session neuve | plans v2.1 et v2.2 | 2 lancements PowerShell séparés (1 : champs + SaveAs .docx ; 2 : réouverture + SaveAs .pdf) | — |

## Décisions à prendre

- ~~Police de titre et de sous-titres~~ → Lilita One + Montserrat ExtraBold (bible § 5).
- ~~Palette par série~~ → bible § 4.
- ~~Nom de chaîne / pseudo~~ → ico-vid / @yehz (bible § 7).
- Jingle de 1 s — toujours ouvert.
