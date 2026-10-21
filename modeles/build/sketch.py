import sys; sys.path.insert(0, ".")
from lib import B, CTRL, col

M = "SKETCH - a remplir"
D = 30
b = B()
b.start(M, 1080, 1920, D, "#1B2340")

# Fond : dégradé radial dont les deux couleurs suivent « Couleur fond »
b.solid("Fond", "#1B2340", 1080, 1920)
b.fx("Fond", "Gradient Ramp", M, start=[540, 760], end=[540, 2100], shape=1)
b.expr("Fond", "effects/#1/startColor",
       f"var c = {col(2)}; [Math.min(1, c[0]*1.9+0.05), Math.min(1, c[1]*1.9+0.05), Math.min(1, c[2]*1.9+0.08), 1]")
b.expr("Fond", "effects/#1/endColor", f"var c = {col(2)}; [c[0]*0.45, c[1]*0.45, c[2]*0.45, 1]")

# Perso (même rig que le sketch 01)
FILL = "contents/group/contents/fill/color"
STROKE = "contents/group/contents/stroke/color"
b.shape("Tete", "ellipse", [520, 520], [540, 760], fill="#FFD24A", stroke="#141826", sw=14)
b.shape("Oeil G", "ellipse", [120, 140], [455, 715], fill="#FFFFFF", stroke="#141826", sw=8)
b.shape("Oeil D", "ellipse", [120, 140], [625, 715], fill="#FFFFFF", stroke="#141826", sw=8)
b.shape("Pupille G", "ellipse", [48, 48], [465, 732], fill="#141826")
b.shape("Pupille D", "ellipse", [48, 48], [635, 732], fill="#141826")
b.shape("Bouche", "ellipse", [160, 70], [540, 895], fill="#141826")
b.expr("Tete", FILL, col(1))
for l in ("Tete", "Oeil G", "Oeil D"):
    b.expr(l, STROKE, col(3))
for l in ("Pupille G", "Pupille D", "Bouche"):
    b.expr(l, FILL, col(3))
b.parent(["Pupille G"], "Oeil G")
b.parent(["Pupille D"], "Oeil D")
b.parent(["Oeil G", "Oeil D", "Bouche"], "Tete")

b.expr("Tete", "transform/scale", f"""var tc = {CTRL}.effect(5)(1);
var base = 126, s = base;
if (time < 0.42) {{
  var u = time / 0.42;
  s = u < 0.6 ? base * 1.14 * (u / 0.6) : base * 1.14 - base * 0.14 * ((u - 0.6) / 0.4);
}}
var d = time - tc;
if (d >= 0 && d < 0.15) s = base + 26 * (d / 0.15);
else if (d >= 0.15 && d < 0.4) s = base + 26 - 18 * ((d - 0.15) / 0.25);
else if (d >= 0.4) s = base + 8;
[s, s, 100];""")
b.expr("Tete", "transform/position", f"""var tc = {CTRL}.effect(5)(1), f = {CTRL}.effect(6)(1);
var bx = 540 + Math.sin(time * 1.4) * 5, by = 760 + Math.sin(time * 2.2) * 8;
var d = time - tc;
if (d >= 0 && d < 0.75) {{
  var k = 1 - d / 0.75;
  bx += Math.sin(time * 86) * f * k; by += Math.cos(time * 71) * f * 0.66 * k;
}}
[bx, by, 0];""")
EYES = f"""var tc = {CTRL}.effect(5)(1);
var x = 100, y = 100;
var p = 3.3, dd = (time + 0.7) % p;
if (dd < 0.14) y = 100 - 92 * Math.sin(Math.PI * dd / 0.14);
var d = time - tc;
if (d >= 0 && d < 0.9) {{ x = 120; y = Math.max(y, 130); }}
[x, y, 100];"""
b.expr("Oeil G", "transform/scale", EYES)
b.expr("Oeil D", "transform/scale", EYES)
b.expr("Bouche", "transform/scale", f"""var tc = {CTRL}.effect(5)(1);
var a = 0;
try {{ a = thisComp.layer("Audio Amplitude").effect(3)(1); }} catch (e) {{ a = 0; }}
var x = 100, y = Math.min(170, 28 + a * 9);
var d = time - tc;
if (d >= 0 && d < 0.8) {{ x = 128; y = 165; }}
[x, y, 100];""")

# Textes
b.text("Nom du perso", "Nom du perso", [540, 1180], font="Lilita One", style="Regular", size=56,
       fill="#F6F1E7", stroke="#141826", sw=10)
b.span(M, "Nom du perso", 0.3, 3.0); b.pop("Nom du perso", 0.3)
b.text("Accroche", "ACCROCHE EN 2 S", [540, 300], font="Lilita One", style="Regular", size=84,
       fill="#FFD24A", stroke="#141826", sw=12)
b.span(M, "Accroche", 0, 2.2); b.pop("Accroche", 0)
b.text("ST 01", "Sous-titre : 20 car.\nmax, 2 lignes max", [540, 1380], size=72,
       stroke="#000000", sw=14, leading=86)
b.span(M, "ST 01", 0.8, 3.5); b.pop("ST 01", 0.8)
b.text("ST chute", "La chute ici.", [540, 1380], size=72, fill="#FFD24A",
       stroke="#000000", sw=14, leading=86)
b.span(M, "ST chute", 20.0, 22.5); b.pop("ST chute", 20.0)

# Contrôles (en dernier : leurs index d'effet sont fixes)
b.controls(M, [("Couleur principale", "#FFD24A"), ("Couleur fond", "#1B2340"),
               ("Couleur contour", "#141826"), ("Couleur accent", "#FF5A4E")],
           [("Temps de la chute (s)", 20), ("Force secousse", 30)])
b.signature(M, D, "#FFD24A")
b.guide()

for layer, path, name in [("Accroche", "text/sourceText", "Accroche (2 premières s)"),
                          ("Nom du perso", "text/sourceText", "Nom du perso"),
                          ("Controles", "effects/#1/color", "Couleur principale"),
                          ("Controles", "effects/#2/color", "Couleur fond"),
                          ("Controles", "effects/#5/slider", "Temps de la chute (s)"),
                          ("Controles", "effects/#6/slider", "Force secousse")]:
    b.eg(M, layer, path, name)

b.write("sketch.jsonl")
open("sketch-finish.js", "w").write(b.finish_js())
print(len(b.s), "étapes")
