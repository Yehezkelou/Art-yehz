
var O = {"remove": [["PIXEL 270x480", "ST 01"]], "durations": [["PIXEL - sortie 1080x1920", 20, 12.0], ["PIXEL 270x480", 20, 12.0]], "spans": [["PIXEL 270x480", "Sous-titre 01", 0.6, 3.0], ["PIXEL 270x480", "Sous-titre 02", 3.0, 4.8], ["PIXEL 270x480", "Sous-titre 03", 6.2, 8.0]], "shift": [], "start": [["PIXEL - sortie 1080x1920", "Signature", 11.0]]};
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
