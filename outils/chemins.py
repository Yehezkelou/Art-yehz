#!/usr/bin/env python3
"""Chemins de l'usine ico-vid, valables sous Linux/WSL (ancienne disposition ~/videos) et Windows natif.

    python -I outils/chemins.py        # affiche les chemins résolus sur cette machine (JSON)

Racine du dépôt : le dossier parent de outils/ (surcharge : variable ICO_VIDEOS).
EffectCraft de production : ~/dev/vid/effectcraft/target/release/effectcraft-cli (+ .exe sous Windows)
(surcharge : ICO_EFFECTCRAFT = chemin du binaire). Presets EffectCraft : même règle que le logiciel
($EC_PRESETS_DIR, sinon $HOME ou %USERPROFILE%/Documents/EffectCraft/Presets).
Bureau : ICO_BUREAU, sinon sous Windows le Bureau du registre puis %USERPROFILE%\\Desktop et
%USERPROFILE%\\OneDrive\\Desktop ; sous WSL, /mnt/c/Users/<seul utilisateur>/OneDrive/Desktop ou Desktop.
None si aucun n'existe (la copie sur le Bureau est alors sautée).
"""
import glob, json, os, sys

HOME = os.path.expanduser("~")
EXE = ".exe" if os.name == "nt" else ""
UTILISATEURS_SYSTEME = {"Public", "Default", "Default User", "All Users", "desktop.ini", "WsiAccount"}


def racine(env=None):
    """Racine du dépôt ico-vid (absolue)."""
    env = os.environ if env is None else env
    r = env.get("ICO_VIDEOS")
    if r:
        return os.path.abspath(os.path.expanduser(r))
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def dans_racine(*parties, env=None):
    return os.path.join(racine(env), *parties)


def effectcraft_cli(env=None, nt=None):
    """Binaire effectcraft-cli de production (absolu ; n'est pas forcément compilé)."""
    env = os.environ if env is None else env
    nt = (os.name == "nt") if nt is None else nt
    r = env.get("ICO_EFFECTCRAFT")
    if r:
        return os.path.abspath(os.path.expanduser(r))
    return os.path.join(HOME, "dev", "vid", "effectcraft", "target", "release",
                        "effectcraft-cli" + (".exe" if nt else ""))


def presets_effectcraft(env=None):
    """Dossier des presets utilisateur, calculé comme EffectCraft (crates/ui-egui/src/panels/effects_presets.rs)."""
    env = os.environ if env is None else env
    if env.get("EC_PRESETS_DIR"):
        return env["EC_PRESETS_DIR"]
    home = env.get("HOME") or env.get("USERPROFILE") or HOME
    return os.path.join(home, "Documents", "EffectCraft", "Presets")


def _bureau_registre():
    try:
        import winreg
        cle = r"Software\Microsoft\Windows\CurrentVersion\Explorer\User Shell Folders"
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, cle) as k:
            return os.path.expandvars(winreg.QueryValueEx(k, "Desktop")[0])
    except (ImportError, OSError):
        return None


def candidats_bureau(env=None, nt=None, users_dir="/mnt/c/Users"):
    """Bureaux possibles, dans l'ordre de préférence (sans vérifier qu'ils existent, sauf sous WSL)."""
    env = os.environ if env is None else env
    nt = (os.name == "nt") if nt is None else nt
    if env.get("ICO_BUREAU"):
        return [env["ICO_BUREAU"]]
    if nt:
        prof = env.get("USERPROFILE") or HOME
        reg = _bureau_registre()
        return [p for p in [reg, os.path.join(prof, "Desktop"), os.path.join(prof, "OneDrive", "Desktop")] if p]
    # Linux / WSL : un seul compte Windows réel sous /mnt/c/Users, sinon rien (pas de devinette)
    comptes = [d for d in glob.glob(os.path.join(users_dir, "*"))
               if os.path.isdir(d) and os.path.basename(d) not in UTILISATEURS_SYSTEME
               and (os.path.isdir(os.path.join(d, "Desktop")) or os.path.isdir(os.path.join(d, "OneDrive", "Desktop")))]
    if len(comptes) != 1:
        return []
    return [os.path.join(comptes[0], "OneDrive", "Desktop"), os.path.join(comptes[0], "Desktop")]


def bureau(env=None, nt=None, users_dir="/mnt/c/Users"):
    """Premier Bureau existant, ou None."""
    for p in candidats_bureau(env, nt, users_dir):
        if os.path.isdir(p):
            return p
    return None


def main():
    print(json.dumps({"racine": racine(), "effectcraft_cli": effectcraft_cli(),
                      "effectcraft_cli_present": os.path.exists(effectcraft_cli()),
                      "presets_effectcraft": presets_effectcraft(), "bureau": bureau(),
                      "python": sys.executable}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
