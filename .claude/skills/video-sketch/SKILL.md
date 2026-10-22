---
name: video-sketch
description: Monte un sketch d'humour adulte ico-vid (vertical 9:16, 15–45 s) dans EffectCraft à partir d'une idée : script en 3 temps validé par l'utilisateur, perso rond rigé, sous-titres, secousse et zoom sur la chute, signature, aperçus puis rendu .mp4. Utiliser quand l'utilisateur demande un sketch, une blague ou une vidéo d'humour.
---

# Recette : sketch d'humour (modèle « ico-vid · Sketch humour »)

## Règles d'écriture

- Structure : **situation banale → montée → silence → chute inattendue**. Une seule idée.
- Accroche lisible dans les 2 premières secondes (champ `accroche`, ≤ 22 caractères, propre).
- 3 à 6 répliques ; chacune doit **tenir en 2 lignes de 20 caractères** (≈ 35 caractères au plus, `monter.py` prévient sinon) ; la dernière porte `chute = true`.
- Le gros mot ponctue la chute, pas avant ; jamais dans l'accroche ni le titre (monétisation
  YouTube, diffusion TikTok/Instagram). Proposer une variante « bip » si la chute est très crue.
- Durée 15–45 s ; laisser `debut`/`fin` vides sans voix (minutage auto + 1 s de silence avant la chute).
- `perso` = nom affiché sous le perso au début (court).

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
format = "sketch"
accroche = "MA MÈRE ET LE CLOUD"
perso = "Moi"
[[repliques]]
texte = "Ma mère m'a demandé c'est quoi le cloud."
[[repliques]]
texte = "J'ai dit : l'ordi de quelqu'un d'autre."
[[repliques]]
texte = "Elle : nos photos chez un inconnu ?"
[[repliques]]
texte = "Putain. Elle a compris avant moi."
chute = true
```
