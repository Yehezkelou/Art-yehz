---
name: video-pixel
description: Monte une vidéo pixel art ico-vid (9:16, 10–30 s, comp 270×480 agrandie ×4 en pixels nets, 12 i/s) dans EffectCraft à partir d'une idée : gag ou mini-histoire façon jeu vidéo rétro, script validé, sous-titres Press Start 2P, sauts/dégâts au marqueur, aperçus puis rendu. Utiliser quand l'utilisateur demande du pixel art, du rétro ou un gag jeu vidéo.
---

# Recette : pixel art (modèle « ico-vid · Pixel art »)

## Règles d'écriture

- Gag court en 2–4 temps, lisible **sans le son** ; ambiance jeu vidéo (saut, pièce, dégâts, game over).
- Sous-titres en **MAJUSCULES**, police pixel : chaque réplique doit **tenir en 2 lignes de 12 caractères** (≈ 20 car.).
- `titre` ≤ 12 caractères (police pixel). Durée 10–30 s.
- Mouvements : `[[effets]]` avec `comp = "PIXEL 270x480"`, `calque = "Heros"` et
  `rapide = "pixel-saut"` ou `"pixel-degats"` + `temps = […]` (un marqueur par saut / coup).
  `pixel-saut` remplace le saut automatique du héros (toutes les 2 s) par des sauts aux marqueurs.
- Règle d'or du pixel art : positions entières, agrandissements entiers, pas de rotation.
- Sprites et décors du commerce interdits ; packs CC0 (Kenney, OpenGameArt) avec licence notée.

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
format = "pixel"
titre = "LE SAUT"
[[repliques]]
texte = "JE PEUX SAUTER"
[[repliques]]
texte = "OUPS"
chute = true
[[effets]]
comp = "PIXEL 270x480"
calque = "Heros"
rapide = "pixel-saut"
temps = [2.0, 4.5]
[[effets]]
comp = "PIXEL 270x480"
calque = "Heros"
rapide = "pixel-degats"
temps = [5.2]
```
