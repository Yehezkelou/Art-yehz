"""Petite bibliothèque pour générer les scripts de construction des modèles (.jsonl)."""
import json

BIBLE = "/home/Yehezou/videos/bible/bible.ecproj"


class B:
    def __init__(self):
        self.s = []
        self.spans = []      # (comp, layer, in, out)
        self.fxnames = []    # (comp, layer, index, name)

    def c(self, cmd, **p):
        self.s.append({"command": cmd, "params": p})

    # --- calques -------------------------------------------------------------
    def text(self, name, text, pos, font="Montserrat", style="ExtraBold", size=72, fill="#FFFFFF",
             stroke=None, sw=0, justify="center", **extra):
        p = dict(name=name, text=text, position=pos, font=font, style=style, size=size,
                 fill=fill, justify=justify, applyFill=True)
        if stroke:
            p.update(stroke=stroke, applyStroke=True, strokeWidth=sw, strokeOverFill=False)
        p.update(extra)
        self.c("layer.newText", **p)

    def shape(self, name, kind, size, pos, fill=None, stroke=None, sw=0):
        p = dict(name=name, kind=kind, size=size, position=pos)
        if fill:
            p["fill"] = fill
        if stroke:
            p.update(stroke=stroke, strokeWidth=sw)
        self.c("layer.newShape", **p)

    def solid(self, name, color, w, h, pos=None):
        self.c("layer.newSolid", name=name, color=color, width=w, height=h)
        if pos:
            self.c("layer.setTransform", layers=[name], prop="position", value=[pos[0], pos[1], 0])

    def null(self, name):
        self.c("layer.newNull")
        self.c("layer.rename", layer="#1", name=name)

    def fx(self, layer, effect, comp, label=None, **values):
        self.c("effect.apply", layer=layer, effect=effect)
        idx = sum(1 for f in self.fxnames if f[0] == comp and f[1] == layer) + 1
        if label:
            self.fxnames.append((comp, layer, idx, label))
        for k, v in values.items():
            self.set(layer, f"effects/#{idx}/{k.replace('__', '/')}", v)
        return idx

    # --- propriétés ----------------------------------------------------------
    def set(self, layer, path, value):
        self.c("prop.set", layer=layer, path=path, value=value)

    def expr(self, layer, path, e):
        self.c("prop.setExpression", layer=layer, path=path, expression=e)

    def key(self, layer, path, t, v):
        self.c("prop.addKey", layer=layer, path=path, time=t, timeBase="comp", value=v)

    def keys(self, layer, path, kv):
        for t, v in kv:
            self.key(layer, path, t, v)

    def pop(self, layer, t0):
        """Pop d'entrée de la bible (sous-titres) : échelle 86 → 107 → 100 %, opacité 0 → 100."""
        self.keys(layer, "transform/scale", [(t0, [86, 86, 100]), (t0 + 0.12, [107, 107, 100]),
                                             (t0 + 0.22, [100, 100, 100])])
        self.keys(layer, "transform/opacity", [(t0, 0), (t0 + 0.08, 100)])

    def span(self, comp, layer, i, o):
        self.spans.append((comp, layer, i, o))

    def parent(self, layers, parent):
        self.c("layer.setParent", layers=layers, parent=parent)

    def eg(self, comp, layer, path, name):
        self.c("essential.addProperty", comp=comp, layer=layer, path=path, name=name)

    # --- sorties -------------------------------------------------------------
    def write(self, path):
        with open(path, "w", encoding="utf-8") as f:
            for st in self.s:
                f.write(json.dumps(st, ensure_ascii=False) + "\n")

    def finish_js(self):
        """Script JS : points d'entrée/sortie et noms des effets (pas de commande pour ça)."""
        data = json.dumps({"spans": self.spans, "fx": self.fxnames}, ensure_ascii=False)
        return ("var D = " + data + ";\n"
                "function compByName(n){for(var i=1;i<=app.project.numItems;i++){var it=app.project.item(i);"
                "if(it.name===n&&it.numLayers!==undefined)return it;}return null;}\n"
                "app.beginUndoGroup('Finitions du modèle'); var log=[];\n"
                "for(var i=0;i<D.spans.length;i++){var s=D.spans[i];var c=compByName(s[0]);"
                "var l=c?c.layer(s[1]):null; if(!l){log.push('absent '+s[1]);continue;} l.inPoint=s[2]; l.outPoint=s[3];}\n"
                "for(var j=0;j<D.fx.length;j++){var f=D.fx[j];var c2=compByName(f[0]);"
                "var l2=c2?c2.layer(f[1]):null; if(!l2){log.push('absent '+f[1]);continue;} l2.effect(f[2]).name=f[3];}\n"
                "app.endUndoGroup(); 'spans '+D.spans.length+' fx '+D.fx.length+' '+log.join(',');")

    # --- squelette commun ----------------------------------------------------
    def start(self, comp, w, h, dur, bg, fps=24):
        self.c("file.newProject")
        self.c("file.importProject", path=BIBLE)
        self.c("comp.new", name=comp, width=w, height=h, frameRate=fps, duration=dur, background=bg, open=True)

    def controls(self, comp, colors, sliders=()):
        """Null « Controles » : contrôles couleur puis curseurs, référencés par index d'effet."""
        self.null("Controles")
        for i, (label, color) in enumerate(colors, 1):
            self.fx("Controles", "Color Control", comp, label, color=color)
        for label, v in sliders:
            self.fx("Controles", "Slider Control", comp, label, slider=v)

    def signature(self, main, dur, fill, sig="Signature"):
        self.c("comp.open", comp=sig)
        self.c("layer.setText", layer="Nom chaine", fill=fill)
        self.c("comp.open", comp=main)
        self.c("layer.addItem", item=sig, time=dur - 1, index=1)

    def guide(self, item="Guide zones 9:16"):
        self.c("layer.addItem", item=item, time=0, index=1)
        self.c("layer.setSwitch", layers=["#1"], switch="guide", value=True)
        self.c("layer.setTransform", layers=["#1"], prop="opacity", value=55)
        self.c("layer.setSwitch", layers=["#1"], switch="lock", value=True)

    def save(self, stem, name, description):
        self.c("file.saveAs", path=f"/home/Yehezou/videos/modeles/{stem}.ecproj")
        self.c("templates.saveAs", name=name, description=description, category="ico-vid")


CTRL = 'thisComp.layer("Controles")'


def col(i, ctrl=CTRL):
    return f"{ctrl}.effect({i})(1)"
