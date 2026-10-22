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

1. **Lire** `bible.md` (formats, zones sûres, sous-titres, structure) et
   `outils/README.md` (format du fichier d'épisode). Ne pas toucher au code d'EffectCraft.
2. **Écrire le script** à partir de l'idée (règles du format ci-dessus) et le **présenter** :
   tableau `# · qui parle · réplique · à l'écran · durée estimée` + les textes du modèle + durée totale.
   La colonne « à l'écran » dit, pour chaque réplique, quel élément apparaît, quand et où (ou « — »).
   Ajouter le **budget de fabrication** : nouveaux assets à dessiner (et ceux repris de `assets/`),
   presets lents éventuels, temps de rendu estimé.
   **Attendre la validation avant de monter quoi que ce soit.** Corriger autant de fois que demandé.
3. **Dossier** : `<slug>/` (slug = `<format>-NN-mot`, NN = numéro suivant d'après `ls` à la racine).
   Si le dossier existe déjà, demander avant d'écrire dedans.
4. **Écrire** `<slug>/episode.toml`, puis lancer
   `python3 -I outils/monter.py <slug>/episode.toml`.
5. **Lire les alertes** du résumé JSON. Réplique trop longue → la raccourcir (ne pas laisser un
   sous-titre coupé en deux), puis relancer avec `--ecraser` *tant que le projet n'a pas été ouvert
   ni retouché par l'utilisateur*. Toute « ERREUR D'EXPRESSION » doit être corrigée avant d'aller plus loin.
6. **Montrer les 3 aperçus** (`apercu-1..3.png`, les lire avec Read) avec une phrase chacun ; vérifier
   au passage que chaque élément n'est visible que pendant son moment (rien qui traîne avant ou après), et
   demander : valider, ou quoi changer.
7. **Rendu** une fois validé : `monter.py … --rendu` en arrière-plan (Bash `run_in_background`),
   prévenir de la durée (~0,25 s/image sans preset, ~1 s/image en fantasy). Donner le chemin du
   `.mp4` et la copie sur le Bureau.
8. **Journal** : ajouter à `ce-qui-m-a-gene.md` toute gêne rencontrée (une ligne, avec le slug).

## Mise en scène

Méthode reprise du guide « motion design avec Claude » (@cassandre.rollet, 2026), réécrite pour
ico-vid ; analyse : `agents/rapports/claude/2026-10-22-motion-design-opus.md`.

- **Montrer au lieu de dire** : quand la voix donne un chiffre, une durée ou une preuve, prévoir
  un élément visuel à ce moment-là (colonne « à l'écran ») plutôt que du texte seul.
- **Chaque demande d'effet en 5 éléments** : quoi (le calque), quand (`temps` ou marqueur), où
  (zone sûre de la bible), style (toujours celui de la bible : palette, polices, pas de flou ni de
  semi-transparence), mouvement (`rapide = …`). Un élément sans l'un des 5 n'est pas prêt.
- **3 ou 4 moments forts au plus** par vidéo (effets en plus du modèle) : au-delà, rien ne ressort.
- **3 allers-retours de retouche au plus** sur les aperçus ; au-delà, revenir au script.
- La bible prime sur le guide : rebonds et secousses restent permis (l'humour en vit), cadences
  de la bible (24 ou 12 i/s), pas de verre dépoli, de fondu en transparence, de vrai logo ni de
  fausse interface d'application.

## Validations et relectures

Méthode tirée de l'analyse d'OpenMontage (décision D16 : idées seulement, rien d'installé ni de
copié) ; détail : `agents/rapports/claude/2026-10-22-openmontage.md`.

- **Trace écrite** : chaque étape présentée à l'utilisateur (script, aperçus, rendu) ajoute une
  ligne à `<slug>/validations.md` : `| date | étape | statut | ce qui est montré |`. On s'arrête
  là ; à sa réponse, statut `validé` ou `à refaire` avec ses mots résumés. Pas de `--rendu` tant que
  script et aperçus ne sont pas `validé`.
- **Relecture classée** (verificateur, portes Gemini, relecture des aperçus) : `bloquant` (faux,
  cassé, hors bible ou hors licence : correctif exact obligatoire, sinon c'est une `piste`),
  `à améliorer`, `détail`, `piste`. Un bloquant trouvé → chercher les autres du même genre.
  **2 tours de relecture au plus**, puis on livre avec les remarques restantes écrites.
- **Ne jamais livrer moins sans le dire** : si un élément promis par la colonne « à l'écran » ne
  peut pas être fait, s'arrêter et proposer 2 options (changer la ligne du script ou fabriquer
  l'élément) ; jamais de remplacement silencieux par du texte seul ou un cadre vide (journal n° 26).
- **Vidéo de référence** (« dans le style de ») : la regarder avec `watch`, en tirer 4–5 lignes
  (structure, rythme, accroche, ressort), puis proposer **2 ou 3 concepts différents** entre eux
  et de la référence. Une idée reprise, jamais la forme ; la référence reste dans `references/`.
- **Est-ce un diaporama ?** Sur les aperçus : se ressemblent-ils tous ? un moment de plus de 3 s
  où rien ne bouge (hors silence voulu) ? plus de la moitié de l'écran en texte là où une image
  suffirait ? Deux « oui » → le dire avec une retouche proposée.

## Garde-fous

- **Accord avant de ralentir** : demander avant d'ajouter un `preset = …` lent (≈ 1 s/image au
  rendu) ou de lancer un rendu estimé à plus de 10 min ; annoncer la durée prévue.
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
