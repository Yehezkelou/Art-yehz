"""Mouvements « rapides » ico-vid : une expression posée sur la transformation du calque.

Contrairement aux presets .ecpreset (qui passent par l'effet Transform, ~1 s par image sur cette
machine), ces expressions ne coûtent rien au rendu, gardent la valeur du calque (`value`) et
entraînent les calques enfants (un perso rigé bouge en entier). Elles remplacent l'expression
déjà présente sur la propriété visée.

    python3 -I rapides.py <dossier>   # écrit un script .jsonl par mouvement (calque sélectionné)
"""
import json, os, sys

MK = ("var t0 = -1; for (var i = 1; i <= marker.numKeys; i++) { if (marker.key(i).time <= time) t0 = marker.key(i).time; }\n"
      "var d = t0 < 0 ? -1 : time - t0;\n")

# nom -> (description, [(chemin, expression)]) ; réglages en tête de chaque expression
RAPIDES = {
    "secousse": ("Secousse comique à chaque marqueur", [("transform/position", MK +
        "var F = 30, L = 0.6;   // force (px), durée (s)\n"
        "var o = [0, 0];\nif (d >= 0 && d < L) { var k = 1 - d / L; o = [Math.sin(time * 86) * F * k, Math.cos(time * 71) * F * 0.66 * k]; }\n"
        "value + o;")]),
    "zoom": ("Zoom de réaction à chaque marqueur", [("transform/scale", MK +
        "var Z = 20;   // zoom en %\nvar k = 0;\n"
        "if (d >= 0 && d < 0.15) k = Z * d / 0.15;\nelse if (d >= 0.15 && d < 0.4) k = Z - Z * 0.7 * (d - 0.15) / 0.25;\nelse if (d >= 0.4) k = Z * 0.3;\n"
        "var v = value.slice(); v[0] *= 1 + k / 100; v[1] *= 1 + k / 100; v;")]),
    "pop": ("Pop d'apparition au point d'entrée", [
        ("transform/scale", "var d = time - inPoint, k = 1;\nif (d < 0.15) k = 1.1 * d / 0.15;\nelse if (d < 0.27) k = 1.1 - 0.1 * (d - 0.15) / 0.12;\nvar v = value.slice(); v[0] *= k; v[1] *= k; v;"),
        ("transform/opacity", "value * Math.max(0, Math.min(1, (time - inPoint) / 0.08));")]),
    "respiration": ("Respiration en boucle", [("transform/scale",
        "var A = 1.2;   // amplitude en %\nvar s = Math.sin(time * 2.1) * A / 100;\nvar v = value.slice(); v[0] *= 1 - s * 0.5; v[1] *= 1 + s; v;")]),
    "clignement": ("Clignement automatique (sur un œil)", [("transform/scale",
        "var P = 3.3;   // intervalle (s)\nvar dd = (time + 0.7) % P;\nvar y = dd < 0.14 ? 1 - 0.92 * Math.sin(Math.PI * dd / 0.14) : 1;\nvar v = value.slice(); v[1] *= y; v;")]),
    "rebond": ("Rebond squash & stretch depuis le point d'entrée", [
        ("transform/position", "var H = 300, F = 1.6, AM = 0.5;   // hauteur (px), rebonds/s, amortissement\n"
         "var d = Math.max(0, time - inPoint), a = Math.abs(Math.sin(Math.PI * d * F)), dec = Math.exp(-AM * d);\nvalue - [0, H * a * dec];"),
        ("transform/scale", "var F = 1.6, AM = 0.5;\nvar d = Math.max(0, time - inPoint), a = Math.abs(Math.sin(Math.PI * d * F)), dec = Math.exp(-AM * d);\n"
         "var c = Math.max(0, 1 - a / 0.2) * dec;\nvar v = value.slice(); v[0] *= 1 + 0.25 * c; v[1] *= 1 - 0.25 * c; v;")]),
    "fondu": ("Fondu entrée + sortie (0,5 s)", [("transform/opacity",
        "var A = 0.5, B = 0.5;   // entrée, sortie (s) ; 0 = pas de fondu\nvar k = 1;\n"
        "if (A > 0) k = Math.min(k, (time - inPoint) / A);\nif (B > 0) k = Math.min(k, (outPoint - time) / B);\nvalue * Math.max(0, Math.min(1, k));")]),
    "pixel-degats": ("Pixel : clignotement de dégâts à chaque marqueur", [("transform/opacity", MK +
        "(d >= 0 && d < 0.6) ? (Math.floor(d * 12) % 2 ? 0 : value) : value;")]),
    "pixel-saut": ("Pixel : saut avec arc à chaque marqueur (pixels entiers)", [("transform/position", MK +
        "var H = 40, L = 0.5;   // hauteur (px), durée (s)\nvar h = 0;\nif (d >= 0 && d < L) { var u = d / L; h = Math.round(4 * H * u * (1 - u)); }\n"
        "var v = value.slice(); v[0] = Math.round(v[0]); v[1] = Math.round(v[1]) - h; v;")]),
    "pixel-scintillement": ("Pixel : scintillement de pièce", [
        ("transform/opacity", "Math.floor(time * 4) % 2 ? value : value * 0.55;"),
        ("transform/position", "var v = value.slice(); v[0] = Math.round(v[0]); v[1] = Math.round(v[1]) + (Math.floor(time * 3) % 2 ? 0 : -2); v;")]),
}


def steps(nom, layer=None):
    out = []
    for path, e in RAPIDES[nom][1]:
        p = {"path": path, "expression": e}
        if layer is not None:
            p["layer"] = layer
        out.append({"command": "prop.setExpression", "params": p})
    return out


if __name__ == "__main__":
    d = sys.argv[1]
    os.makedirs(d, exist_ok=True)
    for nom, (desc, _) in RAPIDES.items():
        with open(os.path.join(d, f"ico rapide - {nom}.jsonl"), "w", encoding="utf-8") as f:
            f.write(f"// ico-vid rapide : {desc}. S'applique au calque sélectionné (remplace son expression).\n")
            f.write("// Réglages : les nombres en tête de l'expression (Propriété ▸ expression).\n")
            for s in steps(nom):
                f.write(json.dumps(s, ensure_ascii=False) + "\n")
    print(len(RAPIDES), "scripts ->", d)
