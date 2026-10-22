---
name: video-fantasy
description: Monte un épisode de la série d'aventure fantasy ico-vid (16:9, 60–120 s) dans EffectCraft : générique, titre d'épisode, décor en parallaxe avec brume et particules, narration sous-titrée, carton « à suivre » et signature, à partir d'un pitch validé par l'utilisateur ; aperçus puis rendu. Utiliser quand l'utilisateur parle de la série fantasy, du jeune héros ou d'un nouvel épisode.
---

# Recette : épisode fantasy (modèle « ico-vid · Aventure fantasy »)

## Règles d'écriture

- Série : un héros, un objectif par saison, **un cliffhanger par épisode** (champ `suivant`).
  Relire les épisodes précédents (`ls ~/videos | grep fantasy`, leurs `episode.toml`) pour la continuité.
- Narration courte : 6 à 14 répliques, chacune doit **tenir en 2 lignes de 40 caractères** (≈ 75 car.).
- La 1re réplique commence **après le générique et le titre d'épisode** : `debut = 8` minimum.
- Champs : `serie`, `numero` (« ÉPISODE N »), `titre`, `suivant`. Durée 60–120 s
  (le carton « à suivre » et la signature prennent les 5 dernières secondes).
- Rendu lourd (~1 s/image, ≈ 20–40 min) : prévenir, et ne lancer qu'après validation des aperçus.
- `Heros (a remplacer)` est une silhouette provisoire en attendant les dessins (VectorCraft).

## Méthode (toujours dans cet ordre)

1. **Lire** `~/videos/bible.md` (formats, zones sûres, sous-titres, structure) et
   `~/videos/outils/README.md` (format du fichier d'épisode). Ne pas toucher au code d'EffectCraft.
2. **Écrire le script** à partir de l'idée (règles du format ci-dessus) et le **présenter** :
   tableau `# · qui parle · réplique · durée estimée` + les textes du modèle + durée totale.
   **Attendre la validation avant de monter quoi que ce soit.** Corriger autant de fois que demandé.
3. **Dossier** : `~/videos/<slug>/` (slug = `<format>-NN-mot`, NN = numéro suivant d'après `ls ~/videos`).
   Si le dossier existe déjà, demander avant d'écrire dedans.
4. **Écrire** `~/videos/<slug>/episode.toml`, puis lancer
   `python3 -I ~/videos/outils/monter.py ~/videos/<slug>/episode.toml`.
5. **Lire les alertes** du résumé JSON. Réplique trop longue → la raccourcir (ne pas laisser un
   sous-titre coupé en deux), puis relancer avec `--ecraser` *tant que le projet n'a pas été ouvert
   ni retouché par l'utilisateur*. Toute « ERREUR D'EXPRESSION » doit être corrigée avant d'aller plus loin.
6. **Montrer les 3 aperçus** (`apercu-1..3.png`, les lire avec Read) avec une phrase chacun, et
   demander : valider, ou quoi changer.
7. **Rendu** une fois validé : `monter.py … --rendu` en arrière-plan (Bash `run_in_background`),
   prévenir de la durée (~0,25 s/image sans preset, ~1 s/image en fantasy). Donner le chemin du
   `.mp4` et la copie sur le Bureau.
8. **Journal** : ajouter à `~/videos/ce-qui-m-a-gene.md` toute gêne rencontrée (une ligne, avec le slug).

## Garde-fous

- Jamais d'écrasement sans `--ecraser`, et jamais `--ecraser` sur un projet que l'utilisateur a
  retouché dans l'app : dans ce cas, faire les retouches sur le projet ouvert (outils MCP
  `effectcraft-app`, un seul groupe d'annulation) ou sur une copie.
- Pas de personnages, musiques ou marques sous droits ; tout élément externe va dans `licences/`.
- Mouvements en plus : `[[effets]]` avec `rapide = …` (gratuit au rendu) plutôt que `preset = …`.
- Voix : si l'utilisateur fournit un enregistrement, le mettre dans le dossier, `voix = "…"`, et
  caler `debut`/`fin` des répliques sur ce qu'il indique (ou les écouter dans l'app) ; la bouche du
  sketch suit alors la voix toute seule.

## Exemple d'épisode

```toml
format = "fantasy"
serie = "LA QUÊTE DE TIM"
numero = "ÉPISODE 1"
titre = "La forêt qui parle"
suivant = "Prochain épisode : la grotte"
duree = 60
[[repliques]]
texte = "Tim n'avait jamais quitté son village."
debut = 8
[[repliques]]
texte = "Ce matin-là, la forêt l'appela par son nom."
```
