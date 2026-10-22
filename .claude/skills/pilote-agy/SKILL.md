---
name: pilote-agy
description: >-
  Pilote les agents spécialisés et modèles Gemini d'Antigravity (CLI agy) pour l'usine ico-vid
  (Usine 2.2 / 2.3). Utiliser aux 3 Portes (Porte Script, Porte Rendu, Porte Bilan), pour déléguer
  du code d'outils (camera.py, verifier_pixels.py, regarder.py), un audit de direction artistique
  pixel, ou lancer un essaim de sous-agents Gemini en parallèle.
---

# Recette : Piloter Antigravity / Gemini (`pilote_agy.py`)

L'utilisateur a configuré et autorisé à 100 % la collaboration entre **Claude Code** et **Antigravity (`agy`)** dans `~/videos`.
`agy` dispose désormais de son contexte projet automatique (`GEMINI.md`) et de **4 compétences d'agents spécialisés** (`.agents/skills/ico-*/SKILL.md`), pilotables en une seule commande via `outils/pilote_agy.py`.

## 1. Les 6 Profils d'Agents Prêts à l'Emploi

| Profil | Commande | Modèle par défaut | Mode | Usage dans l'Usine 2.2 / 2.3 |
|---|---|---|---|---|
| **`critique`** | `pilote_agy.py critique "…"` | `gemini-4-argon-high` | `plan` (lecture) | **Porte Script & Bilan** : classer les 5 idées du lundi, critiquer un `episode.toml` (accroche < 2 s, chute comique, lien Gag ↔ Science), auditer les stats M3/M6/M12 |
| **`rendu`** | `pilote_agy.py rendu "…" --video X.mp4` | `gemini-4-argon-high` | `plan` (lecture) | **Porte Rendu & J+7** : contrôler la checklist § 11.2, planches contact, zones sûres 9:16, miniature à 10 %, décrochages J+7 (*injecte automatiquement la sonde audio factuelle du `.mp4`*) |
| **`da`** | `pilote_agy.py da "…"` | `gemini-4-argon-high` | `auto` (écriture) | **Direction Artistique Pixel** : vérifier/générer des planches 32×32, scripts Lua Aseprite, conformité `ico-pixel-32`, décors parallaxe, moodboards (`image-generator`) |
| **`architecte`** | `pilote_agy.py architecte "…"` | `gemini-4-argon-high` | `auto` (écriture) | **Ingénierie Pipeline** : coder ou tester `camera.py`, `verifier_pixels.py`, `verifier_licences.py`, `decouper_planche.py`, `regarder.py`, `monter.py v2` |
| **`flash`** | `pilote_agy.py flash "…"` | `gemini-3.8-flash-high` | `plan` (lecture) | **Contrôle Rapide** : vérification éclair d'un lot de sous-titres, de longueurs de lignes ou de manifeste |
| **`essaim`** | `pilote_agy.py essaim "…"` | `gemini-4-argon-high` | `auto` (écriture) | **Multi-Agents Parallèles** : demande à `agy` de lancer ses propres sous-agents (`research`, `self`, `image-generator`) en parallèle sur une grosse tâche |

## 2. Exemples de Commandes (depuis Claude Code)

```bash
# 1. Porte Script (lundi) : critiquer un épisode avant enregistrement de la voix
python3 -I outils/pilote_agy.py critique \
  "Audite vulga-01-gps/episode.toml et propose un gag court de Tim qui renvoie vers cet épisode."

# 2. Porte Rendu : contrôler une vidéo rendue (la sonde audio est injectée automatiquement)
python3 -I outils/pilote_agy.py rendu \
  "Vérifie sketch-01/sketch-01-cloud.mp4 et ses aperçus selon la checklist § 11.2." \
  --video sketch-01/sketch-01-cloud.mp4 \
  --sortie sketch-01/rapport-gemini.md

# 3. Déléguer la création ou le test d'un outil Python à l'agent Architecte
python3 -I outils/pilote_agy.py architecte \
  "Écris et teste outils/verifier_pixels.py selon le § 6.6 du plan." --ecrire

# 4. Direction Artistique : vérifier une planche de sprites ou générer une action Lua Aseprite
python3 -I outils/pilote_agy.py da \
  "Vérifie assets/persos/tim/tim-planche.png et ajoute l'action saut dans tim.lua." --ecrire
```

## 3. Options Utiles

- `--model <id>` : choisir explicitement parmi `gemini-4-argon-high`, `gemini-4-argon-medium`, `gemini-3.8-flash-high`, `gemini-3.8-flash-medium`.
- `--ecrire` (ou `--auto`) : active `--mode auto --dangerously-skip-permissions` pour que l'agent `agy` puisse créer/modifier des fichiers et lancer les outils de test sans blocage.
- `--lecture` (ou `--plan`) : force le mode lecture seule (`--mode plan`).
- `--video <chemin.mp4>` : sonde automatiquement les flux vidéo/audio du fichier `.mp4` avant de l'envoyer à Gemini, empêchant toute hallucination de voix sur une vidéo muette.
- `--sortie <fichier.md>` : sauvegarde directement le rapport dans le fichier indiqué.
