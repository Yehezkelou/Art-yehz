#!/usr/bin/env python3
"""pixel-04-binaire3d : bruitages 8 bits et musique chiptune (avec batterie) synthétisés ici (aucun son d'autrui), mixés
sous la voix.

    python3 -I pixel-04-binaire3d/.montage/sons.py    # lit evenements.json (composer.py) → voix/mix.wav

Un son = un marqueur = un effet : chaque événement de composer.py a son bruitage, au même instant.
Mix : voix 1,0 ; bruitages ≈ 0,3 ; musique ≈ 0,06 (baissée de moitié quand la voix parle) ; crête à −1 dBFS.
"""
import array, json, math, os, random, wave

ICI = os.path.dirname(os.path.abspath(__file__))
EP = os.path.dirname(ICI)
SR = 48000
DUREE = 76.9

rnd = random.Random(7)


def carre(f, t, cyc=0.5):
    return 1.0 if (f * t) % 1.0 < cyc else -1.0


def tri(f, t):
    x = (f * t) % 1.0
    return 4 * x - 1 if x < 0.5 else 3 - 4 * x


def env(i, n, a=0.003, r=None):
    t = i / SR
    d = n / SR
    r = d * 0.7 if r is None else r
    e = min(1.0, t / a) if a else 1.0
    if t > d - r:
        e *= max(0.0, (d - t) / r)
    return e


def balayage(f0, f1, duree, vol, forme=carre, cyc=0.5):
    n = int(duree * SR)
    out, ph = [], 0.0
    for i in range(n):
        f = f0 + (f1 - f0) * i / n
        ph += f / SR
        s = (1.0 if ph % 1.0 < cyc else -1.0) if forme is carre else tri(1, ph)
        out.append(vol * s * env(i, n))
    return out


def bruit(duree, vol, filtre=0.5, montee=0.0):
    n = int(duree * SR)
    out, y = [], 0.0
    for i in range(n):
        k = filtre if not montee else min(0.95, filtre + montee * math.sin(math.pi * i / n))
        y += k * (rnd.uniform(-1, 1) - y)
        out.append(vol * y * env(i, n, 0.01, duree * 0.5))
    return out


def suite(*morceaux, ecart=0.0):
    out = []
    for m in morceaux:
        out += m + [0.0] * int(ecart * SR)
    return out


def notes(freqs, duree, vol, forme=carre):
    return suite(*[balayage(f, f, duree, vol, forme) for f in freqs])


SONS = {
    "pop": lambda: balayage(600, 1300, 0.06, 0.25),
    "pop_grave": lambda: balayage(260, 620, 0.09, 0.28),
    "pop_aigu": lambda: balayage(900, 2000, 0.06, 0.2),
    "clic": lambda: bruit(0.012, 0.35, 0.9),
    "clic3": lambda: suite(bruit(0.012, 0.35, 0.9), bruit(0.012, 0.35, 0.9), bruit(0.012, 0.35, 0.9), ecart=0.05),
    "imprime": lambda: suite(*[bruit(0.01, 0.25, 0.9) for _ in range(12)], ecart=0.025),
    "impact": lambda: [a + b for a, b in zip(balayage(110, 38, 0.32, 0.5), bruit(0.32, 0.35, 0.25) + [0] * 99999)],
    "impact_doux": lambda: balayage(170, 70, 0.16, 0.35),
    "whoosh": lambda: bruit(0.28, 0.4, 0.05, 0.5),
    "whoosh_bas": lambda: bruit(0.22, 0.45, 0.03, 0.25),
    "volet": lambda: suite(bruit(0.14, 0.3, 0.08, 0.5), bruit(0.01, 0.25, 0.9)),
    "glisse": lambda: bruit(0.15, 0.3, 0.1, 0.4),
    "zoom": lambda: balayage(220, 900, 0.16, 0.14),
    "bip": lambda: balayage(1000, 1000, 0.12, 0.18),
    "bip_bin": lambda: balayage(820, 820, 0.05, 0.14),
    "tampon": lambda: [a + b for a, b in zip(balayage(70, 45, 0.25, 0.55), bruit(0.25, 0.45, 0.2) + [0] * 99999)],
    "rayons": lambda: notes([523, 659, 784, 1047, 1319], 0.06, 0.13, tri),
    "craie": lambda: bruit(0.05, 0.18, 0.7),
    "bloup": lambda: balayage(520, 190, 0.13, 0.25, tri),
    "coupe": lambda: suite(bruit(0.03, 0.4, 0.8), balayage(1500, 1500, 0.03, 0.12)),
    "defile": lambda: notes([660, 880, 740, 990, 830, 1110, 930, 1240], 0.07, 0.11),
    "plongee": lambda: balayage(1300, 160, 0.5, 0.18),
    "allume": lambda: balayage(180, 1300, 0.3, 0.16),
    "feutre": lambda: bruit(0.32, 0.12, 0.6),
    "ciseaux": lambda: suite(bruit(0.015, 0.4, 0.9), bruit(0.05, 0.45, 0.6), ecart=0.04),
    "flash": lambda: bruit(0.05, 0.18, 0.9),
    "scintille": lambda: notes([1568, 2093, 2637, 3136], 0.05, 0.09, tri),
    "piece": lambda: suite(balayage(988, 988, 0.08, 0.2), balayage(1319, 1319, 0.32, 0.2)),
    "chute3d": lambda: suite(balayage(1400, 500, 0.12, 0.12, tri), balayage(140, 60, 0.12, 0.35)),
    "ressort": lambda: suite(*[balayage(300 + 160 * k, 600 + 200 * k, 0.05, 0.14, tri) for k in range(4)]),
    "saut": lambda: balayage(220, 880, 0.16, 0.2),
    "sifflet_chute": lambda: balayage(2200, 300, 0.14, 0.12, tri),
    "colere": lambda: [0.3 * carre(110, i / SR, 0.3) * carre(9, i / SR) * env(i, int(0.4 * SR)) for i in range(int(0.4 * SR))],
    "sueur": lambda: suite(balayage(1800, 700, 0.05, 0.12, tri), balayage(1600, 600, 0.05, 0.1, tri), ecart=0.12),
    "lettres": lambda: suite(*[bruit(0.01, 0.2, 0.9) for _ in range(6)], ecart=0.035),
    "gong": lambda: [0.35 * tri(98, i / SR) * math.exp(-i / SR * 1.6) + 0.15 * tri(147, i / SR) * math.exp(-i / SR * 2.2) for i in range(int(1.6 * SR))],
    "bits": lambda: suite(*[balayage(660 if k % 2 else 990, 660 if k % 2 else 990, 0.03, 0.1) for k in range(8)], ecart=0.02),
}


def lire_voix():
    with wave.open(os.path.join(EP, "voix", "dialogue.wav")) as w:
        assert w.getframerate() == SR and w.getnchannels() == 1 and w.getsampwidth() == 2
        a = array.array("h", w.readframes(w.getnframes()))
    return [v / 32768 for v in a]


def musique(n, voix):
    """Boucle chiptune maison : basse triangle (la min, fa, do, sol), arpège carré 25 %, 112 i/min."""
    bpm = 112
    croche = 60 / bpm / 2
    accords = [(110.0, (220.0, 261.6, 329.6)), (87.3, (174.6, 220.0, 261.6)),
               (130.8, (261.6, 329.6, 392.0)), (98.0, (196.0, 246.9, 293.7))]
    out = [0.0] * n
    # niveau de la voix lissé (pour baisser la musique quand elle parle)
    fen = SR // 10
    niv, acc = [0.0] * n, 0.0
    for i in range(min(n, len(voix))):
        acc += 0.0005 * (abs(voix[i]) - acc)
        niv[i] = acc
    for i in range(n):
        t = i / SR
        k = int(t / croche)
        basse, arp = accords[(k // 8) % 4]
        f = arp[k % 3] * (2 if (k // 3) % 2 else 1)
        dans = (t % croche) / croche
        e = max(0.0, 1 - dans * 1.4)
        v = 0.5 * tri(basse * (2 if k % 4 == 3 else 1), t) + 0.35 * carre(f, t, 0.25) * e
        dans_temps = t % (2 * croche)
        if dans_temps < 0.09:                                   # grosse caisse sur chaque temps
            v += 0.9 * math.sin(2 * math.pi * (60 + 140 * math.exp(-dans_temps * 40)) * dans_temps) * (1 - dans_temps / 0.09)
        if (t % croche) < 0.02:                                 # charleston en croches
            v += 0.25 * rnd.uniform(-1, 1) * (1 - (t % croche) / 0.02)
        baisse = 0.5 if niv[i] > 0.02 else 1.0
        fin = min(1.0, max(0.0, (75.9 - t) / 0.8))
        out[i] = 0.06 * v * baisse * fin * min(1.0, t / 0.3)
    return out


def main():
    n = int(DUREE * SR)
    voix = lire_voix()
    mix = musique(n, voix)
    for i, v in enumerate(voix[:n]):
        mix[i] += v
    with open(os.path.join(ICI, "evenements.json"), encoding="utf-8") as f:
        evs = json.load(f)
    cache = {}
    manquants = set()
    for t, nom in evs:
        if nom not in SONS:
            manquants.add(nom)
            continue
        s = cache.setdefault(nom, SONS[nom]())
        i0 = int(t * SR)
        for i, v in enumerate(s):
            if 0 <= i0 + i < n:
                mix[i0 + i] += 1.2 * v
    crete = max(abs(v) for v in mix) or 1
    g = 0.89 / crete
    out = array.array("h", (int(max(-1, min(1, v * g)) * 32767) for v in mix))
    chemin = os.path.join(EP, "voix", "mix.wav")
    with wave.open(chemin, "wb") as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR)
        w.writeframes(out.tobytes())
    print(json.dumps({"mix": chemin, "evenements": len(evs), "sons": len(cache),
                      "inconnus": sorted(manquants), "gain": round(g, 3)}, ensure_ascii=False))


if __name__ == "__main__":
    main()
