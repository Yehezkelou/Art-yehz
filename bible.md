# Bible de la chaîne — v1 (20 octobre 2026)

Étape 2 du plan. **Décisions prises une seule fois** : les modèles (étape 3), les presets (étape 4)
et les recettes Claude (étape 5) lisent ce fichier. On le modifie seulement après une vraie vidéo
qui montre qu'une règle ne marche pas (et on note pourquoi dans `ce-qui-m-a-gene.md`).

Fichiers associés : `bible/bible.ecproj` (comps *Planche bible*, *Guide zones 9:16*, *Signature*),
`bible/planche-bible.png`, `bible/guide-zones-9x16.png`, `licences/`.

## 1. Formats et cadence

| | Valeur |
|---|---|
| Format principal | **Vertical 1080×1920** (Shorts, TikTok, Reels) |
| Format long | 1920×1080 pour les vidéos > 1 min (fantasy, vulgarisation longue) |
| Images par seconde | **24 i/s** pour la comp |
| Animation des persos | **« en 2s »** : `posterizeTime(12)` sur les propriétés des persos (look cartoon) ; caméra, textes et effets restent à 24 |
| Pixel art | comp de travail **270×480** (×4 = 1080×1920) à 12 i/s, imbriquée en qualité *Draft* ; facteurs d'échelle entiers uniquement |
| Export | modèle de sortie **« Short 9:16 H.264 »** (H.264, 12 Mb/s, audio auto 48 kHz stéréo) — enregistré dans l'app et mis par défaut pour les films |

## 2. Zones sûres (9:16) — voir `bible/guide-zones-9x16.png`

| Zone | Pixels | Règle |
|---|---|---|
| Haut | y 0–150 (8 %) | rien d'important (pseudo, barre de l'appli) |
| Bas | y 1632–1920 (15 %) | **interdit** : description, musique, boutons |
| Bords | x 0–60 et 1020–1080 | aucun texte |
| Colonne boutons | x 940–1080, y 900–1632 | ni texte ni visage (j'aime, commentaires, partage) |
| Sous-titres | x 140–940, y 1300–1560 | voir § 5 |
| Visage + action | x 60–1020, y 150–1300 | le perso qui parle et la chute se jouent ici |

La comp *Guide zones 9:16* s'imbrique dans chaque modèle en **calque guide** (visible à l'écran,
jamais exporté).

## 3. Durées et structure

| Format | Durée |
|---|---|
| Sketch humour | 15–45 s |
| Pixel art | 10–30 s |
| Aventure fantasy | 60–120 s (épisode) |
| Vulgarisation | 45–90 s |

- **Accroche dans les 2 premières secondes** (le 1er sous-titre arrive avant 1 s).
- **Une seule idée par vidéo.**
- Humour : situation → montée → **silence ~0,5–1 s** → chute ; le juron ponctue la chute, pas avant.
- **Fin qui boucle** : la dernière image renvoie à la première (même cadrage / même phrase).
- Signature (§ 7) collée à la fin, après la chute — jamais avant.

## 4. Palettes (une par série, 6 couleurs) — voir `bible/planche-bible.png`

Ordre : 1 principal · 2 fond · 3 contour/ombre · 4 accent chaud · 5 accent froid · 6 clair.

| Série | 1 | 2 | 3 | 4 | 5 | 6 |
|---|---|---|---|---|---|---|
| Sketch humour | `#FFD24A` | `#1B2340` | `#141826` | `#FF5A4E` | `#4FD1E8` | `#F6F1E7` |
| Pixel art | `#F4C542` | `#1D1B2E` | `#3E5BA9` | `#E5533D` | `#3FB56B` | `#F2EDE4` |
| Aventure fantasy | `#C9A227` | `#0F2A2E` | `#2F6B4F` | `#F28C38` | `#7A4FB3` | `#E8D9B5` |
| Vulgarisation | `#2E86DE` | `#0E1A2B` | `#22C39B` | `#FF5C7A` | `#FFB020` (surligneur) | `#F4F6FA` |

## 5. Polices (toutes en licence OFL, licences dans `licences/fonts/`)

| Usage | Police | Réglages |
|---|---|---|
| Titres, cartons, signature | **Lilita One** Regular | 100–170 px |
| Sous-titres | **Montserrat ExtraBold** | voir ci-dessous |
| Série pixel art (titres + sous-titres) | **Press Start 2P** | multiples de 8 px dans la comp 270×480 (8 ou 16), jamais de taille non entière ; sous-titres en 16 px, **≤ 12 caractères par ligne** |

Les polices sont installées dans `~/.local/share/fonts/videos/` (Linux/WSL). Pour une build Windows
native, il faudra les installer aussi côté Windows.

### Sous-titres — toujours présents

- Montserrat ExtraBold **72 px**, blanc `#FFFFFF`, **contour noir 14 px derrière le remplissage**.
- Centrés à x = 540, **1re ligne à y = 1380**, interligne 86.
- **2 lignes max, ≤ 20 caractères par ligne**, largeur ≤ 800 px.
- Le mot de la chute peut prendre la couleur 1 de la série.
- Entrée en pop : échelle 86 → 107 → 100 % sur 0,22 s + opacité 0 → 100 sur 0,08 s (déjà dans le sketch 01).

## 6. Personnages

- Formes simples, gros yeux, contour couleur 3 de la série (12–14 px à l'échelle 100 %).
- Rig minimal : `Tete` parent de tout ; yeux parents des pupilles ; bouche enfant de la tête.
- Bouche pilotée par l'audio dès qu'il y a une voix (`keys.audioToKeyframes`).

## 7. Signature (1 s) — comp *Signature*

- Chaîne **ico-vid** (en minuscules), pseudo **@yehz**.
- « ico-vid » en Lilita One 170, couleur 1 de la série + contour couleur 3, pop d'entrée, « @yehz » en Montserrat ExtraBold 48 en dessous.
- Jingle de 1 s : à trouver (Freesound CC0) ou à enregistrer ; noter la source dans `licences/`.

## 8. Contrôle avant export (checklist)

- [ ] Accroche avant 2 s, une seule idée.
- [ ] Rien dans les zones rouges / orange du guide.
- [ ] Sous-titres ≤ 2 lignes, ≤ 20 car./ligne.
- [ ] Palette de la série respectée.
- [ ] Signature à la fin.
- [ ] Sources de tous les éléments notées dans `licences/`.
