### 1. Fichiers de palette créés et vérifiés

Les deux fichiers ont été créés avec exactement les **32 couleurs** du § 4.4 de [plan-2.3.txt](file:///home/Yehezou/videos/plans/plan-2.3.txt#L369-L411), dans l'ordre des 8 rampes de 4 teintes (de la plus sombre à la plus claire) :
- [ico-pixel-32.gpl](file:///home/Yehezou/videos/bible/palette/ico-pixel-32.gpl) (`GIMP Palette`, `Name: ico-pixel-32`, `Columns: 4`, lignes `R G B	rampe-numéro`)
- [ico-pixel-32.hex](file:///home/Yehezou/videos/bible/palette/ico-pixel-32.hex) (32 lignes, 6 caractères hexadécimaux en minuscules sans `#`)

#### Liste des 32 couleurs (`ico-pixel-32`) et présence des 6 couleurs de la [bible.md](file:///home/Yehezou/videos/bible.md#L50-L60)

| # | Nom (`.gpl`) | Hex (`.hex`) | R G B | Rampe | Couleur Bible v1 |
|---:|---|---|---|---|---|
| 1 | `nuits-1` | `0e0d18` | `14 13 24` | 1. Nuits et contours | — |
| 2 | `nuits-2` | `1d1b2e` | `29 27 46` | 1. Nuits et contours | **Oui (`#1D1B2E` — 2. fond)** |
| 3 | `nuits-3` | `2f2c45` | `47 44 69` | 1. Nuits et contours | — |
| 4 | `nuits-4` | `4a4663` | `74 70 99` | 1. Nuits et contours | — |
| 5 | `neutres-1` | `6e6a80` | `110 106 128` | 2. Neutres et crème | — |
| 6 | `neutres-2` | `9a96a6` | `154 150 166` | 2. Neutres et crème | — |
| 7 | `neutres-3` | `c9c4c8` | `201 196 200` | 2. Neutres et crème | — |
| 8 | `neutres-4` | `f2ede4` | `242 237 228` | 2. Neutres et crème | **Oui (`#F2EDE4` — 6. clair)** |
| 9 | `bleus-1` | `1f2e5c` | `31 46 92` | 3. Bleus (ciel, eau) | — |
| 10 | `bleus-2` | `3e5ba9` | `62 91 169` | 3. Bleus (ciel, eau) | **Oui (`#3E5BA9` — 3. contour/ombre)** |
| 11 | `bleus-3` | `5e8fd6` | `94 143 214` | 3. Bleus (ciel, eau) | — |
| 12 | `bleus-4` | `9cc7f0` | `156 199 240` | 3. Bleus (ciel, eau) | — |
| 13 | `verts-1` | `1e4d3a` | `30 77 58` | 4. Verts (herbe, feuilles) | — |
| 14 | `verts-2` | `2e7d4f` | `46 125 79` | 4. Verts (herbe, feuilles) | — |
| 15 | `verts-3` | `3fb56b` | `63 181 107` | 4. Verts (herbe, feuilles) | **Oui (`#3FB56B` — 5. accent froid)** |
| 16 | `verts-4` | `8fdb86` | `143 219 134` | 4. Verts (herbe, feuilles) | — |
| 17 | `ors-1` | `7a4e1e` | `122 78 30` | 5. Ors (pièces, lumière) | — |
| 18 | `ors-2` | `b9802b` | `185 128 43` | 5. Ors (pièces, lumière) | — |
| 19 | `ors-3` | `f4c542` | `244 197 66` | 5. Ors (pièces, lumière) | **Oui (`#F4C542` — 1. principal)** |
| 20 | `ors-4` | `fbe58c` | `251 229 140` | 5. Ors (pièces, lumière) | — |
| 21 | `rouges-1` | `5a1e2b` | `90 30 43` | 6. Rouges (danger, cœur) | — |
| 22 | `rouges-2` | `9e2f33` | `158 47 51` | 6. Rouges (danger, cœur) | — |
| 23 | `rouges-3` | `e5533d` | `229 83 61` | 6. Rouges (danger, cœur) | **Oui (`#E5533D` — 4. accent chaud)** |
| 24 | `rouges-4` | `f59a7a` | `245 154 122` | 6. Rouges (danger, cœur) | — |
| 25 | `terres-1` | `3b2a22` | `59 42 34` | 7. Terres (bois, chemin) | — |
| 26 | `terres-2` | `6b4a35` | `107 74 53` | 7. Terres (bois, chemin) | — |
| 27 | `terres-3` | `9c7451` | `156 116 81` | 7. Terres (bois, chemin) | — |
| 28 | `terres-4` | `c9a57a` | `201 165 122` | 7. Terres (bois, chemin) | — |
| 29 | `violets-1` | `3d2550` | `61 37 80` | 8. Violets (magie, nuit) | — |
| 30 | `violets-2` | `6b3f87` | `107 63 135` | 8. Violets (magie, nuit) | — |
| 31 | `violets-3` | `a066b8` | `160 102 184` | 8. Violets (magie, nuit) | — |
| 32 | `violets-4` | `e0a6d9` | `224 166 217` | 8. Violets (magie, nuit) | — |

Les **6 couleurs** de la série Pixel art de la bible (`F4C542`, `1D1B2E`, `3E5BA9`, `E5533D`, `3FB56B`, `F2EDE4`) sont toutes présentes.

---

### 2. Contrôle de conformité PNG (décodage `zlib` / `struct` Python standard, lecture seule)

#### A. [tim-planche.png](file:///home/Yehezou/videos/assets/persos/tim/tim-planche.png) (`128×64 px`, PNG indexé `color_type=3`, 8 192 px au total)
- **Transparence** : `5 816 px` transparents (`alpha = 0`, index 0 `#000000` dans `PLTE`/`tRNS`), `2 376 px` opaques (`alpha = 255`), **`0 px` semi-transparent**.
- **Couleurs visibles (`alpha > 0`) hors palette `ico-pixel-32`** : **Aucune (0 couleur hors palette, 0 pixel fautif)**.
- Les 14 couleurs opaques utilisées appartiennent toutes à `ico-pixel-32` :
  `1d1b2e` (726 px), `c9a57a` (508 px), `7a4e1e` (360 px), `3fb56b` (318 px), `3e5ba9` (122 px), `e5533d` (96 px), `3b2a22` (64 px), `6b4a35` (48 px), `2e7d4f` (42 px), `f2ede4` (28 px), `b9802b` (16 px), `f59a7a` (16 px), `9c7451` (16 px), `1f2e5c` (16 px).

---

#### B. [chat.png](file:///home/Yehezou/videos/assets/portraits/chat/chat.png) (`96×96 px`, PNG indexé `color_type=3`, 9 216 px au total)
- **Transparence** : `0 px` transparent, `9 216 px` opaques (`alpha = 255`), `0 px` semi-transparent.
- **Couleurs dans la palette** : seulement **2 couleurs** (`9cc7f0` : 6 px, `5e8fd6` : 4 px, soit 10 px sur 9 216).
- **Couleurs HORS palette `ico-pixel-32`** : **16 couleurs** totalisant **9 206 pixels** (99,89 % de l'image) :

| # | Hex hors palette | R G B | Nombre de pixels |
|---:|---|---|---:|
| 1 | `#292524` (`292524`) | `41 37 36` | **2 364 px** |
| 2 | `#FC8393` (`fc8393`) | `252 131 147` | **775 px** |
| 3 | `#DD646C` (`dd646c`) | `221 100 108` | **757 px** |
| 4 | `#CD575A` (`cd575a`) | `205 87 90` | **708 px** |
| 5 | `#BE4A4A` (`be4a4a`) | `190 74 74` | **631 px** |
| 6 | `#AD423F` (`ad423f`) | `173 66 63` | **621 px** |
| 7 | `#ED737F` (`ed737f`) | `237 115 127` | **605 px** |
| 8 | `#9D3A35` (`9d3a35`) | `157 58 53` | **567 px** |
| 9 | `#8D332B` (`8d332b`) | `141 51 43` | **548 px** |
| 10 | `#7C2C23` (`7c2c23`) | `124 44 35` | **470 px** |
| 11 | `#210B07` (`210b07`) | `33 11 7` | **288 px** |
| 12 | `#8C4A4E` (`8c4a4e`) | `140 74 78` | **277 px** |
| 13 | `#6B261C` (`6b261c`) | `107 38 28` | **225 px** |
| 14 | `#5A1F16` (`5a1f16`) | `90 31 22` | **170 px** |
| 15 | `#481910` (`481910`) | `72 25 16` | **155 px** |
| 16 | `#36120B` (`36120b`) | `54 18 11` | **45 px** |
| **Total** | **16 couleurs hors palette** | — | **9 206 px** |


---
**Vérification Claude (21/10/2026)** : les 32 couleurs de ico-pixel-32.hex = celles du § 4.4 du plan, même ordre (contrôle automatique). Chat hors palette : étude de style voulue, marquée non vendable au manifeste.
