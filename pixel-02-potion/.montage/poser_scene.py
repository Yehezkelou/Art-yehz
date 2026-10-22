#!/usr/bin/env python3
"""pixel-02-potion : pose la séquence de composer.py dans le projet fait par monter.py.

    python3 -I outils/monter.py pixel-02-potion/episode.toml [--ecraser]
    python3 -I pixel-02-potion/.montage/composer.py
    python3 -I pixel-02-potion/.montage/poser_scene.py      # retire Heros/Oeil/Piece, importe la scène, 3 aperçus

Dans la comp « PIXEL 270x480 », les calques provisoires du modèle (Heros, Oeil, Piece) sont retirés et
la séquence (12 i/s, 270×480, transparente) est posée à sa place, en [135, 240] (pixels entiers), sous le
titre et les sous-titres. Refuse de poser deux fois.
"""
import json, os, subprocess, sys

ICI = os.path.dirname(os.path.abspath(__file__))
EP = os.path.dirname(ICI)
sys.path.insert(0, os.path.join(EP, "..", "outils"))
import chemins  # noqa: E402

CLI = chemins.effectcraft_cli()
PROJ = os.path.join(EP, "pixel-02-potion.ecproj")
SCENE = os.path.join(ICI, "scene", "scene_0000.png")
COMP, MAIN, ITEM = "PIXEL 270x480", "PIXEL - sortie 1080x1920", "scene_[0000-0179].png"
APERCUS = [6.0, 9.5, 11.0]         # ticket, fouille, miette tendue

RETIRER_JS = r"""
var c = null; for (var i = 1; i <= app.project.numItems; i++) { var it = app.project.item(i); if (it.name === "%s" && it.numLayers !== undefined) c = it; }
var log = [];
for (var j = 1; j <= c.numLayers; j++) if (c.layer(j).name === "Scene") throw new Error("la scène est déjà posée");
var noms = ["Oeil", "Heros", "Piece"];
for (var k = 0; k < noms.length; k++) {
  var l = null; for (var j = 1; j <= c.numLayers; j++) if (c.layer(j).name === noms[k]) l = c.layer(j);
  if (l) { l.locked = false; l.remove(); log.push("retiré " + noms[k]); } else log.push("absent " + noms[k]);
}
var idx = 0; for (var j = 1; j <= c.numLayers; j++) if (c.layer(j).name === "Sol") idx = j;
writeLn(log.join(", ") + " ; Sol en " + idx);
""" % COMP


def cli(*args):
    r = subprocess.run([CLI, *args], capture_output=True, text=True)
    if r.returncode != 0:
        sys.exit(f"ERREUR effectcraft-cli {args[0]} : {(r.stderr or r.stdout).strip()[-500:]}")
    return r.stdout


def main():
    for f in (PROJ, SCENE):
        if not os.path.exists(f):
            sys.exit(f"ERREUR : {f} introuvable (lancer monter.py puis composer.py)")
    js = os.path.join(ICI, "retirer.jsx")
    with open(js, "w", encoding="utf-8", newline="\n") as f:
        f.write(RETIRER_JS)
    sortie = cli("script", js, PROJ)
    idx = int(sortie.rsplit("Sol en ", 1)[1].split()[0])     # la scène se glisse juste au-dessus du sol
    pas = [
        ("file.runScript", {"path": js}),
        ("comp.open", {"comp": COMP}),
        ("file.import", {"paths": [SCENE], "sequence": True, "frameRate": 12}),
        ("layer.addItem", {"item": ITEM, "time": 0, "index": idx, "position": [135, 240]}),
    ]
    args = ["run"]
    for cmd, p in pas:
        args += [cmd, json.dumps(p, ensure_ascii=False)]
    res = json.loads(cli(*args, "--project", PROJ, "--save", "--json"))
    verif = os.path.join(ICI, "verifier.jsx")
    with open(verif, "w", encoding="utf-8", newline="\n") as f:
        f.write('var c=null;for(var i=1;i<=app.project.numItems;i++){var it=app.project.item(i);if(it.name==="%s"&&it.numLayers!==undefined)c=it;}'
                'for(var j=1;j<=c.numLayers;j++){var l=c.layer(j);writeLn(j+" "+l.name+" "+l.transform.position.value);}' % COMP)
    calques = cli("script", verif, PROJ).strip().splitlines()
    for j, line in enumerate(calques):
        if line.split(" ", 2)[1].startswith("scene_"):
            calques[j] = line + "  <- renommé Scene"
    cli("run", "comp.open", json.dumps({"comp": COMP}), "layer.rename",
        json.dumps({"layer": ITEM, "name": "Scene"}), "--project", PROJ, "--save")
    apercus = []
    for i, t in enumerate(APERCUS, 1):
        png = os.path.join(EP, f"apercu-{i}.png")
        cli("render-frame", "--project", PROJ, "--comp", MAIN, "--time", f"{t:.3f}", "--max-side", "720", "--out", png)
        apercus.append({"image": png, "temps": t})
    print(json.dumps({"retirer": sortie.strip(), "commandes": [r.get("command") for r in res.get("result", [])],
                      "calques": calques, "apercus": apercus}, ensure_ascii=False, indent=1))


if __name__ == "__main__":
    main()
