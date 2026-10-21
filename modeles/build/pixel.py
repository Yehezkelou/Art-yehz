import sys; sys.path.insert(0, ".")
from lib import B, col

M = "PIXEL - sortie 1080x1920"
P = "PIXEL 270x480"
D = 20
X = f'comp("{M}").layer("Controles")'   # contrôles vus depuis la comp basse résolution
FILL = "contents/group/contents/fill/color"
b = B()
b.start(M, 1080, 1920, D, "#1D1B2E")

# --- comp basse résolution : 270×480 à 12 i/s (= animation « en 2s ») ---
b.c("comp.new", name=P, width=270, height=480, frameRate=12, duration=D, background="#1D1B2E",
    preserveFrameRate=True, open=True)
b.shape("Ciel", "rect", [270, 480], [135, 240], fill="#1D1B2E")
b.expr("Ciel", FILL, col(2, X))
b.shape("Lune", "ellipse", [24, 24], [214, 132], fill="#F2EDE4")
b.shape("Sol", "rect", [270, 72], [135, 444], fill="#3FB56B")
b.expr("Sol", FILL, col(3, X))
b.shape("Piece", "rect", [8, 8], [176, 352], fill="#F4C542")
b.expr("Piece", FILL, col(1, X))
b.expr("Piece", "transform/opacity", "Math.floor(time * 4) % 2 ? 100 : 55")       # scintillement
b.expr("Piece", "transform/position", "[176, 352 + (Math.floor(time * 3) % 2 ? 0 : -2), 0]")
b.shape("Heros", "rect", [16, 16], [80, 400], fill="#E5533D")
b.expr("Heros", FILL, col(4, X))
b.shape("Oeil", "rect", [4, 4], [84, 396], fill="#1D1B2E")
b.parent(["Oeil"], "Heros")
# Saut avec arc toutes les 2 s, positions entières uniquement (pixels nets)
b.expr("Heros", "transform/position", """var p = 2, d = time % p, h = 0;
if (d < 0.5) { var u = d / 0.5; h = 4 * 40 * u * (1 - u); }
[80, Math.round(400 - h), 0];""")
b.text("Titre pixel", "TITRE", [135, 80], font="Press Start 2P", style="Regular", size=16, fill="#F2EDE4")
b.expr("Titre pixel", "text/sourceText", f'comp("{M}").layer("TXT Titre").text.sourceText')
b.span(P, "Titre pixel", 0, 3)
b.text("ST 01", "SOUS-TITRE\n12 CAR. MAX", [135, 340], leading=24, font="Press Start 2P", style="Regular", size=16, fill="#F2EDE4")
b.span(P, "ST 01", 0.8, 3.5)

# --- comp de sortie ---
b.c("comp.open", comp=M)
b.c("layer.addItem", item=P, time=0, index=1)
b.c("layer.setTransform", layers=[P], prop="scale", value=[400, 400, 100])
b.c("layer.setSwitch", layers=[P], switch="quality", value=False)        # Draft = pixels nets
b.text("TXT Titre", "TITRE", [540, 200], font="Press Start 2P", style="Regular", size=32)
b.c("layer.setSwitch", layers=["TXT Titre"], switch="video", value=False)  # source cachée du titre
b.controls(M, [("Couleur principale (pièces)", "#F4C542"), ("Couleur fond", "#1D1B2E"),
               ("Couleur sol", "#3FB56B"), ("Couleur héros", "#E5533D")])
b.signature(M, D, "#F4C542")
b.guide()
for layer, path, name in [("TXT Titre", "text/sourceText", "Titre (police pixel)"),
                          ("Controles", "effects/#1/color", "Couleur principale (pièces)"),
                          ("Controles", "effects/#2/color", "Couleur fond"),
                          ("Controles", "effects/#3/color", "Couleur sol"),
                          ("Controles", "effects/#4/color", "Couleur héros")]:
    b.eg(M, layer, path, name)

b.write("pixel.jsonl")
open("pixel-finish.js", "w").write(b.finish_js())
print(len(b.s), "étapes")
