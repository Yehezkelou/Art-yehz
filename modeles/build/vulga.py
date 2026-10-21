import sys; sys.path.insert(0, ".")
from lib import B, col

M = "VULGA - a remplir"
D = 60
FILL = "contents/group/contents/fill/color"
STROKE = "contents/group/contents/stroke/color"
BLUE, NIGHT, GREEN, PINK, YELLOW, LIGHT = "#2E86DE", "#0E1A2B", "#22C39B", "#FF5C7A", "#FFB020", "#F4F6FA"
b = B()
b.start(M, 1080, 1920, D, NIGHT)

b.solid("Fond", NIGHT, 1080, 1920)
b.fx("Fond", "Gradient Ramp", M, start=[540, 0], end=[540, 1920])
b.expr("Fond", "effects/#1/startColor", f"var c = {col(2)}; [Math.min(1, c[0]*2+0.04), Math.min(1, c[1]*2+0.04), Math.min(1, c[2]*2+0.06), 1]")
b.expr("Fond", "effects/#1/endColor", col(2))

# Zone schéma
b.shape("Zone schema", "rounded", [960, 760], [540, 860], fill="#16263D", stroke=BLUE, sw=6)
b.expr("Zone schema", FILL, f"var c = {col(2)}; [Math.min(1, c[0]*1.6+0.02), Math.min(1, c[1]*1.6+0.03), Math.min(1, c[2]*1.6+0.05), 1]")
b.expr("Zone schema", STROKE, col(1))
b.keys("Zone schema", "transform/opacity", [(1.0, 0), (1.4, 100)])
b.keys("Zone schema", "transform/scale", [(1.0, [92, 92, 100]), (1.4, [100, 100, 100])])

# Question + surligneur (trait épais sous le titre, qui se déroule depuis la gauche)
b.shape("Surligneur", "rect", [700, 26], [190, 330], fill=YELLOW)
b.expr("Surligneur", FILL, col(5))
b.c("layer.setTransform", layers=["Surligneur"], prop="anchor", value=[-350, 0, 0])
b.keys("Surligneur", "transform/scale", [(0.5, [0, 100, 100]), (0.9, [100, 100, 100])])
b.text("Question", "La grande question ?", [540, 300], font="Lilita One", style="Regular", size=88,
       fill=LIGHT, stroke=NIGHT, sw=10)
b.pop("Question", 0)

# Textes à révéler (dans la zone schéma)
for i, (t, y) in enumerate([(3, 640), (7, 800), (11, 960)], 1):
    n = f"Point {i}"
    b.text(n, f"{i}. Point {i} à remplir", [140, y], size=54, fill=LIGHT, justify="left")
    b.keys(n, "transform/opacity", [(t, 0), (t + 0.25, 100)])
    b.keys(n, "transform/position", [(t, [100, y, 0]), (t + 0.3, [140, y, 0])])

# Flèche animée (trait qui se déroule + pointe en chevron) et conclusion
b.shape("Fleche trait", "rect", [560, 14], [140, 1120], fill=PINK)
b.expr("Fleche trait", FILL, col(4))
b.c("layer.setTransform", layers=["Fleche trait"], prop="anchor", value=[-280, 0, 0])
b.keys("Fleche trait", "transform/scale", [(13, [0, 100, 100]), (13.4, [100, 100, 100])])
for name, y, rot in [("Fleche pointe haut", 1102, 40), ("Fleche pointe bas", 1138, -40)]:
    b.shape(name, "rect", [56, 14], [679, y], fill=PINK)
    b.expr(name, FILL, col(4))
    b.c("layer.setTransform", layers=[name], prop="rotation", value=rot)
    b.keys(name, "transform/opacity", [(13.35, 0), (13.45, 100)])
b.text("Conclusion fleche", "donc…", [740, 1140], font="Lilita One", style="Regular", size=60,
       fill=GREEN, justify="left")
b.pop("Conclusion fleche", 13.6)
for n in ("Zone schema", "Point 1", "Point 2", "Point 3", "Fleche trait", "Fleche pointe haut",
          "Fleche pointe bas", "Conclusion fleche", "Surligneur", "Question"):
    b.span(M, n, 0, 52)

b.text("ST 01", "Sous-titre : 20 car.\nmax, 2 lignes max", [540, 1380], size=72,
       stroke="#000000", sw=14, leading=86)
b.span(M, "ST 01", 1.5, 4.5); b.pop("ST 01", 1.5)

# Récap final (52–59 s) + sources
b.solid("Voile recap", NIGHT, 1080, 1920)
b.keys("Voile recap", "transform/opacity", [(52, 0), (52.4, 94)])
b.text("En resume", "EN RÉSUMÉ", [540, 640], size=48, fill=YELLOW, tracking=200)
b.text("Recap", "Le récap en\nune seule phrase.", [540, 780], font="Lilita One", style="Regular",
       size=88, fill=LIGHT, leading=100)
b.text("Sources", "Sources : auteur (année), site", [540, 1590], style="SemiBold", size=30, fill="#C9CFDC")
for n, t in [("Voile recap", 52), ("En resume", 52.3), ("Recap", 52.6), ("Sources", 53)]:
    b.span(M, n, t, 59)
for n, t in [("En resume", 52.3), ("Recap", 52.6)]:
    b.pop(n, t)
b.keys("Sources", "transform/opacity", [(53, 0), (53.4, 100)])

b.controls(M, [("Couleur principale", BLUE), ("Couleur fond", NIGHT), ("Couleur vert", GREEN),
               ("Couleur accent (flèches)", PINK), ("Couleur surligneur", YELLOW)])
b.signature(M, D, BLUE)
b.guide()
for layer, path, name in [("Question", "text/sourceText", "Question (titre)"),
                          ("Point 1", "text/sourceText", "Point 1"),
                          ("Point 2", "text/sourceText", "Point 2"),
                          ("Point 3", "text/sourceText", "Point 3"),
                          ("Conclusion fleche", "text/sourceText", "Conclusion de la flèche"),
                          ("Recap", "text/sourceText", "Récap en une phrase"),
                          ("Sources", "text/sourceText", "Sources"),
                          ("Controles", "effects/#1/color", "Couleur principale"),
                          ("Controles", "effects/#2/color", "Couleur fond"),
                          ("Controles", "effects/#4/color", "Couleur accent (flèches)"),
                          ("Controles", "effects/#5/color", "Couleur surligneur")]:
    b.eg(M, layer, path, name)

b.write("vulga.jsonl")
open("vulga-finish.js", "w").write(b.finish_js())
print(len(b.s), "étapes")
