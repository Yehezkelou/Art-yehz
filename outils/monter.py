#!/usr/bin/env python3
"""Monte un épisode EffectCraft à partir d'un fichier d'épisode (TOML) et d'un modèle ico-vid.

    python3 -I ~/videos/outils/monter.py ~/videos/<slug>/episode.toml            # projet + 3 aperçus
    python3 -I ~/videos/outils/monter.py ~/videos/<slug>/episode.toml --ecraser  # refait le projet (copie de sauvegarde avant)
    python3 -I ~/videos/outils/monter.py ~/videos/<slug>/episode.toml --rendu    # rend le .mp4 (+ copies dans rendu/ et sur le Bureau)

Le projet est construit en headless par effectcraft-cli à partir de ~/videos/modeles/<format>.ecproj :
textes, sous-titres minutés (pop de la bible), voix + bouche (sketch), durée, marqueurs + presets,
signature à la fin. Rien n'est écrasé sans --ecraser. Format du fichier : voir ~/videos/outils/README.md.
"""
import json, math, os, re, shutil, subprocess, sys, time, tomllib

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import chemins  # noqa: E402
import rapides  # noqa: E402

CLI = chemins.effectcraft_cli()          # surcharge : ICO_EFFECTCRAFT
MODELES = chemins.dans_racine("modeles")  # racine = outils/.. (surcharge : ICO_VIDEOS)
PRESETS = chemins.presets_effectcraft()  # comme EffectCraft : EC_PRESETS_DIR, sinon ~/Documents/EffectCraft/Presets
BUREAU = chemins.bureau()                # None : copie sur le Bureau sautée
RENDU = chemins.dans_racine("rendu")      # toutes les vidéos finies (ignoré par git : *.mp4)

# Ce que chaque modèle contient (noms de comps/calques et minutages du modèle d'origine)
FORMATS = {
    "sketch": dict(modele="sketch-humour.ecproj", main="SKETCH - a remplir", d0=30, st_comp=None,
                   st=dict(pos=[540, 1380], size=72, sw=14, leading=86, font="Montserrat", style="ExtraBold"),
                   car=20, placeholders=["ST 01", "ST chute"], signature="Signature", duree=(15, 45),
                   comps_duree=[]),
    "pixel": dict(modele="pixel-art.ecproj", main="PIXEL - sortie 1080x1920", d0=20, st_comp="PIXEL 270x480",
                  st=dict(pos=[135, 340], size=16, sw=0, leading=24, font="Press Start 2P", style="Regular"),
                  car=12, placeholders=["ST 01"], signature="Signature", duree=(10, 30),
                  comps_duree=["PIXEL 270x480"]),
    "fantasy": dict(modele="aventure-fantasy.ecproj", main="FANTASY - episode", d0=90, st_comp=None,
                    st=dict(pos=[960, 905], size=54, sw=10, leading=64, font="Montserrat", style="ExtraBold"),
                    car=40, placeholders=["ST 01"], signature="Signature 16:9", duree=(60, 120),
                    comps_duree=["Decor parallaxe"]),
    "vulga": dict(modele="vulgarisation.ecproj", main="VULGA - a remplir", d0=60, st_comp=None,
                  st=dict(pos=[540, 1380], size=72, sw=14, leading=86, font="Montserrat", style="ExtraBold"),
                  car=20, placeholders=["ST 01"], signature="Signature", duree=(45, 90),
                  comps_duree=[]),
}
MOTS_PAR_S = 2.8      # débit parlé moyen (français) pour le minutage automatique


def fail(msg):
    print("ERREUR :", msg, file=sys.stderr)
    sys.exit(1)


def wrap(text, n):
    """Coupe en lignes de ≤ n caractères (mots entiers) ; les \\n du texte sont respectés."""
    lines = []
    for para in text.split("\n"):
        cur = ""
        for w in para.split():
            if cur and len(cur) + 1 + len(w) > n:
                lines.append(cur); cur = w
            else:
                cur = (cur + " " + w).strip()
        if cur:
            lines.append(cur)
    return lines


def balance(words, n):
    """Deux lignes ≤ n caractères les plus égales possible (pas de mot orphelin), ou None."""
    best = None
    for k in range(1, len(words)):
        a, b = " ".join(words[:k]), " ".join(words[k:])
        if len(a) <= n and len(b) <= n and (best is None or max(len(a), len(b)) < best[0]):
            best = (max(len(a), len(b)), a + "\n" + b)
    return best[1] if best else None


def chunks(text, n):
    """Blocs d'au plus 2 lignes (règle de la bible), lignes équilibrées."""
    if "\n" not in text and len(text) > n:
        two = balance(text.split(), n)
        if two:
            return [two]
    lines = wrap(text, n)
    out = []
    for i in range(0, len(lines), 2):
        pair = lines[i:i + 2]
        two = balance(" ".join(pair).split(), n) if len(pair) == 2 else None
        out.append(two or "\n".join(pair))
    return out


def timing(reps, fmt, warn):
    """Minutage automatique des répliques sans début/fin : départ 0,8 s, silence avant la chute."""
    t = 0.8
    out = []
    for r in reps:
        txt = r["texte"]
        words = len(txt.split())
        dur = max(1.2, words / MOTS_PAR_S + 0.35)
        if r.get("chute") and "debut" not in r:
            t += 1.0                                   # le silence qui fait rire
        a = float(r.get("debut", t))
        b = float(r.get("fin", a + dur))
        if b <= a:
            fail(f"réplique « {txt[:30]} » : fin ≤ début")
        out.append(dict(r, debut=a, fin=b))
        t = b + 0.25
    return out


class Script:
    def __init__(self):
        self.steps, self.ops = [], {"remove": [], "durations": [], "spans": [], "shift": [], "start": []}

    def c(self, cmd, **p):
        self.steps.append({"command": cmd, "params": p})

    def key(self, layer, path, t, v):
        self.c("prop.addKey", layer=layer, path=path, time=t, timeBase="comp", value=v)

    def pop(self, layer, t0):
        for dt, s in ((0, 86), (0.12, 107), (0.22, 100)):
            self.key(layer, "transform/scale", t0 + dt, [s, s, 100])
        self.key(layer, "transform/opacity", t0, 0)
        self.key(layer, "transform/opacity", t0 + 0.08, 100)


FINISH_JS = r"""
var O = __OPS__;
function comp(n){for(var i=1;i<=app.project.numItems;i++){var it=app.project.item(i);if(it.name===n&&it.numLayers!==undefined)return it;}return null;}
function lay(c,n){if(!c)return null;for(var i=1;i<=c.numLayers;i++){if(c.layer(i).name===n)return c.layer(i);}return null;}
function each(c,f){var ls=[];for(var i=1;i<=c.numLayers;i++)ls.push(c.layer(i));for(var j=0;j<ls.length;j++){var l=ls[j];var lk=l.locked;l.locked=false;f(l);l.locked=lk;}}
var log=[];
app.beginUndoGroup("Montage de l'épisode");
for(var i=0;i<O.remove.length;i++){var l=lay(comp(O.remove[i][0]),O.remove[i][1]); if(l){l.locked=false;l.remove();} else log.push("absent "+O.remove[i][1]);}
for(var i=0;i<O.start.length;i++){var s=O.start[i];var l=lay(comp(s[0]),s[1]); if(!l){log.push("absent "+s[1]);continue;} var lk=l.locked;l.locked=false; l.startTime=s[2]; l.locked=lk;}
for(var i=0;i<O.shift.length;i++){var s=O.shift[i];var l=lay(comp(s[0]),s[1]); if(!l){log.push("absent "+s[1]);continue;} var lk=l.locked;l.locked=false; l.startTime=l.startTime+s[2]; l.locked=lk;}
for(var i=0;i<O.durations.length;i++){var d=O.durations[i];var c=comp(d[0]); if(!c){log.push("comp absente "+d[0]);continue;}
  each(c,function(l){ if(Math.abs(l.outPoint-d[1])<0.05) l.outPoint=d[2]; });}
for(var i=0;i<O.spans.length;i++){var s=O.spans[i];var l=lay(comp(s[0]),s[1]); if(!l){log.push("absent "+s[1]);continue;} var lk=l.locked;l.locked=false; if(s[2]!==null)l.inPoint=s[2]; if(s[3]!==null)l.outPoint=s[3]; l.locked=lk;}
app.endUndoGroup();
"ok " + log.join(", ");
"""


def build(ep, epdir):
    fmt = ep.get("format")
    if fmt not in FORMATS:
        fail(f"format inconnu « {fmt} » (sketch | pixel | fantasy | vulga)")
    F = FORMATS[fmt]
    warn = []
    reps = timing(ep.get("repliques", []), fmt, warn)
    if not reps:
        fail("aucune réplique")
    chutes = [r for r in reps if r.get("chute")]
    last_end = max(r["fin"] for r in reps)
    D = float(ep.get("duree", math.ceil(last_end + 2.0)))
    if fmt == "fantasy":
        D = max(D, math.ceil(last_end + 6.0))       # carton « à suivre » (4 s) + signature
    if fmt == "vulga":
        pt0 = ep.get("points_temps", [3, 7, 11])
        ft0 = float(ep.get("fleche_temps", pt0[-1] + 2))
        D = max(D, math.ceil(last_end + 9.0), math.ceil(ft0 + 3 + 9))   # flèche, récap (8 s), signature
    lo, hi = F["duree"]
    if "duree" not in ep:
        D = max(D, lo)                               # au moins la durée minimale de la bible
    if not lo <= D <= hi:
        warn.append(f"durée {D:.0f} s hors de la bible ({lo}–{hi} s pour « {fmt} »)")
    if last_end > D - 1:
        warn.append(f"la dernière réplique finit à {last_end:.1f} s, après le début de la signature ({D - 1:.0f} s)")

    M, S = F["main"], Script()
    stc = F["st_comp"] or M
    d0 = F["d0"]
    # Durées
    for cname in [M] + F["comps_duree"]:
        S.c("comp.settings", comp=cname, duration=D)
        S.ops["durations"].append([cname, d0, D])
    S.c("comp.open", comp=M)
    S.ops["start"].append([M, F["signature"], D - 1])
    for ph in F["placeholders"]:
        S.ops["remove"].append([stc, ph])
    if ep.get("couleur"):
        S.c("prop.set", layer="Controles", path="effects/#1/color", value=ep["couleur"])

    # Textes du modèle
    def settext(comp, layer, text):
        if text:
            S.c("comp.open", comp=comp); S.c("layer.setText", layer=layer, text=text)
    if fmt == "sketch":
        settext(M, "Accroche", ep.get("accroche") or ep.get("titre"))
        settext(M, "Nom du perso", ep.get("perso"))
        tc = chutes[0]["debut"] if chutes else reps[-1]["debut"]
        S.c("comp.open", comp=M)
        S.c("prop.set", layer="Controles", path="effects/#5/slider", value=round(tc, 3))
    elif fmt == "pixel":
        settext(M, "TXT Titre", ep.get("titre"))
    elif fmt == "fantasy":
        settext(M, "TXT Titre serie", ep.get("serie"))
        settext(M, "TXT Numero episode", ep.get("numero"))
        settext(M, "TXT Titre episode", ep.get("titre"))
        settext(M, "TXT Episode suivant", ep.get("suivant"))
        for l in ("Voile a suivre", "A suivre", "Episode suivant"):
            S.ops["shift"].append([M, l, D - 90])
    elif fmt == "vulga":
        q = ep.get("question") or ep.get("titre")
        settext(M, "Question", q)
        if q and len(q) > 22:                       # 88 px tient ~22 car. dans les bords sûrs
            S.c("layer.setText", layer="Question", size=round(88 * 22 / len(q)))
            warn.append(f"question de {len(q)} car. : taille réduite à {round(88 * 22 / len(q))} px")
        pts = ep.get("points", [])
        for i, p in enumerate(pts[:3], 1):
            settext(M, f"Point {i}", f"{i}. {p}")
        settext(M, "Conclusion fleche", ep.get("conclusion"))
        settext(M, "Recap", ep.get("recap"))
        settext(M, "Sources", ep.get("sources"))
        pt = ep.get("points_temps", [3, 7, 11])
        for i, (t, t0) in enumerate(zip(pt, [3, 7, 11]), 1):
            S.ops["shift"].append([M, f"Point {i}", t - t0])
        ft = float(ep.get("fleche_temps", pt[-1] + 2))
        for l in ("Fleche trait", "Fleche pointe haut", "Fleche pointe bas", "Conclusion fleche"):
            S.ops["shift"].append([M, l, ft - 13])
        for l in ("Voile recap", "En resume", "Recap", "Sources"):
            S.ops["shift"].append([M, l, (D - 8) - 52])
        for l in ("Zone schema", "Point 1", "Point 2", "Point 3", "Fleche trait", "Fleche pointe haut",
                  "Fleche pointe bas", "Conclusion fleche", "Surligneur", "Question"):
            S.ops["spans"].append([M, l, None, D - 8])
        if len(pts) > 3:
            warn.append("plus de 3 points : seuls les 3 premiers sont placés")

    # Sous-titres
    st = F["st"]
    principale = ep.get("couleur", {"sketch": "#FFD24A", "pixel": "#F4C542", "fantasy": "#C9A227", "vulga": "#FFB020"}[fmt])
    S.c("comp.open", comp=stc)
    n = 0
    for r in reps:
        blocs = chunks(r["texte"], F["car"])
        if len(blocs) > 1:
            warn.append(f"« {r['texte'][:40]}… » fait {len(blocs)} sous-titres (> 2 lignes de {F['car']} car.) : raccourcir ?")
        total = sum(len(b) for b in blocs)
        a = r["debut"]
        for b in blocs:
            n += 1
            name = f"Sous-titre {n:02d}"
            dur = (r["fin"] - r["debut"]) * len(b) / total
            p = dict(name=name, text=b, position=st["pos"], font=st["font"], style=st["style"],
                     size=st["size"], fill=principale if r.get("chute") else ("#F2EDE4" if fmt == "pixel" else "#FFFFFF"),
                     applyFill=True, justify="center", leading=st["leading"])
            if st["sw"]:
                p.update(stroke="#000000", applyStroke=True, strokeWidth=st["sw"], strokeOverFill=False)
            S.c("layer.newText", **p)
            S.pop(name, a)
            S.ops["spans"].append([stc, name, a, a + dur])
            a += dur

    # Voix (+ bouche du sketch pilotée par « Audio Amplitude »)
    if ep.get("voix"):
        vp = os.path.join(epdir, ep["voix"])
        if not os.path.exists(vp):
            fail(f"voix introuvable : {vp}")
        S.c("comp.open", comp=M)
        S.c("file.import", paths=[vp])
        S.c("layer.addItem", item=os.path.basename(vp), time=float(ep.get("voix_debut", 0)))
        S.c("layer.select", layers=[os.path.basename(vp)])
        S.c("keys.audioToKeyframes", comp=M)

    # Effets : marqueurs + presets
    for e in ep.get("effets", []):
        comp = e.get("comp", M)
        S.c("comp.open", comp=comp)
        for t in e.get("temps", []):
            S.c("layer.addMarker", layers=[e["calque"]], time=float(t))
        if "rapide" in e:                 # expression sur la transformation : gratuit au rendu
            if e["rapide"] not in rapides.RAPIDES:
                fail(f"mouvement rapide inconnu « {e['rapide']} » ({', '.join(rapides.RAPIDES)})")
            if fmt == "sketch" and e["calque"] == "Tete":
                fail("la tête du sketch a déjà ses mouvements (respiration, secousse + zoom au « Temps de la chute ») : "
                     "ne mets pas d'effet rapide dessus")
            S.steps.extend(rapides.steps(e["rapide"], layer=e["calque"]))
        else:                             # preset .ecpreset (réglable, mais ~1 s par image au rendu)
            path = os.path.join(PRESETS, e["preset"] + ".ecpreset")
            if not os.path.exists(path):
                fail(f"preset introuvable : {path}")
            S.c("anim.applyPreset", path=path, layers=[e["calque"]])
            warn.append(f"preset « {e['preset']} » sur « {e['calque']} » : ~1 s de plus par image au rendu ; "
                        "préférer `rapide = …` si l'équivalent existe")
    S.c("comp.open", comp=M)
    S.c("time.set", time=1.2)

    # Images clés à montrer avant le rendu
    mid = reps[len(reps) // 2]
    if fmt == "sketch":
        keys = [1.2, (mid["debut"] + mid["fin"]) / 2, tc + 0.25]
    elif fmt == "pixel":
        keys = [1.2, (mid["debut"] + mid["fin"]) / 2, D - 3]
    elif fmt == "fantasy":
        keys = [2.0, 5.5, (mid["debut"] + mid["fin"]) / 2]
    else:
        keys = [pt[-1] + 0.6, ft + 1.0, D - 5]
    return S, M, D, keys, warn


def cli(*args, check=True):
    r = subprocess.run([CLI, *args], capture_output=True, text=True)
    if check and r.returncode != 0:
        fail(f"effectcraft-cli {' '.join(args[:2])} : {r.stderr.strip() or r.stdout.strip()}")
    return r


def main():
    if len(sys.argv) < 2:
        fail(__doc__)
    tpath = os.path.abspath(os.path.expanduser(sys.argv[1]))
    epdir = os.path.dirname(tpath)
    with open(tpath, "rb") as f:
        ep = tomllib.load(f)
    slug = ep.get("slug") or os.path.basename(epdir)
    proj = os.path.join(epdir, slug + ".ecproj")
    S, M, D, keys, warn = build(ep, epdir)

    if "--rendu" in sys.argv:
        if not os.path.exists(proj):
            fail("pas de projet : lance d'abord le montage")
        out = os.path.join(epdir, slug + ".mp4")
        if os.path.exists(out) and "--ecraser" not in sys.argv:
            fail(f"{out} existe déjà (ajoute --ecraser pour le refaire)")
        t0 = time.time()
        cli("render", "--project", proj, "--comp", M, "--out", out, "--format", "h264",
            "--bitrate", "12000", "--audio", "auto")
        msg = {"video": out, "secondes": round(time.time() - t0)}
        os.makedirs(RENDU, exist_ok=True)
        shutil.copy2(out, os.path.join(RENDU, slug + ".mp4"))
        msg["rendu"] = os.path.join(RENDU, slug + ".mp4")
        if BUREAU and os.path.isdir(BUREAU) and "--sans-bureau" not in sys.argv:
            shutil.copy2(out, os.path.join(BUREAU, slug + ".mp4"))
            msg["bureau"] = os.path.join(BUREAU, slug + ".mp4")
        print(json.dumps(msg, ensure_ascii=False, indent=1))
        return

    if os.path.exists(proj):
        if "--ecraser" not in sys.argv:
            fail(f"{proj} existe déjà : rien n'est écrasé sans --ecraser")
        bak = proj.replace(".ecproj", time.strftime(".sauvegarde-%Y%m%d-%H%M%S.ecproj"))
        shutil.copy2(proj, bak)
        warn.append(f"ancien projet copié dans {bak}")
    build_dir = os.path.join(epdir, ".montage")
    os.makedirs(build_dir, exist_ok=True)
    jl, js = os.path.join(build_dir, "montage.jsonl"), os.path.join(build_dir, "finitions.js")
    with open(jl, "w", encoding="utf-8") as f:
        for st in S.steps:
            f.write(json.dumps(st, ensure_ascii=False) + "\n")
    with open(js, "w", encoding="utf-8") as f:
        f.write(FINISH_JS.replace("__OPS__", json.dumps(S.ops, ensure_ascii=False)))
    modele = os.path.join(MODELES, FORMATS[ep["format"]]["modele"])
    r = cli("run", "file.runScript", json.dumps({"path": jl}), "file.runScript", json.dumps({"path": js}),
            "--project", modele, "--save-as", proj, "--json")
    if '"ok ' not in r.stdout and "ok " not in r.stdout:
        warn.append("finitions : " + r.stdout.strip()[-300:])
    m = re.search(r'ok ([^"]*)"', r.stdout)
    if m and m.group(1).strip():
        warn.append("finitions : " + m.group(1).strip())
    F = FORMATS[ep["format"]]
    comps = list(dict.fromkeys([M] + F["comps_duree"] + ([F["st_comp"]] if F["st_comp"] else [])
                               + [e["comp"] for e in ep.get("effets", []) if "comp" in e]))
    for cname in comps:                      # toutes les comps de l'épisode, à chaque image clé
        for t in keys:
            err = cli("exec", "expr.errors", "--params", json.dumps({"comp": cname, "time": t}), "--project", proj, "--json", check=False)
            try:
                res = json.loads(err.stdout)
                res = res.get("result", res)
                for line in res.get("text", []):
                    if line not in " ".join(warn):
                        warn.append("ERREUR D'EXPRESSION : " + line)
            except (ValueError, AttributeError):
                warn.append(f"contrôle des expressions impossible ({cname}) : " + (err.stderr or err.stdout)[:200])
    apercus = []
    for i, t in enumerate(keys, 1):
        png = os.path.join(epdir, f"apercu-{i}.png")
        cli("render-frame", "--project", proj, "--comp", M, "--time", f"{t:.3f}", "--max-side", "720", "--out", png)
        apercus.append({"image": png, "temps": round(t, 2)})
    print(json.dumps({"projet": proj, "comp": M, "duree": D, "sous_titres": sum(1 for s in S.steps if s["command"] == "layer.newText"),
                      "apercus": apercus, "alertes": warn}, ensure_ascii=False, indent=1))


if __name__ == "__main__":
    main()
