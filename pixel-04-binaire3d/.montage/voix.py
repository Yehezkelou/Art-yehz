#!/usr/bin/env python3
"""pixel-04-binaire3d : dialogue ElevenLabs v3 (émotions par balises), une réplique par appel, assemblé.

    python3 -I pixel-04-binaire3d/.montage/voix.py [--seulement 3,7]   # écrit voix/ligne_NN.mp3, voix/dialogue.wav,
                                                                       # voix/alignement.json (mots + instants)
Voix (bibliothèque ElevenLabs, pas de voix clonée) : N narrateur « Spuds Oxley - Grandpa », T Tim « Liam »,
M le marchand « Callum ». Clé dans ~/.config/elevenlabs/.env (hors dépôt, jamais affichée). Le texte part chez
ElevenLabs (accord de @yehz) ; les fichiers audio restent sur la machine (*.mp3, *.wav ignorés par git).
Le narrateur est accéléré ×1,2 (atempo, hauteur conservée) ; un silence de RESPIRATION sépare les répliques.
"""
import base64, json, os, re, subprocess, sys, urllib.request, wave, array

ICI = os.path.dirname(os.path.abspath(__file__))
EP = os.path.dirname(ICI)
sys.path.insert(0, os.path.join(EP, "..", "pixel-03-binaire", ".montage"))
VOIX = {"N": ("NOpBlnGInO9m6vDvFkFC", 1.2), "T": ("TX3LPaxmHKxFdv7VOQHJ", 1.0), "M": ("N2lVS1w4EtoT3dr4eOWO", 1.0)}
RESPIRATION = {"N": 0.25, "T": 0.2, "M": 0.2}       # silence après la réplique (s)
TEMPO_LIGNE = {10: 1.3, 12: 1.4}                     # tirades de chiffres : plus vives que le reste du narrateur
SR = 48000


def ffmpeg():
    import glob, shutil
    return shutil.which("ffmpeg") or glob.glob(os.path.join(os.environ.get("LOCALAPPDATA", ""), "Microsoft", "WinGet",
                                                            "Packages", "Gyan.FFmpeg*", "*", "bin", "ffmpeg.exe"))[0]


def cle():
    with open(os.path.expanduser("~/.config/elevenlabs/.env"), encoding="utf-8") as f:
        for l in f:
            if l.startswith("ELEVENLABS_API_KEY="):
                return l.split("=", 1)[1].strip()
    sys.exit("ERREUR : ELEVENLABS_API_KEY absente")


def repliques():
    out = []
    with open(os.path.join(EP, "narration.tsv"), encoding="utf-8") as f:
        for l in f:
            if l.strip() and not l.startswith("#"):
                v, t = l.rstrip("\n").split("\t")
                out.append((v, t))
    return out


def generer(k, v, texte):
    vid, _ = VOIX[v]
    corps = json.dumps({"text": texte, "model_id": "eleven_v3"}).encode()
    req = urllib.request.Request(f"https://api.elevenlabs.io/v1/text-to-speech/{vid}/with-timestamps?output_format=mp3_44100_128",
                                 data=corps, headers={"xi-api-key": cle(), "Content-Type": "application/json"})
    try:
        d = json.load(urllib.request.urlopen(req, timeout=300))
    except urllib.error.HTTPError as e:
        sys.exit(f"ERREUR ElevenLabs (ligne {k}) HTTP {e.code} : {e.read()[:300].decode(errors='replace')}")
    with open(os.path.join(EP, "voix", f"ligne_{k:02d}.mp3"), "wb") as f:
        f.write(base64.b64decode(d["audio_base64"]))
    with open(os.path.join(EP, "voix", f"ligne_{k:02d}.json"), "w", encoding="utf-8") as f:
        json.dump(d["alignment"], f, ensure_ascii=False)


def wav(k, tempo):
    sortie = os.path.join(EP, "voix", f"ligne_{k:02d}.wav")
    subprocess.run([ffmpeg(), "-loglevel", "error", "-y", "-i", os.path.join(EP, "voix", f"ligne_{k:02d}.mp3"),
                    "-af", f"atempo={tempo},silenceremove=start_periods=1:start_threshold=-45dB,areverse,silenceremove=start_periods=1:start_threshold=-45dB:start_silence=0.08,areverse", "-ar", str(SR), "-ac", "1", sortie],
                   check=True)
    with wave.open(sortie) as w:
        return array.array("h", w.readframes(w.getnframes()))


def main():
    lignes = repliques()
    seul = None
    if "--seulement" in sys.argv:
        seul = {int(x) for x in sys.argv[sys.argv.index("--seulement") + 1].split(",")}
    for k, (v, t) in enumerate(lignes):
        if seul is None or k in seul or not os.path.exists(os.path.join(EP, "voix", f"ligne_{k:02d}.mp3")):
            generer(k, v, t)
    total, mots, t0 = array.array("h"), [], 0.0
    for k, (v, texte) in enumerate(lignes):
        tempo = TEMPO_LIGNE.get(k, VOIX[v][1])
        a = json.load(open(os.path.join(EP, "voix", f"ligne_{k:02d}.json"), encoding="utf-8"))
        s = wav(k, tempo)
        ch = "".join(a["characters"])
        debut0 = None
        # mots hors balises [..] ; instants ramenés au tempo, décalés du silence de tête retiré
        propre = re.sub(r"\[[^\]]*\]", lambda m: " " * len(m.group()), ch)
        for m in re.finditer(r"[\wÀ-ÿ'-]+", propre):
            d0 = a["character_start_times_seconds"][m.start()] / tempo
            d1 = a["character_end_times_seconds"][m.end() - 1] / tempo
            if debut0 is None:
                debut0 = d0
            mots.append({"mot": m.group(), "voix": v, "ligne": k, "debut": round(t0 + d0 - debut0 + 0.02, 3),
                         "fin": round(t0 + d1 - debut0 + 0.02, 3)})
        total.extend(s)
        total.extend(array.array("h", [0]) * int(RESPIRATION[v] * SR))
        t0 = len(total) / SR
    with wave.open(os.path.join(EP, "voix", "dialogue.wav"), "wb") as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR); w.writeframes(total.tobytes())
    with open(os.path.join(EP, "voix", "alignement.json"), "w", encoding="utf-8", newline="\n") as f:
        json.dump({"duree": round(t0, 3), "mots": mots}, f, ensure_ascii=False, indent=0)
    print(json.dumps({"repliques": len(lignes), "mots": len(mots), "duree": round(t0, 2),
                      "caracteres": sum(len(t) for _, t in lignes)}, ensure_ascii=False))


if __name__ == "__main__":
    main()
