# Mission : audit de la planche de Tim (§ 7.1)

- **Date** : 2026-10-22 · **Agent** : da (Gemini) · **Mode** : lecture seule · **Étape** : semaine 1 J3–J4

## But
Vérifier `assets/persos/tim/tim-planche.png`, `tim.json`, `tim.lua` (et `tim.aseprite` si lisible) contre § 7.1 et § 4.5 : taille multiple de 32, une ligne par action, étiquettes (frameTags) et durées du JSON, ligne de sol (pieds alignés sur la même ligne dans toutes les cases : donne la ligne mesurée par case), pixels semi-transparents, cases vides. Proposer le contenu de `assets/persos/tim/tim.toml` (format du § 7.1) cohérent avec le JSON réel.

## Critère de fin
Rapport dans agents/rapports/gemini/2026-10-22-audit-planche-tim.md avec mesures par case (preuve : méthode de lecture du PNG en Python standard).
