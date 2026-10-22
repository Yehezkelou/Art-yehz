# Outils de montage ico-vid (étape 5)

`monter.py` construit un épisode complet à partir d'un **fichier d'épisode** (`episode.toml`) et du
modèle du format (`~/videos/modeles/`). Il tourne en headless (pas besoin d'ouvrir l'app) et ne
modifie jamais le modèle.

```bash
python3 -I ~/videos/outils/monter.py ~/videos/<slug>/episode.toml             # projet + 3 aperçus PNG
python3 -I ~/videos/outils/monter.py ~/videos/<slug>/episode.toml --ecraser    # refaire (copie de sauvegarde)
python3 -I ~/videos/outils/monter.py ~/videos/<slug>/episode.toml --rendu      # .mp4 + copie sur le Bureau
```

Sortie : `~/videos/<slug>/<slug>.ecproj`, `apercu-1..3.png`, puis `<slug>.mp4`. Le script affiche
un résumé JSON avec des **alertes** à lire : durée hors bible, réplique trop longue (coupée en
plusieurs sous-titres), erreur d'expression dans n'importe quelle comp.

Rien n'est écrasé sans `--ecraser`, et `--ecraser` copie d'abord l'ancien projet
(`<slug>.sauvegarde-AAAAMMJJ-HHMMSS.ecproj`). **Si le projet a été retouché dans l'app, ne pas
le refaire avec `--ecraser`** : les retouches seraient remplacées (elles restent dans la copie).

## Le fichier d'épisode

```toml
format = "sketch"            # sketch | pixel | fantasy | vulga
slug = "sketch-02-cloud"     # facultatif : nom du dossier par défaut
duree = 30                   # facultatif : sinon calculée (≥ minimum de la bible)
couleur = "#FFD24A"          # facultatif : couleur principale de la série
voix = "voix.m4a"            # facultatif : fichier dans le dossier de l'épisode
voix_debut = 0.0             # facultatif : où poser la voix (s)

# Textes du modèle, selon le format
accroche = "MA MÈRE ET LE CLOUD"   # sketch (2 premières secondes)
perso = "Moi"                      # sketch
titre = "LE SAUT"                  # pixel : titre ; fantasy : titre de l'épisode
serie = "LA QUÊTE DE TIM"          # fantasy
numero = "ÉPISODE 1"               # fantasy
suivant = "Prochain épisode : …"   # fantasy (carton « à suivre »)
question = "Pourquoi le ciel est bleu ?"   # vulga
points = ["…", "…", "…"]           # vulga (3 au plus)
points_temps = [3, 7, 11]          # vulga, facultatif
fleche_temps = 13                  # vulga, facultatif
conclusion = "donc…"               # vulga (texte au bout de la flèche)
recap = "Une phrase\nen 2 lignes." # vulga
sources = "Sources : …"            # vulga

[[repliques]]                      # une par phrase dite (dans l'ordre)
texte = "Ma mère m'a demandé c'est quoi le cloud."
debut = 0.8                        # facultatif : sinon ~2,8 mots/s, départ à 0,8 s
fin = 4.0                          # facultatif
chute = true                       # sketch : la chute (silence de 1 s avant, réaction, couleur)

[[effets]]                         # facultatif : mouvements sur un calque du modèle
calque = "Nom du perso"
comp = "…"                         # facultatif (défaut : comp principale)
rapide = "pop"                     # mouvement « rapide » (gratuit au rendu), ou :
# preset = "ico - Pop apparition"  # preset .ecpreset (réglable, mais ~1 s de plus par image)
temps = [12.0]                     # marqueurs posés sur le calque (pour les « … (marqueur) »)
```

Mouvements rapides : `secousse`, `zoom` (au marqueur) · `pop`, `rebond`, `fondu` (au point
d'entrée) · `respiration`, `clignement` · `pixel-degats`, `pixel-saut` (au marqueur),
`pixel-scintillement`. Ils remplacent l'expression déjà posée sur la propriété (la tête du sketch
est protégée : elle a déjà respiration, secousse et zoom au « Temps de la chute »).

Calques utiles par modèle : sketch `Tete`, `Oeil G/D`, `Bouche`, `Nom du perso`, `Accroche` ·
pixel (comp `PIXEL 270x480`) `Heros`, `Piece`, `Lune` · fantasy `Heros (a remplacer)` ·
vulga `Question`, `Point 1..3`, `Zone schema`.

## Rendu et performances (cette machine, CPU)

~0,25 s par image pour un sketch sans preset (≈ 2 min pour 30 s), ~1 s par image en fantasy
(≈ 40 min pour 90 s). Chaque preset `.ecpreset` ajoute ~1 s par image : préférer `rapide`.

## Fichiers

- `monter.py` — l'outil ; `rapides.py` — les mouvements rapides (aussi en scripts `.jsonl` dans
  `~/videos/presets/rapides/`, pour les appliquer à la main dans l'app).
- `pilote_agy.py` — pilote les 6 profils d'agents Antigravity / Gemini (`critique`, `rendu`, `da`,
  `architecte`, `flash`, `essaim`) avec sonde MP4 automatique et chargement de `~/videos/GEMINI.md`
  et `~/videos/.agents/skills/ico-*/SKILL.md` (voir `.claude/skills/pilote-agy/SKILL.md`).
- Chaque épisode garde ses scripts de construction dans `~/videos/<slug>/.montage/`.
