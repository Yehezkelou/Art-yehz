# ico-vid : contexte pour Claude

Chaîne vidéo pixel art de @yehz (YouTube, TikTok, Instagram). Tout se passe dans `~/videos`.

- **Décisions validées** : `plans/decisions.md` (priment sur le plan et sur GEMINI.md).
- **Plan** : `plans/EffectCraft_Usine_2.3_Plan.docx` (texte brut : `plans/plan-2.3.txt`), généré par `plans/plan-v2.3.js`.
- **Bible** : `bible.md` ; palette `bible/palette/ico-pixel-32.{gpl,hex}` ; journal des gênes `ce-qui-m-a-gene.md`.
- **Outils** : `outils/` (monter.py, rapides.py, verifier_licences.py, pilote_agy.py) ; tests : `python3 -I -m unittest discover -s outils/tests`.
- **Logiciels** : `logiciel/` (suite ArtCraft + VoiceStudio, dépôts séparés, hors git). Copie de production d'EffectCraft : `~/dev/vid/effectcraft` (ne rien y modifier).

## Rôle de la session principale : orchestrateur
La session principale orchestre tous les agents Claude (`.claude/agents/`) et pilote les agents Gemini (`outils/pilote_agy.py`). Organisation, cycle mission → rapport → vérification → intégration et règles : `agents/README.md`. L'orchestrateur seul fait les commits.

## Règles qui ne bougent pas
- Règle d'or : on ne code une fonction dans un logiciel que si son absence a gêné sur 2 vraies vidéos (journal).
- Pas de licence, pas d'usage : tout fichier de `assets/` est au manifeste (`assets/manifeste.toml`) ; `references/` n'entre jamais dans une vidéo.
- Pixel : échelles entières, positions arrondies, palette ico-pixel-32, pas de flou ni de semi-transparence.
- Pas de voix ni de vidéo d'autrui réutilisée ; idées reprises, forme réécrite.
- Rien ne sort de la machine sans l'accord de @yehz. Gemini en lecture seule sauf autorisation explicite de @yehz pour une mission.
- Commits : terminer par `Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>`.
