#!/usr/bin/env python3
"""pixel-05-vitrine3d : son (bruitages + musique maison de pixel-04, sans voix) et .mp4 de la vitrine 3D.

    python3 -I pixel-05-vitrine3d/.montage/finir.py    # 3d/vitrine/f_*.png (270×480) → ×4 pixels nets + son
Sortie : pixel-05-vitrine3d/pixel-05-vitrine3d.mp4, copies dans rendu/ et sur le Bureau. Instants : rapport
agents/rapports/claude/2026-10-22-vitrine3d.md (un son = un marqueur = un effet).
"""
import array, importlib.util, os, shutil, subprocess, sys, wave

ICI = os.path.dirname(os.path.abspath(__file__))
EP = os.path.dirname(ICI)
RACINE = os.path.dirname(EP)
sys.dont_write_bytecode = True
spec = importlib.util.spec_from_file_location("sons4", os.path.join(RACINE, "pixel-04-binaire3d", ".montage", "sons.py"))
S = importlib.util.module_from_spec(spec); spec.loader.exec_module(S)
sys.path.insert(0, os.path.join(RACINE, "outils"))
import chemins  # noqa: E402

DUREE, SR = 20.0, S.SR
EVENEMENTS = [(0.0, "rayons"), (4.0, "glisse")] + [(4.0 + 0.35 * k, "clic") for k in range(6)] + [
    (6.2, "pop"), (6.6, "scintille"), (8.0, "saut"), (8.5, "sifflet_chute"), (9.0, "chute3d"), (9.3, "sueur"),
    (9.6, "colere"), (11.0, "whoosh"), (11.0, "ressort"), (12.7, "glisse"), (13.5, "pop_aigu"), (15.0, "volet"),
    (15.5, "bloup"), (15.9, "scintille"), (16.2, "pop"), (18.0, "whoosh"), (18.6, "piece")]


def main():
    n = int(DUREE * SR)
    mix = S.musique(n, [])
    for i in range(n):                                   # fondu de fin (boucle propre)
        mix[i] *= min(1.0, (DUREE - i / SR) / 0.8) * 1.6
    for t, nom in EVENEMENTS:
        s = S.SONS[nom]()
        i0 = int(t * SR)
        for i, v in enumerate(s):
            if i0 + i < n:
                mix[i0 + i] += 1.1 * v
    g = 0.89 / (max(abs(v) for v in mix) or 1)
    wav = os.path.join(ICI, "son.wav")
    with wave.open(wav, "wb") as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR)
        w.writeframes(array.array("h", (int(max(-1, min(1, v * g)) * 32767) for v in mix)).tobytes())
    out = os.path.join(EP, "pixel-05-vitrine3d.mp4")
    subprocess.run([S.__dict__.get("FFMPEG") or _ffmpeg(), "-loglevel", "error", "-y", "-framerate", "24",
                    "-i", os.path.join(ICI, "3d", "vitrine", "f_%04d.png"), "-i", wav,
                    "-vf", "scale=iw*4:ih*4:flags=neighbor", "-c:v", "libx264", "-preset", "slow", "-crf", "12",
                    "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "192k", "-shortest", out], check=True)
    copies = [os.path.join(RACINE, "rendu", "pixel-05-vitrine3d.mp4")]
    os.makedirs(os.path.dirname(copies[0]), exist_ok=True)
    if chemins.bureau():
        copies.append(os.path.join(chemins.bureau(), "pixel-05-vitrine3d.mp4"))
    for c in copies:
        shutil.copy2(out, c)
    print(out, *copies, sep="\n")


def _ffmpeg():
    import glob
    return shutil.which("ffmpeg") or glob.glob(os.path.join(os.environ.get("LOCALAPPDATA", ""), "Microsoft", "WinGet",
                                                            "Packages", "Gyan.FFmpeg*", "*", "bin", "ffmpeg.exe"))[0]


if __name__ == "__main__":
    main()
