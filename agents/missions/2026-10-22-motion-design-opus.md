# Mission : apprendre la méthode « Guide OPUS — motion design avec Claude »

- **Date** : 2026-10-22
- **Agents** : Claude `general-purpose` (analyse + brouillon de skill) et Gemini `essaim` (avis contradictoire + recherche), en parallèle
- **Mode** : Claude écrit seulement les fichiers listés ; Gemini n'écrit rien (son rapport est archivé par pilote_agy.py)
- **Étape du plan** : hors plan, demandé par @yehz le 22/10/2026

## But
Comprendre la méthode du guide (Claude Code + Hyperframes + video-use) et dire comment l'usine ico-vid peut en tirer parti : ce qu'on a déjà (EffectCraft, monter.py, presets, FilmCraft), ce qui manque, ce qui contredit nos règles. Produire un **brouillon** de skill adapté à ico-vid. Rien n'est installé : on propose, @yehz décide.

## Contexte à lire
- `a-trier/guide-opus/guide.txt` (texte du guide, 17 pages) ; le PDF est à côté (`Guide-OPUS-Motion-Design_v2.pdf`) pour les images
- `CLAUDE.md`, `plans/decisions.md`, `bible.md`, `ce-qui-m-a-gene.md`, `outils/README.md`
- Recettes existantes : `.claude/skills/video-*/SKILL.md`
- Dépôts cités par le guide (lecture web seulement) : `github.com/heygen-com/hyperframes`, `github.com/browser-use/video-use`

## Règles de fond
- **Idées reprises, forme réécrite** : le guide est l'œuvre de @cassandre.rollet. Ne copier aucun paragraphe ; reformuler, citer la source.
- Règles pixel de la bible : échelles entières, palette ico-pixel-32, **pas de flou ni de semi-transparence** (le motion design classique en use beaucoup : le signaler).
- Règle d'or : on n'ajoute un logiciel que si son absence a gêné sur 2 vraies vidéos. Vérifier dans le journal si une gêne y correspond.
- Licences des deux dépôts à vérifier (fichier LICENSE réel), ainsi que ce qu'ils envoient hors de la machine (API, télémétrie, clés).

## Fichiers autorisés en écriture (Claude seulement)
- `agents/rapports/claude/2026-10-22-motion-design-opus.md` (rapport)
- `a-trier/guide-opus/brouillon-skill-motion/SKILL.md` (brouillon, hors git, pas dans `.claude/skills/`)

## Critère de fin
- Rapport : résumé de la méthode en 10 lignes max ; tableau « technique du guide → équivalent ico-vid existant (fichier:ligne) / manque / conflit avec une règle » ; licences et sorties réseau de Hyperframes et video-use (preuves : URL du LICENSE, lignes de code) ; recommandation chiffrée (quoi adopter, quoi laisser).
- Brouillon de skill au format `.claude/skills/*/SKILL.md` (frontmatter `name`, `description`), qui s'appuie d'abord sur EffectCraft/monter.py et ne mentionne Hyperframes que comme option à décider.

## Format du rapport
Résultat d'abord, puis preuves (chemin:ligne, URL, commande + sortie), puis ce qui reste incertain.
