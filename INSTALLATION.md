# Installer ico-vid sur une nouvelle machine

À lire par @yehz **et** par les agents (Claude Code, Antigravity / Gemini) au premier lancement sur une machine neuve.
Objectif : retrouver exactement l'usine de l'ancienne machine (mêmes chemins, mêmes logiciels, mêmes agents).

## 0. Convention de chemins (ne pas changer)

Tout tourne **dans WSL2**, pas sous Windows natif : Claude Code, `agy`, Python, cargo, les logiciels Craft, la voix.
Ancienne machine : **Fedora Linux 44 (WSL)**. Garder Fedora évite toute surprise ; avec Ubuntu, remplacer `dnf` par `apt` et les paquets `-devel` par `-dev`.

| Quoi | Chemin attendu | Pourquoi |
|---|---|---|
| Ce dépôt | `~/videos` | les outils, skills et GEMINI.md y font référence |
| EffectCraft de production | `~/dev/vid/effectcraft` (binaire `target/release/effectcraft-cli`) | lu par `outils/monter.py` et `outils/pilote_agy.py` |
| Suite ArtCraft + VoiceStudio (sources) | `~/videos/logiciel/<nom>` | dépôts séparés, ignorés par git |
| Moteur de voix omnivoice.cpp | `~/.local/src/omnivoice.cpp` | utilisé par VoiceStudio (ses binaires `bin/` sont des fichiers vides) |
| Modèles de voix | `~/.local/share/omnivoice/models` | jamais dans git |
| Modèles Whisper (FilmCraft) | `~/.local/share/filmcraft/models` | téléchargés par FilmCraft lui-même |
| Utilisateur Linux | `Yehezou` de préférence | `modeles/build/lib.py` et les `.jsonl` de `bible/` et `modeles/build/` contiennent `/home/Yehezou/videos` en dur |
| Aseprite (Windows) | `C:\Users\<toi>\ico-pixel\` | Aseprite.exe ne lit pas `\\wsl.localhost\…` (journal n° 29) |
| Bureau Windows | `/mnt/c/Users/Yehezkelou/OneDrive/Desktop` | `monter.py --rendu` y copie le .mp4 ; si le dossier n'existe pas, la copie est simplement sautée |

Si le nom d'utilisateur Linux ou Windows change, l'agent Claude corrige ces chemins en **une** mission (`outilleur`) avant toute vidéo.

## 1. Inventaire complet des logiciels

| Logiciel | Où | Sert à | Installation |
|---|---|---|---|
| Pilote NVIDIA | Windows | GPU pour WSL2 | pilote Windows à jour ; **aucun** pilote NVIDIA dans Linux ; vérifier `nvidia-smi` dans WSL |
| Claude Code (`claude`) | WSL | orchestrateur | déjà installé ; se connecter |
| Antigravity (`agy`) | WSL | agents Gemini | déjà installé ; se connecter ; attendu dans le PATH ou `~/.local/bin/agy` |
| git, gcc, cmake, pkg-config | WSL | compiler | § 2.1 |
| Rust (rustup, cargo) | WSL | compiler les 5 Craft | § 2.1 |
| Python ≥ 3.11 | WSL | `outils/` (bibliothèque standard seulement ; ancienne machine 3.14) | § 2.1 |
| Node.js + npm | WSL | générer le plan `.docx` (`plans/plan-vX.Y.js`, paquet `docx` installé dans un dossier temporaire) | § 2.1 |
| ffmpeg / ffprobe | WSL | facultatif : sonde audio ; sinon `filmcraft-cli probe` prend le relais | § 2.1 |
| CUDA Toolkit | WSL | compiler la voix sur le GPU (`/usr/local/cuda/bin/nvcc`) | dépôt NVIDIA « CUDA on WSL » pour Fedora ; **pas** le paquet pilote |
| **EffectCraft** | WSL | montage, rendu headless (`effectcraft-cli`) | § 2.3 et § 2.4 |
| **FilmCraft** | WSL | transcription Whisper `.srt`, sonde, détection de plans, assemblage long | § 2.3, option `whisper` |
| **SoundCraft** | WSL | voix, jingle, chiptune | § 2.3 |
| **PhotoCraft** | WSL | PSD multicalques, miniatures | § 2.3 |
| **VectorCraft** | WSL | SVG logo / icônes | § 2.3 |
| **VoiceStudio** + omnivoice.cpp | WSL | voix inventée (pas de micro) | § 2.5 |
| Aseprite | Windows | dessin pixel, scripts `.lua` | installeur Windows, `C:\Program Files\Aseprite\Aseprite.exe` |
| Microsoft Word | Windows | export PDF du plan (via `powershell.exe`, COM) | facultatif |

Sur l'ancienne machine, seuls EffectCraft et FilmCraft avaient déjà été compilés ; PhotoCraft, SoundCraft et VectorCraft n'étaient que clonés. On les compile tous les cinq sur la nouvelle machine.

## 2. Installer

### 2.1 Paquets système (Fedora, avec mot de passe)

```bash
sudo dnf install -y git gcc gcc-c++ make cmake pkgconf-pkg-config python3 nodejs npm ffmpeg-free \
  libxkbcommon-devel wayland-devel libX11-devel libXrandr-devel libXi-devel mesa-libGL-devel gtk3-devel \
  alsa-lib-devel openssl-devel
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y
```

Les paquets graphiques (`libxkbcommon`… `gtk3`) servent aux fenêtres des logiciels Craft (liste de `photocraft/docs/development.md`) ; `alsa-lib` au son. Si une compilation réclame une autre bibliothèque, lire le `docs/development.md` du logiciel concerné.

### 2.2 Cloner

```bash
git clone https://github.com/Yehezkelou/Art-yehz.git ~/videos

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
```

### 2.3 Compiler la suite Craft (`~/videos/logiciel`)

Chaque logiciel a une application (fenêtre) et un `-cli` (headless, utilisé par les agents).

```bash
cd ~/videos/logiciel
(cd filmcraft   && cargo build --release -p filmcraft -p filmcraft-cli --features whisper)
(cd soundcraft  && cargo build --release -p soundcraft -p soundcraft-cli)
(cd photocraft  && cargo build --release -p photocraft -p photocraft-cli)
(cd vectorcraft && cargo build --release -p vectorcraft -p vectorcraft-cli)
(cd effectcraft && cargo build --release -p effectcraft)   # application ; le CLI de production est au § 2.4
```

FilmCraft : l'option `whisper` (transcription sur le processeur + téléchargement des modèles) n'est pas activée par défaut et elle est indispensable. Le modèle `whisper-base` se télécharge au premier `transcript.generate` (ou `transcript.downloadModel`) dans `~/.local/share/filmcraft/models`.
Les binaires sont dans `<logiciel>/target/release/`. Si un nom de paquet `-p` n'existe pas, `cargo metadata --no-deps --format-version 1` donne les bons.

### 2.4 EffectCraft de production (copie séparée, on n'y modifie rien)

```bash
mkdir -p ~/dev/vid && git clone https://github.com/storytold/effectcraft.git ~/dev/vid/effectcraft
cd ~/dev/vid/effectcraft && git checkout 9db7f3b2
cargo build --release -p effectcraft -p effectcraft-cli
```

### 2.5 Voix : VoiceStudio + omnivoice.cpp, sur le GPU

Ancienne machine : processeur seul, 36 min pour 25 s de voix (rapport `agents/rapports/claude/2026-10-22-test-voix-transcription.md`). Avec la carte graphique, on compile en CUDA.

```bash
mkdir -p ~/.local/src && git clone https://github.com/ServeurpersoCom/omnivoice.cpp.git ~/.local/src/omnivoice.cpp
cd ~/.local/src/omnivoice.cpp && git checkout 886fc07
./buildcuda.sh            # demande le CUDA Toolkit dans /usr/local/cuda ; à défaut ./buildcpu.sh
# Si gcc est trop récent pour nvcc : NVCC_CCBIN=g++-13 ./buildcuda.sh (voir son README)

# Modèles déjà convertis (Hugging Face, Apache-2.0) : https://huggingface.co/Serveurperso/OmniVoice-GGUF
mkdir -p ~/.local/share/omnivoice/models
# y mettre omnivoice-base-Q4_K_M.gguf et omnivoice-tokenizer-Q4_K_M.gguf (ceux de l'ancienne machine) ;
# avec le GPU, la version Q8_0 (meilleure qualité) devient raisonnable
```

Voix retenue par @yehz : « voix-1 » = `male, middle-aged, low pitch`, seed 7, `--lang French`.
VoiceStudio lui-même (interface) : suivre son `README.md` ; il s'appuie sur ce moteur.

## 3. Ce qui n'est PAS dans le dépôt (à copier à la main)

- `references/*.jpeg|jfif` : images d'autres artistes (droits d'auteur), **jamais publiées**. Copier depuis l'ancienne machine (clé USB). Leur description reste dans `references/README.md`.
- Les modèles de voix (660 Mo, `~/.local/share/omnivoice/models`) : retéléchargeables, ou à copier par clé USB pour gagner du temps.
- Les rendus `.mp4`, `.wav`, `.mov` : refaits depuis les projets (`monter.py --rendu`).
- `a-trier/`, `regards/` : dossiers de travail.
- Connexions (Claude, Gemini, GitHub) : à refaire sur la nouvelle machine. Ne jamais copier `~/.gemini/*creds*` ni un jeton dans ce dépôt.

## 4. Vérifier que tout marche

```bash
cd ~/videos
nvidia-smi                                               # la carte graphique est vue dans WSL
python3 -I -m unittest discover -s outils/tests          # tous verts
python3 -I outils/verifier_licences.py                   # manifeste OK
~/dev/vid/effectcraft/target/release/effectcraft-cli --help
ls ~/videos/logiciel/*/target/release/ | grep -E 'craft(-cli)?$'   # les binaires des 5 Craft
~/videos/logiciel/filmcraft/target/release/filmcraft-cli commands | grep transcript
python3 -I outils/pilote_agy.py --liste                  # agy trouvé, 6 profils
python3 -I outils/monter.py vulga-01-gps/episode.toml    # projet + 3 aperçus (refuse d'écraser sans --ecraser)
```

Puis un essai de voix courte sur le GPU (une phrase) et sa transcription FilmCraft, à comparer au rapport du test J2.

## 5. Premier message à donner à Claude Code sur la nouvelle machine

> On vient de migrer ico-vid sur une nouvelle machine. Lis CLAUDE.md, INSTALLATION.md et agents/README.md. Installe tous les logiciels de l'inventaire du § 1 en suivant le § 2 (clones aux bonnes versions, compilation des 5 Craft, EffectCraft de production, voix sur le GPU), puis lance les vérifications du § 4 et fais-moi le bilan. Ne modifie pas les fichiers du dépôt sans mon accord.

Les commandes `sudo` (paquets `dnf`, CUDA Toolkit) demandent ton mot de passe : Claude te les donne et tu les tapes toi-même avec `! sudo dnf install …` dans la session. Aseprite et Word s'installent côté Windows, à la main.

Gemini (`agy`) lit `GEMINI.md` tout seul dans `~/videos` ; ses 4 compétences sont dans `.agents/skills/`.
Les skills Claude (`video-*`, `pilote-agy`) sont dans `.claude/skills/` : rien à copier dans `~/.claude/`.
