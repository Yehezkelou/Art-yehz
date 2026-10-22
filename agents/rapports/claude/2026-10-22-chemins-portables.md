# Rapport : chemins portables (WSL et Windows natif)

- **Mission** : `agents/missions/2026-10-22-chemins-portables.md`
- **Agent** : outilleur (Claude), 2026-10-22, Windows 11 natif, Python 3.15.1 (`C:\Python315\python.exe`)

## Résultat

Les quatre critères de fin sont remplis sous Windows natif :
- tests : 32 tests, OK (11 nouveaux dans `outils/tests/test_chemins.py`) ;
- `verifier_licences.py` : **VERT — manifeste conforme**, code 0 ;
- `pilote_agy.py --liste` : code 0, `agy` trouvé, `dossier_usine` = le dépôt ;
- plus de `/home/Yehezou` ni de `Yehezkelou` dans le code exécuté ; les seuls `~/videos` qui restent dans `outils/` sont dans les docstrings d'usage (lignes 1 à 10).

Ce qui a changé : un petit module `outils/chemins.py` calcule les chemins, et les outils l'importent au lieu d'utiliser `os.path.expanduser("~") + "videos/…"`.
- **Racine** : `outils/..`, ou la variable `ICO_VIDEOS` si elle est définie.
- **EffectCraft** : `~/dev/vid/effectcraft/target/release/effectcraft-cli`, avec `.exe` quand `os.name == "nt"`. La variable `ICO_EFFECTCRAFT` remplace ce chemin.
- **Presets EffectCraft** : même règle que le logiciel, lue dans `crates/ui-egui/src/panels/effects_presets.rs:28-35` (`EC_PRESETS_DIR`, sinon `$HOME`, sinon `%USERPROFILE%`, puis `Documents/EffectCraft/Presets`).
- **Bureau** :
  - si `ICO_BUREAU` est définie, on la prend ;
  - sous Windows, on prend le Bureau du registre (`HKCU\…\User Shell Folders\Desktop`), puis `%USERPROFILE%\Desktop`, puis `%USERPROFILE%\OneDrive\Desktop` ;
  - sous WSL, on prend `/mnt/c/Users/<compte>/OneDrive/Desktop` puis `Desktop`, mais seulement s'il y a un seul compte Windows réel ;
  - sinon on renvoie `None` et la copie est sautée.
- `python -I outils/chemins.py` affiche les chemins trouvés sur la machine.

## Fichiers modifiés

| Fichier | Changement |
|---|---|
| `outils/chemins.py` (nouveau) | `racine`, `dans_racine`, `effectcraft_cli`, `presets_effectcraft`, `candidats_bureau`, `bureau`, `EXE` |
| `outils/monter.py:15-21` | `CLI`, `MODELES`, `PRESETS`, `BUREAU` passent par `chemins` ; `:329` vérifie que `BUREAU` n'est pas `None` |
| `outils/pilote_agy.py:14-21` | `VIDEOS_DIR` = racine ; `EC_CLI` passe par `chemins` ; `FC_CLI` prend `.exe` sous Windows |
| `outils/pilote_agy.py:198-201` | l'en-tête envoyé à Gemini donne la racine réelle et des chemins relatifs (avant : `~/videos/...`, faux sous Windows) |
| `outils/verifier_licences.py:15-18` | `RACINE` = `chemins.dans_racine("assets")` |
| `outils/verifier_pixels.py:20-23` | `PALETTE` = `chemins.dans_racine("bible", "palette", "ico-pixel-32.hex")` |
| `outils/tests/test_chemins.py` (nouveau) | 11 tests : racine, `ICO_VIDEOS`, `.exe`, `ICO_EFFECTCRAFT`, presets, Bureau (Windows, WSL avec 1 / 2 / 0 comptes), `chemins.py` et `pilote_agy.py --liste` lancés en sous-processus avec `sys.executable` |
| `modeles/build/lib.py:2-7, 130` | `RACINE` = `modeles/build/../..` (ou `ICO_VIDEOS`) ; `BIBLE` et `file.saveAs` utilisent des chemins absolus de la plateforme |
| `presets/build/test_presets.py:1-4` | `D` = `<racine>/presets/` en chemin absolu |
| `assets/persos/tim/tim.lua:5-6, 137` | `SORTIE = app.fs.joinPath(os.getenv("USERPROFILE") or os.getenv("HOME"), "ico-pixel", …)` ; `app.fs.makeAllDirectories(app.fs.filePath(SORTIE))` avant `saveAs` |
| `assets/portraits/chat/chat.lua:8-9, 320` | même changement (CRLF et UTF-8 conservés) |

Aucun appel `"python3"` dans un sous-processus n'existait (grep vide). Les nouveaux tests utilisent `sys.executable`.

## Preuves

### Tests
```
$ python -I -m unittest discover -s outils/tests
................................
----------------------------------------------------------------------
Ran 32 tests in 0.227s

OK
```

### Licences
```
$ python -I outils/verifier_licences.py
VERT — manifeste conforme.
code 0
```

### Pilote agy
```
$ python -I outils/pilote_agy.py --liste | head -5
{
  "binaire_agy": "C:\\Users\\HP\\AppData\\Local\\agy\\bin\\agy.EXE",
  "dossier_usine": "C:\\Users\\HP\\Documents\\yehz\\Art-yehz",
  "agents": {
    "critique": {
code 0
```

### Chemins trouvés sur cette machine
```
$ python -I outils/chemins.py
{
  "racine": "C:\\Users\\HP\\Documents\\yehz\\Art-yehz",
  "effectcraft_cli": "C:\\Users\\HP\\dev\\vid\\effectcraft\\target\\release\\effectcraft-cli.exe",
  "effectcraft_cli_present": false,
  "presets_effectcraft": "C:\\Users\\HP\\Documents\\EffectCraft\\Presets",
  "bureau": "C:\\Users\\HP\\Desktop",
  "python": "C:\\Python315\\python.exe"
}
```

### Essais sur de vrais fichiers
```
$ python -I outils/verifier_pixels.py assets/persos/tim/tim-planche.png --echelle 1
VERT — assets/persos/tim/tim-planche.png (128×64, ×1) : 0 bloc(s) fautif(s) sur 8192, 0 couleur(s) hors palette

$ python -I -c "import sys; sys.path.insert(0,'outils'); import monter; print(monter.CLI, monter.MODELES, monter.PRESETS, monter.BUREAU, sep='\n')"
C:\Users\HP\dev\vid\effectcraft\target\release\effectcraft-cli.exe
C:\Users\HP\Documents\yehz\Art-yehz\modeles
C:\Users\HP\Documents\EffectCraft\Presets
C:\Users\HP\Desktop

$ python -I -c "…import lib; print(lib.BIBLE); b=lib.B(); b.save('sketch','n','d'); print(b.s[0]); print(os.path.isfile(lib.BIBLE))"
C:\Users\HP\Documents\yehz\Art-yehz\bible\bible.ecproj
{'command': 'file.saveAs', 'params': {'path': 'C:\\Users\\HP\\Documents\\yehz\\Art-yehz\\modeles\\sketch.ecproj'}}
True
```

`presets/build/test_presets.py` a été lancé depuis le dossier temporaire de la session, pour ne pas réécrire `presets/build/test.json{,l}`. Sortie : `87` commandes. Les 12 `anim.applyPreset` pointent vers des fichiers qui existent (`C:\Users\HP\Documents\yehz\Art-yehz\presets\ico - Pop apparition.ecpreset …`, `all(isfile) = True`).

### Grep du critère de fin
```
$ grep -rnE "/home/Yehezou|Yehezkelou|~/videos" --include=*.py --include=*.lua --include=*.js --include=*.sh . | grep -v "^./logiciel/"
```
Résultats :
- dans `outils/`, uniquement des docstrings : `chemins.py:2`, `monter.py:4-10`, `pilote_agy.py:5-10`, `png.py:6`, `verifier_licences.py:2-6`, `verifier_pixels.py:4-7`, et la ligne 1 de chacun des trois anciens fichiers de tests ;
- sinon, seulement `plans/plan-v2.*.js`, qui sont le texte des plans et pas du code de l'usine.

Aucun résultat dans `modeles/`, `presets/` ni `assets/`.

### `.jsonl` (non réécrits)
Ces fichiers contiennent encore `/home/Yehezou` : `bible/bible-reorder.jsonl`, `modeles/build/{fantasy,pixel,sketch,vulga}.jsonl`, `presets/build/test.jsonl` (et `presets/build/test.json`).

**Aucun outil ne les rejoue.** Ce sont des sorties produites par `modeles/build/*.py` (`b.write("sketch.jsonl")`, par exemple `sketch.py:99`) et par `test_presets.py:44`, puis lancées à la main dans EffectCraft. Il suffit de relancer le script générateur, depuis `modeles/build/` ou `presets/build/`, pour obtenir des chemins de la nouvelle machine. `monter.py` écrit son propre `.montage/montage.jsonl` à chaque lancement. `bible-reorder.jsonl` a servi une seule fois. Rien de bloquant donc.

## Ce qui reste incertain

1. **EffectCraft n'est pas encore compilé** (`effectcraft_cli_present: false`). `monter.py` n'a donc pas été lancé de bout en bout. Le chemin est calculé, mais le rendu réel n'est pas testé. Cela reste à faire : `python -I outils/monter.py vulga-01-gps/episode.toml` une fois `cargo build` terminé.
2. **Lua non testé** : Aseprite n'est pas installé (`C:\Program Files\Aseprite` est absent). `app.fs.joinPath`, `app.fs.filePath` et `app.fs.makeAllDirectories` existent dans l'API Lua d'Aseprite (v1.2.30 ou plus récent), mais je ne l'ai pas vérifié ici. Il faut aussi vérifier que `os.getenv` est autorisé : il fait partie de la bibliothèque `os`, que le mode `-b --script` expose normalement. Avant, `saveAs` échouait si `ico-pixel\…` n'existait pas ; maintenant le dossier est créé.
3. **Presets** : l'ancien chemin `~/Documents/EffectCraft/Presets` est conservé sous Windows, sur le modèle d'EffectCraft. Si les Documents sont redirigés vers OneDrive, EffectCraft et `monter.py` visent tous les deux `%USERPROFILE%\Documents`, ce qui reste cohérent. Mais il faudra y copier les `.ecpreset` du dépôt (`presets/`) pour que les effets à marqueur de `monter.py` les trouvent.
4. **Bureau sous WSL** : l'ancien chemin codé en dur (`/mnt/c/Users/Yehezkelou/OneDrive/Desktop`) est devenu une détection : un seul compte dans `/mnt/c/Users`, `OneDrive/Desktop` avant `Desktop`. Sur l'ancienne machine, cela retombe sur le même dossier si Yehezkelou était le seul compte. Sinon, définir `ICO_BUREAU`.
5. **Hors du périmètre autorisé, mais encore faux sur cette machine** (à confier à une autre mission) :
   - `.agents/skills/ico-directeur-artistique/SKILL.md:44-49` et `GEMINI.md:21,79` donnent encore `C:\Users\Yehezkelou\ico-pixel` et `/mnt/c/...` à Gemini ;
   - `INSTALLATION.md` § 0 décrit encore « tout dans WSL2 » ;
   - `sketch-01/sketch-01-cloud.ecproj` contient `/home/Yehezou/videos/sketch-01/sketch-01-cloud.mp4` (deux fois) ;
   - `outils/README.md` n'a pas été relu.
6. `pilote_agy.py` repère les `.mp4` cités dans la mission avec `[\w./~-]+\.mp4`, une expression qui ne reconnaît pas les chemins Windows à barres obliques inverses (`C:\…\x.mp4`). Les chemins relatifs avec `/` et l'option `--video` marchent. Je n'ai rien changé.
7. Si `ICO_VIDEOS` est définie au moment des tests, `test_racine_deduite_du_script` et `test_outils_utilisent_la_racine` échouent, ce qui est voulu puisqu'ils vérifient la valeur par défaut.
