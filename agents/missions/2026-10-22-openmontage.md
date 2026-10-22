# Mission : évaluer OpenMontage (guide @bencodezero)

- **Date** : 2026-10-22
- **Agents** : Claude `general-purpose` (analyse + brouillon de skill) et Gemini `essaim` (avis contradictoire + recherche), en parallèle
- **Mode** : Claude écrit seulement les fichiers listés ; Gemini n'écrit rien (son rapport est archivé par pilote_agy.py)
- **Étape du plan** : hors plan, demandé par @yehz le 22/10/2026

## But
Comprendre OpenMontage (github.com/calesthio/OpenMontage) tel que présenté par le guide, et dire ce que l'usine ico-vid peut en tirer : ce qu'on a déjà (recettes `video-*`, monter.py, EffectCraft, VoiceStudio, `watch`, agents et portes Claude/Gemini), ce qui manque, ce qui contredit nos règles. Produire un **brouillon** de skill adapté à ico-vid si une partie mérite d'être reprise. Rien n'est installé : on propose, @yehz décide.

## Contexte à lire
- `a-trier/guide-video/guide.txt` (texte du guide, 8 pages) ; le PDF est à côté (`video.pdf`) pour les images
- `CLAUDE.md`, `plans/decisions.md` (D15 : décision sur le guide motion précédent), `bible.md`, `ce-qui-m-a-gene.md`, `agents/README.md`
- Analyse précédente du même genre, pour ne pas refaire le travail : `agents/rapports/claude/2026-10-22-motion-design-opus.md`
- Le dépôt OpenMontage (lecture web seulement : README, LICENSE, code des appels réseau, skills/agents qu'il installe)

## Points à trancher
- **Licence AGPL-3.0** : qu'implique-t-elle si on copie du code ou des skills dans notre dépôt public, ou si on l'utilise seulement en local ? (preuve : texte de la licence)
- **Images et vidéos générées par IA** : quels services, quels coûts (le guide annonce 0,24 $ pour 15 s), quelles licences des sorties — compatibles avec « pas de licence, pas d'usage » (`assets/manifeste.toml`) et la bible pixel (palette ico-pixel-32, pas de flou) ?
- **Ce qui sort de la machine** : clés API demandées, services appelés, télémétrie.
- **Recoupements** avec ce qu'on a déjà (cycle mission → rapport → vérification, portes de validation, recettes) : quelles idées d'organisation ou de méthode valent d'être reprises, réécrites.
- **Règle d'or** : une gêne du journal y correspond-elle ?

## Règles de fond
- Idées reprises, forme réécrite : ne copier aucun paragraphe du guide ni de code AGPL.
- Ne rien installer, ne rien cloner dans le dépôt, ne créer aucun compte, ne saisir aucune clé.

## Fichiers autorisés en écriture (Claude seulement)
- `agents/rapports/claude/2026-10-22-openmontage.md` (rapport)
- `a-trier/guide-video/brouillon-skill/SKILL.md` (brouillon, hors git), seulement si une partie mérite d'être reprise

## Critère de fin
Rapport : résumé en 10 lignes max ; tableau « élément d'OpenMontage → équivalent ico-vid (fichier:ligne) / manque / conflit avec une règle » ; licence, coûts et sorties réseau avec preuves (URL, lignes de code) ; recommandation nette (adopter / transposer / ignorer, par élément).

## Format du rapport
Résultat d'abord, puis preuves (chemin:ligne, URL, commande + sortie), puis ce qui reste incertain. Fins de ligne LF.
