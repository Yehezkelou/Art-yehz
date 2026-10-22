# Rapport : OpenMontage (guide @bencodezero)

- **Mission** : `agents/missions/2026-10-22-openmontage.md`
- **Agent** : Claude `general-purpose`, 2026-10-22, Windows 11
- **Sources** : `a-trier/guide-video/guide.txt` (8 pages) ; dépôt `github.com/calesthio/OpenMontage`, branche `main`, commit `c8066452325cb57c8fc1ba8c2a71b6e8842e6b65` (lu le 22/10/2026, alors que le guide a audité le commit `9327439` du 03/10). Lecture web uniquement : 249 fichiers texte (`tools/`, `lib/`, `backlot/`, `skills/meta/`, `pipeline_defs/`, `LICENSE`…) ont été téléchargés en brut dans le dossier temporaire de la session, hors du dépôt, pour y faire des `grep`. Rien n'a été exécuté ni installé, et rien n'a été cloné dans le dépôt.
- **Écrit** : ce rapport, plus le brouillon `a-trier/guide-video/brouillon-skill/SKILL.md` (ignoré par git, `.gitignore:16`). Rien n'est commité.

## Résultat

### Résumé en 10 lignes
1. OpenMontage n'est pas un logiciel de montage. C'est un ensemble de consignes (Markdown + YAML) et d'outils Python : l'agent de code (Claude Code…) sert lui-même d'orchestrateur, et le rendu passe par Remotion, HyperFrames ou FFmpeg.
2. Son déroulé (recherche → proposition → script → plan des scènes → médias → montage → rendu, avec des validations humaines) **recoupe presque point par point** notre cycle (script validé → aperçus → rendu, portes Gemini).
3. Son intérêt visuel repose sur les images et vidéos générées par IA (fal/FLUX, Google, Kling, Runway…). Cela **contredit** la bible pixel (palette ico-pixel-32, pas de flou), D3 (héros dessinés par @yehz) et le manifeste des licences, qui ne connaît aucune licence « IA ».
4. Licence AGPL-3.0 : on peut l'utiliser en local sans condition, et les vidéos produites ne sont pas touchées. En revanche, **copier du code ou des skills dans notre dépôt public, c'est le « transmettre »**, et l'AGPL s'appliquerait alors à cette partie.
5. Sorties réseau : chaque fournisseur reçoit les textes (prompts) et les fichiers dès que sa clé est dans `.env` (≈ 50 variables). Je n'ai vu aucune télémétrie dans le code Python, mais HyperFrames, appelé par `make setup`, a sa télémétrie PostHog active par défaut (rapport précédent).
6. Le garde-fou de budget est plus mou que ce que dit le guide : en mode `warn`, celui par défaut, dépasser les 10 $ **n'arrête rien**. Une alerte est seulement notée.
7. Aucune gêne du journal ne réclame OpenMontage. La règle d'or ne justifie aucune installation.
8. **Recommandation : ne pas l'installer.** On peut transposer 5 idées de méthode, sans code, dans un brouillon de skill : trace des validations, relecture classée par gravité avec un correctif obligatoire, aucun remplacement en silence, une référence donne 2 ou 3 concepts différents, contrôle « effet diaporama » sur les aperçus.
9. Le reste est déjà chez nous (recettes `video-*`, `monter.py`, `watch`, `pilote_agy.py`, VoiceStudio, `regarder.py` prévu) ou n'a pas sa place : Backlot, choix de fournisseur sur 7 critères, budget en dollars.
10. Le guide se trompe sur un point (l'arrêt à 10 $) et sa liste de clés est en retard sur le dépôt actuel : il cite 4 chemins, le dépôt compte une trentaine de fournisseurs.

### Recommandation par élément
| Élément d'OpenMontage | Décision | Pourquoi |
|---|---|---|
| Installation (`make setup`, Remotion, HyperFrames, Piper) | **Ignorer** | EffectCraft fait le rendu, VoiceStudio fait la voix (D4 bis) et D15 a déjà écarté HyperFrames. Aucune gêne au journal |
| Images et vidéos IA (FLUX, Imagen/Gemini, Kling, Veo…) | **Ignorer (refuser)** | Bible pixel, D3, manifeste ; texte envoyé au fournisseur ; voir § Coûts |
| Banques Pexels, Pixabay, Unsplash | **Ignorer** | Licences « maison », absentes de `verifier_licences.py:19` ; photos hors style pixel |
| Validations humaines « imposées » par un état écrit (`awaiting_human`) | **Transposer** (méthode) | Écrire la validation de @yehz dans le dossier de l'épisode : on sait où on en est, et l'agent ne peut pas « oublier » une porte |
| Relecteur : gravité critique, suggestion, détail ou piste ; correctif obligatoire ; 2 tours au plus | **Transposer** | Utile pour `verificateur` et pour la lecture des rapports Gemini aux portes |
| « Promesse de livraison » et interdiction de remplacer en silence | **Transposer** | Cas vécu : n° 26, le cadre « schéma » restait vide. Il faut s'arrêter et demander, au lieu de livrer moins |
| Analyse d'une vidéo de référence, puis 2 ou 3 concepts différents | **Transposer** | Va dans le sens de « idées reprises, forme réécrite » ; `watch` et `pilote_agy.py --video` existent déjà |
| Score « effet diaporama » (6 critères) | **Transposer en 3 questions** | Le guide note un rendu « diaporama ». À poser sur les aperçus, sans code |
| Relecture après rendu (ffprobe, images à 4 positions, son, sous-titres) | **Déjà prévu** | `regarder.py` (`plans/plan-2.3.txt:1091`) ; ne pas l'avancer sans 2ᵉ gêne |
| Journal de décisions en ajout seul (on ne réécrit pas, on ajoute) | **Déjà là** | `plans/decisions.md:10` (« D8 remplacée par D14 ») |
| Backlot (tableau local `127.0.0.1:4750`) | **Ignorer** | Local et inoffensif (`backlot/__main__.py:85`), mais c'est du code de plus. Aperçus + rapports suffisent |
| Budget en dollars, choix de fournisseur sur 7 critères | **Ignorer** | Notre chaîne coûte 0 $ par vidéo ; à rouvrir seulement si une API payante entre un jour |
| Galerie de demandes (« use only free tools ») | **Ignorer** | Nos recettes `video-*` sont plus précises |

### Tableau : élément d'OpenMontage → ico-vid
| Élément d'OpenMontage (preuve) | Équivalent ico-vid (fichier:ligne) | Manque | Conflit avec une règle |
|---|---|---|---|
| Agent = orchestrateur, consignes en Markdown/YAML (README « Architecture » ; `CLAUDE.md` → `AGENT_GUIDE.md`) | `CLAUDE.md:20-21` ; `agents/README.md:50-75` ; recettes `.claude/skills/video-*/SKILL.md` | — | — |
| Étapes idée → proposition → script → plan des scènes → médias → montage → rendu → publication (`pipeline_defs/animated-explainer.yaml:61-262`) | Recette : lire → script validé → épisode → alertes → aperçus → rendu → journal (`.claude/skills/video-pixel/SKILL.md:19-40`) | pas d'étape « proposition » séparée ; c'est inutile à 0 $ | — |
| Validations `human_approval_default: true` sur proposition, script, plan des scènes, médias, publication (`animated-explainer.yaml:91,128,150,187,262`) | « Attendre la validation avant de monter » (`video-pixel/SKILL.md:26`) ; aperçus à valider (`:34-36`) ; portes Gemini (`plans/plan-2.3.txt:1125-1137`) | aucune trace écrite de la validation de @yehz dans le dossier de l'épisode | — |
| Validation vérifiée par le code : `GATE VIOLATION` si `completed` sans `human_approved=True` (`lib/checkpoint.py:472-493`) | règle écrite seulement | trace de validation (brouillon de skill) | Limite : c'est l'agent lui-même qui écrit `human_approved=True` ; le contrôle empêche l'oubli, pas la triche |
| Reprise après coupure : `checkpoint_<étape>.json`, historique archivé (AGENT_GUIDE « Checkpoint ») | `episode.toml` + `--ecraser` avec copie de sauvegarde (`video-pixel/SKILL.md:31-33`) | — | — |
| Relecteur : critique / suggestion / détail / piste, correctif obligatoire, 2 tours au plus (`skills/meta/reviewer.md:15-17,42-45,85-86`) | `verificateur` (`agents/README.md:62`) ; « rien n'est retenu sans preuve » (`:81`) | pas de gravité ni de correctif obligatoire dans les rapports | — |
| 3 révisions au plus par étape (`animated-explainer.yaml:49`) | 3 allers-retours au plus (`video-pixel/SKILL.md:53`) | — | — |
| Journal de décisions en ajout seul (AGENT_GUIDE « Re-log Changed Decisions ») | `plans/decisions.md:10,17` | — | — |
| Promesse de livraison verrouillée, aucun remplacement en silence (`lib/delivery_promise.py:1-9`) | — | règle « s'arrêter et demander » ; cas vécu, journal n° 26 (`ce-qui-m-a-gene.md:35`) | — |
| Risque « diaporama » en 6 critères, échec si ≥ 4 (`lib/slideshow_risk.py:3-18`) | « 3 ou 4 moments forts » ; « montrer au lieu de dire » (`video-pixel/SKILL.md:47-52`) | 3 questions sur les aperçus (brouillon) | — |
| Relecture après rendu : ffprobe, images à 25 %…, niveaux (`tools/analysis/visual_qa.py:155,210`) | 3 aperçus + alertes JSON (`outils/monter.py:371-377`) ; `regarder.py` prévu (`plans/plan-2.3.txt:806,1091`) | planche contact (journal n° 3, `ce-qui-m-a-gene.md:11`, 1 seule vidéo) | — |
| Référence vidéo → analyse → 2 ou 3 concepts différents (AGENT_GUIDE « Reference Video Entry Point » ; `skills/meta/video-reference-analyst.md`) | skill `watch` (`.claude/skills/watch/SKILL.md:3`) ; sonde audio (`outils/pilote_agy.py:75`) | consigne « 2 ou 3 concepts, jamais une copie » | `tools/analysis/video_downloader.py` (yt-dlp) : `references/` n'entre jamais dans une vidéo (`CLAUDE.md:25`) |
| Images IA : FLUX, Imagen/Gemini, GPT Image, Grok, Seedream… (`tools/graphics/*.py`) | Aseprite + CC0 (D3, `plans/decisions.md:7`) ; `verifier_pixels.py` | icônes simples pour le cadre schéma (n° 26), à dessiner | **Palette et pas de flou** (`CLAUDE.md:26`) ; **manifeste** : aucune licence « IA » acceptée (`outils/verifier_licences.py:19`) ; **rien ne sort** (`CLAUDE.md:28`) |
| Vidéo IA : Kling, Veo, Runway, Seedance, Sora… (`tools/video/*.py`) | EffectCraft + modèles (`outils/monter.py`) | — | idem, plus le coût |
| Voix : ElevenLabs, Google, OpenAI… ; Piper hors ligne (`tools/audio/*.py`) | VoiceStudio, voix inventée (D4 bis, `plans/decisions.md:9`) | — | voix en ligne = texte envoyé au fournisseur |
| Musique Suno / ElevenLabs ; Pixabay, Freesound | SoundCraft / jsfxr, Freesound CC0 (`plans/plan-2.3.txt:564,568`) | jingle encore ouvert (`ce-qui-m-a-gene.md:47`) | Pixabay n'est pas du CC0 (`verifier_licences.py:19`) |
| Banques Pexels / Pixabay / Unsplash (`tools/graphics/pexels_image.py:178`, `pixabay_image.py:191`) | CC0 (Kenney, OpenGameArt) au manifeste | — | licence absente de `verifier_licences.py:19` ; photo réelle hors style |
| Rendu Remotion (React) / HyperFrames (HTML) / FFmpeg | EffectCraft headless (`outils/monter.py:301`, `cli`) | — | D15 (`plans/decisions.md:17`) : HyperFrames non installé |
| Sous-titres trop petits, zone sûre non prise en compte (guide p. 07, test de l'auteur) | Bible : zones (`bible.md:21-30`), sous-titres 72 px ≤ 20 car. (`bible.md:72-76`) ; alertes de longueur dans `monter.py` (journal n° 27) | contrôle de la conclusion vulga (journal n° 31, `ce-qui-m-a-gene.md:40`) | — (chez nous, la bible est plus stricte) |
| Backlot, tableau local (`backlot/__main__.py:71-85`, `.claude/launch.json`) | aperçus PNG + `agents/rapports/` | — | — |
| Budget : 0,50 $ par action, 10 $ au total (`config.yaml:9-14`, `tools/cost_tracker.py:128-153`) | 0 $ : tout est local | — | « Rien ne sort de la machine » : chaque dépense est une sortie |
| 49 skills dans `.claude/skills/` (three.js, remotion, elevenlabs, heygen, faceswap…) | 7 skills ciblées (`.claude/skills/`) | — | `faceswap`, `avatar-video` : contraires à « pas de voix ni de vidéo d'autrui » (`CLAUDE.md:27`) |

## Preuves

### Licence AGPL-3.0
- Le fichier `LICENSE` du commit `c806645` contient le texte complet de la « GNU AFFERO GENERAL PUBLIC LICENSE, Version 3, 19 November 2007 » (l. 1), sans clause ajoutée. Certaines skills tierces ont leur propre licence : `.claude/skills/manimce-best-practices/LICENSE.txt` et `manimgl-best-practices/LICENSE.txt`, non lues.
- **Usage local, sans modification** : § 2, l. 146-147, « unlimited permission to run the unmodified Program ». On peut aussi le modifier et l'utiliser sans le transmettre, sans condition (l. 152-153).
- **Les vidéos produites** : § 2, l. 147-149, la sortie n'est couverte que si son contenu est lui-même une œuvre couverte. Un MP4 rendu n'est pas du code AGPL. Il faut toutefois vérifier séparément la licence de chaque média qui y entre (Remotion, polices, banques).
- **Copier dans notre dépôt public** : la définition de « convey » (l. 87-89) couvre toute propagation qui permet à d'autres de recevoir une copie. Pousser sur un GitHub public, c'est donc transmettre. Une version modifiée transmise doit être placée entière sous AGPL (§ 5 c, l. 210). Un fichier juxtaposé sans lien peut rester un « agrégat » non contaminé (l. 227-231). En revanche, un outil de `outils/` qui importerait du code OpenMontage formerait une œuvre combinée sous AGPL.
- **Réseau** : § 13 (« Remote Network Interaction ») ne joue que si l'on modifie le programme **et** qu'on le rend accessible à des utilisateurs à distance. Ce n'est pas notre cas.
- **Conclusion** : aucune copie de code ni de skill (Markdown compris : les skills font partie du programme). Les idées de méthode, réécrites, ne sont pas protégées. C'est la voie choisie pour le brouillon.
- **Remotion**, la dépendance de rendu, a sa propre licence (`remotion-dev/remotion/LICENSE.md`) : gratuite pour « an individual » et les entreprises de 3 salariés au plus, licence entreprise payante au-delà. @yehz seul entre dans la version gratuite.

### Coûts et licences des sorties IA
- **0,24 $ pour 15 s (guide p. 06)** : c'est cohérent avec le code. `tools/graphics/google_imagen.py:206-208` estime un modèle `gemini-*` à 0,039 $ par image (« ~1290 output tokens per image at $30/1M »). 6 images ≈ 0,234 $, la voix Gemini fait le reste. Imagen 4 : 0,04 $, *fast* 0,02 $, *ultra* 0,06 $ (`:209-213`). Le modèle par défaut est `imagen-4.0-generate-001` (`:129`) ; `gemini-3.1-flash-image` exige un devis (`:202-204`).
- **Galerie** (`PROMPT_GALLERY.md`) : de 0 $ (démos, Remotion seul) à ≈ 0,15–1 $ avec `FAL_KEY` et ≈ 1,50–2,50 $ en « tout activé ». Elle ne dit **rien** de la licence des sorties.
- **Licence des images Gemini** (`ai.google.dev/gemini-api/terms`, « Use of Generated Content ») : Google ne revendique pas la propriété des sorties, mais l'utilisateur en est responsable, et Google peut produire un contenu semblable pour d'autres. En version gratuite, les entrées et les sorties servent à améliorer les produits et peuvent être lues par des humains (« Unpaid Services »). Il faut avoir 18 ans. Dans l'EEE, au Royaume-Uni et en Suisse, une application ne peut être proposée qu'en version payante.
- **Compatibilité avec nos règles** : aucune, à mon avis.
  - (1) `verifier_licences.py:19` n'accepte que `propriétaire, CC0, CC-BY-4.0, CC-BY-3.0, itch-commercial, OFL-1.1`. Une image IA serait en rouge (« licence inconnue »), et lui inventer une catégorie « propriétaire » serait faux : rien ne garantit qu'on ait un droit d'auteur sur une image générée.
  - (2) Une image générée n'est pas tenue à la palette ico-pixel-32 et contient des dégradés et de l'anticrénelage, contraire à `CLAUDE.md:26`. Il faudrait la requantifier et la redessiner, autant la dessiner dans Aseprite.
  - (3) D3 (`plans/decisions.md:7`) : les héros sont dessinés par @yehz ; ce sont les seuls vendables en pack (`plans/plan-2.3.txt:265`).
  - (4) Chaque prompt part chez le fournisseur (`CLAUDE.md:28`).

### Ce qui sort de la machine
- **Clés** : `.env.example` liste environ 50 variables. Exemples : `FAL_KEY`, `GOOGLE_API_KEY`, `OPENAI_API_KEY`, `ELEVENLABS_API_KEY`, `KLING_API_KEY`, `RUNWAY_API_KEY`, `HEYGEN_API_KEY`, `ARK_API_KEY`, `REPLICATE_API_TOKEN`, `HIGGSFIELD_API_KEY/SECRET`, `DASHSCOPE_API_KEY`, `TENCENT_TOKENHUB_API_KEY`, `VOLC_ACCESSKEY/SECRETKEY`, `SUNO_API_KEY`, `PEXELS_API_KEY`, `PIXABAY_API_KEY`, `UNSPLASH_ACCESS_KEY`, `HF_TOKEN`, `AZURE_SPEECH_KEY`, `IDEOGRAM_API_KEY`, `CARTESIA_API_KEY`, `INWORLD_API_KEY`. Le guide n'en cite que 4 groupes : le dépôt a beaucoup grossi depuis l'audit du guide.
- **Hôtes appelés par le code Python** : sortie de `grep -rhoE 'https?://[a-zA-Z0-9._-]+' --include=*.py | sort | uniq -c`, extrait. `queue.fal.run` (12), `fal.run`, `rest.alpha.fal.ai`, `generativelanguage.googleapis.com`, `texttospeech.googleapis.com`, `api.elevenlabs.io`, `api.x.ai`, `api.minimax.io` / `api.minimaxi.com`, `api.heygen.com`, `api.replicate.com`, `api.atlascloud.ai`, `dashscope.aliyuncs.com`, `ark.cn-beijing.volces.com`, `openspeech.bytedance.com`, `api.dev.runwayml.com`, `api.ltx.io`, `api.ideogram.ai`, `api.inworld.ai`, `api.sunoapi.org`, `api.pexels.com`, `api.unsplash.com`, `images-api.nasa.gov`, `api.videvo.net`, ainsi que `huggingface.co` (téléchargement de modèles, `tools/_comfyui/metadata.py:39-68`). Plusieurs fournisseurs sont en Chine (Volcengine, Alibaba, Tencent, MiniMax CN).
- **Télémétrie** :
  - Aucune bibliothèque de mesure d'audience dans `requirements.txt` (pyyaml, pydantic, jsonschema, python-dotenv, Pillow, numpy, requests, google-auth, google-genai, openai, fastapi, uvicorn, watchfiles).
  - `grep -rniE 'telemetr|posthog|sentry|mixpanel|analytics|DO_NOT_TRACK|NO_TELEMETRY'` sur les 249 fichiers ne trouve qu'un commentaire (`tools/base_tool.py:455`, des notes de qualité locales, sans envoi).
  - **Mais** `make setup` lance `npx --yes hyperframes --version` (Makefile, ≈ l. 66), et `tools/video/hyperframes_compose.py` appelle `npx hyperframes` sans régler `HYPERFRAMES_NO_TELEMETRY` ni `DO_NOT_TRACK` (grep vide). Or la télémétrie PostHog d'HyperFrames est active par défaut (`agents/rapports/claude/2026-10-22-motion-design-opus.md:70-74`). L'affirmation du guide « aucun mouchard » ne vaut donc que pour le code d'OpenMontage lui-même.
- **Serveurs locaux** : Backlot sur `127.0.0.1:4750` (`backlot/__main__.py:85`, `uvicorn.run(..., host="127.0.0.1")`), plus un `http.server 4788 --bind 127.0.0.1` (`.claude/launch.json`). Les deux sont locaux.
- **Téléchargements à l'installation** : PyPI, npm (`remotion-composer`, Remotion ^4.0.484), npx HyperFrames, voix Piper (`tools/audio/piper_tts.py:41`), éventuellement Python 3.10 par uv.
- **Budget, ce que dit vraiment le code** : `config.yaml:10` règle `mode: warn`, `total_usd: 10.00`, `single_action_approval_usd: 0.50`. Dans `tools/cost_tracker.py:128-153` :
  - le seuil de 0,50 $ et la « première utilisation payante d'un outil » lèvent `ApprovalRequiredError` (hors mode `observe`) ;
  - le dépassement du budget total ne lève `BudgetExceededError` qu'en mode `cap`. En mode `warn` (par défaut), il ne pose qu'un drapeau `budget_warning`.
  - Le guide (p. 05, « s'arrête à 10 $ ») est donc inexact pour la configuration par défaut.

### Règle d'or (journal des gênes)
| Gêne | Vue sur | Ce qu'OpenMontage y apporterait | Verdict |
|---|---|---|---|
| n° 2, sous-titres à la main (`ce-qui-m-a-gene.md:10`) | sketch-01 | sous-titres FFmpeg/Remotion | déjà réglé par FilmCraft (`plans/plan-2.3.txt:951`, D14) |
| n° 3, une image par appel (`:11`) | sketch-01 | `visual_qa` | planche contact prévue (`plans/plan-2.3.txt:806`) |
| n° 7, pas de voix française (`:15`) | sketch-01 | Piper / API | réglé par VoiceStudio (D4 bis) |
| n° 26, cadre schéma vide (`:35`) | vulga-01-gps | images IA | refusé (pixel, licences) ; c'est l'idée « ne pas livrer moins en silence » qui sert |
| n° 12, 27, 31, débordements de zone sûre | sketch-01, vulga-01-gps | rien (le guide note le même défaut chez OpenMontage) | alertes de `monter.py` |

Aucune gêne vue sur 2 vraies vidéos ne demande OpenMontage : la règle d'or (`CLAUDE.md:24`) ne justifie **aucune installation**. Les 5 idées transposées ne demandent pas de code.

### Commandes lancées (dossier temporaire de session, hors dépôt)
- `curl -sL https://api.github.com/repos/calesthio/OpenMontage/git/trees/main?recursive=1` → sha `c806645…`, `truncated: False`, 2 630 entrées.
- Téléchargement brut de 249 fichiers, ensuite `grep` / `sed -n` sur : `lib/checkpoint.py:465-495`, `lib/slideshow_risk.py:3-18`, `lib/delivery_promise.py:1-9`, `tools/cost_tracker.py:115-160`, `tools/graphics/google_imagen.py:199-215`, `skills/meta/reviewer.md`, `pipeline_defs/animated-explainer.yaml`, `backlot/__main__.py`, `remotion-composer/package.json`.
- `sed -n '/13. Remote/,/14. Revised/p' LICENSE` et `grep -n` sur les l. 87-89, 146-149, 152-153, 210, 227-231.
- WebFetch : README, `.env.example`, `.claude/` (`commands/` : animated-drawing, backlot, ink-art ; `skills/` : 49 dossiers ; `launch.json`), `CLAUDE.md`, `AGENT_GUIDE.md`, `PROMPT_GALLERY.md`, `config.yaml`, `Makefile`, licence Remotion, conditions de l'API Gemini.
- `git check-ignore -v a-trier/guide-video/brouillon-skill/SKILL.md` → `.gitignore:16:a-trier/*`.

## Ce qui reste incertain
- Les numéros de ligne du Makefile et de `.env.example` sont **approximatifs** (lecture web). Ceux de `lib/`, `tools/`, `backlot/` et `LICENSE` viennent d'un `grep` sur les fichiers bruts du commit `c806645` et sont exacts pour ce commit. Le dépôt change vite : la liste des fournisseurs a beaucoup grossi depuis le guide.
- **Télémétrie** : seuls `tools/`, `lib/` et `backlot/` en Python ont été cherchés. Je n'ai lu ni `remotion-composer/src`, ni `ink-theater/`, ni `scripts/`, ni les 49 skills, ni les dépendances transitives npm/PyPI. La télémétrie d'HyperFrames dans la version que tire `npx` vient du rapport précédent ; je ne l'ai pas revérifiée sur la version du jour.
- **Remotion** : je n'ai pas vérifié s'il envoie quelque chose (licence, statistiques).
- **Licences des voix Piper françaises** : non vérifiées (elles varient selon la voix). Sans objet tant que VoiceStudio sert (D4 bis).
- **Juridique** : la lecture de l'AGPL (transmission par dépôt public, agrégat contre œuvre combinée, skills Markdown couvertes) est une interprétation du texte, pas un avis d'avocat. La protection par le droit d'auteur des images générées par IA varie selon les pays. C'est une raison de plus pour ne pas les mettre au manifeste.
- Pages du PDF non regardées en image (le texte suffisait) : la capture de Backlot p. 05 n'est pas décrite ici.
- Gemini (essaim) donne un avis indépendant en parallèle : il faut comparer les deux avant d'intégrer quoi que ce soit, en particulier sur le budget `warn` et sur la télémétrie d'HyperFrames.
