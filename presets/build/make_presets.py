"""Génère les presets ico-vid (.ecpreset) à partir des effets d'un preset enregistré par EffectCraft.

catalog-effets.ecpreset contient une instance de chaque effet utilisé (Transform, Slider Control,
Linear Wipe, Iris Wipe), sérialisée par le logiciel lui-même : on la copie, on la renomme et on
pose valeurs et expressions. Les presets ne touchent à aucune propriété du calque (seulement à
leurs propres effets) : appliquer un preset ne déplace ni ne redimensionne jamais le calque.
"""
import copy, json, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
CAT = {g["match"]: g for g in json.load(open(os.path.join(HERE, "catalog-effets.ecpreset")))["effects"]}
CENTER = "[thisLayer.width / 2, thisLayer.height / 2]"
# Déclencheur « au marqueur » : dernier marqueur du calque à ou avant l'instant courant (aucun = rien)
MK = ("var t0 = -1; for (var i = 1; i <= marker.numKeys; i++) { if (marker.key(i).time <= time) t0 = marker.key(i).time; }\n"
      "var d = t0 < 0 ? -1 : time - t0;\n")


def effect(match, name, values=None, exprs=None):
    g = copy.deepcopy(CAT[match])
    g["name"] = name
    for ch in g["children"]:
        m = ch.get("match")
        ch.pop("expr", None)
        if values and m in values:
            ch["value"]["v"] = values[m]
        if exprs and m in exprs:
            ch["expr"] = {"enabled": True, "text": exprs[m]}
    return g


def slider(name, v):
    return effect("ec.control.slider", name, {"slider": float(v)})


def transform(name, exprs, uniform=True):
    e = {"anchor": CENTER, "position": CENTER}
    e.update(exprs)
    return effect("ec.distort.transform", name, {"uniform": uniform}, e)


def S(name):
    return f'effect("{name}")("Slider")'


INOUT = lambda a, b: (f"var a = {S(a)}, b = {S(b)}, k = 1;\n"
                      "if (a > 0) k = Math.min(k, (time - inPoint) / a);\n"
                      "if (b > 0) k = Math.min(k, (outPoint - time) / b);\n"
                      "k = Math.max(0, Math.min(1, k));\n")

P = {}
P["ico - Pop apparition"] = [transform("ico Pop", {
    "scaleHeight": "var d = time - inPoint, k = 100;\nif (d < 0.15) k = 110 * d / 0.15;\nelse if (d < 0.27) k = 110 - 10 * (d - 0.15) / 0.12;\nk;",
    "opacity": "Math.max(0, Math.min(100, (time - inPoint) / 0.08 * 100));"})]

BOUNCE = (f"var h = {S('Hauteur rebond (px)')}, f = {S('Rebonds par seconde')}, am = {S('Amortissement')};\n"
          "var d = Math.max(0, time - inPoint), a = Math.abs(Math.sin(Math.PI * d * f)), dec = Math.exp(-am * d);\n"
          "var c = Math.max(0, 1 - a / 0.2) * dec;\n")
PIVOT = f"{CENTER} + [0, {S('Pivot vers le bas (px)')}]"
P["ico - Rebond squash et stretch"] = [
    slider("Hauteur rebond (px)", 300), slider("Rebonds par seconde", 1.6), slider("Amortissement", 0.5),
    slider("Pivot vers le bas (px)", 0),
    transform("ico Rebond", {"anchor": PIVOT, "position": BOUNCE + PIVOT + " + [0, -h * a * dec];",
                             "scaleWidth": BOUNCE + "100 + 25 * c;", "scaleHeight": BOUNCE + "100 - 25 * c;"},
              uniform=False)]

P["ico - Secousse comique (marqueur)"] = [
    slider("Force secousse", 30), slider("Durée secousse (s)", 0.6),
    transform("ico Secousse", {"position": MK + f"var F = {S('Force secousse')}, L = {S('Durée secousse (s)')}, o = [0, 0];\n"
              "if (d >= 0 && d < L) { var k = 1 - d / L; o = [Math.sin(time * 86) * F * k, Math.cos(time * 71) * F * 0.66 * k]; }\n"
              f"{CENTER} + o;"})]

P["ico - Zoom de reaction (marqueur)"] = [
    slider("Zoom réaction %", 20),
    transform("ico Zoom", {"scaleHeight": MK + f"var Z = {S('Zoom réaction %')}, k = 0;\n"
              "if (d >= 0 && d < 0.15) k = Z * d / 0.15;\n"
              "else if (d >= 0.15 && d < 0.4) k = Z - Z * 0.7 * (d - 0.15) / 0.25;\n"
              "else if (d >= 0.4) k = Z * 0.3;\n100 + k;"})]

P["ico - Clignement auto"] = [
    slider("Intervalle clignement (s)", 3.3),
    transform("ico Clignement", {"scaleHeight": f"var p = {S('Intervalle clignement (s)')}, dd = (time + 0.7) % p;\n"
              "dd < 0.14 ? 100 - 92 * Math.sin(Math.PI * dd / 0.14) : 100;"}, uniform=False)]

P["ico - Respiration"] = [
    slider("Amplitude respiration %", 1.2),
    transform("ico Respiration", {"scaleHeight": f"100 + Math.sin(time * 2.1) * {S('Amplitude respiration %')};",
                                  "scaleWidth": f"100 - Math.sin(time * 2.1) * {S('Amplitude respiration %')} * 0.5;"},
              uniform=False)]

P["ico - Transition fondu au noir"] = [
    slider("Fondu entrée (s)", 0.5), slider("Fondu sortie (s)", 0.5),
    transform("ico Fondu", {"opacity": INOUT("Fondu entrée (s)", "Fondu sortie (s)") + "k * 100;"})]

P["ico - Transition volet"] = [
    slider("Volet entrée (s)", 0.4), slider("Volet sortie (s)", 0),
    effect("ec.transition.linearwipe", "ico Volet", {"feather": 30.0},
           {"completion": INOUT("Volet entrée (s)", "Volet sortie (s)") + "(1 - k) * 100;"})]

P["ico - Transition iris cartoon (sur solide noir)"] = [
    slider("Iris ouverture (s)", 0.6), slider("Iris fermeture (s)", 0.8),
    slider("Iris décalage X", 0), slider("Iris décalage Y", 0),
    effect("ec.transition.iriswipe", "ico Iris", {"points": 48.0}, {
        "center": f"{CENTER} + [{S('Iris décalage X')}, {S('Iris décalage Y')}];",
        "outerRadius": INOUT("Iris ouverture (s)", "Iris fermeture (s)") +
        "var R = Math.sqrt(thisLayer.width * thisLayer.width + thisLayer.height * thisLayer.height) / 2 + 40;\nR * k;"})]

P["ico pixel - Clignotement degats (marqueur)"] = [transform("ico Degats", {
    "opacity": MK + "(d >= 0 && d < 0.6) ? (Math.floor(d * 12) % 2 ? 0 : 100) : 100;"})]

P["ico pixel - Saut avec arc (marqueur)"] = [
    slider("Hauteur saut (px)", 40), slider("Durée saut (s)", 0.5),
    transform("ico Saut", {"position": MK + f"var H = {S('Hauteur saut (px)')}, L = {S('Durée saut (s)')}, h = 0;\n"
              "if (d >= 0 && d < L) { var u = d / L; h = Math.round(4 * H * u * (1 - u)); }\n"
              f"{CENTER} + [0, -h];"})]

P["ico pixel - Scintillement piece"] = [transform("ico Scintillement", {
    "opacity": "Math.floor(time * 4) % 2 ? 100 : 55;",
    "position": f"{CENTER} + [0, Math.floor(time * 3) % 2 ? 0 : -2];"})]

out = sys.argv[1]
os.makedirs(out, exist_ok=True)
for name, fx in P.items():
    doc = {"effectcraftAnimationPreset": 1, "name": name, "properties": [], "effects": fx}
    with open(os.path.join(out, name + ".ecpreset"), "w", encoding="utf-8") as f:
        json.dump(doc, f, ensure_ascii=False, indent=1)
print(len(P), "presets ->", out)
