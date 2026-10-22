import json, os, sys
# presets/ du dépôt (presets/build/..), chemin absolu ; surcharge de la racine : ICO_VIDEOS
D = os.path.join(os.path.abspath(os.environ.get("ICO_VIDEOS")
                                 or os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..")), "presets", "")
S = []
c = lambda cmd, **p: S.append({"command": cmd, "params": p})
c("file.newProject")
c("comp.new", name="test 9x16", width=1080, height=1920, frameRate=24, duration=6, open=True)
tests = [  # (calque, preset, marqueur?, [(chemin, temps)])
 ("pop", "ico - Pop apparition", None, [("effects/#1/scaleHeight", 0.15), ("effects/#1/scaleHeight", 1)]),
 ("rebond", "ico - Rebond squash et stretch", None, [("effects/#5/position", 0.3), ("effects/#5/scaleHeight", 0.625)]),
 ("secousse", "ico - Secousse comique (marqueur)", 2, [("effects/#3/position", 1), ("effects/#3/position", 2.1)]),
 ("zoom", "ico - Zoom de reaction (marqueur)", 2, [("effects/#2/scaleHeight", 1), ("effects/#2/scaleHeight", 2.15), ("effects/#2/scaleHeight", 3)]),
 ("clign", "ico - Clignement auto", None, [("effects/#2/scaleHeight", 2.67)]),
 ("respi", "ico - Respiration", None, [("effects/#2/scaleHeight", 0.75)]),
 ("fondu", "ico - Transition fondu au noir", None, [("effects/#3/opacity", 0.25), ("effects/#3/opacity", 3), ("effects/#3/opacity", 5.75)]),
 ("volet", "ico - Transition volet", None, [("effects/#3/completion", 0.2), ("effects/#3/completion", 2)]),
 ("iris", "ico - Transition iris cartoon (sur solide noir)", None, [("effects/#5/outerRadius", 0.3), ("effects/#5/outerRadius", 3), ("effects/#5/center", 3)]),
]
for name, preset, mk, checks in tests:
    c("layer.newShape", kind="ellipse", name=name, size=[200, 200], fill="#ffd24a", position=[300, 700])
    c("layer.setTransform", layers=[name], prop="scale", value=[126, 126, 100])
    if mk is not None:
        c("layer.addMarker", layers=[name], time=mk)
    c("anim.applyPreset", path=D + preset + ".ecpreset", layers=[name])
    c("prop.get", layer=name, path="transform/position")
    c("prop.get", layer=name, path="transform/scale")
    for path, t in checks:
        c("prop.get", layer=name, path=path, time=t)
c("expr.errors", time=0.3); c("expr.errors", time=2.1)
c("comp.new", name="test pixel", width=270, height=480, frameRate=12, duration=4, open=True)
for name, preset, mk, checks in [
    ("degats", "ico pixel - Clignotement degats (marqueur)", 1, [("effects/#1/opacity", 1.05), ("effects/#1/opacity", 1.13), ("effects/#1/opacity", 2)]),
    ("saut", "ico pixel - Saut avec arc (marqueur)", 1, [("effects/#3/position", 1.25), ("effects/#3/position", 2)]),
    ("piece", "ico pixel - Scintillement piece", None, [("effects/#1/position", 0.4), ("effects/#1/opacity", 0.3)])]:
    c("layer.newShape", kind="rect", name=name, size=[16, 16], fill="#E5533D", position=[80, 400])
    if mk is not None:
        c("layer.addMarker", layers=[name], time=mk)
    c("anim.applyPreset", path=D + preset + ".ecpreset", layers=[name])
    for path, t in checks:
        c("prop.get", layer=name, path=path, time=t)
c("expr.errors", time=1.1)
json.dump(S, open("test.json", "w"), ensure_ascii=False)
with open("test.jsonl", "w", encoding="utf-8") as f:
    for s in S: f.write(json.dumps(s, ensure_ascii=False) + "\n")
print(len(S))
