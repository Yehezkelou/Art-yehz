# Outils de montage ico-vid (étape 5)

`monter.py` construit un épisode complet à partir d'un **fichier d'épisode** (`episode.toml`) et du
modèle du format (`modeles/`). Il tourne en headless (pas besoin d'ouvrir l'app) et ne
modifie jamais le modèle.

```bash
python3 -I outils/monter.py <slug>/episode.toml             # projet + 3 aperçus PNG
python3 -I outils/monter.py <slug>/episode.toml --ecraser    # refaire (copie de sauvegarde)
python3 -I outils/monter.py <slug>/episode.toml --rendu      # .mp4 + copie sur le Bureau
```

Sortie : `<slug>/<slug>.ecproj`, `apercu-1..3.png`, puis `<slug>.mp4`. Le script affiche
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

## Rendu 3D pixel art (rendu3d)

Une scène three.js (r186) rendue image par image en séquence PNG que les compositeurs d'épisode
superposent : `<dossier>/f_0000.png …`, RGBA 8 bits, couleurs ico-pixel-32 seulement, alpha 0 ou 255.

```
cd outils/rendu3d && npm ci                    # une fois par clone (three 0.186.1, puppeteer-core 25.16.0)
node outils/rendu3d/rendu3d.mjs --scene <fichier.mjs> --out <dossier> --debut <s> --fin <s> \
     [--ips 24] [--largeur 270] [--hauteur 480] [--fond transparent|RRGGBB] [--params '<json>'] [--images 0,5,9]
python3 -I outils/rendu3d.py <fichier.mjs> <dossier> --debut 0 --fin 2      # même chose depuis Python
```

Depuis un compositeur : `rendu3d.rendre(scene, sortie, debut, fin, ips=24, fond="transparent", params=None)`
(+ `largeur`, `hauteur`, `images`, `delai`) → résumé JSON en dict, `rendu3d.ErreurRendu` en cas d'échec.
L'image i est l'instant `debut + i/ips`, fin exclue (`round((fin - debut) × ips)` images) ; `--images`
ne rend que ces numéros. Résumé sur stdout : `images`, `ms_par_image`, `gpu`, `lumiere_defaut`…

Module de scène (ESM, servi depuis son propre dossier : les `import` relatifs vers ce dossier marchent,
`import * as THREE from "three"` et `"three/addons/…"` aussi) :

```js
export default function creer(THREE, outils, params) {
  const scene = new THREE.Scene();
  const camera = new THREE.PerspectiveCamera(35, outils.largeur / outils.hauteur, 1, 200);
  const mot = outils.voxelTexte("0,1", { cube: 1, profondeur: 2, couleur: 19 });
  scene.add(mot);
  return { scene, camera, update(t) { mot.rotation.y = t; } };   // t en secondes absolues
}
```

`outils` : `palette` (32 « #RRGGBB » dans l'ordre du .hex, `palette[0]` = couleur 1 = `#0E0D18`) ·
`couleur(i)` (i = 1–32 → THREE.Color) · `materiau(i, {ombre = "toon"})` (`"toon"`/`true` : MeshToon 3 paliers ;
`"lambert"` ; `"plat"`/`false` : MeshBasic, couleur exacte) · `voxelTexte(texte, {cube = 1, profondeur = 1,
couleur = 8, ombre = "toon"})` (Group centré, un sous-groupe par caractère avec `userData.caractere`/`index`,
un cube par « # » de ico5x7 ; caractère absent → erreur qui liste les disponibles : majuscules seulement) ·
`hasard(graine)` (→ `() => [0, 1)` reproductible) · `lisse(u)` · `entre(t, t0, t1)` · `ressort(u)`
(dépassement ≈ 12 %, 1 exact à u ≥ 1) · `largeur`, `hauteur`, `ips`.

Règles : tout dépend de t seul (`Math.random` de la page est remplacé par un générateur à graine fixe,
mais utiliser `outils.hasard`) ; sans lumière dans la scène, une ambiance + un soleil sont ajoutés ;
`--fond` ne s'applique que si la scène ne pose pas `scene.background`. Chaque image passe à la couleur de
palette la plus proche (RGB euclidien), alpha < 128 → transparent. Navigateur : `ICO_CHROME`, sinon
Chrome puis Edge (GPU haute performance demandé) ; node : `ICO_NODE`, sinon le PATH. Sur le PC « HP »
(RTX 3050) : ~0,7 s de démarrage puis ~20 ms par image en 270×480 pour la démo
(`outils/rendu3d/exemples/demo.mjs`).

## Fichiers

- `monter.py` — l'outil ; `rapides.py` — les mouvements rapides (aussi en scripts `.jsonl` dans
  `presets/rapides/`, pour les appliquer à la main dans l'app).
- `pilote_agy.py` — pilote les 6 profils d'agents Antigravity / Gemini (`critique`, `rendu`, `da`,
  `architecte`, `flash`, `essaim`) avec sonde MP4 automatique et chargement de `GEMINI.md`
  et `.agents/skills/ico-*/SKILL.md` (voir `.claude/skills/pilote-agy/SKILL.md`).
- Chaque épisode garde ses scripts de construction dans `<slug>/.montage/`.
