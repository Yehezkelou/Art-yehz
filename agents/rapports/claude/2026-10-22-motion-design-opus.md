# Rapport : méthode « Guide OPUS — motion design avec Claude »

- **Mission** : `agents/missions/2026-10-22-motion-design-opus.md`
- **Agent** : Claude `general-purpose`, 2026-10-22, Windows 11
- **Source étudiée** : guide de @cassandre.rollet (`a-trier/guide-opus/guide.txt`, PDF à côté). Les idées sont résumées et reformulées ici ; aucun paragraphe n'est recopié.
- **Écrit** : ce rapport et le brouillon `a-trier/guide-opus/brouillon-skill-motion/SKILL.md`. Rien n'est installé, rien n'est commité.

## Résultat

### La méthode en 10 lignes
1. Une animation est une page web qui bouge : Claude écrit du HTML/CSS minuté, Hyperframes le filme (Chrome sans fenêtre) et le passe dans FFmpeg pour en faire un MP4.
2. video-use fait le dérushage : il coupe les blancs et les hésitations et pose des sous-titres simples. La transcription passe par ElevenLabs.
3. Règle de base : on valide les coupes d'abord, l'animation vient ensuite.
4. Quatre étapes : rush propre (une idée) → transcription mot à mot → storyboard minuté (3–4 moments forts, validé avant de construire) → construction → 3 retouches maximum → export.
5. Une demande se décrit avec 5 éléments : quoi, quand (sur quel mot), où, style, mouvement.
6. Une « phrase de style » fixe la DA : 2–3 couleurs, 2 polices, le type de mouvement et ce qui est interdit. On la rappelle à chaque demande.
7. Repères de durée : grand titre ~1 s, mot dynamique ~0,3 s, carte 0,6–0,9 s, texte à lire ≥ 1,5 s.
8. Le goût défendu : une seule chose bouge à la fois, 2 neutres et 1 accent, des mouvements doux, pas de rebond ni de flash. Les preuves sont « montrées » en 3 à 5 pleins écrans, chacun avec sa texture.
9. Accroche très forte au début (formule sur 7 s). On regarde une planche contact de 10–15 images avant chaque rendu complet.
10. Son : 5 à 6 effets discrets calés sur l'image, environ 8 dB sous la voix, mixage final vers −14 LUFS.

### Recommandation chiffrée
| | Quoi | Coût | Décision proposée |
|---|---|---|---|
| **Adopter tout de suite (0 install, 0 code)** | 6 idées de méthode : colonne « À l'écran » dans le tableau du script ; demande en 5 éléments traduite en `[[effets]]` ; rappel de la DA de la bible à chaque demande ; limite de 3 à 4 moments forts ; 3 allers-retours de retouche au plus ; contrôle « chaque élément est invisible hors de son moment » sur les aperçus | réécriture des recettes, ~1 h | oui : c'est le brouillon de skill |
| **Déjà au plan, à faire passer devant** | planche contact 16 images (`plans/plan-2.3.txt:806`, journal n° 3) ; `.srt` FilmCraft lu par `monter.py` (`plans/plan-2.3.txt:218,805`, journal n° 2) | code dans monter.py v2, prévu | oui, mais seulement sur une 2ᵉ vraie vidéo (gênes n° 2 et 3 vues sur sketch-01 seulement) |
| **À reprendre plus tard, sur gêne** | chiffre animé (compteur) et courbe qui se trace en vulga | faisable dans EffectCraft (expressions sur le texte source, calques de forme) ; 0 logiciel | quand une vidéo de science le demande |
| **Laisser : Hyperframes** | moteur HTML → MP4 | Node 22, Chrome/Puppeteer, npm ; télémétrie PostHog active par défaut | **non installé** ; option à rouvrir seulement si EffectCraft échoue 2 fois sur un même type d'élément (graphique, interface) |
| **Laisser : video-use** | dérushage + sous-titres | clé ElevenLabs payante ; envoie l'audio chez ElevenLabs | **non** : contraire à « rien ne sort de la machine », et FilmCraft fait déjà la même chose en local |
| **Refuser** | flou, verre dépoli, fondus en semi-transparence en pixel ; vrais logos, fausses interfaces TikTok/iPhone ; sons Pixabay sans manifeste | — | non |

En résumé : on garde **6 idées de méthode** et **2 outils déjà prévus au plan** (planche contact, `.srt`). On n'installe **aucun des 2 logiciels**, et on écarte **5 effets du guide** (verre dépoli, passage du flou au net, vrai logo qui explose, fausse feuille de commentaires, détourage d'une personne).

### Tableau : technique du guide → ico-vid
| Technique du guide (guide.txt) | Équivalent ico-vid existant | Manque | Conflit avec une règle |
|---|---|---|---|
| HTML → MP4 via Chrome (l.15-18, 32-34, 237) | EffectCraft headless : `monter.py:326` (`render … h264`), modèles `modeles/*.ecproj` | — | Rendu navigateur lissé (anticrénelage, sous-pixels) : contraire à « échelles entières, positions arrondies » (`CLAUDE.md:26`) sans réglages stricts |
| Dérushage : coupe des blancs et des « euh » (l.134-137, 191-199) | FilmCraft `transcript.removeFillers` / `transcript.removePauses` (`logiciel/filmcraft/docs/transcripts.md:33-34`) | pas encore compilé avec l'option `whisper` (`plans/plan-2.3.txt:999`) | video-use envoie l'audio à ElevenLabs : « rien ne sort de la machine » (`CLAUDE.md:28`) ; inutile pour les gags sans voix (D4, `plans/decisions.md:8`) |
| Transcription mot à mot avant d'animer (l.205, 221, 416) | FilmCraft `transcript.generate` en local, Whisper (`transcripts.md:25`, `:69-71`) ; la voix VoiceStudio part d'un texte connu (D4 bis, `decisions.md:9`) | `monter.py` estime à 2,8 mots/s (`monter.py:42`, `timing` l.90) et ne lit pas encore de `.srt` | — |
| Storyboard minuté validé avant de construire (l.204-222, 418) | Étape 2 des recettes : tableau du script validé avant de monter (`.claude/skills/video-pixel/SKILL.md:23-25`) | colonne « À l'écran » (quel élément, quand, où) | — |
| Élément minuté `data-start` / `data-duration` (l.237) | `[[effets]]` + `temps` (marqueurs) ; sous-titres découpés avec point d'entrée et de sortie (`monter.py:251`) | — | — |
| Demande en 5 ingrédients (l.282-307) | `[[effets]]` : calque (où), `temps` (quand), `rapide` (mouvement) (`outils/README.md:216-221`) | pas de champ « style » : il est figé par le modèle et la bible | — |
| Phrase de style / DA écrite une fois (l.312-321, 638-649) | `bible.md` (palettes l.50, polices l.61-78), palette `bible/palette/ico-pixel-32` | — | La DA « luxe » du guide (ivoire, verre, Didot, 60 i/s) est l'opposé de la bible : on garde la bible |
| Titre d'accroche, révélation par masque (l.340-341) | Titre du modèle (`TXT Titre`, `monter.py:195`) ; caches de calque dans EffectCraft (`logiciel/effectcraft/docs/architecture.md:87,129`) | aucun `rapide` « révélation par cache » | En pixel : un cache doit avancer par paliers entiers, sans bord adouci |
| Sous-titres mot par mot (l.344-345, 394) | `presets/ico - Sous-titre mot par mot surligne.jsonl` (`presets/README.md`, § « Sous-titres mot par mot ») ; pop de la bible (`bible.md:78`) | calage mot à mot sur la vraie voix (`.srt`) | Italique fin : contraire aux polices de la bible (Montserrat ExtraBold / Press Start 2P) |
| Texte derrière le sujet (détourage) (l.348, 538-543) | Pas de détourage à faire : héros et décor sont déjà des calques séparés, il suffit de placer le texte entre les deux | — | Pas de face caméra dans ico-vid (D3, D4 bis) ; détourage d'une vidéo réelle hors sujet |
| Widget réaliste « verre dépoli », capture flottante (l.351-352, 366-367) | Cadre « schéma » du modèle vulga (`outils/README.md:231`) | icônes simples (journal n° 26, `ce-qui-m-a-gene.md:35`, 1 seule vidéo) | **Flou + semi-transparence** (`CLAUDE.md:26`) ; imitation d'interfaces de marque (iPhone, TradingView) |
| Chiffre / compteur animé, courbe (l.355, 550-554) | Expressions sur le texte source d'EffectCraft (`logiciel/effectcraft/docs/agents.md:558`) | aucun `rapide` « compteur » ; aucune gêne au journal | En pixel, le compteur doit sauter par valeurs entières à 12 i/s |
| Zoom doux sur la punchline (l.358) | `rapide = "zoom"` au marqueur (`outils/rapides.py:21`) ; zoom de la chute du sketch, réglé par le curseur « Temps de la chute » (`monter.py:193`) | — | En pixel : zoom par paliers entiers seulement (×1 → ×2), pas de zoom continu |
| Transition de chapitre en fondu (l.362) | presets `ico - Transition fondu au noir / volet / iris` (`presets/README.md`) ; `rapide = "fondu"` (`rapides.py:37`) | — | Fondu = semi-transparence : interdit en pixel (volet ou iris à bord net à la place) |
| Durées repères (l.386-401) | Pop 0,22 s (`bible.md:78`) ; ≥ 1,2 s par réplique (`monter.py:97`) ; structure (`bible.md:44-49`) | pas de minimum de 1,5 s pour un texte à lire (question, récap, conclusion) | — |
| « Pas de rebond, pas de secousse » (l.406-408, 662) | Le contraire : `rapides.py:17` (secousse), `:32` (rebond), structure comique de la bible (`bible.md:46`) | — | Choix de style opposé, voulu pour l'humour et le rétro : la bible prime |
| Peu de couleurs : 2 neutres + 1 accent (l.414, 659) | 6 couleurs par série (`bible.md:50-59`), palette ico-pixel-32 | — | Compatible (sous-ensemble de la palette) |
| Zones cachées : rien dans le bas ≈ 20 % ni à droite (l.423) | Zones sûres plus précises : bas 15 % interdit, colonne des boutons x 940–1080 (`bible.md:26,28`), calque guide | — | — (la bible est plus précise) |
| Export 1080×1920 en 30 ou 60 i/s (l.428) | 24 i/s, et 12 i/s en pixel (`bible.md:16,18`) | — | 60 i/s contraire à la bible et à l'animation « en 2s » |
| Accroche en 7 s, pleins écrans sur les preuves (l.476-525) | Accroche avant 2 s (`bible.md:44`) ; une idée par vidéo (`bible.md:45`) | — | Plein écran « éclair » de moins d'une seconde : à éviter en pixel à 12 i/s (moins de 12 images) |
| Logo réel qui explose (l.506-507, 538-544) | — | — | Marques sous droits interdites (`.claude/skills/video-pixel/SKILL.md:45`) |
| CTA : fausse feuille de commentaires TikTok (l.558-563) | Signature de fin (`bible.md:86-90`) | — | Imitation de l'interface d'une plateforme : risqué, et « pas de forme reprise » |
| Planche contact 10–15 images avant le rendu (l.569-571, 649, 684) | 3 aperçus PNG (`monter.py:288-297`, `:371-375`) ; contrôle des expressions à chaque image clé (`monter.py:360-362`) | **planche contact 16 images** (journal n° 3, `ce-qui-m-a-gene.md:11` ; prévue `plans/plan-2.3.txt:806`) | — |
| « Chaque élément est invisible hors de son moment » (l.681-682) | Points d'entrée et de sortie posés par `monter.py` (`:225`, `:251`) | aucun contrôle automatique : à regarder sur la planche | — |
| Sons Pixabay (l.584-608) | SoundCraft / jsfxr (`plans/plan-2.3.txt:564`), Freesound CC0 (`:568`), manifeste `assets/manifeste.toml` | jingle encore ouvert (`ce-qui-m-a-gene.md`, « Décisions à prendre ») | La licence Pixabay n'est pas du CC0 : tout fichier passe au manifeste (`CLAUDE.md:25`) |
| Mixage : effets ~8 dB sous la voix, −14 LUFS (l.612-618) | Cible voix −16 LUFS (`plans/plan-2.3.txt:1009`) ; mesure BS.1770 prévue dans regarder.py (`:1086`) | mesure LUFS pas encore codée | — (cible à fixer par @yehz) |
| Itération : une retouche à la fois, 3 allers-retours au plus (l.248-256) | Étapes 5-6 des recettes, `--ecraser` avec copie de sauvegarde (`outils/README.md:181-183`) | limite des 3 tours non écrite | — |

## Preuves : licences et sorties réseau

### Hyperframes (`github.com/heygen-com/hyperframes`)
- **Licence** : Apache 2.0, « Copyright 2026 HeyGen, Inc. ». Lu dans https://raw.githubusercontent.com/heygen-com/hyperframes/main/LICENSE. Compatible avec un usage local.
- **Prérequis** (README) : Node.js 22+, FFmpeg, Chrome sans fenêtre piloté par Puppeteer (paquet `@hyperframes/engine`).
- **Télémétrie : active par défaut.**
  - `packages/cli/src/telemetry/config.ts` : `telemetryEnabled: true` par défaut (~l. 355) ; configuration dans `~/.hyperframes/config.json` (l. 15-16).
  - `packages/cli/src/telemetry/transport.ts` : `POSTHOG_HOST = "https://us.i.posthog.com"` (~l. 10) ; envoi par `fetch(\`${POSTHOG_HOST}/batch/\`)` (~l. 139), plus un envoi à la sortie depuis un processus enfant détaché (~l. 178).
  - `packages/cli/src/telemetry/client.ts` (~l. 65-73) : les événements contiennent l'OS, le CPU, la RAM, la version de Node, la présence de CI, Docker ou WSL, l'agent détecté et un identifiant d'installation.
  - Pour la couper : `HYPERFRAMES_NO_TELEMETRY=1` ou `DO_NOT_TRACK=1` (`packages/cli/src/telemetry/policy.ts`, ~l. 32-35).
- **Autres sorties réseau** :
  - Modèles Whisper téléchargés depuis `huggingface.co/ggerganov/whisper.cpp` (`packages/cli/src/whisper/manager.ts`, ~l. 43). La transcription elle-même tourne en local.
  - Modèle de détourage `u2net_human_seg.onnx` téléchargé depuis les releases GitHub de `danielgatis/rembg` (`packages/cli/src/background-removal/manager.ts`, ~l. 8-13). L'inférence ONNX tourne en local.
  - Les exemples de composition chargent GSAP depuis `cdn.jsdelivr.net`.
  - `.env.example` propose une clé `GEMINI_API_KEY` facultative (légende d'images lors d'une capture de site).
  - Le dépôt contient aussi `cloud/`, `auth/`, `tts/` et `@hyperframes/aws-lambda` (rendu dans le cloud, facultatif). Ces dossiers n'ont pas été lus en détail.
- **Installation proposée par le guide** : `npx skills add … -g` (guide.txt:140), qui installe des skills tiers globalement dans Claude. À ne pas faire sans relecture complète (règle « fichiers que Claude n'a pas lus »).

### video-use (`github.com/browser-use/video-use`)
- **Licence** : MIT, « Copyright (c) 2026 Browser Use ». Lu dans https://raw.githubusercontent.com/browser-use/video-use/main/LICENSE.
- **Sortie réseau obligatoire** : `helpers/transcribe.py` envoie l'audio à ElevenLabs.
  - Adresse : `SCRIBE_URL = "https://api.elevenlabs.io/v1/speech-to-text"` (~l. 33).
  - La clé `ELEVENLABS_API_KEY` est lue dans `.env` ou dans l'environnement (~l. 43-45), puis envoyée dans l'en-tête `xi-api-key` (~l. 101).
  - `requests.post(…, files={"file": (…, "audio/wav")})` (~l. 99-105) envoie le WAV mono 16 kHz extrait par ffmpeg (~l. 72-78), avec le modèle `scribe_v1` (~l. 88) et la diarisation activée.
- Autres points :
  - `yt-dlp` est facultatif.
  - Les dépendances (`pyproject.toml`) sont `requests`, `librosa`, `matplotlib`, `pillow`, `numpy`.
  - L'installation se fait par un lien symbolique dans `~/.claude/skills/video-use`, avec la clé stockée dans `.env` à la racine du skill. C'est un secret placé dans un dossier de skills, à ne jamais faire dans le dépôt public.
  - Aucune télémétrie n'est vue dans le README ni dans `transcribe.py`.

### Journal des gênes (règle d'or)
Aucune gêne du journal ne réclame un moteur HTML ou un dérusheur. Celles qui s'en approchent n'ont été vues que sur **une** vidéo :
- n° 2 (sous-titres à la main, sketch-01) : réglée par FilmCraft (`.srt`), déjà décidé (D14, `decisions.md:16`) ;
- n° 3 (une image par appel, sketch-01) : réglée par la planche contact prévue ;
- n° 26 (cadre schéma vide, vulga-01-gps) : icônes, pas un logiciel.

La règle d'or (`CLAUDE.md:24`) ne justifie donc l'ajout ni d'Hyperframes ni de video-use.

### Commandes lancées
- `grep -n … outils/monter.py`, `sed -n 90,143p` et `sed -n 300,381p` pour les numéros de ligne ci-dessus.
- `grep -n "removeFillers\|removePauses" logiciel/filmcraft/docs/transcripts.md` → l. 33-34.
- `pdftoppm -png -r 50 -f 10 -l 10` sur le PDF (page 10, l'étude de cas), dans le dossier scratch hors du dépôt. Elle montre un vrai logo After Effects en plein écran, ce qui confirme le risque de marque.

## Ce qui reste incertain
- Les numéros de ligne des fichiers GitHub sont **approximatifs** : ils viennent d'une lecture web, sans clone. La branche lue est `main` du 22/10/2026, et le code peut changer.
- Hyperframes : `cloud/`, `auth/`, `tts/`, `media-use/` et la « HeyGen » citée par le skill média n'ont pas été audités. D'autres appels réseau peuvent exister (TTS hébergé, connexion HeyGen).
- La faisabilité dans EffectCraft du compteur (expression sur le texte source) et de la révélation par cache est **déduite de la documentation**, pas testée par un rendu.
- La cible de volume (−14 LUFS mixage final dans le guide, −16 LUFS pour la voix dans le plan) reste à fixer par @yehz.
- Gemini (essaim) donne un avis indépendant en parallèle : à comparer avant d'intégrer quoi que ce soit.
