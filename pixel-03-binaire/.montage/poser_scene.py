#!/usr/bin/env python3
"""pixel-03-binaire : pose la séquence de composer.py (1080×1920, 24 i/s, opaque) dans le projet de monter.py.

    python3 -I outils/monter.py pixel-03-binaire/episode.toml [--ecraser]
    python3 -I pixel-03-binaire/.montage/composer.py && python3 -I pixel-03-binaire/.montage/sons.py
    python3 -I pixel-03-binaire/.montage/poser_scene.py      # vide la comp pixel, pose la scène, 3 aperçus

La comp « PIXEL 270x480 » (12 i/s) ne garde que les sous-titres (sans fondu d'opacité) : ciel, sol, lune,
héros provisoire et titre sont retirés (l'accroche est l'équation de la scène 1). La scène va dans la comp de sortie (24 i/s),
sous la comp pixel et sous la signature, à 100 % en [540, 960] : aucun rééchantillonnage. Refuse de
poser deux fois.
"""
import json, os, subprocess, sys

ICI = os.path.dirname(os.path.abspath(__file__))
EP = os.path.dirname(ICI)
sys.path.insert(0, os.path.join(EP, "..", "outils"))
import chemins  # noqa: E402

CLI = chemins.effectcraft_cli()
PROJ = os.path.join(EP, "pixel-03-binaire.ecproj")
SCENE = os.path.join(ICI, "scene", "scene_0000.png")
COMP, MAIN = "PIXEL 270x480", "PIXEL - sortie 1080x1920"
APERCUS = [6.8, 23.5, 49.6]          # le 4 du ticket, 0,333… à l'infini, l'erreur entourée

VIDER_JS = r"""
function comp(n) { for (var i = 1; i <= app.project.numItems; i++) { var it = app.project.item(i); if (it.name === n && it.numLayers !== undefined) return it; } }
function retirer(c, noms, log) {
  for (var k = 0; k < noms.length; k++) {
    var l = null; for (var j = 1; j <= c.numLayers; j++) if (c.layer(j).name === noms[k]) l = c.layer(j);
    if (l) { l.locked = false; l.remove(); log.push("retiré " + noms[k]); } else log.push("absent " + noms[k]);
  }
}
var p = comp("%s"), m = comp("%s"), log = [];
for (var j = 1; j <= m.numLayers; j++) if (m.layer(j).name === "Scene") throw new Error("la scène est déjà posée");
retirer(p, ["Titre pixel", "Oeil", "Heros", "Piece", "Sol", "Lune", "Ciel"], log);
retirer(m, ["TXT Titre"], log);
// sous-titres : pas de fondu d'opacité (à 12 i/s le texte serait invisible 1/12 s sur sa bande sombre) ;
// le rebond d'échelle de la bible reste
var ko = 0;
for (var j = 1; j <= p.numLayers; j++) { var l = p.layer(j); if (l.name.indexOf("Sous-titre") !== 0) continue;
  var o = l.transform.opacity; ko += o.numKeys; while (o.numKeys > 0) o.removeKey(1); o.setValue(100); }
log.push(ko + " clés d'opacité retirées");
var idx = 0; for (var j = 1; j <= m.numLayers; j++) if (m.layer(j).name === "%s") idx = j;
writeLn(log.join(", ") + " ; pixel en " + idx);
""" % (COMP, MAIN, COMP)


def cli(*args):
    r = subprocess.run([CLI, *args], capture_output=True, text=True)
    if r.returncode != 0:
        sys.exit(f"ERREUR effectcraft-cli {args[0]} : {(r.stderr or r.stdout).strip()[-500:]}")
    return r.stdout


def main():
    for f in (PROJ, SCENE):
        if not os.path.exists(f):
            sys.exit(f"ERREUR : {f} introuvable (lancer monter.py puis composer.py)")
    n = len([f for f in os.listdir(os.path.dirname(SCENE)) if f.endswith(".png")])
    item = f"scene_[0000-{n - 1:04d}].png"
    js = os.path.join(ICI, "vider.jsx")
    with open(js, "w", encoding="utf-8", newline="\n") as f:
        f.write(VIDER_JS)
    sortie = cli("script", js, PROJ)
    idx = int(sortie.rsplit("pixel en ", 1)[1].split()[0])
    pas = [
        ("file.runScript", {"path": js}),
        ("comp.open", {"comp": MAIN}),
        ("file.import", {"paths": [SCENE], "sequence": True, "frameRate": 24}),
        ("layer.addItem", {"item": item, "time": 0, "index": idx + 1, "position": [540, 960]}),
        ("layer.rename", {"layer": item, "name": "Scene"}),
    ]
    args = ["run"]
    for cmd, p in pas:
        args += [cmd, json.dumps(p, ensure_ascii=False)]
    cli(*args, "--project", PROJ, "--save", "--json")
    apercus = []
    for i, t in enumerate(APERCUS, 1):
        png = os.path.join(EP, f"apercu-{i}.png")
        cli("render-frame", "--project", PROJ, "--comp", MAIN, "--time", f"{t:.3f}", "--max-side", "720", "--out", png)
        apercus.append({"image": png, "temps": t})
    print(json.dumps({"vider": sortie.strip(), "scene": item, "apercus": apercus}, ensure_ascii=False, indent=1))


if __name__ == "__main__":
    main()
