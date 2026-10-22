# Rapport Critique Éditorial — Porte Script : « GPS et Einstein » (`vulga-01-gps`) + 3 Gags Pixel liés (D10)

- **Date** : 2026-10-22
- **Agent** : `critique` (`ico-critique-editorial`)
- **Mode** : Lecture seule (aucune commande shell exécutée)
- **Référentiels appliqués** : [`plans/decisions.md`](file:///home/Yehezou/videos/plans/decisions.md), [`bible.md`](file:///home/Yehezou/videos/bible.md), [`GEMINI.md`](file:///home/Yehezou/videos/GEMINI.md), [`SKILL.md`](file:///home/Yehezou/videos/.agents/skills/ico-critique-editorial/SKILL.md), [`outils/monter.py`](file:///home/Yehezou/videos/outils/monter.py)

---

## Verdict Immédiat

> **À CORRIGER AVANT MONTAGE**

Le script de [`vulga-01-gps/episode.toml`](file:///home/Yehezou/videos/vulga-01-gps/episode.toml#L1-L49) est solide sur le fond vulgarisé et respecte la contrainte des sous-titres (`≤ 2 lignes` de `≤ 20 caractères`, vérifié dans [`vulga-01-gps/.montage/montage.jsonl`](file:///home/Yehezou/videos/vulga-01-gps/.montage/montage.jsonl#L19-L132) qui génère exactement 19 sous-titres pour 19 répliques sans coupure forcée). **Toutefois**, il présente **4 défauts structurels de rétention et de synchronisation** (question tronquée en taille par `monter.py`, paradoxe retardé à `t = 4,26 s`, tunnel visuel de `17,6 s` sans point affiché, et trou muet de `8,56 s` en fin d'épisode) ainsi qu'une nuance scientifique à préciser sur le chiffre de `10 km/jour`.

---

## 1. Audit Scientifique des Chiffres (`vulga-01-gps/episode.toml`)

Référence citée dans [`vulga-01-gps/episode.toml`](file:///home/Yehezou/videos/vulga-01-gps/episode.toml#L10) : `gps.gov` et Neil Ashby (2003), *« Relativity in the Global Positioning System »*, *Living Reviews in Relativity*, 6(1).

| Affirmation dans `episode.toml` | Ligne | Calcul physique & Référence | Statut | Correction / Précision proposée |
|---|---|---|---|---|
| `à 5 m près` / `à 5 mètres près` | [L8](file:///home/Yehezou/videos/vulga-01-gps/episode.toml#L8), [L13](file:///home/Yehezou/videos/vulga-01-gps/episode.toml#L13) | Selon `gps.gov` (*SPS Performance Standard*), la précision horizontale moyenne d'un récepteur civil à ciel ouvert est de **4,9 m** ($\approx 5\text{ m}$). | **SÛR** | Aucune modification nécessaire. |
| `31 satellites, à 20 000 km.` | [L25](file:///home/Yehezou/videos/vulga-01-gps/episode.toml#L25) | Demi-grand axe orbital $a \approx 26\,560\text{ km}$, soit une altitude de **$20\,180\text{ km}$** ($\approx 20\,000\text{ km}$) pour une vitesse orbitale $v \approx 3,874\text{ km/s}$. La constellation compte 24 satellites nominaux et **31 opérationnels** (`gps.gov`). | **SÛR** | Aucune modification nécessaire. |
| `Sa vitesse : −7µs chaque jour.` | [L39](file:///home/Yehezou/videos/vulga-01-gps/episode.toml#L39) | **Relativité restreinte** (dilatation cinématique) : $\frac{\Delta \tau}{\tau} \approx -\frac{v^2}{2c^2} \approx -8,35 \times 10^{-11}$, soit **$-7,21\text{ }\mu\text{s/jour}$** (Ashby 2003). L'arrondi à $-7\text{ }\mu\text{s/j}$ est exact. | **SÛR** | Ajouter une espace insécable/fine avant l'unité : `−7 µs` (évite aussi un bug de prononciation TTS VoiceStudio, cf. `D4 bis` dans [`plans/decisions.md`](file:///home/Yehezou/videos/plans/decisions.md#L9)). |
| `Moins de gravité, +45µs par jour.` | [L41](file:///home/Yehezou/videos/vulga-01-gps/episode.toml#L41) | **Relativité générale** (potentiel gravitationnel terrestre vs orbite) : $\frac{\Delta \tau}{\tau} \approx \frac{\Phi_{\text{sat}} - \Phi_{\text{géoïde}}}{c^2} \approx +5,28 \times 10^{-10}$, soit **$+45,6\text{ }\mu\text{s/jour}$** (souvent tronqué à $+45\text{ }\mu\text{s/j}$ ou arrondi à $+46\text{ }\mu\text{s/j}$). | **SÛR** | Écrire `+45 µs par jour.` (avec espace). |
| `Bilan : 38µs d'avance par jour.` | [L43](file:///home/Yehezou/videos/vulga-01-gps/episode.toml#L43) | $+45,6 - 7,2 = \mathbf{+38,4\text{ }\mu\text{s/jour}}$ (et $+45 - 7 = +38\text{ }\mu\text{s/jour}$). Cohérence arithmétique parfaite avec les deux répliques précédentes. | **SÛR** | Écrire `Bilan : +38 µs par jour.` (avec espace et signe `+`). |
| `dérive de 10 km/jour.` / `Sans correction : 10 km par jour !` | [L9](file:///home/Yehezou/videos/vulga-01-gps/episode.toml#L9), [L45](file:///home/Yehezou/videos/vulga-01-gps/episode.toml#L45) | **Double vérification requise** :<br>1) **Arithmétique** : $38,4\text{ }\mu\text{s} \times c$ ($299\,792\text{ km/s}$) $= \mathbf{11,5\text{ km/jour}}$ (et $38 \times 0,3 = \mathbf{11,4\text{ km/jour}}$). Dire « 10 km » après « 38 µs » est un arrondi d'ordre de grandeur.<br>2) **Physique du récepteur** : Comme le téléphone résout 4 inconnues $(x, y, z, t_{\text{récepteur}})$ avec 4 satellites ([L35](file:///home/Yehezou/videos/vulga-01-gps/episode.toml#L35)), un décalage commun constant serait partiellement absorbé dans l'horloge du téléphone **si** les satellites étaient fixes ; mais comme les satellites défilent à $3,9\text{ km/s}$ et que leurs éphémérides + l'excentricité orbitale dépendent du temps GPS synchronisé au sol, l'erreur de télémétrie ($c \cdot \Delta t$) atteint bien **~10 à 11,4 km/jour** sans le décalage d'usine ([L47](file:///home/Yehezou/videos/vulga-01-gps/episode.toml#L47)). | **À VÉRIFIER / PRÉCISER** | Remplacer `10 km par jour` par **`~10 km par jour`** (ou **`11 km par jour`** pour coller exactement à $38\text{ }\mu\text{s} \times 300\,000\text{ km/s} = 11,4\text{ km}$). |
| `On les règle donc avant le départ.` | [L47](file:///home/Yehezou/videos/vulga-01-gps/episode.toml#L47) | Les horloges atomiques GPS sont ralenties en usine avant lancement d'un facteur $\Delta f / f = -4,4647 \times 10^{-10}$ (passant de $10,23\text{ MHz}$ à $10,22999999543\text{ MHz}$, Ashby 2003). | **SÛR** | Très bonne synthèse en 7 mots. |

---

## 2. Top 3 des Points Faibles & Critique Ligne par Ligne

> [!IMPORTANT]
> **Note préalable sur le format (Décision D11)** : [`plans/decisions.md`](file:///home/Yehezou/videos/plans/decisions.md#L13) valide que « La science en pixel » garde le format long **6–10 min** (16:9). Or [`vulga-01-gps/episode.toml`](file:///home/Yehezou/videos/vulga-01-gps/episode.toml#L2) utilise le modèle court vertical `format = "vulga"` de **62 s** ([`bible.md`](file:///home/Yehezou/videos/bible.md#L42) : 45–90 s). L'audit ci-dessous évalue `vulga-01-gps/episode.toml` dans son format `vulga` actuel (62 s), tout en préparant la passerelle D10.

### Faiblesse n° 1 — Accroche trop lente (`t = 4,26 s`) et titre réduit automatiquement ([`episode.toml:4, 12-15`](file:///home/Yehezou/videos/vulga-01-gps/episode.toml#L4))
- **Preuve code & montage** :
  - Ligne 4 : `question = "Sans Einstein, pas de GPS ?"` compte **27 caractères**. Or [`outils/monter.py`](file:///home/Yehezou/videos/outils/monter.py#L206-L208) réduit la police dès `len(q) > 22` : dans [`vulga-01-gps/.montage/montage.jsonl`](file:///home/Yehezou/videos/vulga-01-gps/.montage/montage.jsonl#L5), `Question` tombe de `88 px` à **`72 px`**.
  - Lignes 12–15 : Le `Sous-titre 01` (`"Ton GPS te trouve à 5 mètres près."`) occupe `0,80 s → 4,01 s` ([`finitions.js`](file:///home/Yehezou/videos/vulga-01-gps/.montage/finitions.js#L2)). Le conflit narratif (`"Et il doit ça à Einstein."`) n'apparaît qu'à **`t = 4,26 s`**, soit après la barrière critique des 3 premières secondes ([`SKILL.md`](file:///home/Yehezou/videos/.agents/skills/ico-critique-editorial/SKILL.md#L18)).
- **Correction** :
  - Ramener `question` à `≤ 22 caractères` (ex. `"Einstein dans ton GPS?"` = 22 car., garde sa taille maximale de `88 px`).
  - Fusionner l'accroche et le paradoxe dès les 2 premières répliques (`0,8 s → 4,5 s`) en mettant l'enjeu destructeur tout de suite : `"Sans Einstein, ton GPS est faux."` (`0,8 s`) suivi de `"Il dériverait de 11 km par jour !"` (`2,7 s`).

### Faiblesse n° 2 — Tunnel visuel de 17,6 s puis télescopage des `points_temps` ([`episode.toml:5-8`](file:///home/Yehezou/videos/vulga-01-gps/episode.toml#L5-L8))
- **Preuve code & montage** :
  - Ligne 6 : `points_temps = [20.4, 31.3, 34.1]`.
  - De `t = 0,0 s` à `t = 20,4 s` (**20,4 secondes !**), aucun des 3 points du tableau ne s'affiche dans la zone centrale, alors que l'analogie de l'orage ([L17-L23](file:///home/Yehezou/videos/vulga-01-gps/episode.toml#L17-L23), `7,0 s → 17,36 s`) et l'introduction des satellites ([L25](file:///home/Yehezou/videos/vulga-01-gps/episode.toml#L25), `17,61 s`) sont déjà passées ([`finitions.js`](file:///home/Yehezou/videos/vulga-01-gps/.montage/finitions.js#L2)).
  - Inversement, `Point 2` (`31,3 s`) et `Point 3` (`34,1 s`) apparaissent à seulement **2,8 s d'intervalle**, puis plus rien ne bouge dans le schéma entre `34,1 s` et `48,5 s` (**14,4 s** d'immobilité pendant les calculs relativistes des lignes 37–45).
  - Lignes 7–8 : `fleche_temps = 48.5` et `conclusion = "à 5 m près"` font surgir `"à 5 m près"` pendant que la voix dit `"On les règle donc avant le départ."` (`48,14 s → 50,99 s`, [`finitions.js`](file:///home/Yehezou/videos/vulga-01-gps/.montage/finitions.js#L2)) : dissonance texte/audio.
- **Correction** :
  - Aligner `points_temps` sur les 3 vrais actes du script :
    - `Point 1` dès l'entrée des satellites/horloges (`~15,0 s`),
    - `Point 2` sur les 4 satellites (`~27,5 s`),
    - `Point 3` sur le basculement relativiste (`~32,5 s`).
  - Aligner `fleche_temps` sur la résolution (`~46,0 s`) avec une `conclusion` qui correspond à la phrase prononcée : `"réglées au sol"` ou `"à 5 m près !"` si la dernière réplique boucle sur les 5 mètres.
  - Ajouter des mouvements gratuits en CPU (`rapide = "secousse"` / `"zoom"` sur marqueurs via [`outils/monter.py`](file:///home/Yehezou/videos/outils/monter.py#L266-L277)) aux temps clés pour respecter la relance visuelle toutes les 3–4 s ([`SKILL.md`](file:///home/Yehezou/videos/.agents/skills/ico-critique-editorial/SKILL.md#L29)).

### Faiblesse n° 3 — Chute non marquée (`chute = true` absent), absence de boucle et 8,5 s de vide final ([`episode.toml:48-49`](file:///home/Yehezou/videos/vulga-01-gps/episode.toml#L48-L49))
- **Preuve code & montage** :
  - Ligne 49 : `texte = "Merci, Albert."` ne comporte pas `chute = true`. Dans [`vulga-01-gps/.montage/montage.jsonl`](file:///home/Yehezou/videos/vulga-01-gps/.montage/montage.jsonl#L127), `Sous-titre 19` est donc rendu en blanc `#FFFFFF` au lieu du jaune surligneur `#FFB020` ([`outils/monter.py`](file:///home/Yehezou/videos/outils/monter.py#L231) et [`L245`](file:///home/Yehezou/videos/outils/monter.py#L245)).
  - Règle de la bible ([`bible.md`](file:///home/Yehezou/videos/bible.md#L47)) : *« Fin qui boucle : la dernière image renvoie à la première (même cadrage / même phrase). »* Or `"Merci, Albert."` ne renvoie pas à la réplique 1 (`"Ton GPS te trouve à 5 mètres près."`).
  - Dans [`outils/monter.py`](file:///home/Yehezou/videos/outils/monter.py#L161), la durée auto d'un épisode `vulga` est `math.ceil(last_end + 9.0)`. Comme `Sous-titre 19` finit à `52,44 s` ([`finitions.js`](file:///home/Yehezou/videos/vulga-01-gps/.montage/finitions.js#L2)), la vidéo reste muette de `52,44 s` à `61,0 s` (**8,56 secondes sans voix** sur le carton récap).
- **Correction** :
  - Ajouter `chute = true` sur la dernière réplique et boucler explicitement sur l'accroche : `"Voilà comment il te trouve… à 5 mètres près."` (qui enchaîne directement avec le début si le Short reboucle).

---

## 3. Correction Prête à Coller (`vulga-01-gps/episode.toml`)

### 3 Variantes de Titres / Questions (`≤ 22 car.` pour conserver `88 px` dans `monter.py:206`)
1. **`"Einstein dans ton GPS?"`** *(22 car. — garde 88 px, direct et intrigant)*
2. **`"Un GPS sans Einstein ?"`** *(22 car. — garde 88 px, proche de l'original)*
3. **`"Le GPS triche-t-il ?"`** *(20 car. — garde 88 px, angle mystère)*

### Fichier `vulga-01-gps/episode.toml` corrigé

```toml
# Vulgarisation 01 — Le GPS et Einstein (corrigé porte script 2026-10-22)
format = "vulga"
slug = "vulga-01-gps"
question = "Un GPS sans Einstein ?"
points = ["31 horloges en orbite", "4 signaux = ta position", "Là-haut, le temps file"]
points_temps = [15.5, 29.0, 32.0]
fleche_temps = 46.0
conclusion = "réglées au sol !"
recap = "Sans Einstein, le GPS\ndérive de 11 km/jour."
sources = "Sources : gps.gov · Ashby (2003)"

[[repliques]]
texte = "Sans Einstein, ton GPS est perdu."
[[repliques]]
texte = "Il se tromperait de 11 km par jour !"
[[repliques]]
texte = "Imagine un orage au loin."
[[repliques]]
texte = "Tu comptes : éclair… puis tonnerre."
[[repliques]]
texte = "Le délai donne la distance."
[[repliques]]
texte = "Le GPS fait pareil avec la lumière."
[[repliques]]
texte = "31 satellites, à 20 000 km."
[[repliques]]
texte = "Chacun a une horloge atomique."
[[repliques]]
texte = "Il envoie : l'heure et sa position."
[[repliques]]
texte = "Ton tél mesure le retard du signal."
[[repliques]]
texte = "Retard = distance au satellite."
[[repliques]]
texte = "Avec 4 satellites, il te situe."
[[repliques]]
texte = "Mais là-haut, le temps triche."
[[repliques]]
texte = "Sa vitesse : −7 µs chaque jour."
[[repliques]]
texte = "Moins de gravité : +45 µs par jour."
[[repliques]]
texte = "Bilan : +38 µs d'avance par jour."
[[repliques]]
texte = "À la vitesse de la lumière : 11 km !"
[[repliques]]
texte = "On ralentit donc l'horloge au sol."
[[repliques]]
texte = "Pour te trouver… à 5 mètres près."
chute = true

[[effets]]
calque = "Zone schema"
rapide = "secousse"
temps = [3.0, 32.0, 43.0]
```

---

## 4. Volet D10 — 3 Shorts « Gags Pixel » Muets (15–40 s) avec Tim

Conformément à la décision **D10** ([`plans/decisions.md`](file:///home/Yehezou/videos/plans/decisions.md#L12)), **D4 / D4 bis** ([`plans/decisions.md`](file:///home/Yehezou/videos/plans/decisions.md#L8-L9) : *« gags toujours sans voix »*) et à la bible technique pixel ([`bible.md`](file:///home/Yehezou/videos/bible.md#L18), [`L40`](file:///home/Yehezou/videos/bible.md#L40), [`L67`](file:///home/Yehezou/videos/bible.md#L67) : scène `270×480` ×4, police **Press Start 2P** 16 px en **MAJUSCULES**, **≤ 2 lignes de 12 caractères**, durée cible 20–28 s pour respecter à la fois la mission `15–40 s` et le plafond `30 s` de [`outils/monter.py`](file:///home/Yehezou/videos/outils/monter.py#L31)), voici **3 gags muets** mettant **Tim** face aux 3 mécanismes physiques de la vidéo GPS.

---

### Gag 1 — `pixel-gps-01-10km` : « À 5 MÈTRES PRÈS » (Le problème de la dérive de 10–11 km)
- **Idée en 1 phrase (11 mots)** : Tim suit son GPS pour aller aux toilettes et atterrit au volcan.
- **Durée** : **22 s** (boucle parfaite sur la porte des WC).
- **Concept scientifique lié (`vulga-01-gps/episode.toml:45`)** : Sans correction relativiste (`+38 µs/j`), la position GPS dérive de `~10–11 km` par jour.
- **Décors & Assets (« 1 travail = 3 usages »)** :
  - Réutilise `Tim` (course pressée, sueur pixel `#9CC7F0`, regard caméra) + décor 5 plans parallaxe (herbe/chemin terre palette `ico-pixel-32` → lave `#E5533D`).
  - **Usage boutique** : Emote animée Twitch/Discord `Tim_Panic_Run` + Alerte `GPS_Lost`.

#### Découpage en 3 temps (sans voix, SFX 8 bits + bulles `Press Start 2P` ≤ 12 car./ligne)
1. **Mise en place (`0,0 s – 3,5 s`) — L'urgence à 5 mètres** :
   - **`t = 0,0 s` (Accroche < 1 s)** : Tim sautille sur place en se tenant le ventre (animation 12 i/s). À droite du cadre (à 5 mètres), une cabane de toilettes en bois avec un cœur pixel.
   - **`t = 0,5 s`** : Tim sort une carte/boussole GPS pixel qui clignote en vert (`#3FB56B`) avec un bip 8 bits joyeux.
   - **Bulle 1 (`0,8 s – 2,8 s`)** :
     ```text
     WC : 5 M
     TOUT DROIT !
     ```
     *(10 car. / 12 car.)*
2. **Développement / Escalade (`3,5 s – 14,5 s`) — La dérive relativiste** :
   - **`t = 3,5 s`** : Au ciel (plan `P = 0.1`), un petit satellite pixel passe à toute vitesse. Son horloge embarquée affiche `+38 µs` en rouge (`#E5533D`) avec un bruitage de ressort détraqué (*boing-zzzt*).
   - **`t = 5,5 s`** : La flèche du GPS de Tim tourne brusquement de 180° vers la gauche (`scale X = -100 %`).
   - **Bulle 2 (`6,0 s – 8,5 s`)** :
     ```text
     RECALCUL...
     +11 KM !
     ```
     *(11 car. / 8 car.)*
   - **`t = 8,5 s – 14,5 s`** : Tim obéit aveuglément à la flèche et sprinte à gauche (`CAM` en suivi rapide `24 i/s` à travers 3 décors en parallaxe : forêt → désert → cratère volcanique).
3. **Pause comique & Chute (`14,5 s – 22,0 s`)** :
   - **`t = 14,5 s – 15,3 s` (Silence franc de 0,8 s)** : Toute la musique/bruitage coupe net. Tim s'arrête au bord d'un lac de lave en fusion (`#E5533D` / `#F4C542`). Pas un bruit.
   - **`t = 15,3 s` (Chute visuelle + sonore)** : Bip joyeux de validation 8 bits (*TADA!*). Zoom caméra par palier (`100 % → 200 %`) + `secousse` sur Tim dont les sourcils grillent (`pixel-degats`).
   - **Bulle 3 — Chute (`15,5 s – 18,5 s`, couleur `#F4C542`)** :
     ```text
     VOUS ÊTES
     ARRIVÉ !
     ```
     *(9 car. / 8 car.)*
   - **Bulle 4 — Renvoi D10 vers la vidéo Science (`18,5 s – 21,0 s`)** :
     ```text
     MERCI QUI ?
     VOIR EINSTEIN
     ```
     *(11 car. / 12 car. — flèche pixel pointant vers le lien de la vidéo reliée en bas)*
   - **`t = 21,0 s – 22,0 s`** : Signature `ico-vid` + retour au cadrage exact de `t = 0,0 s` (boucle).

---

### Gag 2 — `pixel-gps-02-4satellites` : « IL EN FAUT 4 ! » (La trilatération par 4 signaux)
- **Idée en 1 phrase (11 mots)** : Tim cherche son coffre avec un, deux, trois, puis quatre satellites.
- **Durée** : **24 s**.
- **Concept scientifique lié (`vulga-01-gps/episode.toml:29-35`)** : Un seul signal donne une sphère/cercle géant ; il faut **4 satellites** pour fixer $(x, y, z)$ et l'heure exacte.
- **Décors & Assets (« 1 travail = 3 usages »)** :
  - Réutilise `Tim` avec pelle pixel + `Piece` / coffre du modèle `pixel-art.ecproj` + icône satellite 16×16.
  - **Usage boutique** : Pack d'icônes pixel HUD « Signal 1/4 à 4/4 » pour overlays streamers.

#### Découpage en 3 temps (sans voix, SFX 8 bits + bulles `Press Start 2P` ≤ 12 car./ligne)
1. **Mise en place (`0,0 s – 4,0 s`) — La chasse au trésor haute technologie** :
   - **`t = 0,0 s` (Accroche < 1 s)** : Tim plante une pelle dans le sol dès la 1re image (`t = 0,2 s`, bruitage *clong*). Il regarde son détecteur GPS qui cherche un coffre doré (`#F4C542`).
   - **Bulle 1 (`0,8 s – 3,2 s`)** :
     ```text
     TRÉSOR ICI ?
     1 SATELLITE
     ```
     *(12 car. / 11 car.)*
2. **Développement / Escalade (`4,0 s – 16,0 s`) — La règle des 4 signaux** :
   - **`t = 4,0 s`** : Avec **1 satellite**, un cercle pointillé géant s'affiche autour de Tim : il creuse à gauche, fait jaillir une taupe furieuse (*couic* 8 bits).
   - **`t = 8,0 s`** : **2 satellites** s'allument dans le ciel (`#5E8FD6`). Deux cercles se croisent en deux points.
   - **Bulle 2 (`8,2 s – 10,8 s`)** :
     ```text
     2 SIGNAUX :
     PILE OU FACE
     ```
     *(11 car. / 12 car.)*
   - **`t = 11,0 s`** : Tim creuse à droite : il perce un tuyau d'eau pixel qui l'arrose (`#9CC7F0`).
   - **`t = 13,0 s`** : **3 satellites** s'allument : la croix rouge s'affiche pile sous les pieds de Tim… mais à 10 mètres **en l'air** (erreur d'altitude / d'horloge sans le 4e satellite !). Tim saute avec sa pelle dans le vide (`pixel-saut`) et retombe à plat ventre.
   - **Bulle 3 (`13,5 s – 15,8 s`)** :
     ```text
     3 SIGNAUX :
     MAUVAISE H !
     ```
     *(11 car. / 12 car.)*
3. **Pause comique & Chute (`16,0 s – 24,0 s`)** :
   - **`t = 16,0 s – 16,8 s` (Silence franc de 0,8 s)** : Tim, couvert de terre au fond de ses 3 trous, lève les yeux au ciel. Silence total.
   - **`t = 16,8 s` (Chute visuelle + sonore)** : Le **4e satellite** s'allume (`#F4C542`, accord 8 bits parfait). Les 4 rayons convergent pile sur… le coffre sur lequel Tim avait posé son sac dès le début, qui s'affaisse et tombe sur sa tête (*BONK* + `secousse` caméra `200 %`).
   - **Bulle 4 — Chute (`17,0 s – 20,0 s`, couleur `#F4C542`)** :
     ```text
     4 SATELLITES
     = DANS LE MIL
     ```
     *(12 car. / 12 car.)*
   - **Bulle 5 — Renvoi D10 (`20,0 s – 23,0 s`)** :
     ```text
     POURQUOI 4 ?
     VOIR VIDÉO !
     ```
     *(12 car. / 12 car.)*

---

### Gag 3 — `pixel-gps-03-gravite` : « LE TEMPS FILE LÀ-HAUT » (Gravité +45 µs vs Vitesse −7 µs)
- **Idée en 1 phrase (12 mots)** : Tim monte son réveil en altitude pour faire cuire son œuf plus vite.
- **Durée** : **25 s**.
- **Concept scientifique lié (`vulga-01-gps/episode.toml:37-43`)** : En altitude, moins de gravité fait tourner les horloges plus vite (`+45 µs/j`), ce qui l'emporte sur le ralentissement dû à la vitesse (`−7 µs/j`).
- **Décors & Assets (« 1 travail = 3 usages »)** :
  - Réutilise `Tim` + une horloge/sablier pixel géant + décor tour/montagne vers l'espace (`#0E0D18`).
  - **Usage boutique** : Écran animé *Starting Soon* / compte à rebours pixel avec horloge pour streamers.

#### Découpage en 3 temps (sans voix, SFX 8 bits + bulles `Press Start 2P` ≤ 12 car./ligne)
1. **Mise en place (`0,0 s – 4,0 s`) — L'impatience au sol** :
   - **`t = 0,0 s` (Accroche < 1 s)** : Gros plan (`200 %`) sur Tim affamé devant un œuf à la coque et un gros réveil pixel qui fait *tic... tac...* très lentement au sol.
   - **Bulle 1 (`0,8 s – 3,2 s`)** :
     ```text
     CUISSON :
     TROP LENT !
     ```
     *(9 car. / 11 car.)*
2. **Développement / Escalade (`4,0 s – 16,5 s`) — Course vs Gravité** :
   - **`t = 4,0 s`** : Tim se met à courir très vite avec son réveil (effet relativité restreinte : vitesse). Mais le réveil ralentit encore plus (*tiiiiic...*) !
   - **Bulle 2 (`5,0 s – 8,0 s`)** :
     ```text
     VITESSE :
     -7 µS / JOUR
     ```
     *(9 car. / 12 car.)*
   - **`t = 8,5 s`** : Tim a une illumination (ampoule `#FBE58C`). Il attache son réveil et son œuf à un ballon fusée et grimpe tout en haut d'un pic spatial à `20 000 km` (travelling vertical `CAM` du plan `action` vers le plan `ciel` étoilé `#0E0D18`).
   - **`t = 12,5 s`** : Là-haut, les aiguilles du réveil s'affolent à toute vitesse (*tic-tic-tic-tic* aigu 8 bits).
   - **Bulle 3 (`13,0 s – 16,0 s`)** :
     ```text
     ALTITUDE :
     +45 µS / JOUR
     ```
     *(10 car. / 12 car.)*
3. **Pause comique & Chute (`16,5 s – 25,0 s`)** :
   - **`t = 16,5 s – 17,4 s` (Silence franc de 0,9 s)** : Le réveil sonne enfin (*DRIIING* coupé net). Silence complet pendant que Tim casse délicatement la coquille de son œuf.
   - **`t = 17,4 s` (Chute visuelle + sonore)** : Au lieu d'un œuf cuit, un poussin pixel avec la moustache et les cheveux blancs d'Einstein sort de l'œuf et règle lui-même le réveil à coups de clé à molette (`secousse` + jingle 8 bits).
   - **Bulle 4 — Chute (`17,6 s – 21,0 s`, couleur `#F4C542`)** :
     ```text
     AVANCE DE
     +38 µS / J !
     ```
     *(9 car. / 12 car.)*
   - **Bulle 5 — Renvoi D10 (`21,0 s – 24,0 s`)** :
     ```text
     LE SECRET ?
     VOIR LE GPS !
     ```
     *(11 car. / 12 car.)*

---
**Vérification de l'orchestrateur (22/10/2026)**
- Confirmé dans le code : question de 27 car. réduite à 72 px (monter.py:206-208, montage.jsonl) ; dernière réplique sans `chute = true` → sous-titre blanc au lieu de #FFB020 (monter.py:245) ; points_temps = [20.4, 31.3, 34.1] et fleche_temps = 48.5 (episode.toml:6-7) ; durée max des gags pixel = 30 s (monter.py:27, duree=(10, 30)).
- Confirmé par le calcul : −7,2 µs/j (vitesse), +45,7 µs/j (gravité, approximation sphérique), 38,4 µs × c = 11,5 km.
- **Mal jugé** : les « 8,56 s de vide final » sont le carton récap (8 s) + la signature prévus par le modèle vulga (monter.py:161, « flèche, récap (8 s), signature »), pas un trou.
- Le script corrigé proposé change l'accroche et la fin : à valider par @yehz (porte script), non appliqué.
