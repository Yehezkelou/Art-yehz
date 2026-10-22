#!/usr/bin/env python3
"""pixel-03-binaire : voix off ElevenLabs avec horodatage des caractères.

    python3 -I pixel-03-binaire/.montage/voix.py      # écrit voix/narration.mp3 et voix/alignement.json

Clé lue dans ~/.config/elevenlabs/.env (hors dépôt, jamais affichée). Le texte (narration.txt) part chez
ElevenLabs : accord de @yehz du 22/10/2026. La voix (mp3) reste sur la machine (*.mp3 ignoré par git).
"""
import base64, json, os, sys, urllib.request

EP = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
VOIX_ID = "NOpBlnGInO9m6vDvFkFC"          # « Spuds Oxley - Grandpa », bibliothèque partagée ElevenLabs
MODELE = "eleven_multilingual_v2"


def cle():
    with open(os.path.expanduser("~/.config/elevenlabs/.env"), encoding="utf-8") as f:
        for l in f:
            if l.startswith("ELEVENLABS_API_KEY="):
                return l.split("=", 1)[1].strip()
    sys.exit("ERREUR : ELEVENLABS_API_KEY absente de ~/.config/elevenlabs/.env")


def main():
    with open(os.path.join(EP, "narration.txt"), encoding="utf-8") as f:
        texte = " ".join(l.strip() for l in f if l.strip())
    corps = json.dumps({"text": texte, "model_id": MODELE,
                        "voice_settings": {"stability": 0.45, "similarity_boost": 0.8, "style": 0.35, "speed": 1.15}}).encode()
    req = urllib.request.Request(f"https://api.elevenlabs.io/v1/text-to-speech/{VOIX_ID}/with-timestamps?output_format=mp3_44100_128",
                                 data=corps, headers={"xi-api-key": cle(), "Content-Type": "application/json"})
    try:
        d = json.load(urllib.request.urlopen(req, timeout=300))
    except urllib.error.HTTPError as e:
        sys.exit(f"ERREUR ElevenLabs HTTP {e.code} : {e.read()[:400].decode(errors='replace')}")
    out = os.path.join(EP, "voix"); os.makedirs(out, exist_ok=True)
    with open(os.path.join(out, "narration.mp3"), "wb") as f:
        f.write(base64.b64decode(d["audio_base64"]))
    al = d.get("normalized_alignment") or d["alignment"]
    with open(os.path.join(out, "alignement.json"), "w", encoding="utf-8", newline="\n") as f:
        json.dump({"texte": texte, "alignement": d["alignment"]}, f, ensure_ascii=False)
    fin = d["alignment"]["character_end_times_seconds"][-1]
    print(json.dumps({"caracteres": len(texte), "duree": round(fin, 2), "voix": os.path.join(out, "narration.mp3")}, ensure_ascii=False))


if __name__ == "__main__":
    main()
