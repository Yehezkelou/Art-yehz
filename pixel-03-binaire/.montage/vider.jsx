
function comp(n) { for (var i = 1; i <= app.project.numItems; i++) { var it = app.project.item(i); if (it.name === n && it.numLayers !== undefined) return it; } }
function retirer(c, noms, log) {
  for (var k = 0; k < noms.length; k++) {
    var l = null; for (var j = 1; j <= c.numLayers; j++) if (c.layer(j).name === noms[k]) l = c.layer(j);
    if (l) { l.locked = false; l.remove(); log.push("retiré " + noms[k]); } else log.push("absent " + noms[k]);
  }
}
var p = comp("PIXEL 270x480"), m = comp("PIXEL - sortie 1080x1920"), log = [];
for (var j = 1; j <= m.numLayers; j++) if (m.layer(j).name === "Scene") throw new Error("la scène est déjà posée");
retirer(p, ["Titre pixel", "Oeil", "Heros", "Piece", "Sol", "Lune", "Ciel"], log);
retirer(m, ["TXT Titre"], log);
var idx = 0; for (var j = 1; j <= m.numLayers; j++) if (m.layer(j).name === "PIXEL 270x480") idx = j;
writeLn(log.join(", ") + " ; pixel en " + idx);
