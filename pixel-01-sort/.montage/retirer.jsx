
var c = null; for (var i = 1; i <= app.project.numItems; i++) { var it = app.project.item(i); if (it.name === "PIXEL 270x480" && it.numLayers !== undefined) c = it; }
var log = [];
for (var j = 1; j <= c.numLayers; j++) if (c.layer(j).name === "Scene") throw new Error("la scène est déjà posée");
var noms = ["Oeil", "Heros", "Piece"];
for (var k = 0; k < noms.length; k++) {
  var l = null; for (var j = 1; j <= c.numLayers; j++) if (c.layer(j).name === noms[k]) l = c.layer(j);
  if (l) { l.locked = false; l.remove(); log.push("retiré " + noms[k]); } else log.push("absent " + noms[k]);
}
var idx = 0; for (var j = 1; j <= c.numLayers; j++) if (c.layer(j).name === "Sol") idx = j;
writeLn(log.join(", ") + " ; Sol en " + idx);
