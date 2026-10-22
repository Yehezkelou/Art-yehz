# Mission : exploiter la bibliothèque « awesome-opus5-5-videos »

- **Date** : 2026-10-22
- **Agents** : Claude `general-purpose` (tri + brouillon) et Gemini `essaim` (avis contradictoire), en parallèle
- **Mode** : Claude écrit seulement les fichiers listés ; Gemini n'écrit rien (son rapport est archivé par pilote_agy.py)
- **Étape du plan** : hors plan, demandé par @yehz le 22/10/2026

## But
La bibliothèque (github.com/yihui-dev/awesome-opus5-5-videos, commit 92aee2f, MIT) rassemble 703 prompts de vidéos animées que des créateurs ont fait écrire en code (HTML, Canvas, SVG, Three.js) par Claude Opus 5.5. Copie locale : `a-trier/awesome-opus/` (`data/videos.json` = tout en un fichier ; `prompts/*.md` = une fiche par vidéo). Dire ce que l'usine ico-vid peut en tirer, sans rien installer.

## Questions
1. **Idées pour nos 4 formats** (vulga 9:16 45–90 s, sketch, pixel art 270×480 ×4 à 12 i/s, fantasy 16:9) : parmi les ~116 explainers, ~21 prompts pixel, rétro et fantasy, retenir 10 à 15 concepts réellement transposables, chacun réécrit en une idée d'épisode ico-vid (format, accroche, ce qu'on montre). Jamais une copie : idée reprise, forme réécrite, auteur d'origine cité (slug + compte).
2. **Façon d'écrire les prompts** : quelles régularités des prompts qui marchent (structure, contraintes « un seul fichier », synchronisation son/image, `?t=` pour sauter à un instant, durée, style) valent d'être reprises dans nos recettes `.claude/skills/video-*` ou dans notre façon de demander un `episode.toml` ?
3. **Voie « Canvas 2D → vidéo »** : un Canvas sans lissage (`imageSmoothingEnabled = false`, coordonnées entières) peut donner du pixel art exact, contrairement au DOM/CSS refusé en D15. Évaluer honnêtement si cela ouvre une voie utile à côté d'EffectCraft (ce qu'il faudrait pour capturer en MP4, coûts, conflit avec D15 et la règle d'or), sans rien installer.
4. **Droits** : la licence MIT couvre la compilation ; les prompts et vidéos appartiennent à leurs auteurs. Que peut-on en faire (s'inspirer, citer) et que ne doit-on pas faire (copier un prompt dans le dépôt public, refaire une vidéo à l'identique) ?

## Contexte à lire
- `CLAUDE.md`, `plans/decisions.md` (D15), `bible.md`, `ce-qui-m-a-gene.md`, recettes `.claude/skills/video-*/SKILL.md`
- Analyses précédentes, pour ne pas refaire le travail : `agents/rapports/claude/2026-10-22-motion-design-opus.md`, `agents/rapports/claude/2026-10-22-openmontage.md`

## Règles de fond
- Ne rien installer ni exécuter des prompts ; ne pas ouvrir les liens x.com ni skillry.dev (traceurs `utm_*`) sauf nécessité, et alors sans s'identifier.
- Ne copier aucun prompt entier dans un fichier suivi par git.

## Fichiers autorisés en écriture (Claude seulement)
- `agents/rapports/claude/2026-10-22-awesome-opus-videos.md` (rapport, LF)
- `a-trier/awesome-opus/idees-ico-vid.md` (liste d'idées d'épisodes, hors git, LF)

## Critère de fin
Rapport : réponse aux 4 questions ; tableau des 10–15 idées (format · idée ico-vid réécrite · source slug/auteur · ce qu'il faudrait de neuf) ; liste des régularités de prompts à reprendre avec l'endroit exact où les mettre (fichier:section) ; verdict sur la voie Canvas.

## Format du rapport
Résultat d'abord, puis preuves (chemin:ligne, slug), puis ce qui reste incertain.
