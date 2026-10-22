---
name: video-vulga
description: Monte une vidéo de vulgarisation ico-vid (9:16, 45–90 s : vie, informatique, science) dans EffectCraft : question accrocheuse, 3 points révélés, flèche vers la conclusion, récap en une phrase et sources, à partir d'un script vérifié et validé par l'utilisateur ; aperçus puis rendu. Utiliser quand l'utilisateur veut expliquer un sujet, faire un explainer ou de la vulgarisation.
---

# Recette : vulgarisation (modèle « ico-vid · Vulgarisation »)

## Règles d'écriture

- Structure : **question accrocheuse → analogie du quotidien → 3 points → récap en une phrase**.
- **Vérifier les faits** avant de proposer le script ; donner 1–2 sources fiables dans `sources`
  (« Sources : … », ≤ 40 caractères) et signaler à l'utilisateur ce qui reste incertain.
- `question` ≤ 22 caractères pour la taille pleine (au-delà, `monter.py` la réduit ; 30 au plus) ; `points` : 3 au plus, ≤ 26 caractères chacun ; `conclusion` ≤ 12 ;
  `recap` en 2 lignes (`\n`), ≤ 22 caractères par ligne.
- Répliques (la voix off) : chacune doit tenir en 2 lignes de 20 caractères (≈ 35 car.) ; caler `points_temps` sur le moment où chaque
  point est dit (sinon 3 / 7 / 11 s) et `fleche_temps` sur la conclusion.
- Un élément à la fois à l'écran : les textes apparaissent quand la voix les dit.

## Méthode (toujours dans cet ordre)

1. **Lire** `bible.md` (formats, zones sûres, sous-titres, structure) et
   `outils/README.md` (format du fichier d'épisode). Ne pas toucher au code d'EffectCraft.
2. **Écrire le script** à partir de l'idée (règles du format ci-dessus) et le **présenter** :
   tableau `# · qui parle · réplique · à l'écran · durée estimée` + les textes du modèle + durée totale.
   La colonne « à l'écran » dit, pour chaque réplique, quel élément apparaît, quand et où (ou « — »).
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
format = "vulga"
question = "Pourquoi le ciel est bleu ?"
points = ["La lumière mélange tout", "Le bleu rebondit plus", "Il arrive de partout"]
conclusion = "donc bleu"
recap = "L'air disperse le bleu\nplus que le rouge."
sources = "Sources : NASA (2024)"
[[repliques]]
texte = "Le soleil envoie toutes les couleurs."
[[repliques]]
texte = "L'air fait rebondir le bleu partout."
[[repliques]]
texte = "Résultat : du bleu dans tout le ciel."
```
