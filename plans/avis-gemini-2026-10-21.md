Voici mon deuxième avis stratégique sur [briefing.md](file:///tmp/claude-1001/-home-Yehezou-videos/3d9dde96-f39d-473f-b741-ee6e724871f5/scratchpad/agy/briefing.md) et [plan-2.2.txt](file:///tmp/claude-1001/-home-Yehezou-videos/3d9dde96-f39d-473f-b741-ee6e724871f5/scratchpad/agy/plan-2.2.txt).

---

### 1. Critique franche de la stratégie : les 3 angles morts majeurs

#### A. Dispersion éditoriale mortelle pour l'algorithme et le temps de dessin ([§ 12](file:///tmp/claude-1001/-home-Yehezou-videos/3d9dde96-f39d-473f-b741-ee6e724871f5/scratchpad/agy/plan-2.2.txt#L1017-L1124))
* **Où je ne suis pas d'accord :** Empiler dès le mois 2 quatre séries (Gags gaming muets, Science parlée, Fiction « Tim », Ambiances de 1–3 h) sur une même chaîne débutante fragmente l'audience en sous-publics incompatibles. Un spectateur abonné pour une boucle lo-fi de 2 h ou un gag RPG de 20 s ne cliquera pas sur 8 minutes de physique : le taux de clic (CTR) des abonnés chutera, freinant les impressions YouTube (*mécanisme de recommandation YouTube : sûr*). De plus, compter sur les Ambiances de 2 h pour les 8 000 h ([§ 12.2](file:///tmp/claude-1001/-home-Yehezou-videos/3d9dde96-f39d-473f-b741-ee6e724871f5/scratchpad/agy/plan-2.2.txt#L1040-L1058)) reste très risqué : même avec quelques micro-événements, une chaîne qui tire l'essentiel de ses heures de boucles longues s'expose à un refus au moment de l'examen humain YPP pour « contenu répétitif » (*règle YouTube sur les boucles : sûre ; sévérité de l'examinateur : incertaine*). Enfin, tenir 1 changement de plan toutes les 3–4 s ([§ 11.2](file:///tmp/claude-1001/-home-Yehezou-videos/3d9dde96-f39d-473f-b741-ee6e724871f5/scratchpad/agy/plan-2.2.txt#L1009)) sur une vidéo de science de 8 min exige ~130 plans illustrés : l'estimation de 3 h humaines ([§ 11](file:///tmp/claude-1001/-home-Yehezou-videos/3d9dde96-f39d-473f-b741-ee6e724871f5/scratchpad/agy/plan-2.2.txt#L985)) est irréaliste.
* **Correction concrète :**
  1. **Lier Gags et Science pendant 6 mois** : chaque Short de gag met Tim face au problème concret traité dans la vidéo longue de la quinzaine (ex. Tim perdu à cause du décalage d'horloge → renvoie vers la vidéo GPS).
  2. **Raccourcir les vidéos longues de science à 4–5 min** (format beaucoup plus dense, rétention supérieure, tenable en 3 h).
  3. **Sortir les Ambiances de 1–3 h de la chaîne principale** (les vendre uniquement en boucles de 60 s en boutique) et reporter la série narrative « Tim » au mois 6.

#### B. L'illusion des ventes passives itch.io et du TikTok > 1 min compilé ([§ 13](file:///tmp/claude-1001/-home-Yehezou-videos/3d9dde96-f39d-473f-b741-ee6e724871f5/scratchpad/agy/plan-2.2.txt#L1125-L1215), [§ 14](file:///tmp/claude-1001/-home-Yehezou-videos/3d9dde96-f39d-473f-b741-ee6e724871f5/scratchpad/agy/plan-2.2.txt#L1216-L1323))
* **Où je ne suis pas d'accord :** Le [§ 14.2](file:///tmp/claude-1001/-home-Yehezou-videos/3d9dde96-f39d-473f-b741-ee6e724871f5/scratchpad/agy/plan-2.2.txt#L1235-L1256) suppose que l'audience des vidéos générera 20 ventes/mois de packs et 2 commandes à 80 $. Or une audience francophone de vulgarisation scientifique ne contient presque aucun acheteur d'assets de jeu (développeurs indés) ni de clients d'overlays Twitch (*écart de cible : très sûr*). De plus, sur itch.io, un pack d'un seul personnage 32×32 isolé se vend très mal : les développeurs achètent des ensembles cohérents complets. Côté TikTok, compiler des Shorts muets de 20 s pour dépasser 1 min ([§ 12.1](file:///tmp/claude-1001/-home-Yehezou-videos/3d9dde96-f39d-473f-b741-ee6e724871f5/scratchpad/agy/plan-2.2.txt#L1025)) est régulièrement disqualifié du *Creator Rewards Program* pour manque d'originalité (*règle TikTok sur les compilations : sûre*).
* **Correction concrète :**
  1. **Orienter la boutique à 100 % vers les streamers/créateurs au départ** (packs d'emotes animées de Tim, écrans « Starting Soon / BRB », alertes Twitch), beaucoup plus faciles à produire à l'unité qu'un tileset de jeu complet.
  2. **Publier un mini-pack gratuit d'appel sur itch.io** dès la semaine 6 pour capter le moteur de recherche interne d'itch.io et rediriger vers le pack payant.
  3. **Remplacer les compilations TikTok** par une version verticale parlée de 65 s des épisodes « Science en pixel ».

#### C. Sur-ingénierie de la chaîne logicielle aux semaines 1 à 3 ([§ 10](file:///tmp/claude-1001/-home-Yehezou-videos/3d9dde96-f39d-473f-b741-ee6e724871f5/scratchpad/agy/plan-2.2.txt#L729-L904), [§ 15.1](file:///tmp/claude-1001/-home-Yehezou-videos/3d9dde96-f39d-473f-b741-ee6e724871f5/scratchpad/agy/plan-2.2.txt#L1325-L1389))
* **Où je ne suis pas d'accord :** Compiler et intégrer en MCP 4 nouveaux logiciels en alpha/pré-alpha tout en codant le moteur caméra, `monter.py v2` et les premiers épisodes en 3 semaines contredit la règle d'or du [§ 1](file:///tmp/claude-1001/-home-Yehezou-videos/3d9dde96-f39d-473f-b741-ee6e724871f5/scratchpad/agy/plan-2.2.txt#L51). Utiliser PhotoCraft (alpha précoce) pour dessiner des décors pixel en PSD alors qu'Aseprite est déjà acheté, gère la palette `.gpl`, les calques et l'export CLI par calque (`aseprite.exe -b --save-as`), ajoute un maillon fragile sans gain.
* **Correction concrète :** **N'installer que FilmCraft au mois 1** (pour Whisper `.srt` et l'assemblage long). Faire 100 % du pixel art (sprites **et** décors multicalques) dans Aseprite. Reporter SoundCraft, PhotoCraft et VectorCraft après la 10e vidéo publiée.

---

### 2. « Regarder les vidéos » (`regarder.py` + MCP)

* **Utile tel quel ?** Oui pour le **contrôle qualité objectif** (zones sûres 9:16, présence des sous-titres, vérification des coupes, niveaux LUFS) et pour inspecter l'image exacte d'un décrochage à J+7.
* **Ce qui est surestimé ou manque :**
  * *Surestimé :* Un modèle qui lit des planches PNG (même en rafale sur 1–2 s) juge mal le *feeling* du mouvement à 24 i/s (sautillement de parallaxe, timing comique) et ne perçoit pas si un bruitage 8 bits masque l'intelligibilité d'une consonne malgré un bon niveau LUFS.
  * *Ce qui manque à `regarder.py` :*
    1. **Un score de mouvement inter-frames** (% de pixels qui changent par seconde) pour détecter automatiquement les plans statiques de plus de 3 s.
    2. **L'incrustation des métadonnées sur la planche contact** : nom du plan (`episode.toml`), texte du sous-titre et écart voix/musique en dB sous chaque vignette.
    3. **Un test de miniature en contexte** : coller la miniature au milieu de 5 miniatures concurrentes réelles réduites à 10 % pour juger son impact relatif.
* **Usage stratégique (au-delà du contrôle qualité) :**
  1. **Autopsie automatique des décrochages (J+7)** : croiser la courbe de rétention YouTube Studio avec `regarder.py` pour extraire systématiquement la rafale des **3 secondes précédant chaque chute brusque de rétention** et mettre à jour les recettes Claude.
  2. **Devis automatisé pour les commandes** : passer `regarder.py` sur la vidéo de référence d'un client pour compter les plans, chiffrer les assets réutilisables de `~/videos/assets/` et générer un cahier des charges chiffré en 2 minutes.

---

### 3. Mon rôle (Gemini via `agy`) dans l'usine

* **Où j'apporte une vraie valeur :**
  1. **Perception multimodale native (`.mp4` / `.wav`)** : contrairement à un flux découpé en vignettes fixes + SRT, Gemini traite nativement la vidéo et l'audio continus (rythme réel du montage, énergie de la voix, agressivité ou répétitivité d'une boucle chiptune) (*capacité native des modèles Gemini : sûre*).
  2. **« Red Team » éditoriale et stratégique** : Claude construit les scripts et les outils ; il a un biais d'auto-validation. Je sers d'avocat du diable indépendant sur l'humour des gags, la rigueur scientifique des scripts et les bilans trimestriels.
* **Où je serais du bruit :**
  * Le code des outils Python, le pilotage MCP quotidien d'ArtCraft et l'exécution du montage. Un seul agent doit tenir le volant technique.
* **Règle simple de consultation (« Règle des 3 Portes ») :**
  > Ne m'appeler via `agy` que dans trois cas :
  > 1. **Porte Script (lundi, 5 min)** : classer les 5 idées de la semaine et critiquer le script `episode.toml` de science *avant* d'enregistrer la voix.
  > 2. **Porte Rendu (jeudi, vidéos longues)** : évaluer le `.mp4` final et la miniature face à la concurrence avant publication.
  > 3. **Porte Bilan (M3, M6, M12)** : auditer froidement `~/videos/stats/` pour recommander quel format couper ou accélérer.
