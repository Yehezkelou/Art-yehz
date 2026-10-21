import sys; sys.path.insert(0, ".")
from lib import B, col

M = "FANTASY - episode"
GEN, EP, DEC = "Generique", "Titre episode", "Decor parallaxe"
SIG, GUIDE = "Signature 16:9", "Guide zones 16:9"
D = 90
X = f'comp("{M}").layer("Controles")'
FILL = "contents/group/contents/fill/color"
GOLD, NIGHT, MOSS, MAGIC, PARCH = "#C9A227", "#0F2A2E", "#2F6B4F", "#7A4FB3", "#E8D9B5"
W, H = 1920, 1080
b = B()
b.start(M, W, H, D, NIGHT)

def src(layer_in_precomp, txt_layer):
    b.expr(layer_in_precomp, "text/sourceText", f'comp("{M}").layer("{txt_layer}").text.sourceText')

# --- Décor en 3 plans + brume + particules (parallaxe par expression) ---
b.c("comp.new", name=DEC, width=W, height=H, frameRate=24, duration=D, background=NIGHT, open=True)
b.solid("Ciel", NIGHT, W, H)
b.fx("Ciel", "Gradient Ramp", DEC, start=[960, 0], end=[960, 1080])
b.expr("Ciel", "effects/#1/startColor", f"var c = {col(2, X)}; [Math.min(1, c[0]*2.2+0.06), Math.min(1, c[1]*2.2+0.06), Math.min(1, c[2]*2.2+0.1), 1]")
b.expr("Ciel", "effects/#1/endColor", col(2, X))
b.shape("Lune", "ellipse", [150, 150], [1480, 230], fill=PARCH)
PLANES = [("Plan loin", [4200, 900], 820, 0.25, 0.55), ("Plan milieu", [4000, 700], 980, 0.6, 0.8),
          ("Premier plan", [4400, 520], 1120, 1.2, 0.0)]
for name, size, y, f, k in PLANES:
    b.shape(name, "ellipse", size, [1300, y], fill=MOSS)
    if k:   # plan éclairci/assombri à partir de « Couleur mousse »
        b.expr(name, FILL, f"var c = {col(3, X)}; [c[0]*{k}, c[1]*{k}, c[2]*{k}, 1]")
    else:   # premier plan : couleur fond assombrie (silhouette)
        b.expr(name, FILL, f"var c = {col(2, X)}; [c[0]*0.5, c[1]*0.5, c[2]*0.5, 1]")
    b.expr(name, "transform/position", f"[1300 - time * {X}.effect(5)(1) * {f}, {y}, 0]")
# Brume calculée en 480×270 puis agrandie ×4 (630 ms → 42 ms par image)
b.solid("Brume", "#FFFFFF", 480, 270)
b.c("layer.setTransform", layers=["Brume"], prop="scale", value=[400, 400, 100])
b.fx("Brume", "Fractal Noise", DEC, contrast=160, brightness=-35, transform__scale=175, complexity=3)
b.expr("Brume", "effects/#1/evolution", "time * 25")
b.expr("Brume", "effects/#1/transform/offset", "[0.5 + time * 0.004, 0.5]")
b.c("layer.setBlendMode", layers=["Brume"], mode="Screen")
b.c("layer.setTransform", layers=["Brume"], prop="opacity", value=22)
b.solid("Particules", "#000000", W, H)
b.fx("Particules", "CC Particle Systems II", DEC, birthRate=0.8, longevity=6,
     producer__position=[0.5, 0.75], producer__radiusX=1000, producer__radiusY=300,
     physics__animation=1, physics__velocity=0.25, physics__gravity=-0.05,
     particle__particleType=2, particle__birthSize=0.12, particle__deathSize=0.03,
     particle__maxOpacity=80, particle__transferMode=2)
b.expr("Particules", "effects/#1/particle/birthColor", col(1, X))
b.expr("Particules", "effects/#1/particle/deathColor", col(4, X))
b.c("layer.setBlendMode", layers=["Particules"], mode="Add")

# --- Générique d'ouverture (4 s) ---
b.c("comp.new", name=GEN, width=W, height=H, frameRate=24, duration=4, background="#000000", open=True)
b.solid("Fond generique", "#000000", W, H)
b.fx("Fond generique", "Gradient Ramp", GEN, start=[960, 540], end=[960, 1500], shape=1)
b.expr("Fond generique", "effects/#1/startColor", col(2, X))
b.set("Fond generique", "effects/#1/endColor", "#000000")
b.text("Titre serie", "LA QUÊTE DE ...", [960, 580], font="Lilita One", style="Regular", size=150,
       fill=GOLD, stroke=NIGHT, sw=10)
src("Titre serie", "TXT Titre serie")
b.keys("Titre serie", "transform/scale", [(0, [94, 94, 100]), (4, [104, 104, 100])])
b.keys("Titre serie", "transform/opacity", [(0, 0), (0.6, 100), (3.4, 100), (4, 0)])
b.text("Sous-titre serie", "une série ico-vid", [960, 680], size=40, fill=PARCH)
b.keys("Sous-titre serie", "transform/opacity", [(0.8, 0), (1.4, 100), (3.4, 100), (4, 0)])

# --- Titre d'épisode (3 s, par-dessus le décor) ---
b.c("comp.new", name=EP, width=W, height=H, frameRate=24, duration=3, background="#000000", open=True)
b.text("Numero episode", "ÉPISODE 1", [960, 470], size=48, fill=PARCH, tracking=200)
src("Numero episode", "TXT Numero episode")
b.text("Titre ep", "Le titre de l'épisode", [960, 600], font="Lilita One", style="Regular", size=110,
       fill=GOLD, stroke=NIGHT, sw=10)
src("Titre ep", "TXT Titre episode")
for l in ("Numero episode", "Titre ep"):
    b.keys(l, "transform/opacity", [(0, 0), (0.5, 100), (2.4, 100), (3, 0)])
b.pop("Titre ep", 0.15)

# --- Signature 16:9 (1 s) ---
b.c("comp.new", name=SIG, width=W, height=H, frameRate=24, duration=1, background="#101218", open=True)
b.solid("Fond signature", "#101218", W, H)
b.text("Nom chaine", "ico-vid", [960, 580], font="Lilita One", style="Regular", size=150,
       fill=GOLD, stroke="#141826", sw=14)
b.text("Pseudo", "@yehz", [960, 660], size=44, fill="#F6F1E7")
b.keys("Nom chaine", "transform/scale", [(0, [0, 0, 100]), (0.17, [118, 118, 100]), (0.29, [96, 96, 100]),
                                         (0.38, [100, 100, 100]), (0.85, [100, 100, 100]), (1.0, [108, 108, 100])])
b.keys("Pseudo", "transform/opacity", [(0.25, 0), (0.42, 100)])

# --- Guide 16:9 : zone titre 90 % + zone sous-titres ---
b.c("comp.new", name=GUIDE, width=W, height=H, frameRate=24, duration=1, background="#000000", open=True)
for name, w, h, x, y in [("Bord haut", W, 54, 960, 27), ("Bord bas", W, 54, 960, 1053),
                         ("Bord gauche", 96, H, 48, 540), ("Bord droit", 96, H, 1872, 540)]:
    b.solid(name, "#FF3B30", w, h, [x, y])
    b.c("layer.setTransform", layers=[name], prop="opacity", value=55)
b.solid("Zone sous-titres", "#0A84FF", 1440, 150, [960, 925])
b.c("layer.setTransform", layers=["Zone sous-titres"], prop="opacity", value=40)

# --- Comp principale ---
b.c("comp.open", comp=M)
b.c("layer.addItem", item=DEC, time=0, index=1)
b.shape("Heros (a remplacer)", "rounded", [130, 230], [700, 800], fill=PARCH, stroke=NIGHT, sw=8)
b.shape("Tete heros", "ellipse", [110, 110], [700, 630], fill=PARCH, stroke=NIGHT, sw=8)
b.parent(["Tete heros"], "Heros (a remplacer)")
b.expr("Heros (a remplacer)", "transform/scale", "var s = Math.sin(time * 2.1) * 1.2; [100 - s * 0.5, 100 + s, 100]")
b.c("layer.addItem", item=EP, time=4, index=1)
b.c("layer.addItem", item=GEN, time=0, index=1)
b.text("ST 01", "Sous-titre : 2 lignes max,\nreste dans la zone bleue", [960, 905], size=54,
       stroke="#000000", sw=10, leading=64)
b.span(M, "ST 01", 7.5, 10.5); b.pop("ST 01", 7.5)
# Carton « à suivre » (85–89 s)
b.solid("Voile a suivre", "#000000", W, H)
b.keys("Voile a suivre", "transform/opacity", [(85, 0), (85.8, 75)])
b.span(M, "Voile a suivre", 85, 89)
b.text("A suivre", "À suivre…", [960, 560], font="Lilita One", style="Regular", size=130,
       fill=GOLD, stroke=NIGHT, sw=10)
b.span(M, "A suivre", 85.4, 89); b.pop("A suivre", 85.4)
b.text("Episode suivant", "Prochain épisode : ...", [960, 650], size=44, fill=PARCH)
src_main = "TXT Episode suivant"
b.expr("Episode suivant", "text/sourceText", f'thisComp.layer("{src_main}").text.sourceText')
b.span(M, "Episode suivant", 86, 89)
b.keys("Episode suivant", "transform/opacity", [(86, 0), (86.5, 100)])
# Sources cachées des textes exposés
for name, value in [("TXT Titre serie", "LA QUÊTE DE ..."), ("TXT Numero episode", "ÉPISODE 1"),
                    ("TXT Titre episode", "Le titre de l'épisode"), ("TXT Episode suivant", "Prochain épisode : ...")]:
    b.text(name, value, [960, 100], size=30)
    b.c("layer.setSwitch", layers=[name], switch="video", value=False)
b.controls(M, [("Couleur principale (or)", GOLD), ("Couleur fond (nuit)", NIGHT),
               ("Couleur mousse", MOSS), ("Couleur magie", MAGIC)],
           [("Vitesse caméra (px/s)", 6)])
b.c("layer.addItem", item=SIG, time=D - 1, index=1)
b.guide(GUIDE)
for layer, path, name in [("TXT Titre serie", "text/sourceText", "Titre de la série"),
                          ("TXT Numero episode", "text/sourceText", "Numéro d'épisode"),
                          ("TXT Titre episode", "text/sourceText", "Titre de l'épisode"),
                          ("TXT Episode suivant", "text/sourceText", "Carton « à suivre »"),
                          ("Controles", "effects/#1/color", "Couleur principale (or)"),
                          ("Controles", "effects/#2/color", "Couleur fond (nuit)"),
                          ("Controles", "effects/#3/color", "Couleur mousse"),
                          ("Controles", "effects/#4/color", "Couleur magie"),
                          ("Controles", "effects/#5/slider", "Vitesse caméra (px/s)")]:
    b.eg(M, layer, path, name)

b.write("fantasy.jsonl")
open("fantasy-finish.js", "w").write(b.finish_js())
print(len(b.s), "étapes")
