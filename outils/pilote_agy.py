#!/usr/bin/env python3
"""Pilote Antigravity (agy / Gemini) depuis Claude Code avec des profils d'agents et modèles prêts.

Usage :
    python3 -I ~/videos/outils/pilote_agy.py --liste
    python3 -I ~/videos/outils/pilote_agy.py critique "Analyse vulga-01-gps/episode.toml"
    python3 -I ~/videos/outils/pilote_agy.py rendu "Contrôle ce rendu" --video sketch-01/sketch-01-cloud.mp4
    python3 -I ~/videos/outils/pilote_agy.py da "Vérifie la planche assets/persos/tim/tim-planche.png"
    python3 -I ~/videos/outils/pilote_agy.py architecte "Implémente verifier_pixels.py" --ecrire
    python3 -I ~/videos/outils/pilote_agy.py essaim "Audit parallèle : DA + Script + Outils" --ecrire
"""
import argparse, json, os, re, shutil, subprocess, sys, time

HOME = os.path.expanduser("~")
VIDEOS_DIR = os.path.join(HOME, "videos")
EXE = ".exe" if os.name == "nt" else ""  # Windows natif : binaires Rust en .exe
AGY_BIN = shutil.which("agy") or os.path.join(HOME, ".local/bin/agy")
EC_CLI = os.path.join(HOME, "dev/vid/effectcraft/target/release/effectcraft-cli" + EXE)
FC_CLI = os.path.join(VIDEOS_DIR, "logiciel/filmcraft/target/release/filmcraft-cli" + EXE)

AGENTS = {
    "critique": {
        "skill": "ico-critique-editorial",
        "model": "gemini-4-argon-high",
        "effort": "high",
        "mode": "plan",
        "skip_perms": False,
        "desc": "Porte Script & Red-Team (idées, episode.toml, humour/chute, science, bilans M3/M6/M12)",
    },
    "da": {
        "skill": "ico-directeur-artistique",
        "model": "gemini-4-argon-high",
        "effort": "high",
        "mode": "auto",
        "skip_perms": True,
        "desc": "Direction Artistique Pixel (planches 32x32, palette ico-pixel-32, Lua Aseprite, décors, image-generator)",
    },
    "rendu": {
        "skill": "ico-controle-rendu",
        "model": "gemini-4-argon-high",
        "effort": "high",
        "mode": "plan",
        "skip_perms": False,
        "desc": "Porte Rendu & QA Multimodal (checklist § 11.2, planches contact, zones sûres 9:16, miniatures, J+7)",
    },
    "architecte": {
        "skill": "ico-architecte-usine",
        "model": "gemini-4-argon-high",
        "effort": "high",
        "mode": "auto",
        "skip_perms": True,
        "desc": "Ingénieur Pipeline & Moteur Caméra (camera.py, verifier_pixels.py, regarder.py, monter.py v2, ArtCraft CLI)",
    },
    "flash": {
        "skill": "ico-controle-rendu",
        "model": "gemini-3.8-flash-high",
        "effort": "high",
        "mode": "plan",
        "skip_perms": False,
        "desc": "Vérification ultra-rapide (sous-titres, longueurs de lignes, conformité rapide d'un lot)",
    },
    "essaim": {
        "skill": "ico-architecte-usine",
        "model": "gemini-4-argon-high",
        "effort": "high",
        "mode": "auto",
        "skip_perms": True,
        "desc": "Orchestrateur Multi-Agents (délègue en parallèle à des sous-agents research, self, image-generator)",
    },
}


def probe_video(video_path):
    """Extrait les métadonnées factuelles d'une vidéo (notamment la présence réelle d'audio)."""
    abspath = os.path.abspath(os.path.expanduser(video_path))
    if not os.path.exists(abspath):
        return {"erreur": f"Fichier introuvable : {abspath}"}

    info = {"fichier": abspath, "taille_octets": os.path.getsize(abspath)}
    ffprobe = shutil.which("ffprobe")
    if ffprobe:
        r = subprocess.run(
            [ffprobe, "-v", "quiet", "-print_format", "json", "-show_format", "-show_streams", abspath],
            capture_output=True, text=True
        )
        if r.returncode == 0:
            try:
                data = json.loads(r.stdout)
                streams = data.get("streams", [])
                v_streams = [s for s in streams if s.get("codec_type") == "video"]
                a_streams = [s for s in streams if s.get("codec_type") == "audio"]
                info["pistes_video"] = len(v_streams)
                info["pistes_audio"] = len(a_streams)
                info["audio_present"] = len(a_streams) > 0
                if v_streams:
                    v = v_streams[0]
                    info["resolution"] = f"{v.get('width')}x{v.get('height')}"
                    info["codec_video"] = v.get("codec_name")
                    info["fps"] = v.get("r_frame_rate")
                if a_streams:
                    a = a_streams[0]
                    info["codec_audio"] = a.get("codec_name")
                    info["sample_rate"] = a.get("sample_rate")
                else:
                    info["AVERTISSEMENT_AUDIO"] = "AUCUNE PISTE AUDIO DANS CE FICHIER (VIDÉO 100% MUETTE). N'invente aucune voix ni son."
                info["duree_s"] = round(float(data.get("format", {}).get("duration", 0)), 2)
                return info
            except Exception:
                pass

    # Sans ffprobe : fiche technique de FilmCraft (filmcraft-cli probe), qui lit vraiment le conteneur
    if os.path.exists(FC_CLI):
        r = subprocess.run([FC_CLI, "probe", abspath], capture_output=True, text=True)
        if r.returncode == 0:
            try:
                data = json.loads(r.stdout)
                v, audio = data.get("video") or {}, data.get("audio_streams") or []
                fr = v.get("frame_rate") or {}
                info.update(audio_present=bool(audio), pistes_audio=len(audio), codec_video=v.get("codec"),
                            resolution=f"{v.get('width')}x{v.get('height')}",
                            fps=f"{fr.get('num')}/{fr.get('den')}", duree_s=round(data.get("duration", 0) / 254016000000, 2),
                            source_sonde="filmcraft-cli probe")
                if not audio:
                    info["AVERTISSEMENT_AUDIO"] = "AUCUNE PISTE AUDIO DANS CE FICHIER (VIDÉO 100% MUETTE). N'invente aucune voix ni son."
                return info
            except Exception:
                pass

    # Dernier recours : inspecter les atomes MP4 (début + fin du fichier car moov est souvent en fin)
    try:
        size = os.path.getsize(abspath)
        with open(abspath, "rb") as f:
            head = f.read(min(size, 1024 * 1024))
            if size > 1024 * 1024:
                f.seek(max(0, size - 1024 * 1024))
                tail = f.read(1024 * 1024)
            else:
                tail = b""
        raw = head + tail
        has_vide = b"vide" in raw or b"avc1" in raw or b"hev1" in raw or b"vp09" in raw
        has_soun = b"soun" in raw or b"mp4a" in raw or b"Opus" in raw
        info["pistes_video_detectees"] = has_vide
        info["audio_present"] = has_soun
        if not has_soun:
            info["AVERTISSEMENT_AUDIO"] = (
                "AUCUN FLUX AUDIO DÉTECTÉ DANS LE CONTENEUR MP4 (VIDÉO MUETTE). "
                "INTERDICTION FORMELLE de décrire une voix, une intonation ou un bruitage."
            )
    except Exception as e:
        info["erreur_lecture"] = str(e)
    return info


def main():
    parser = argparse.ArgumentParser(description="Pilote les agents Antigravity (agy / Gemini) pour l'usine ico-vid.")
    parser.add_argument("agent", nargs="?", choices=list(AGENTS.keys()), help="Profil d'agent à mobiliser")
    parser.add_argument("mission", nargs="?", help="Instruction ou question à confier à l'agent")
    parser.add_argument("--liste", action="store_true", help="Afficher les profils d'agents et modèles disponibles")
    parser.add_argument("--model", help="Forcer un modèle précis (ex. gemini-4-argon-high, gemini-4-argon-medium, gemini-3.8-flash-high)")
    parser.add_argument("--effort", choices=["low", "medium", "high", "xhigh", "max"], help="Niveau de réflexion")
    parser.add_argument("--mode", choices=["plan", "accept-edits", "auto"], help="Mode d'exécution")
    parser.add_argument("--ecrire", "--auto", dest="ecrire", action="store_true",
                        help="Autoriser l'écriture de fichiers et l'exécution de commandes sans blocage (--mode auto --dangerously-skip-permissions)")
    parser.add_argument("--lecture", "--plan", dest="lecture", action="store_true",
                        help="Forcer le mode lecture seule (--mode plan)")
    parser.add_argument("--video", action="append", default=[],
                        help="Chemin d'une vidéo .mp4 à sonder avant l'analyse (anti-hallucination audio)")
    parser.add_argument("--sortie", help="Enregistrer la réponse Markdown dans ce fichier")
    parser.add_argument("--timeout", default="900s", help="Délai maximum (défaut : 900s)")
    args = parser.parse_args()

    if args.liste or not args.agent:
        print(json.dumps({"binaire_agy": AGY_BIN, "dossier_usine": VIDEOS_DIR, "agents": AGENTS}, ensure_ascii=False, indent=2))
        return

    if not args.mission:
        parser.error("Tu dois préciser la mission (ex: pilote_agy.py critique \"Analyse ce script\")")

    cfg = AGENTS[args.agent]
    model = args.model or cfg["model"]
    effort = args.effort or cfg["effort"]
    mode = args.mode or ("auto" if args.ecrire else ("plan" if args.lecture else cfg["mode"]))
    skip_perms = True if args.ecrire else (False if args.lecture else cfg["skip_perms"])

    # Détecter automatiquement tout fichier .mp4 mentionné dans la mission en plus de --video
    videos = list(args.video)
    for m in re.findall(r"[\w./~-]+\.mp4", args.mission):
        p = os.path.expanduser(m)
        if not os.path.isabs(p):
            p = os.path.join(VIDEOS_DIR, p)
        if os.path.exists(p) and p not in videos:
            videos.append(p)

    header_parts = [
        f"[PROFIL AGENT : {args.agent.upper()} · SKILL À ACTIVER : {cfg['skill']}]",
        f"Lis et applique les règles de ~/videos/.agents/skills/{cfg['skill']}/SKILL.md ainsi que ~/videos/GEMINI.md.",
        "Les décisions validées par @yehz (~/videos/plans/decisions.md) priment sur tout ; l'organisation du binôme est "
        "dans ~/videos/agents/README.md. Donne une preuve (chemin:ligne, commande + sortie) pour chaque fait affirmé.",
    ]
    if args.agent == "essaim":
        header_parts.append(
            "MODE ESSAIM MULTI-AGENTS : Utilise define_subagent et invoke_subagent (self, research, image-generator) "
            "pour paralléliser le travail entre sous-agents spécialisés avant de synthétiser ou d'exécuter."
        )
    if videos:
        probes = [probe_video(v) for v in videos]
        header_parts.append(
            "SONDE TECHNIQUE FACTUELLE DES VIDÉOS (VÉRITÉ TERRAIN OBLIGATOIRE — NE JAMAIS CONTREDIRE) :\n"
            + json.dumps(probes, ensure_ascii=False, indent=2)
        )

    full_prompt = "\n\n".join(header_parts) + "\n\n--- MISSION DEMANDÉE PAR CLAUDE / @YEHZ ---\n" + args.mission

    cmd = [
        AGY_BIN,
        "-p", full_prompt,
        "--model", model,
        "--effort", effort,
        "--mode", mode,
        "--print-timeout", args.timeout,
    ]
    if skip_perms:
        cmd.append("--dangerously-skip-permissions")

    r = subprocess.run(cmd, cwd=VIDEOS_DIR, capture_output=True, text=True)
    out = r.stdout.strip()
    if r.returncode != 0:
        sys.stderr.write(f"[pilote_agy] Erreur (code {r.returncode}) :\n{r.stderr}\n")
        if out:
            print(out)
        sys.exit(r.returncode)

    # Par défaut, chaque réponse est archivée dans agents/rapports/gemini/
    sortie = args.sortie or os.path.join(VIDEOS_DIR, "agents/rapports/gemini",
                                         time.strftime("%Y-%m-%d-%H%M") + f"-{args.agent}.md")
    if sortie:
        out_path = os.path.abspath(os.path.expanduser(sortie))
        os.makedirs(os.path.dirname(out_path), exist_ok=True)
        with open(out_path, "w", encoding="utf-8") as f:
            f.write(out + "\n")

    print(out)


if __name__ == "__main__":
    main()
