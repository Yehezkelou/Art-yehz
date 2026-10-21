# Agents ico-vid : qui fait quoi

Une seule chaîne de commandement : **@yehz décide → Claude (session principale) orchestre → les agents exécutent.**
Les décisions validées sont dans [`../plans/decisions.md`](../plans/decisions.md) ; elles priment sur tout.

## Les deux équipes

| Équipe | Où sont-ils définis | Comment on les lance | Par défaut |
|---|---|---|---|
| **Agents Claude** (sous-agents de Claude Code) | `../.claude/agents/*.md` + contexte `../CLAUDE.md` | par l'orchestrateur (outil Agent) | lisent, écrivent et testent dans `~/videos` |
| **Agents Gemini** (Antigravity, CLI `agy`) | `../.agents/skills/ico-*/SKILL.md` + contexte `../GEMINI.md` | `python3 -I ~/videos/outils/pilote_agy.py <profil> "<mission>"` | **lecture seule** ; ils rédigent, Claude relit et écrit |

| Agent | Équipe | Rôle |
|---|---|---|
| `verificateur` | Claude | Vérifie toute affirmation (d'un agent, d'un plan, de Gemini) contre les fichiers, le code et les mesures. Ne modifie rien. |
| `outilleur` | Claude | Écrit et teste les outils Python de `outils/` (souvent à partir d'un brouillon de l'architecte Gemini). |
| `monteur` | Claude | Monte, prévisualise et rend les épisodes (monter.py, EffectCraft, recettes video-*), puis lance les contrôles. |
| `critique` | Gemini | Porte script et porte bilan : avis contradictoire sur idées, scripts, stratégie. |
| `rendu` / `flash` | Gemini | Porte rendu : regarde le .mp4 et les planches, checklist § 11.2. |
| `da` | Gemini | Direction artistique pixel : palette, planches, décors, Lua Aseprite. |
| `architecte` / `essaim` | Gemini | Brouillons d'outils et recherches parallèles. |

## Le cycle d'une mission

1. **Mission** : l'orchestrateur écrit `missions/AAAA-MM-JJ-sujet.md` à partir de [`missions/MODELE.md`](missions/MODELE.md) (but, fichiers autorisés, critère de fin).
2. **Exécution** : un agent (Claude ou Gemini) la traite ; son rapport va dans `rapports/claude/` ou `rapports/gemini/` (même nom de fichier).
3. **Vérification** : tout rapport Gemini, et tout rapport Claude qui affirme un fait non mesuré, passe par le `verificateur` (ou l'orchestrateur) avant d'être utilisé.
4. **Intégration** : l'orchestrateur applique, lance les tests, met à jour le journal et fait le commit.

## Règles

- **Un seul écrivain par fichier et par mission** : deux agents ne modifient jamais le même fichier en même temps.
- **Gemini en lecture seule par défaut.** Le mode `--ecrire` (toutes permissions, sans confirmation) n'est utilisé que si @yehz l'autorise pour une mission précise.
- **Rien n'est retenu sans preuve** : chemin:ligne, commande lancée avec sa sortie, ou mesure (fiche technique, transcription, image extraite). Une observation vidéo de Gemini sans mesure qui la confirme reste « à vérifier ».
- **Rien ne sort de la machine** (publication, envoi, achat) sans l'accord de @yehz.
- **Pas de secret** (mot de passe, clé, identifiant) dans une mission ni dans un rapport.
- Les commits sont faits par l'orchestrateur, jamais par un agent.

## Rangement

```
agents/
  README.md            ce fichier
  missions/            une fiche par mission (MODELE.md = gabarit)
  rapports/claude/     réponses des agents Claude
  rapports/gemini/     réponses des agents Gemini (pilote_agy.py y écrit par défaut)
```
