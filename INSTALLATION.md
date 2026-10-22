# Installer ico-vid sur une nouvelle machine

À lire par @yehz **et** par les agents (Claude Code, Antigravity / Gemini) au premier lancement sur une machine neuve.
Objectif : retrouver exactement l'usine de l'ancienne machine (mêmes chemins, mêmes outils, mêmes agents).

## 0. Convention de chemins (ne pas changer)

Tout tourne **dans WSL2 (Ubuntu)**, pas sous Windows natif : Claude Code, `agy`, Python, cargo, EffectCraft.

| Quoi | Chemin attendu | Pourquoi |
|---|---|---|
| Ce dépôt | `~/videos` | les outils, skills et GEMINI.md y font référence |
| EffectCraft de production | `~/dev/vid/effectcraft` (binaire `target/release/effectcraft-cli`) | lu par `outils/monter.py` et `outils/pilote_agy.py` |
| Suite ArtCraft + VoiceStudio | `~/videos/logiciel/<nom>` | dépôts séparés, ignorés par git |
| Utilisateur Linux | `Yehezou` de préférence | `modeles/build/lib.py` et les `.jsonl` de `bible/` et `modeles/build/` contiennent `/home/Yehezou/videos` en dur |
| Aseprite (Windows) | `C:\Users\<toi>\ico-pixel\` | Aseprite.exe ne lit pas `\\wsl.localhost\…` (journal n° 29) |
| Bureau Windows | `/mnt/c/Users/Yehezkelou/OneDrive/Desktop` | `monter.py --rendu` y copie le .mp4 ; si le dossier n'existe pas, la copie est simplement sautée |

Si le nom d'utilisateur Linux ou Windows change, l'agent Claude corrige ces chemins en **une** mission (`outilleur`) avant toute vidéo.

## 1. Système (une fois)

1. Windows : pilote NVIDIA à jour. **Ne pas** installer de pilote NVIDIA dans Ubuntu : WSL2 utilise celui de Windows. Vérifier dans Ubuntu : `nvidia-smi`.
2. Ubuntu (WSL2) : `sudo apt install git build-essential pkg-config python3 nodejs npm ffmpeg` puis Rust via rustup.
   Python ≥ 3.11 suffit (les outils n'utilisent que la bibliothèque standard ; ancienne machine : 3.14).
3. Claude Code (`claude`) et Antigravity (`agy`) installés **dans Ubuntu** et connectés (`agy` attendu dans le PATH ou `~/.local/bin/agy`).
4. Windows : Aseprite (`C:\Program Files\Aseprite\Aseprite.exe`).

## 2. Récupérer le code

```bash
git clone <URL-de-ce-depot> ~/videos

mkdir -p ~/videos/logiciel && cd ~/videos/logiciel
for l in effectcraft filmcraft photocraft soundcraft vectorcraft; do
  git clone https://github.com/storytold/$l.git
done
git clone https://github.com/debpalash/VoiceStudio.git

# Versions de l'ancienne machine (22 oct. 2026, aucune modification locale) : on repart des mêmes
git -C effectcraft checkout 9db7f3b2
git -C filmcraft   checkout 70f0fc7a
git -C photocraft  checkout b097800e
git -C soundcraft  checkout 7b339fe
git -C vectorcraft checkout bc1ae082
git -C VoiceStudio checkout 28bf2c7a

# EffectCraft de production : copie séparée, on n'y modifie rien
mkdir -p ~/dev/vid && git clone https://github.com/storytold/effectcraft.git ~/dev/vid/effectcraft
cd ~/dev/vid/effectcraft
git checkout 9db7f3b2            # version utilisée sur l'ancienne machine (oct. 2026)
cargo build --release -p effectcraft-cli
```

VoiceStudio : suivre son propre README (il profite du GPU). Le test J2 (voix 30 s) est dans `agents/rapports/claude/2026-10-22-test-voix-transcription.md`.

## 3. Ce qui n'est PAS dans le dépôt (à copier à la main)

- `references/*.jpeg|jfif` : images d'autres artistes (droits d'auteur), **jamais publiées**. Copier depuis l'ancienne machine (clé USB). Leur description reste dans `references/README.md`.
- Les rendus `.mp4`, `.wav`, `.mov` : refaits depuis les projets (`monter.py --rendu`).
- `a-trier/`, `regards/` : dossiers de travail.
- Connexions (Claude, Gemini, GitHub) : à refaire sur la nouvelle machine. Ne jamais copier `~/.gemini/*creds*` ni un jeton dans ce dépôt.

## 4. Vérifier que tout marche

```bash
cd ~/videos
python3 -I -m unittest discover -s outils/tests          # tous verts
python3 -I outils/verifier_licences.py                   # manifeste OK
~/dev/vid/effectcraft/target/release/effectcraft-cli --help
python3 -I outils/pilote_agy.py --liste                  # agy trouvé, 6 profils
python3 -I outils/monter.py vulga-01-gps/episode.toml    # projet + 3 aperçus (refuse d'écraser sans --ecraser)
```

## 5. Premier message à donner à Claude Code sur la nouvelle machine

> On vient de migrer ico-vid sur une nouvelle machine. Lis CLAUDE.md, INSTALLATION.md et agents/README.md. Installe ce qui manque en suivant les § 1 et 2 (clones, versions, compilation d'EffectCraft, VoiceStudio selon son README avec le GPU), puis lance les vérifications du § 4 et fais-moi le bilan. Ne modifie pas les fichiers du dépôt sans mon accord.

Les commandes `sudo` (paquets `apt`) demandent ton mot de passe : Claude te les donne et tu les tapes toi-même avec `! sudo apt install …` dans la session.

Gemini (`agy`) lit `GEMINI.md` tout seul dans `~/videos` ; ses 4 compétences sont dans `.agents/skills/`.
Les skills Claude (`video-*`, `pilote-agy`) sont dans `.claude/skills/` : rien à copier dans `~/.claude/`.
