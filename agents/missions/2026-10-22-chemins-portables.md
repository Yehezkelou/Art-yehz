# Mission : chemins portables (WSL et Windows natif)

- **Date** : 2026-10-22
- **Agent** : outilleur
- **Mode** : écriture (fichiers listés ci-dessous seulement)
- **Étape du plan** : INSTALLATION.md § 0 (changement de machine)

## But
Les outils doivent tourner sur la nouvelle machine, sous **Windows natif** (dépôt dans `C:\Users\HP\Documents\yehz\Art-yehz`, utilisateur `HP`, Python 3.15 Windows). Ils doivent continuer de marcher sous WSL/Linux avec l'ancienne disposition (`~/videos`). Décision de @yehz (option B) : pas de WSL sur cette machine.

## Contexte à lire
- `CLAUDE.md`, `INSTALLATION.md` § 0, `agents/README.md`
- Résultat actuel : `python -I outils/verifier_licences.py` → ROUGE « manifeste introuvable : C:\Users\HP\Videos\assets\manifeste.toml » (`~/videos` y désigne le dossier Vidéos de Windows, pas le dépôt).

## Règles de fond
- Racine du dépôt = déduite de l'emplacement du script (`outils/..`), plus de `~/videos` codé en dur dans le code exécuté. Possibilité de surcharge par variable d'environnement `ICO_VIDEOS` si utile.
- EffectCraft de production : `~/dev/vid/effectcraft/target/release/effectcraft-cli` + `.exe` sous Windows (`os.name == "nt"`). Surcharge possible par `ICO_EFFECTCRAFT`. Il est cloné ici dans `C:\Users\HP\dev\vid\effectcraft`, en cours de compilation.
- Bureau : sous Windows, le Bureau de l'utilisateur (`C:\Users\HP\Desktop` ici ; essayer aussi `OneDrive\Desktop`) ; sous WSL, garder l'ancien chemin. Si absent, la copie est sautée comme avant.
- Appels à Python dans des sous-processus : `sys.executable`, pas `"python3"`.
- `modeles/build/lib.py`, `presets/build/test_presets.py` : chemins `/home/Yehezou/videos` remplacés par la racine calculée. Les chemins envoyés à EffectCraft doivent être absolus et valides sur la plateforme courante.
- `assets/**/*.lua` (Aseprite) : `SORTIE` pointe vers `C:\Users\Yehezkelou\ico-pixel\…`. Le remplacer par `os.getenv("USERPROFILE")` ou l'équivalent Lua d'Aseprite (`app.fs.joinPath`, `os.getenv`), pour ne plus dépendre du nom d'utilisateur.
- Les `.jsonl` de `bible/` et `modeles/build/` (journaux de commandes) : **ne pas les réécrire** ; signaler seulement dans le rapport s'ils sont rejoués par un outil et donc bloquants.
- Docstrings et textes d'aide : on peut laisser `~/videos` comme notation, sauf s'ils sont trompeurs.
- Ne rien modifier dans `logiciel/` ni dans `~/dev/vid/effectcraft`. Pas de commit (l'orchestrateur le fera).

## Fichiers autorisés en écriture
- `outils/*.py`, `outils/tests/*.py` (ajouter des tests de résolution de chemins si pertinent)
- `modeles/build/lib.py`, `presets/build/test_presets.py`
- `assets/**/*.lua`
- `agents/rapports/claude/2026-10-22-chemins-portables.md` (rapport)

## Critère de fin
- `python -I -m unittest discover -s outils/tests` : tout vert sous Windows (sortie dans le rapport).
- `python -I outils/verifier_licences.py` : plus d'erreur « manifeste introuvable » (sortie dans le rapport ; s'il reste du rouge pour une autre raison, l'expliquer).
- `python -I outils/pilote_agy.py --liste` fonctionne toujours.
- `grep` montrant qu'il ne reste plus de `/home/Yehezou`, `Yehezkelou` ni de `~/videos` dans du code exécuté (hors docstrings et `.jsonl`).

## Format du rapport
`agents/rapports/claude/2026-10-22-chemins-portables.md` : résultat d'abord, puis preuves (chemin:ligne, commande + sortie), puis ce qui reste incertain.
