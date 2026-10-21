# Sketch 01 — « Le cloud »

Première vidéo de l'étape 1 du plan. But : apprendre le logiciel et remplir
`../ce-qui-m-a-gene.md`, pas faire un chef-d'œuvre.

| Fichier | Quoi |
|---|---|
| `sketch-01-cloud.ecproj` | le projet EffectCraft |
| `sketch-01-cloud.mp4` | export H.264, 1080×1920, 24 i/s, 17 s, muet (copie sur le Bureau Windows) |
| `voix-a-enregistrer.txt` | les 4 répliques et leur minutage, à enregistrer au téléphone |

## Comment c'est construit (12 calques)

- `Fond` : solide + *Gradient Ramp* radial (bleu nuit).
- `Tete` : calque de forme (ellipse jaune, contour sombre).
  - échelle : clés — pop d'entrée 0 → 144 % → 126 %, puis zoom de réaction 152 % à 13,85 s ;
  - position : expression — respiration permanente + **secousse comique** de 13,70 s à 14,45 s.
- `Oeil G` / `Oeil D` (enfants de `Tete`), chacun parent de sa `Pupille` :
  expression de **clignement automatique** (liste de temps) + yeux écarquillés sur la chute.
- `Bouche` (enfant de `Tete`) : expression — bouche fermée au repos, battement pendant
  les répliques, grande ouverte pendant la réaction. **À remplacer par l'audio réel**
  (`keys.audioToKeyframes`) dès que la voix est enregistrée.
- `ST1`…`ST4` : sous-titres (Inter Bold 76–80, blanc, contour noir 16, centrés, 2 lignes max),
  chacun avec un pop d'entrée (échelle 86 → 107 → 100 % + opacité) et ses points d'entrée/sortie.

Structure comique : situation (0,8–4,8) → mise en place (5,2–9,4) → **silence** (9,4–10,6)
→ réplique de la mère (10,6–13,7) → réaction (13,7–14,5) → chute (14,5–16,4).

## Rouvrir / re-rendre

```bash
cargo run --release -p effectcraft -- --control 9877   # puis Fichier ▸ Ouvrir
```
