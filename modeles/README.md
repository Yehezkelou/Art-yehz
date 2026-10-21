# Modèles ico-vid (étape 3)

Dans EffectCraft : **Fichier ▸ Nouveau ▸ Nouveau projet depuis un modèle**, onglet *Templates*,
catégorie **ico-vid**. Le modèle crée une copie sans titre : le modèle lui-même ne change jamais.

Les modèles appliquent `../bible.md` : zones sûres, polices, palettes, sous-titres, signature.
Chaque modèle contient aussi les comps de la bible (*Guide zones*, *Signature*, *Planche bible*).

| Modèle | Format | Comp à ouvrir | Réglages (Objets graphiques essentiels) |
|---|---|---|---|
| Sketch humour | 9:16 · 24 i/s · 30 s | `SKETCH - a remplir` | Accroche, Nom du perso, Couleur principale, Couleur fond, **Temps de la chute (s)**, Force secousse |
| Pixel art | 9:16 · 270×480 ×4 · 12 i/s · 20 s | `PIXEL - sortie 1080x1920` (on dessine dans `PIXEL 270x480`) | Titre, Couleur principale (pièces), fond, sol, héros |
| Aventure fantasy | 16:9 · 24 i/s · 90 s | `FANTASY - episode` | Titre de la série, Numéro d'épisode, Titre de l'épisode, Carton « à suivre », 4 couleurs, Vitesse caméra |
| Vulgarisation | 9:16 · 24 i/s · 60 s | `VULGA - a remplir` | Question, Points 1–3, Conclusion de la flèche, Récap, Sources, 4 couleurs |

Tu changes une valeur dans le panneau, tout ce qui en dépend suit (expressions reliées au calque
`Controles`, qui ne s'exporte pas).

## Mode d'emploi par modèle

**Sketch humour**
- Mets « Temps de la chute » sur la seconde de la chute : la secousse, le zoom de réaction, les
  yeux écarquillés et la bouche grande ouverte s'y calent tout seuls.
- Voix : importe-la, place-la, puis *Animation ▸ Assistant d'images clés ▸ Convertir l'audio en
  images clés*. Le calque créé s'appelle **« Audio Amplitude »** : la bouche le lit
  automatiquement (sans lui, elle reste fermée).
- Sous-titres : duplique `ST 01` (Ctrl+D) pour chaque réplique et règle son entrée/sortie.
  `ST chute` est déjà en couleur principale.

**Pixel art**
- On travaille dans `PIXEL 270x480` : positions et tailles en **pixels entiers**, sinon ça bave.
- 12 i/s = animation « en 2s » automatique. Le héros (16×16) saute toutes les 2 s : c'est
  l'exemple à copier pour les sprites.
- Sous-titres : Press Start 2P 16 px, **≤ 12 caractères par ligne** (sinon on sort de la zone sûre).
- Le titre se tape dans les Objets graphiques essentiels (source cachée `TXT Titre`).

**Aventure fantasy**
- `Decor parallaxe` : 3 plans (loin / milieu / premier plan) qui glissent à des vitesses
  différentes selon « Vitesse caméra ». Remplace les collines par tes décors en gardant leur
  expression de position.
- Brume calculée en 480×270 puis agrandie ×4 (sinon 630 ms par image). Rendu ≈ 1 s/image en
  1080p sur cette machine → ~40 min pour 90 s : préviens-toi en demi-résolution.
- `Heros (a remplacer)` : silhouette provisoire en attendant les dessins (VectorCraft).

**Vulgarisation**
- Les 3 points apparaissent à 3 s, 7 s et 11 s ; la flèche se trace à 13 s ; récap + sources à
  52 s. Décale les clés si ta voix va plus vite ou moins vite.

## Reconstruire un modèle

Les scripts sont dans `build/` (`lib.py` + un script par modèle). Ils génèrent un `.jsonl` de
commandes EffectCraft (`Fichier ▸ Scripts ▸ Exécuter un fichier de script`) et un `.js` de
finitions. Les `.ecproj` à côté sont les projets sources ; les `.ectemplate` sont les copies de ce
qui est installé dans `~/.config/effectcraft/Templates/`.
