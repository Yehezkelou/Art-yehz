// Plan « Usine 2.3 » ico-vid (2.2 + Claude regarde les vidéos + deuxième avis Gemini) — génère le .docx (node plan-v2.3.js <sortie.docx>)
const fs = require("fs");
const {
  Document, Packer, Paragraph, TextRun, HeadingLevel, Table, TableRow, TableCell, WidthType,
  ShadingType, BorderStyle, AlignmentType, LevelFormat, Footer, PageNumber, PageBreak,
  TableOfContents,
} = require("docx");

const W = 9638; // largeur utile A4 avec marges de 2 cm (DXA)
const NAVY = "1B2340", BLUE = "2E5AA0", GREY = "5B6475", LIGHT = "F2F4F8", AMBER = "FFB020", CREAM = "FFF6D6";
const RED = "C0392B", ROSE = "FDECEA", GREEN = "1E7D4F", MINT = "E7F6EE";

// **gras** dans le texte
function runs(text, opts = {}) {
  return text.split("**").map((t, i) => new TextRun({ text: t, bold: i % 2 === 1 || opts.bold, color: opts.color, size: opts.size, italics: opts.italics, font: opts.font }));
}
const P = (t, o = {}) => new Paragraph({ children: runs(t, o), spacing: { after: 120, line: 288 }, alignment: o.align });
const H1 = (t) => new Paragraph({ heading: HeadingLevel.HEADING_1, children: [new TextRun(t)], pageBreakBefore: true });
const H2 = (t) => new Paragraph({ heading: HeadingLevel.HEADING_2, children: [new TextRun(t)], keepNext: true });
const H3 = (t) => new Paragraph({ heading: HeadingLevel.HEADING_3, children: [new TextRun(t)], keepNext: true });
const B = (t, lvl = 0) => new Paragraph({ numbering: { reference: "puces", level: lvl }, children: runs(t), spacing: { after: 60, line: 276 } });
// listes numérotées : chaque liste a sa propre référence (la numérotation repart à 1)
const LISTES = new Set();
const N = (t, ref) => { LISTES.add(ref); return new Paragraph({ numbering: { reference: ref, level: 0 }, children: runs(t), spacing: { after: 60, line: 276 } }); };
const LIST = (ref, items) => items.map((t) => N(t, ref));
const box = (fill, color) => (t) => new Paragraph({
  children: runs(t), spacing: { before: 120, after: 160, line: 288 },
  shading: { type: ShadingType.CLEAR, fill, color: "auto" },
  border: { left: { style: BorderStyle.SINGLE, size: 24, color, space: 8 } },
  indent: { left: 170, right: 170 },
});
const NOTE = box(CREAM, AMBER);   // à retenir
const ALERTE = box(ROSE, RED);    // danger, interdit
const ASTUCE = box(MINT, GREEN);  // conseil, gain
// bloc de code / fichier (une ligne = un paragraphe)
const CODE = (text) => text.split("\n").map((l, i, a) => new Paragraph({
  children: [new TextRun({ text: l === "" ? " " : l, font: "Consolas", size: 17 })],
  shading: { type: ShadingType.CLEAR, fill: LIGHT, color: "auto" },
  border: { left: { style: BorderStyle.SINGLE, size: 18, color: BLUE, space: 8 } },
  indent: { left: 170, right: 170 },
  spacing: { before: i === 0 ? 100 : 0, after: i === a.length - 1 ? 160 : 0, line: 252 },
}));

function table(headers, rows, widths) {
  const tot = widths.reduce((a, b) => a + b, 0);
  const ws = widths.map((w) => Math.round((w * W) / tot));
  ws[ws.length - 1] += W - ws.reduce((a, b) => a + b, 0);
  const border = { style: BorderStyle.SINGLE, size: 4, color: "C9CFDC" };
  const borders = { top: border, bottom: border, left: border, right: border };
  const cell = (t, i, head, zebra) => new TableCell({
    width: { size: ws[i], type: WidthType.DXA }, borders,
    shading: { type: ShadingType.CLEAR, color: "auto", fill: head ? NAVY : zebra ? LIGHT : "FFFFFF" },
    margins: { top: 60, bottom: 60, left: 100, right: 100 },
    children: String(t).split("\n").map((line) => new Paragraph({ children: runs(line, { bold: head, color: head ? "FFFFFF" : undefined, size: 19 }), spacing: { after: 20 } })),
  });
  return new Table({
    width: { size: W, type: WidthType.DXA }, columnWidths: ws,
    rows: [
      new TableRow({ tableHeader: true, cantSplit: true, children: headers.map((h, i) => cell(h, i, true)) }),
      ...rows.map((r, j) => new TableRow({ cantSplit: true, children: r.map((c, i) => cell(c, i, false, j % 2 === 1)) })),
    ],
  });
}
const GAP = () => new Paragraph({ children: [], spacing: { after: 80 } });
// tableau de couleurs (une case colorée par couleur)
function swatches(rampes) {
  const cw = Math.floor((W - 2000) / 4);
  const ws = [W - 4 * cw, cw, cw, cw, cw];
  const border = { style: BorderStyle.SINGLE, size: 4, color: "C9CFDC" };
  const borders = { top: border, bottom: border, left: border, right: border };
  const clair = (hex) => { const n = parseInt(hex, 16); return ((n >> 16) * 299 + ((n >> 8) & 255) * 587 + (n & 255) * 114) / 1000 > 140; };
  return new Table({
    width: { size: W, type: WidthType.DXA }, columnWidths: ws,
    rows: rampes.map(([nom, cols]) => new TableRow({ cantSplit: true, children: [
      new TableCell({ width: { size: ws[0], type: WidthType.DXA }, borders, margins: { top: 60, bottom: 60, left: 100, right: 100 },
        children: [new Paragraph({ children: runs(nom, { size: 19 }) })] }),
      ...cols.map((c, i) => new TableCell({ width: { size: ws[i + 1], type: WidthType.DXA }, borders,
        shading: { type: ShadingType.CLEAR, color: "auto", fill: c }, margins: { top: 100, bottom: 100, left: 100, right: 100 },
        children: [new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun({ text: "#" + c, size: 17, font: "Consolas", color: clair(c) ? "000000" : "FFFFFF" })] })] })),
    ] })),
  });
}

const C = []; // contenu

// ================================================================ page de garde
C.push(
  new Paragraph({ children: [], spacing: { before: 2000 } }),
  new Paragraph({ children: [new TextRun({ text: "ico-vid · Usine 2.3", bold: true, size: 64, color: NAVY })], spacing: { after: 160 } }),
  new Paragraph({ children: [new TextRun({ text: "Plan détaillé : personnages et motion design pixel, moteur caméra, les 5 logiciels de la suite ArtCraft, Claude qui regarde les vidéos, deuxième avis Gemini, production pas à pas, marketing, revenus (objectif 500 $ par mois)", size: 30, color: BLUE })], spacing: { after: 360 } }),
  new Paragraph({ children: runs("Version **2.3** · 21 octobre 2026 · chaîne **ico-vid** · **@yehz**", { color: GREY, size: 24 }), spacing: { after: 120 } }),
  new Paragraph({ children: runs("Remplace les v2.0 à v2.2 du même jour, qui restent archivées. Chaque étape est expliquée en détail (quoi, qui, comment, combien de temps, comment savoir que c'est fini) ; les chiffres de revenus tiennent compte des règles YouTube confirmées pour le 1er février 2027 ; et **les cinq logiciels de ~/videos/logiciel** (EffectCraft, FilmCraft, SoundCraft, PhotoCraft, VectorCraft) ont chacun leur rôle dans la chaîne (§ 10) ; Claude peut désormais **regarder les vidéos** grâce à eux (§ 10.7), et **Gemini** (CLI agy) donne un deuxième avis sur la stratégie (§ 10.8).", { color: GREY, size: 21 }), spacing: { after: 720 } }),
  table(["Version", "Date", "Contenu", "Statut"], [
    ["1.0", "20/10/2026", "Plan initial « EffectCraft sur mesure » : étapes 0 à 8", "Étapes 0–5 faites, 6 commencée"],
    ["2.0", "21/10/2026", "Usine 2.0 : pixel, moteur caméra, marketing, objectif 500 $/mois, limites, versionnage", "Archivée"],
    ["2.1", "21/10/2026", "Version détaillée : spécifications, modes d'emploi, calendrier jour par jour, calculs refaits avec les seuils YouTube 2027", "Archivée"],
    ["2.2", "21/10/2026", "Ce document : 2.1 + intégration de FilmCraft, SoundCraft, PhotoCraft et VectorCraft (rôles, flux de fichiers, pilotage par Claude, installation, tests, plan B)", "Archivée"],
    ["2.3", "21/10/2026", "Ce document : 2.2 + Claude regarde les vidéos (§ 10.7 : images, plans, transcription, son ; usages, limites, test) + deuxième avis Gemini via agy (§ 10.8) et ses retours sur la stratégie", "À valider"],
    ["2.x", "à venir", "Mises à jour après chaque phase (chiffres réels, décisions)", "—"],
  ], [1, 1.4, 5, 1.8]),
);

// ================================================================ sommaire
C.push(
  new Paragraph({ children: [new TextRun({ text: "Sommaire", bold: true, size: 32, color: NAVY })], spacing: { after: 200 }, pageBreakBefore: true }),
  new TableOfContents("Sommaire", { hyperlink: true, headingStyleRange: "1-2" }),
  P("Si le sommaire est vide à l'ouverture : clic droit dessus ▸ **Mettre à jour les champs** (Word calcule les numéros de page à ce moment-là).", { color: GREY, size: 18 }),
);

// ================================================================ 0
C.push(
  H1("0. Comment lire ce document"),
  P("Ce plan est fait pour être **suivi**, pas seulement lu. Chaque chapitre répond aux mêmes questions : **quoi** (le livrable), **qui** (toi, Claude ou la machine), **comment** (les étapes et les commandes), **combien de temps**, et **comment savoir que c'est fini** (le critère de fin)."),
  table(["Si tu veux…", "Lis d'abord"], [
    ["Savoir où on va et pourquoi", "§ 1 (une page) puis § 3 (les décisions à prendre)"],
    ["Commencer à travailler tout de suite", "§ 21 (la semaine 1, jour par jour)"],
    ["Comprendre la technique pixel et caméra", "§ 4 à § 9"],
    ["Savoir quel logiciel sert à quoi", "§ 10 (les 5 logiciels de la suite)"],
    ["Savoir comment Claude regarde une vidéo, et quand Gemini intervient", "§ 10.7 et § 10.8"],
    ["Fabriquer une vidéo de A à Z", "§ 11 (la chaîne de production pas à pas)"],
    ["Préparer la publication et le marketing", "§ 12 et § 13"],
    ["Comprendre l'argent (et ses limites)", "§ 14"],
    ["Voir le calendrier sur 12 mois", "§ 15"],
  ], [4, 5.6]),
  GAP(),
  H2("0.1 Légende"),
  table(["Mot", "Sens dans ce document"], [
    ["**Toi**", "Ce que seul toi peux faire : décider, valider, enregistrer ta voix, publier, dessiner si tu le choisis."],
    ["**Claude**", "Ce que Claude prépare et exécute : scripts, outils, montage, aperçus, textes de publication, bilans."],
    ["**Machine**", "Ce qui tourne tout seul : rendus, contrôles automatiques."],
    ["**Critère de fin**", "La preuve concrète qu'une tâche est terminée. Sans critère rempli, la tâche n'est pas finie."],
    ["Encadré jaune", "À retenir."],
    ["Encadré vert", "Astuce qui fait gagner du temps ou de la qualité."],
    ["Encadré rouge", "Interdit ou danger (droits, monétisation, perte de travail)."],
  ], [2, 7.6]),
  GAP(),
  P("Les mots techniques (RPM, précomp, parallaxe, CC0…) sont expliqués dans le **glossaire** (annexe A)."),
);

// ================================================================ 1
C.push(
  H1("1. En une page"),
  P("**Où on en est.** L'usine 1.0 tourne : une bible de chaîne, 4 modèles de projet, 12 presets et 10 mouvements « rapides », 4 recettes Claude et un outil (**monter.py**) qui monte un épisode complet en **environ 2 secondes** à partir d'un petit fichier texte. Deux vidéos de test existent : le sketch « Le cloud » (17 s) et la vulgarisation « GPS et Einstein » (62 s)."),
  P("**Ce qu'on construit.** Une usine 2.0 spécialisée **pixel art et motion design pixel** : de vrais personnages animés (planches de sprites), des scènes en plusieurs plans, et un **moteur caméra pixel** (travelling, suivi, zoom par paliers, secousse, parallaxe) qui ne fait jamais « baver » un pixel. La chaîne publie des Shorts pour se faire connaître, et des **vidéos longues** parce que ce sont elles qui accumulent des heures de visionnage."),
  P("**Ce qui a changé depuis la v2.0 (important).** YouTube a confirmé sur sa page d'aide officielle qu'à partir du **1er février 2027**, une nouvelle chaîne devra réunir **1 000 abonnés + 8 000 heures de visionnage en 12 mois** (ou 20 millions de vues Shorts en 90 jours) pour toucher la publicité, au lieu de 4 000 h aujourd'hui. Et la part du fonds Shorts demandera **10 millions de vues Shorts en 90 jours**. Conséquence : **pendant la première année, la publicité YouTube rapportera probablement peu ou rien**. Les 500 $ doivent donc venir d'abord d'ailleurs (§ 14)."),
  P("**Claude regarde les vidéos (nouveau en 2.3).** FilmCraft et EffectCraft transforment une vidéo en ce que Claude sait lire : des images choisies, une image par plan, une planche contact, la transcription datée et des mesures du son. Claude peut ainsi contrôler chaque vidéo avant publication, analyser des références, comparer deux versions et regarder l'instant exact où les spectateurs décrochent (§ 10.7). **Gemini**, par la CLI agy, donne un deuxième avis aux moments clés ; ses premières critiques de la stratégie deviennent des décisions à prendre (D10 à D14, § 3 et § 10.8)."),
  P("**Les cinq logiciels.** EffectCraft reste le cœur (scènes, caméra, animation, rendu). Les quatre autres logiciels de **~/videos/logiciel** interviennent là où ils sont les meilleurs : **SoundCraft** enregistre la voix et fabrique la musique et le jingle ; **FilmCraft** transcrit la voix en sous-titres (fini le plus gros travail manuel du journal) et monte les vidéos longues ; **PhotoCraft** fait les décors en calques et les miniatures ; **VectorCraft** fait le logo et les icônes. Tous sont pilotables par Claude (§ 10)."),
  P("**Le but chiffré.** **500 $ bruts par mois vers le mois 12** (environ 380 $ nets après frais et cotisations), en additionnant : **boutique** de packs pixel et de fonds animés, **commandes** d'animation pixel (emotes, overlays de stream), **TikTok** (vidéos de plus d'une minute), **soutiens** des spectateurs, puis la publicité YouTube quand le seuil est atteint."),
  P("**La méthode, dans l'ordre :**"),
  ...LIST("m1", [
    "**Fondations (semaines 1–2)** : dépôt versionné, bibliothèque d'assets avec licences, direction artistique pixel, découpe des planches de sprites, premier personnage ; **compilation et test** de FilmCraft, SoundCraft et PhotoCraft.",
    "**Moteur caméra pixel (semaines 2–3)** : un calque **CAM** pilote 4 à 6 plans à des vitesses différentes, toujours au pixel entier, avec un contrôle automatique « zéro pixel baveux ».",
    "**monter.py v2 (semaine 3)** : un épisode décrit plan par plan dans un fichier texte devient un projet complet.",
    "**Lancement (semaine 4)** : 3 vidéos prêtes d'avance, chaînes ouvertes, premier rythme de publication.",
    "**Production + boutique (mois 2 à 12)** : rythme régulier, 1er pack en vente à la semaine 6, commandes, mesure chaque semaine, bilans aux mois 3, 6 et 12.",
  ]),
  NOTE("**Règle d'or conservée** : on ne code une nouvelle fonction dans EffectCraft que si elle a manqué sur **au moins 2 vraies vidéos** (journal « ce qui m'a gêné », 29 entrées à ce jour). Sinon on construit un logiciel parfait… et zéro vidéo."),
  NOTE("**La règle qui rend le plan optimal : un seul travail, trois usages.** Chaque personnage, décor ou animation fabriqué pour une vidéo sert aussi (1) dans d'autres vidéos, (2) dans un pack vendu sur la boutique, (3) comme vitrine pour décrocher des commandes. On ne dessine jamais « juste pour une vidéo »."),
);

// ================================================================ 2
C.push(
  H1("2. Bilan de l'usine 1.0"),
  table(["Brique", "État au 21/10/2026", "Où"], [
    ["Bible de la chaîne", "Formats, zones sûres 9:16 et 16:9, polices OFL (Lilita One, Montserrat, Press Start 2P), 4 palettes de 6 couleurs, sous-titres, signature ico-vid", "~/videos/bible.md"],
    ["Modèles de projet", "Sketch, Pixel art (270×480 ×4, 12 i/s), Aventure fantasy, Vulgarisation (.ectemplate, galerie de l'app)", "~/videos/modeles/"],
    ["Presets", "12 .ecpreset (pop, rebond, secousse, zoom, iris…) + 10 mouvements rapides en expressions (gratuits au rendu)", "~/videos/presets/"],
    ["Recettes Claude", "video-sketch, video-pixel, video-fantasy, video-vulga", "~/.claude/skills/"],
    ["Outil de montage", "monter.py : episode.toml → projet + 3 aperçus (~2 s), puis rendu .mp4 + copie sur le Bureau", "~/videos/outils/"],
    ["Vidéos sorties", "sketch-01 (17 s, muet), vulga-01-gps (62 s, rendu en 3 min 42 s)", "~/videos/…"],
    ["Journal des gênes", "29 entrées (sous-titres, performances, commandes manquantes, bugs)", "~/videos/ce-qui-m-a-gene.md"],
  ], [2, 5, 2.4]),
  GAP(),
  H2("2.1 Ce que les tests ont prouvé"),
  B("La chaîne **idée → script → projet → aperçus → vidéo** fonctionne de bout en bout **sans ouvrir l'app**."),
  B("Le pixel art agrandi ×4 en qualité Draft reste **net** (plus proche voisin) : contrôle fait, seulement 3 couleurs autour du héros."),
  B("Les **expressions** sur la transformation d'un calque ne coûtent rien au rendu, alors qu'un preset passant par un effet coûte environ 1 s par image : la caméra pixel sera donc faite en expressions."),
  B("Le rendu tourne sur le **processeur** (WSL n'expose pas la carte graphique) : environ 0,25 s par image pour un sketch, 1 s pour la fantasy."),
  H2("2.2 Ce que le journal dit, regroupé par thème"),
  table(["Thème", "Entrées du journal", "Ce que ça coûte aujourd'hui", "Réponse dans ce plan"], [
    ["Sous-titres", "n° 1, 2, 12, 27", "Le plus gros travail manuel par vidéo", "**Transcription de la voix par FilmCraft → fichier .srt → monter.py** (§ 10.1) : aucune ligne de code à ajouter dans EffectCraft"],
    ["Performances de rendu", "n° 10, 10b, 17, 24", "Rendus lents, aperçus lents dans la fenêtre", "Scènes en basse résolution, expressions plutôt qu'effets, rendus la nuit, test Windows natif (§ 17)"],
    ["Pilotage par Claude", "n° 3, 4, 13, 14, 20, 23", "Plus d'appels et de scripts que nécessaire", "Contournés dans les outils ; candidats au fork"],
    ["Presets", "n° 6, 21, 22", "Presets qui déplacent le calque", "Mouvements rapides (déjà fait)"],
    ["Pixel", "n° 18", "Texte légèrement lissé dans la comp pixel", "À vérifier sur la 1re vraie vidéo pixel ; mode « pixel parfait » si confirmé"],
    ["Voix", "n° 7, 8", "Vidéos muettes", "Décision D4 (§ 3) ; enregistrement et nettoyage dans **SoundCraft** (§ 10) ; bouche branchée sur l'audio"],
    ["Bugs et pièges", "n° 5, 16, 19, 25", "Temps perdu à comprendre", "Règles notées dans les outils ; signalés au projet si reproductibles"],
    ["Contenu des modèles", "n° 26, 28", "Cadre vide, récap trop long", "Bibliothèque d'icônes pixel (§ 5) ; durée du récap réglable"],
  ], [1.8, 1.8, 2.8, 3.4]),
);

// ================================================================ 3
C.push(
  H1("3. Les décisions à prendre maintenant"),
  P("Ces choix conditionnent tout le reste. Pour chacun, une recommandation est donnée ; tu peux la suivre telle quelle ou la changer. **Rien ne démarre avant ta réponse sur les décisions D1 à D4.**"),
  table(["#", "Décision", "Options", "Recommandation et raison"], [
    ["D1", "Séries de lancement", "La science en pixel · Gags pixel · Aventure de Tim · Ambiances pixel", "**Gags pixel + La science en pixel.** Les gags attirent (découverte), la science retient (heures de visionnage). Tim et les Ambiances arrivent au mois 2, quand le moteur est rodé."],
    ["D2", "Rythme de publication", "A : 3 Shorts + 1 long toutes les 2 semaines (≈ 6 h/semaine pour toi)\nB : 5 Shorts + 1 long par semaine (≈ 10–12 h/semaine)", "**Commencer en A, passer en B au mois 2 si tu tiens le rythme sans effort.** La régularité compte plus que le volume ; un rythme intenable fait abandonner la chaîne."],
    ["D3", "Source des personnages", "Dessin maison (Aseprite 9,99 $ + taxe, ou Pixelorama gratuit) · packs CC0 · packs payants", "**Héros dessinés par toi dans Aseprite** (identité unique, et seuls vendables en pack ; Aseprite exporte tout seul planche + données, § 7.2) ; **figurants, objets et tuiles** en CC0 au début. Claude prépare les gabarits et vérifie les planches."],
    ["D4", "Voix", "Ta voix (téléphone, micro-cravate ~15 €) · synthèse vocale externe payante · pas de voix (texte + bruitages)", "**Gags : pas de voix** (bruitages 8 bits + bulles, comme un jeu rétro : c'est un style, pas un manque). **Science : ta voix**, avec un micro-cravate. La voix humaine retient mieux et protège contre le reproche de contenu « fabriqué en série »."],
    ["D5", "Langue", "Français seul · français + anglais", "**Français d'abord.** Une version anglaise des gags sans voix ne demande que de changer les bulles : à tester au mois 3."],
    ["D6", "Budget de départ", "0 € · ~50 €", "**~40 €** : Aseprite (11,79 $ taxe comprise, choisi), micro-cravate (~15 €), 1 pack de tuiles payant (~10 $). Le reste est gratuit."],
    ["D7", "Âge et statut", "—", "Plusieurs programmes exigent **18 ans** (TikTok Creator Rewards, paiements) et un statut déclaré pour encaisser (§ 14.5). À vérifier avant le premier paiement."],
    ["D8", "Ordre d'installation des logiciels", "Tout de suite · au fil des besoins", "**Au fil des besoins**, dans cet ordre : FilmCraft (sous-titres) et SoundCraft (voix, jingle) en semaine 1, PhotoCraft (décors, miniatures) en semaine 2, VectorCraft (logo) en semaine 3. Chaque logiciel compilé coûte du temps et de la place ; on ne le compile que quand il sert (§ 10.4)."],
    ["D9", "Les deux copies d'EffectCraft", "Garder les deux · une seule", "**~/dev/vid/effectcraft reste la copie de production** (déjà compilée, utilisée par monter.py et Claude). **~/videos/logiciel/effectcraft devient le futur fork** (branche perso, § 9.2), sinon on la supprime pour ne jamais modifier la mauvaise copie (§ 10.5)."],
    ["D10", "Lier les gags et la science (proposé par Gemini)", "Séries indépendantes · gags qui renvoient à la vidéo longue de la quinzaine", "**Lier pendant 6 mois.** Coût nul, et chaque gag devient une porte d'entrée vers la vidéo qui rapporte des heures (ex. Tim perdu à cause d'une horloge décalée → vidéo GPS)."],
    ["D11", "Durée des vidéos de science (Gemini : 4–5 min)", "6–10 min (plan 2.2) · 4–5 min · 6 min au départ", "**6 min au départ, puis ajuster sur la rétention mesurée.** Gemini a raison sur la charge (≈ 1 plan toutes les 3–4 s = 100 à 130 plans pour 8 min) ; mais une vidéo plus courte rapporte moins d'heures par vue. On tranche au bilan du mois 3, chiffres en main."],
    ["D12", "Ambiances et Tim (Gemini : ambiances hors de la chaîne, Tim au mois 6)", "Mois 2 (plan 2.2) · reporter · sortir de la chaîne", "**Tim au mois 6** (série la plus chère à produire). **Ambiances : une seule au mois 3, en test**, avec de vrais événements à l'écran ; Gemini signale le risque de refus pour contenu répétitif à l'examen YouTube, mais ce sont elles qui accumulent les heures le plus vite (§ 12.2). Décision finale au bilan du mois 6."],
    ["D13", "Cible de la boutique (Gemini : streamers d'abord)", "Packs pour jeux (itch.io) · emotes et écrans de stream · les deux", "**Streamers d'abord** (emotes animées, écrans « Starting soon / BRB », alertes) et un **mini-pack gratuit sur itch.io** en semaine 6 pour se faire trouver. Un spectateur de vulgarisation achète rarement des assets de jeu ; un streamer achète à l'unité."],
    ["D14", "Logiciels au mois 1 (Gemini : FilmCraft seul)", "Plan D8 · FilmCraft seul au mois 1, le reste après la 10e vidéo", "**FilmCraft en semaine 1** (sous-titres et regarder les vidéos), **décors dans Aseprite** au début ; SoundCraft, PhotoCraft et VectorCraft quand une vidéo en a vraiment besoin. C'est la règle d'or appliquée aux logiciels. Remplace D8 si tu valides."],
  ], [0.5, 1.8, 3.2, 4.2]),
  NOTE("**D10 à D14 viennent du deuxième avis de Gemini** (§ 10.8). Claude a vérifié ce que Gemini dit du plan et donne sa propre recommandation pour chacune ; quand les deux modèles divergent, c'est écrit. La décision reste la tienne."),
);

// ================================================================ 4
C.push(
  H1("4. Direction artistique « ico-vid pixel »"),
  P("Le dossier **Bureau ▸ pixel** contient 4 images qui donnent la direction. **Aucune ne peut apparaître dans une vidéo publiée** : ce sont des œuvres d'autres artistes, et l'une représente un personnage de jeu protégé. Elles servent seulement à décrire un style, que l'on refait entièrement avec nos propres dessins."),
  table(["Fichier", "Ce qu'on en retient (style)", "Utilisable en vidéo ?"], [
    ["artistic-pixel_art-1002548", "Ruines en vue plongeante, herbe en aplats, ombres longues, palette verte et douce : ambiance « cosy »", "Non : auteur inconnu, droits réservés"],
    ["artistic-pixel_art-1023270", "Terre et Lune dans l'espace, nébuleuse en tons bleus, étoiles scintillantes", "Non : signé @exilecast"],
    ["artistic-pixel_art-981491", "Village « Owl's nest » : chaumière, rivière, pont, personnages minuscules, cadre par la végétation au premier plan", "Non : droits réservés"],
    ["…final_fantasy…381064", "Mage noir 16 bits : contour noir épais, 4–5 couleurs, silhouette lisible", "Non : personnage de Square Enix"],
  ], [2.6, 4.6, 2.2]),
  GAP(),
  H2("4.1 Les résolutions (le choix le plus important)"),
  P("Tout se dessine et s'anime dans une **petite comp** (la « scène »), puis s'agrandit d'un **facteur entier** en plus proche voisin. Un facteur non entier (×3,5 par exemple) rend certains pixels plus larges que d'autres : c'est interdit."),
  table(["Format", "Scène (pixels de dessin)", "Agrandissement", "Sortie", "Usage"], [
    ["Vertical", "**270×480**", "×4", "1080×1920", "Shorts, TikTok, Reels"],
    ["Horizontal", "**480×270**", "×4", "1920×1080", "Vidéos longues (standard)"],
    ["Horizontal 4K", "480×270", "×8", "3840×2160", "Vidéos longues importantes (voir l'astuce)"],
    ["Gros plan", "240×135 (ou 135×240)", "×8", "1920×1080 (ou 1080×1920)", "Réaction, dialogue, miniature"],
  ], [1.6, 2.2, 1.4, 2, 2.4]),
  ASTUCE("**Astuce qualité YouTube** : une vidéo envoyée en 4K (3840×2160) est réencodée par YouTube avec un meilleur codec et plus de débit, **même quand le spectateur la regarde en 1080p**. Pour le pixel art, plein d'aplats et d'arêtes vives, la différence est visible. Coût : le rendu et l'envoi prennent plus de temps. À faire pour les vidéos longues phares, pas pour chaque Short."),
  H2("4.2 Personnages"),
  B("**Taille** : cellule de **32×32 px** ; le personnage mesure **24 à 28 px de haut** dans sa cellule (il reste de la place pour les bras, le saut, les effets). Gros plans : cellule de 64×64."),
  B("**Contour** : sombre (pas forcément noir : la couleur la plus foncée de sa rampe), 1 px, avec des **coins sans doublon** (pas de « marche d'escalier » de 2 px)."),
  B("**Couleurs** : 4 à 6 couleurs par personnage, prises dans la palette de la série (§ 4.4)."),
  B("**Lisibilité** : test de la silhouette. On remplit le personnage en noir sur fond blanc : on doit reconnaître qui c'est et ce qu'il fait. Sinon on exagère la pose."),
  B("**Tête grosse** (environ 1/3 de la hauteur) : expressions lisibles même sur un téléphone."),
  B("**Regard vers la droite par défaut** ; l'autre sens s'obtient par miroir horizontal (échelle X à −100 %), qui reste net."),
  H2("4.3 Décors"),
  B("**Tuiles de 16×16 px** pour le sol, les murs, l'eau ; objets en multiples de 8 px."),
  B("**Plans de profondeur** (5 au maximum, 6 avec les effets) : ciel · loin · milieu · action · premier plan · effets (pluie, lucioles, poussière)."),
  B("**Contraste par la distance** : les plans lointains sont plus clairs, plus bleus et moins contrastés ; le premier plan est le plus sombre, souvent en silhouette."),
  B("**Largeur des décors** : au moins la largeur de la scène + la course de la caméra. Pour un travelling de 240 px dans une scène de 480 px de large, le plan d'action fait au moins 720 px ; les plans lointains bougent moins, donc ils peuvent être plus étroits (§ 6.3)."),
  B("**Cadre par le premier plan** (feuillages, poteaux, rebords) comme dans la référence « Owl's nest » : c'est lui qui donne la profondeur quand la caméra bouge."),
  H2("4.4 Palette « ico-pixel 32 » (proposition v1)"),
  P("32 couleurs en **8 rampes de 4 teintes** (de la plus sombre à la plus claire). Elle part des 6 couleurs de la série pixel de la bible (**F4C542, 1D1B2E, 3E5BA9, E5533D, 3FB56B, F2EDE4**, toutes présentes) et ajoute les teintes intermédiaires. Les ombres glissent vers le bleu ou le violet plutôt que vers le gris : c'est ce qui donne l'aspect « cosy » des références."),
  swatches([
    ["Nuits et contours", ["0E0D18", "1D1B2E", "2F2C45", "4A4663"]],
    ["Neutres et crème", ["6E6A80", "9A96A6", "C9C4C8", "F2EDE4"]],
    ["Bleus (ciel, eau)", ["1F2E5C", "3E5BA9", "5E8FD6", "9CC7F0"]],
    ["Verts (herbe, feuilles)", ["1E4D3A", "2E7D4F", "3FB56B", "8FDB86"]],
    ["Ors (pièces, lumière)", ["7A4E1E", "B9802B", "F4C542", "FBE58C"]],
    ["Rouges (danger, cœur)", ["5A1E2B", "9E2F33", "E5533D", "F59A7A"]],
    ["Terres (bois, chemin)", ["3B2A22", "6B4A35", "9C7451", "C9A57A"]],
    ["Violets (magie, nuit)", ["3D2550", "6B3F87", "A066B8", "E0A6D9"]],
  ]),
  GAP(),
  P("La palette est enregistrée en trois exemplaires identiques : dans la bible (tableau), en fichier **ico-pixel-32.gpl** (format lu par Pixelorama, Aseprite, GIMP) et en **ico-pixel-32.hex** (une couleur par ligne, lu par les scripts de contrôle). Une couleur hors palette dans un rendu est une erreur détectée automatiquement (§ 6.6)."),
  H2("4.5 Animation : le nombre d'images par action"),
  P("Les personnages s'animent à **12 images par seconde** (une image de dessin tient 2 images de la vidéo à 24 i/s). La caméra, elle, bouge à 24 i/s pour rester fluide."),
  table(["Action", "Images", "Durée à 12 i/s", "Détail"], [
    ["Repos (respiration)", "2 à 4", "en boucle, 1 image toutes les 3–4 (lent)", "Le corps monte d'1 px, les yeux clignent toutes les 3 s environ"],
    ["Marche", "4 (ou 6)", "0,33 à 0,5 s par cycle", "Contact · passage · contact · passage ; avance au sol réglée pour que les pieds ne glissent pas"],
    ["Course", "6", "0,5 s par cycle", "Corps penché, 1 image en l'air"],
    ["Saut", "6 à 8", "0,5 à 0,7 s", "Anticipation (2) · envol (2) · sommet (1) · chute (2) · réception (1)"],
    ["Parler", "2 à 3 bouches", "pilotées par la voix ou le texte", "Fermée · mi-ouverte · ouverte"],
    ["Coup reçu", "3", "0,25 s + clignotement", "Recul de 2 px, image blanche d'1 frame, puis clignotement (mouvement rapide pixel-degats)"],
    ["Surprise / réaction", "2", "tenue 0,5 à 1 s", "Saut sur place d'1 image + « ! » au-dessus de la tête"],
    ["Chute / K.O.", "6", "0,5 s", "Tombe, rebondit d'1 px, étoiles qui tournent"],
  ], [1.8, 1.2, 2.4, 4.2]),
  GAP(),
  H2("4.6 Les interdits du pixel (et pourquoi)"),
  table(["Interdit", "Ce que ça provoque", "À la place"], [
    ["Échelle non entière (×1,5, 133 %…)", "Pixels de tailles différentes, image floue", "Paliers ×1, ×2, ×3 ; changement de cadrage par une coupe"],
    ["Rotation libre (15°, 30°…)", "Bords en escalier irréguliers", "Rotation de 90° ou 180°, ou dessiner l'image tournée"],
    ["Position au demi-pixel", "Le sprite « bave » sur 2 colonnes", "Toutes les positions arrondies (Math.round) dans les expressions"],
    ["Flou, lueur douce, ombre portée floue", "Couleurs hors palette", "Ombres dessinées en aplats ; lueur en 2 ou 3 anneaux de pixels"],
    ["Texte lissé (anticrénelé)", "Contours gris autour des lettres", "Press Start 2P à 8 ou 16 px dans la scène, sans lissage (journal n° 18)"],
    ["Mélanger des tailles de pixels (« mixels »)", "Un objet agrandi ×2 à côté d'objets ×1 : style cassé", "Tout dessiner à la même échelle"],
    ["Fondu d'opacité progressif", "Couleurs intermédiaires hors palette", "Fondu en marches (4 paliers), volet, iris pixel, ou fondu au noir par tramage"],
  ], [2.6, 3.2, 3.8]),
);

// ================================================================ 5
C.push(
  H1("5. Assets et licences : la bibliothèque"),
  P("Un **asset** est tout ce qui entre dans une vidéo sans être fabriqué dans le projet : sprite, tuile, décor, son, musique, police, icône. La bibliothèque est rangée **une seule fois**, et chaque fichier y entre avec sa licence. C'est ce qui permet de produire vite sans jamais risquer une réclamation de droits."),
  H2("5.1 Arborescence"),
  ...CODE(`~/videos/assets/
├── manifest.toml            ← une entrée par asset (source, auteur, licence, date)
├── palettes/                ← ico-pixel-32.gpl, ico-pixel-32.hex
├── persos/
│   └── tim/
│       ├── tim.aseprite     ← fichier source (ou .pxo pour Pixelorama)
│       ├── tim-planche.png  ← planche exportée (grille 32×32)
│       ├── tim.toml         ← description des actions (lignes, nombre d'images)
│       └── actions/         ← images découpées par decouper_planche.py
├── decors/
│   └── village-jour/        ← un PNG par plan : 1-ciel.png … 5-premier.png
├── objets/  icones/  fx/    ← pièces, coffres, éclair, satellite, poussière…
├── sons/                    ← bruitages 8 bits (.wav)
└── musiques/                ← musiques avec licence vérifiée
~/videos/references/         ← inspiration seulement (les 4 images « pixel »), jamais en vidéo`),
  H2("5.2 Le manifeste des licences"),
  P("Chaque asset a une entrée. Un script de contrôle (**verifier_licences.py**) refuse un rendu si un fichier utilisé dans le projet n'a pas d'entrée, ou si sa licence interdit l'usage commercial."),
  ...CODE(`[[asset]]
fichier  = "decors/village-jour/3-milieu.png"
source   = "dessin maison"
auteur   = "@yehz"
licence  = "propriétaire"           # propriétaire | CC0 | CC-BY-4.0 | itch-commercial | …
url      = ""
date     = 2026-10-24
vendable = true                     # peut entrer dans un pack de la boutique ?
credit   = ""                       # texte à mettre en description si la licence l'exige

[[asset]]
fichier  = "objets/kenney-coffre.png"
source   = "Kenney, pack « Pixel Platformer »"
auteur   = "Kenney"
licence  = "CC0"
url      = "https://kenney.nl/…"
date     = 2026-10-24
vendable = false                    # libre, mais on ne revend pas le travail des autres`),
  H2("5.3 Quelles licences accepter"),
  table(["Licence", "Vidéo monétisée ?", "Dans un pack vendu ?", "Obligation"], [
    ["**Propriétaire** (ton dessin, tes sons)", "Oui", "Oui", "Aucune"],
    ["**CC0** (domaine public)", "Oui", "Techniquement oui, mais **non par principe** (et souvent refusé par les boutiques)", "Aucune ; on crédite quand même, c'est apprécié"],
    ["**CC-BY**", "Oui", "Non", "Créditer l'auteur dans la description (texte exact dans le manifeste)"],
    ["**CC-BY-SA**", "Oui, avec prudence", "Non", "Créditer ; la vidéo dérivée devrait être sous la même licence : **à éviter**"],
    ["**CC-BY-NC** (non commercial)", "**Non** (une chaîne monétisée est commerciale)", "Non", "—"],
    ["**CC-BY-ND** (pas de modification)", "Non (on recadre, recolore, anime)", "Non", "—"],
    ["Licence d'un pack itch.io", "Selon le texte du pack", "Presque jamais", "Lire et copier le texte de la licence dans le manifeste"],
    ["Polices OFL", "Oui", "Non (on ne revend pas une police)", "Garder le fichier de licence (déjà fait)"],
  ], [2.4, 2.4, 2.4, 2.4]),
  GAP(),
  ALERTE("**Pas de licence vérifiée, pas d'utilisation.** Une seule réclamation de droits peut démonétiser une vidéo, et plusieurs peuvent fermer une chaîne. Les 4 images du dossier « pixel », les sprites de jeux connus (Mario, Zelda, Final Fantasy, Pokémon…), les musiques de jeux et les « packs gratuits » sans licence écrite sont **interdits**."),
  H2("5.4 Où trouver des assets légaux"),
  table(["Besoin", "Source", "Licence", "Remarque"], [
    ["Tuiles, objets, figurants", "Kenney (kenney.nl), OpenGameArt filtré « CC0 »", "CC0", "Qualité correcte, style déjà vu : pour le décor, pas pour les héros"],
    ["Tilesets complets de qualité", "itch.io (packs « commercial use allowed »)", "Licence du pack", "5–30 $ ; vérifier « utilisation dans des vidéos »"],
    ["Bruitages 8 bits", "**jsfxr / sfxr** (navigateur) ; **SoundCraft** (synthé de batterie, sampler)", "Les sons générés sont à toi", "Saut, pièce, coup, menu : en 2 minutes, sans risque"],
    ["Musique", "Bibliothèque audio YouTube ; Freesound filtré CC0", "Indiquée par fichier", "Vérifier aussi l'usage hors YouTube (TikTok, Instagram)"],
    ["Musique faite maison", "**SoundCraft** (synthé soustractif, batterie, sampler, piano roll MIDI) ; BeepBox (navigateur)", "À toi", "Idéal pour un jingle ico-vid unique (question ouverte de la bible)"],
    ["Icônes de vulgarisation", "Dessin maison 16×16 (Claude prépare des formes simples)", "À toi", "Éclair, satellite, horloge, cerveau… : répond au journal n° 26"],
  ], [2.2, 3, 1.8, 2.6]),
  H2("5.5 Ajouter un asset : la procédure (2 minutes)"),
  ...LIST("m55", [
    "Télécharger dans **~/videos/a-trier/** (jamais directement dans assets/).",
    "Lire la licence sur la page d'origine ; copier son URL.",
    "Dire à Claude « range cet asset » : Claude vérifie le format (PNG transparent, couleurs), le renomme, le range et écrit l'entrée du manifeste.",
    "Si une couleur sort de la palette : Claude propose une version recolorée (la plus proche de la palette) et garde l'original à côté.",
    "git commit : l'asset et sa licence entrent ensemble dans l'historique.",
  ]),
);

// ================================================================ 6
C.push(
  H1("6. Le moteur caméra pixel"),
  P("Un « vrai » mouvement de caméra en pixel art ne peut pas utiliser la caméra 3D classique : elle agrandit et tourne les images à des tailles non entières, et les pixels bavent. On construit donc **un moteur caméra 2,5D** avec ce qu'EffectCraft fait très bien et gratuitement au rendu : des **expressions**, des **précomps** et un **calque nul** de contrôle."),
  H2("6.1 Principe"),
  ...LIST("m61", [
    "La **scène** est une comp en basse résolution (480×270 ou 270×480) qui contient 4 à 6 **plans** (calques ou précomps) : ciel, loin, milieu, action, premier plan, effets.",
    "Un calque nul **CAM** représente la caméra. Sa **position** = le point que la caméra regarde ; son **échelle** = le zoom (100, 200 ou 300 %) ; ses **marqueurs** nommés « secousse » déclenchent les secousses.",
    "Chaque plan suit CAM selon sa **profondeur** (ciel ×0,1 ; loin ×0,3 ; milieu ×0,6 ; action ×1 ; premier plan ×1,4) : c'est la **parallaxe**, qui donne l'illusion de relief.",
    "Toutes les positions sont **arrondies au pixel entier**.",
    "Le **zoom** se fait dans la comp de sortie, sur la scène entière, uniquement en paliers entiers : ×4 (zoom 1), ×8 (zoom 2), ×12 (zoom 3).",
    "La sortie agrandit en qualité **Draft** (plus proche voisin) : aucun flou.",
  ]),
  ASTUCE("**Pourquoi les réglages sont sur la transformation du nul, et pas sur des curseurs ?** Le journal (n° 24) a mesuré qu'un simple effet « Slider Control » coûte environ 200 ms par image sur cette machine. La position, l'échelle et les marqueurs d'un calque nul, eux, ne coûtent rien. Le moteur reste donc **gratuit au rendu**. (Mesure de contrôle prévue en semaine 2 : si un curseur sur un nul est aussi gratuit, on pourra ajouter des réglages nommés.)"),
  H2("6.2 L'expression d'un plan (parallaxe)"),
  P("Posée par **camera.py** sur la position de chaque plan ; seule la ligne **P** change d'un plan à l'autre."),
  ...CODE(`// ico-vid · caméra pixel · plan « milieu »
var P = 0.6;                                   // profondeur : 0 = immobile (ciel), 1 = action
var cam = thisComp.layer("CAM").transform.position;
var C = [thisComp.width / 2, thisComp.height / 2];
var v = value.slice();                         // value est en 2D (journal n° 25)
v[0] = Math.round(v[0] - (cam[0] - C[0]) * P);
v[1] = Math.round(v[1] - (cam[1] - C[1]) * P);
v;`),
  H2("6.3 Taille des décors selon la profondeur"),
  P("Un plan de profondeur P parcourt **P × la course de la caméra**. Largeur minimale d'un plan = largeur de la scène + P × course. Exemple pour une scène de 480 px et un travelling de 300 px :"),
  table(["Plan", "Profondeur P", "Déplacement", "Largeur minimale"], [
    ["Ciel", "0,1", "30 px", "510 px"],
    ["Loin (montagnes)", "0,3", "90 px", "570 px"],
    ["Milieu (village)", "0,6", "180 px", "660 px"],
    ["Action (sol, persos)", "1", "300 px", "780 px"],
    ["Premier plan (feuillage)", "1,4", "420 px", "900 px (ou des éléments espacés, pas une bande pleine)"],
  ], [2.6, 1.6, 2, 3.4]),
  ASTUCE("**Les plans lents « sautillent » ?** Le ciel à P = 0,1 ne bouge que d'1 pixel quand la caméra avance de 10 : à vitesse lente, on voit des petits sauts. C'est normal en pixel art ; pour l'adoucir, on garde des travellings assez rapides (≥ 40 px/s pour la caméra) ou on laisse le ciel immobile (P = 0)."),
  H2("6.4 La comp de sortie (zoom et secousse)"),
  ...CODE(`// Échelle de la scène dans la comp de sortie : paliers entiers seulement
var z = Math.max(1, Math.round(comp("SCENE").layer("CAM").transform.scale[0] / 100));
[400 * z, 400 * z];

// Position : garder le point visé au centre quand on zoome, + secousse au marqueur
var cam  = comp("SCENE").layer("CAM");
var p    = cam.transform.position;              // point visé (pixels de scène)
var z    = Math.max(1, Math.round(cam.transform.scale[0] / 100));
var k    = 4 * z;                               // taille d'un pixel de scène à l'écran
var t0 = -1;
for (var i = 1; i <= cam.marker.numKeys; i++) if (cam.marker.key(i).time <= time) t0 = cam.marker.key(i).time;
var d = t0 < 0 ? -1 : time - t0, s = [0, 0];
if (d >= 0 && d < 0.4) { var a = Math.round(3 * (1 - d / 0.4));   // 3 px de scène, décroissant
  s = [ (Math.floor(time * 24) % 2 ? a : -a), (Math.floor(time * 24) % 3 ? 0 : a) ]; }
var c = [thisComp.width / 2, thisComp.height / 2];
[ c[0] + (comp("SCENE").width / 2 - p[0] + s[0]) * k,
  c[1] + (comp("SCENE").height / 2 - p[1] + s[1]) * k ];`),
  P("Ces expressions sont des **brouillons de spécification** : camera.py les génère et les teste (rendu de contrôle) avant de les poser. Les noms exacts (SCENE, CAM) sont fixés dans le modèle."),
  H2("6.5 Bibliothèque de mouvements"),
  table(["Mouvement", "Comment il est fait", "Réglages", "Usage"], [
    ["**Travelling** latéral ou vertical", "2 clés sur la position de CAM, courbe amortie (ease in/out)", "de, à, durée, courbe", "Suivre une marche, révéler un décor"],
    ["**Panoramique révélation**", "Travelling vertical lent + léger dépassement (2 px) à l'arrêt", "de, à, durée", "Ciel, tour, planète"],
    ["**Suivi** de personnage", "Position de CAM = moyenne de la position du perso sur les 0,1–0,3 s précédentes (la caméra « rattrape »), bornée aux bords du décor", "cible, retard, bornes", "Le héros reste cadré quand il bouge"],
    ["**Zoom par paliers**", "Échelle de CAM 100 → 200 % en coupe franche (ou sur 2 images)", "palier, temps", "Réaction, gag"],
    ["**Secousse** d'impact", "Marqueur « secousse » sur CAM", "force (px de scène), durée", "Chute, explosion, porte qui claque"],
    ["**Caméra à la main**", "Dérive d'1 px très lente (période 3–5 s)", "amplitude", "Scènes calmes, ambiances"],
    ["**Ensemble → rapproché**", "Coupe entre deux cadrages (zoom 1 → zoom 2) sur un mouvement du perso", "temps de coupe", "Raconter : où, puis qui"],
    ["**Iris / volet pixel**", "Cercle ou volet dessiné en marches de pixels, sur la comp de sortie", "centre, durée", "Fin de scène, transition"],
  ], [2.2, 3.6, 1.8, 2]),
  GAP(),
  H2("6.6 Le contrôle « zéro pixel baveux » (automatique)"),
  P("**verifier_pixels.py** prend quelques images rendues **en PNG** (pas le .mp4 : la compression vidéo mélange forcément un peu les couleurs) et vérifie deux choses :"),
  B("**Blocs entiers** : à ×4, chaque carré de 4×4 pixels de l'image doit être d'une seule couleur (sinon un calque est à une position ou une échelle non entière)."),
  B("**Palette** : chaque couleur doit appartenir à la palette de la série, aux couleurs des polices près (sinon un flou, un fondu ou un asset non conforme s'est glissé)."),
  P("Le rapport donne l'image, la zone fautive et le calque probable. **monter.py --rendu refuse de lancer un rendu si ce contrôle échoue** (sauf option --forcer)."),
  H2("6.7 Et la caméra 3D ?"),
  P("Pour les formats qui ne sont pas en pixel (fantasy illustrée, vulgarisation classique), on garde la **caméra 3D d'EffectCraft** : calques 3D, profondeur de champ, flou de mouvement. Les deux voies restent séparées, pour ne pas mélanger les styles dans une même vidéo."),
  H2("6.8 Livrables et critère de fin"),
  table(["Fichier", "Rôle"], [
    ["outils/camera.py", "Génère les expressions de CAM, des plans et de la sortie ; applique un mouvement de la bibliothèque à partir d'une ligne de l'épisode"],
    ["outils/verifier_pixels.py", "Contrôle blocs entiers + palette sur les PNG rendus"],
    ["modeles/scene-pixel-16x9.ecproj, scene-pixel-9x16.ecproj", "SCENE + CAM + 5 plans + sortie déjà reliés ; guide des zones sûres"],
    ["modeles/README.md", "Mode d'emploi des modèles pixel v2 (mis à jour)"],
  ], [3.6, 6]),
  GAP(),
  NOTE("**Critère de fin du moteur** : une scène de 15 s avec 2 personnages, 5 plans de profondeur et 3 mouvements de caméra (travelling, zoom, secousse), montée depuis un fichier texte, rendue, et **verifier_pixels.py au vert sur toutes les images**."),
);

// ================================================================ 7
C.push(
  H1("7. Personnages : de la planche au calque"),
  H2("7.1 Le format de planche (à respecter en dessinant)"),
  B("**PNG transparent**, grille de **32×32** (ou 64×64 pour un gros plan), sans marge ni espacement entre les cases."),
  B("**Une ligne par action**, dans l'ordre de la fiche du personnage ; les images d'une action se lisent de gauche à droite."),
  B("**Pieds alignés** sur la même ligne de pixels dans toutes les cases (ligne de sol), sinon le personnage « flotte » d'une image à l'autre."),
  B("**Transparence totale ou nulle** : aucun pixel semi-transparent."),
  B("Couleurs prises **uniquement** dans la palette de la série."),
  ...CODE(`# persos/tim/tim.toml — fiche du personnage
nom     = "Tim"
cellule = [32, 32]
sol     = 29                 # ligne des pieds (en pixels depuis le haut de la case)
regard  = "droite"

[actions]                    # ligne de la planche, nombre d'images, i/s, boucle
repos  = { ligne = 1, images = 4, ips = 4,  boucle = true }
marche = { ligne = 2, images = 4, ips = 12, boucle = true,  avance = 16 }   # px par cycle
saut   = { ligne = 3, images = 7, ips = 12, boucle = false }
parle  = { ligne = 4, images = 3, ips = 12, boucle = true }
coup   = { ligne = 5, images = 3, ips = 12, boucle = false }`),
  H2("7.2 decouper_planche.py"),
  P("Lit la planche et la fiche, puis :"),
  ...LIST("m72", [
    "**contrôle** la planche : taille multiple de la cellule, pixels semi-transparents, couleurs hors palette, pieds sur la ligne de sol, cases vides là où la fiche attend une image ;",
    "**découpe** chaque action en images numérotées (actions/marche_01.png …) ;",
    "**construit** une précomp par personnage dans le projet : une séquence d'images par action, posée bout à bout ;",
    "**ajoute** l'expression de sélection d'action (§ 7.3) ;",
    "**produit** une planche de contrôle (toutes les actions animées côte à côte, en GIF) pour validation en un coup d'œil.",
  ]),
  ASTUCE("**Avec Aseprite, la fiche s'écrit toute seule.** Dans Aseprite, chaque action est une **étiquette** (tag) sur la timeline : « repos », « marche », « saut »…, avec la durée de chaque image. Aseprite exporte en une commande la planche **et** un fichier JSON qui décrit les étiquettes et les durées. Claude lance cet export sans ouvrir la fenêtre, et decouper_planche.py lit le JSON au lieu de deviner : tu dessines, tu enregistres le .aseprite, et la précomp du personnage se met à jour."),
  ...CODE(`# lancé par Claude depuis WSL (Aseprite installé sous Windows)
aseprite.exe -b tim.aseprite --sheet tim-planche.png --sheet-type rows --split-tags \\
             --data tim.json --format json-array --list-tags`),
  H2("7.3 Changer d'action dans une scène"),
  P("Dans la scène, un personnage est **un seul calque** (la précomp). Ses **marqueurs** portent le nom de l'action : « marche », « saut », « repos »… Une expression de **remappage temporel** lit le dernier marqueur passé et joue la bonne action, en boucle ou une seule fois selon la fiche. Résultat : pour animer, on pose des marqueurs, rien d'autre. monter.py v2 les pose à partir de l'épisode."),
  H2("7.4 Qui dessine quoi"),
  table(["Élément", "Qui", "Temps estimé", "Remarque"], [
    ["Gabarit de planche vide (grille, ligne de sol, palette)", "Claude", "5 min", "Fichier .png + .gpl (ou .aseprite) à ouvrir dans Aseprite"],
    ["Héros (5 actions, ~20 images)", "Toi", "3 à 6 h la première fois, puis 1 à 2 h par perso", "C'est l'investissement qui fait l'identité de la chaîne"],
    ["Figurants, animaux, objets", "Packs CC0 recolorés, ou toi", "10 min à 1 h", "Recoloration automatique vers la palette"],
    ["Prototype en formes simples", "Claude (script)", "quelques minutes", "Sert à tester le moteur avant que le vrai dessin existe"],
    ["Décors en plans (ciel → premier plan)", "Toi dans **PhotoCraft** (un calque par plan, fichier PSD) ou Pixelorama", "1 à 3 h par décor", "EffectCraft importe le PSD comme une comp, calques séparés et à leur place (§ 10.1)"],
    ["Icônes 16×16 de vulgarisation", "Claude propose, toi tu retouches", "15 min par lot de 10", "Bibliothèque icones/"],
  ], [3.2, 1.8, 2.4, 2.2]),
);

// ================================================================ 8
C.push(
  H1("8. L'épisode en fichier texte : episode.toml v2"),
  P("monter.py v1 remplit un modèle. **monter.py v2** construit une vidéo **plan par plan** : chaque plan a son décor, ses personnages, ses actions, son mouvement de caméra, ses sons et ses répliques. Un épisode complet tient sur une page, se relit facilement et se versionne avec git."),
  H2("8.1 Exemple complet (gag de 20 s)"),
  ...CODE(`format  = "pixel2"
slug    = "gag-03-sauvegarde"
ratio   = "9:16"                     # ou "16:9"
palette = "ico-pixel-32"
musique = { fichier = "musiques/boucle-village.wav", volume = -18 }

[[plans]]
nom    = "ouverture"
duree  = 3.0
decor  = "village-jour"
camera = { mouvement = "panoramique", de = [135, 120], a = [135, 300], courbe = "amortie" }
persos = [ { id = "tim", x = 120, y = 410, actions = [ { a = "repos", t = 0 } ] } ]

[[plans]]
nom    = "la course"
duree  = 6.0
decor  = "village-jour"
camera = { mouvement = "suivi", cible = "tim", retard = 0.15 }
persos = [ { id = "tim", x = 60, y = 410, vers = [400, 410],
             actions = [ { a = "marche", t = 0 }, { a = "saut", t = 3.2 }, { a = "marche", t = 3.8 } ] } ]
sons   = [ { fichier = "sons/saut.wav", t = 3.2 } ]

[[plans]]
nom    = "la chute"
duree  = 4.0
decor  = "village-jour"
camera = [ { mouvement = "zoom", palier = 2, t = 0.5 }, { mouvement = "secousse", force = 3, t = 1.2 } ]
persos = [ { id = "tim", x = 200, y = 410, actions = [ { a = "coup", t = 1.2 }, { a = "repos", t = 2.0 } ] } ]
sons   = [ { fichier = "sons/coup.wav", t = 1.2 } ]

[[repliques]]                        # sans voix : bulles et sous-titres Press Start 2P
plan  = "la chute"
texte = "SAUVEGARDE ?"
t     = 2.2
bulle = "tim"                        # affichée dans une bulle au-dessus de Tim`),
  H2("8.2 Ce que monter.py v2 fait de ce fichier"),
  ...LIST("m82", [
    "Vérifie le fichier : assets présents et sous licence, actions connues, temps cohérents, durées dans la bible, textes ≤ 12 caractères par ligne en pixel.",
    "Construit une comp SCENE par plan (à partir du modèle « Scène pixel »), y place les plans du décor et les personnages, pose les marqueurs d'action.",
    "Applique les mouvements de caméra (camera.py) et les positions arrondies.",
    "Enchaîne les plans dans la comp de sortie, ajoute musique, sons, bulles, sous-titres et la signature.",
    "Si un fichier **.srt** (transcription FilmCraft) est à côté de la voix, cale chaque sous-titre sur ses temps exacts au lieu de l'estimation à 2,8 mots par seconde.",
    "Rend **3 aperçus PNG** + une **planche contact** (16 images horodatées sur une seule image, journal n° 3) et lance verifier_pixels.py.",
    "Affiche un résumé avec les **alertes** (texte trop long, plan sans mouvement de caméra, couleur hors palette, son sans licence…).",
  ]),
  NOTE("**Compatibilité** : les épisodes v1 (sketch, vulga…) continuent de fonctionner avec monter.py v2. Le format « pixel2 » est nouveau, il ne remplace rien. C'est pour cela que l'usine passe en **2.0.0** (§ 19)."),
);

// ================================================================ 9
C.push(
  H1("9. Personnalisation d'EffectCraft"),
  H2("9.1 Sans toucher au code (semaines 1–3)"),
  table(["Personnalisation", "Détail", "Comment", "Statut"], [
    ["Espace de travail « ico-vid pixel »", "Timeline large, viewer à 200 ou 400 %, panneaux Effets et presets à droite", "Fenêtre ▸ Espace de travail ▸ Enregistrer", "À faire (toi, 10 min)"],
    ["Modèles « Scène pixel 16:9 / 9:16 »", "SCENE + CAM + 5 plans + sortie + guide", "Claude, comme les modèles v1", "À faire (§ 6)"],
    ["Mouvements rapides caméra", "travelling, suivi, zoom, secousse, main, iris pixel", "Scripts .jsonl (comme les 10 rapides existants)", "À faire"],
    ["Modèles d'export", "« Short 9:16 H.264 » (fait) · « Long 16:9 H.264 » · « Long 4K pixel » · « Boucle GIF / WebM » pour la boutique", "File d'attente de rendu ▸ Enregistrer le modèle (instance GUI, journal n° 15)", "1 sur 4"],
    ["Raccourcis", "Ajouter un marqueur, Draft/Best, appliquer un mouvement rapide", "Édition ▸ Raccourcis clavier", "À faire (toi)"],
    ["Comp « Miniature »", "1280×720 (YouTube) à partir d'une image de la vidéo, gros texte, personnage agrandi ×8", "Modèle + preset de texte", "À faire (§ 13.3)"],
  ], [2.4, 3.2, 2.6, 1.4]),
  GAP(),
  H2("9.2 Avec du code (fork, seulement si le journal l'exige)"),
  P("On travaille sur **un fork** du dépôt EffectCraft, branche **perso**, et on garde le dépôt officiel comme « upstream » pour récupérer ses mises à jour. Chaque fonction ajoutée est une **commande** (id, paramètres) : elle apparaît alors dans les menus, la ligne de commande et pour Claude. Ce qui est utile à tous est proposé au projet officiel (moins de code à maintenir soi-même)."),
  table(["#", "Fonction", "Gêne du journal", "Priorité", "Règle des 2 vidéos"], [
    ["1", "Contrôles d'expression gratuits au rendu", "n° 24 : un curseur coûte ~200 ms par image", "Haute", "À confirmer sur une 2e vidéo"],
    ["2", "Mode « pixel parfait » : texte sans lissage, accrochage aux pixels entiers", "n° 18", "Haute", "À confirmer sur la 1re vraie vidéo pixel"],
    ["3", "Commande pour régler l'entrée et la sortie d'un calque", "n° 1", "Moyenne", "Contourné dans monter.py"],
    ["4", "Import de sous-titres .srt", "n° 2", "Moyenne", "Utile seulement avec une voix"],
    ["5", "Option --config-dir pour la ligne de commande", "n° 15", "Basse", "Contourné"],
    ["6", "Presets qui n'écrasent pas la valeur des propriétés", "n° 21", "Basse", "Contourné (rapides)"],
  ], [0.5, 3, 2.4, 1.2, 2.4]),
  ALERTE("Avant toute modification du code : **cargo xtask ci** au vert, **zéro plantage possible** (pas de unwrap ni de panic dans le code non test), **un test par correction**, un commit par tâche. Ce sont les règles du projet EffectCraft ; elles s'appliquent aussi au fork. Un plantage fait perdre du travail : il passe avant toute nouvelle fonction."),
);

// ================================================================ 10
C.push(
  H1("10. Les cinq logiciels de la suite ArtCraft"),
  P("Le dossier **~/videos/logiciel** contient cinq logiciels de la même famille (ArtCraft). Ils partagent la même philosophie : **chaque action est une commande**, utilisable depuis les menus, la ligne de commande, un canal de contrôle JSON ou un **serveur MCP** que Claude pilote directement. EffectCraft reste le cœur de l'usine ; les quatre autres interviennent chacun à une étape précise, là où ils sont les meilleurs."),
  table(["Logiciel", "Équivalent", "Version (20/10/2026)", "Maturité annoncée", "Rôle dans l'usine"], [
    ["**EffectCraft**", "After Effects", "0.13.0", "Jeune, avance vite", "**Cœur** : scènes pixel, caméra, animation des personnages, sous-titres, rendu des Shorts et des scènes"],
    ["**FilmCraft**", "Premiere Pro", "0.10.0", "Jeune, avance vite", "**Transcription de la voix → sous-titres**, montage des vidéos longues, mixage, mesure du volume, export par plateforme"],
    ["**SoundCraft**", "Pro Tools", "0.10.0", "Pré-alpha", "**Voix** (enregistrement, prises, nettoyage), **musique et jingle** avec ses synthés, bruitages, export normalisé"],
    ["**PhotoCraft**", "Photoshop", "0.11.1", "Alpha précoce", "**Décors en calques** (PSD → plans de parallaxe), **miniatures**, bannière, visuels de la boutique, traitements par lots"],
    ["**VectorCraft**", "Illustrator", "0.14.0", "Développement actif", "**Logo** ico-vid, titres de bannière, icônes vectorielles (formats non pixel), visuels imprimables"],
  ], [1.4, 1.3, 1.3, 1.4, 4.2]),
  GAP(),
  NOTE("**Au 21/10/2026, seul EffectCraft est compilé** (dans ~/dev/vid/effectcraft). Les quatre autres sont téléchargés mais pas encore compilés ni testés : leur rôle ci-dessous est **prévu d'après leur documentation**, et chaque rôle a un test de validation avant d'entrer dans la production (§ 10.4)."),
  H2("10.1 Qui intervient à quelle étape"),
  table(["Étape", "Logiciel", "Ce qu'il fait", "Fichier transmis"], [
    ["Personnages animés", "**Aseprite** (plan B : Pixelorama)", "Dessin image par image avec pelures d'oignon, une étiquette par action, export automatique planche + données. PhotoCraft a un crayon, le mode couleurs indexées et l'agrandissement au plus proche voisin, mais **pas encore de pelures d'oignon ni de timeline d'animation** : il ne remplace pas Aseprite pour animer", "planche .png → decouper_planche.py"],
    ["Décors", "**PhotoCraft**", "Un calque par plan (1-ciel … 5-premier), toile en 480×270 (ou plus large pour les travellings), palette indexée ico-pixel-32", "decor.psd → EffectCraft l'importe **comme une comp, calques séparés et à leur place**"],
    ["Logo, icônes", "**VectorCraft**", "Logo ico-vid, icônes de vulgarisation (formats non pixel), titres de bannière", ".svg → calques de forme dans EffectCraft ; .png à la taille exacte pour le pixel"],
    ["Voix", "**SoundCraft**", "Enregistrement avec plusieurs prises, choix des meilleures, égaliseur, de-esser, compresseur, porte de bruit ; export avec normalisation et mesure du volume (LUFS)", "voix.wav"],
    ["Sous-titres", "**FilmCraft**", "Transcription automatique (Whisper, en local, multilingue), mot par mot avec les temps ; suppression des « euh » et des longs silences ; export **.srt**", "voix.srt → monter.py (sous-titres calés au mot près)"],
    ["Musique, jingle, sons", "**SoundCraft**", "Synthé soustractif, synthé de batterie, sampler, piano roll MIDI : musique chiptune et jingle ico-vid **à toi** (licence propriétaire)", "musique.wav, jingle.wav, sons/*.wav"],
    ["Animation et rendu", "**EffectCraft**", "Scènes, caméra pixel, personnages, sous-titres, signature ; rendu des Shorts complets et des scènes des vidéos longues", ".mp4 (ou séquence PNG)"],
    ["Montage des vidéos longues", "**FilmCraft**", "Enchaîne les scènes rendues, la voix et la musique ; musique atténuée sous la voix ; mesure du volume aux normes EBU R128 ; marqueurs de chapitres ; export avec le préréglage « YouTube 1080p Full HD » ; .srt séparé pour YouTube", "video-longue.mp4 + .srt"],
    ["Miniatures, bannière, boutique", "**PhotoCraft**", "Retouche, texte avec styles de calque (contour, ombre), mosaïques d'aperçu pour la boutique ; traitements par lots (redimensionner, exporter)", ".png 1280×720, 2560×1440…"],
  ], [1.8, 1.6, 4.2, 2]),
  GAP(),
  ASTUCE("**Le gain le plus important** : la transcription de FilmCraft règle le **n° 2 du journal** (« les sous-titres sont le plus gros coût manuel ») **sans écrire une ligne de code dans EffectCraft**. La règle d'or est respectée : on utilise un logiciel existant avant de coder une fonction."),
  H2("10.2 Le circuit des fichiers"),
  ...CODE(`SHORTS (9:16) — tout dans EffectCraft
  Aseprite   ──planche.png──┐
  PhotoCraft ──decor.psd────┤
  SoundCraft ──sons, musique┼──► EffectCraft (monter.py) ──► short.mp4
  FilmCraft  ──voix.srt─────┘                                     │
                                     YouTube · TikTok · Instagram ◄──┘

VIDÉOS LONGUES (16:9) — scènes dans EffectCraft, assemblage dans FilmCraft
  SoundCraft ──voix.wav──► FilmCraft (transcription) ──voix.srt──┐
  EffectCraft ──scene-01.mp4 … scene-12.mp4 ─────────────────────┼──► FilmCraft (montage,
  SoundCraft ──musique.wav ──────────────────────────────────────┘     mixage, chapitres, export)
                                                    longue.mp4 + .srt ──► YouTube

À CÔTÉ
  PhotoCraft ──miniature.png, bannière, visuels boutique
  VectorCraft ──logo.svg ──► EffectCraft (signature), PhotoCraft (bannière)`),
  P("**Règle** : chaque logiciel fait ce qu'il fait le mieux, et on ne refait jamais dans l'un ce que l'autre a déjà produit. Les Shorts restent **100 % EffectCraft** (plus rapide, un seul fichier) ; FilmCraft n'intervient pour eux que pour la transcription."),
  H2("10.3 Claude aux commandes"),
  P("Chaque logiciel a une ligne de commande (traitements sans fenêtre) et un serveur MCP. Une fois un serveur branché, Claude peut ouvrir, modifier, vérifier et exporter dans ce logiciel comme il le fait déjà dans EffectCraft."),
  table(["Logiciel", "Serveur MCP sans fenêtre", "Avec la fenêtre ouverte (mode pont)", "Port réservé"], [
    ["EffectCraft", "Déjà branché (effectcraft)", "effectcraft --control 9877 (effectcraft-app)", "9877"],
    ["FilmCraft", "filmcraft-cli mcp --project p.fcproj", "filmcraft --control 9876, puis mcp --bridge", "9876"],
    ["SoundCraft", "soundcraft-cli mcp", "soundcraft --control 7801", "7801"],
    ["PhotoCraft", "photocraft-cli mcp, limité en lecture et écriture à ~/videos", "photocraft --control (port à choisir)", "9878"],
    ["VectorCraft", "vectorcraft-cli mcp", "vectorcraft --control 7979", "7979"],
  ], [1.6, 3.2, 3.2, 1.6]),
  GAP(),
  NOTE("On ne branche un serveur MCP **que quand le logiciel sert vraiment** : chaque serveur ajoute des dizaines d'outils à Claude, ce qui ralentit et alourdit chaque échange. PhotoCraft est branché avec un accès limité au dossier ~/videos (options automation-read-root et automation-write-root), par prudence."),
  H2("10.4 Installation et tests de validation"),
  P("Ordre recommandé (décision D8) : **un logiciel à la fois, au moment où il sert**. Commande type, lancée par Claude en arrière-plan :"),
  ...CODE(`cd ~/videos/logiciel/filmcraft
CARGO_TARGET_DIR=target cargo build --release -p filmcraft -p filmcraft-cli
# la transcription demande l'option « whisper » (voir docs/transcripts.md au moment de compiler)
claude mcp add filmcraft -- ~/videos/logiciel/filmcraft/target/release/filmcraft-cli mcp`),
  table(["Quand", "Logiciel", "Test de validation (critère de fin)"], [
    ["S1", "FilmCraft", "30 s de ta voix en français transcrites avec **moins de 10 % de mots à corriger** ; temps de transcription noté ; le .srt exporté est lu par monter.py et les sous-titres tombent au bon moment"],
    ["S1", "SoundCraft", "Voix test enregistrée ou importée, chaîne égaliseur + de-esser + compresseur réglée et enregistrée comme préréglage « voix ico-vid » ; export WAV avec volume mesuré (cible de départ : −16 LUFS pour la voix, à ajuster)"],
    ["S2", "PhotoCraft", "Décor test 480×270 en 5 calques, enregistré en PSD, importé dans EffectCraft : 5 calques aux bonnes positions, **verifier_pixels.py au vert** (aucun lissage introduit)"],
    ["S3", "SoundCraft", "Jingle ico-vid de 1 s et une boucle de musique de 30 s, exportés et rangés dans assets/ avec licence « propriétaire »"],
    ["S3", "VectorCraft", "Logo ico-vid en SVG importé dans EffectCraft (signature) et dans PhotoCraft (bannière)"],
    ["S2", "FilmCraft + regarder.py", "Claude « regarde » les deux vidéos de test (« Le cloud », 17 s, muette ; « GPS et Einstein », 62 s) : plans détectés = plans réels (± 1), **aucune voix inventée sur la vidéo muette**, et le rapport retrouve au moins les défauts déjà notés dans le journal pour ces vidéos (bouche qui ne suit pas la voix, n° 8) ; temps d'analyse noté"],
    ["S3–S4", "FilmCraft", "Vidéo longue test de 2 min : 3 scènes EffectCraft + voix + musique atténuée ; export « YouTube 1080p Full HD » + .srt ; lecture sans erreur"],
  ], [1, 1.6, 7]),
  GAP(),
  P("Un logiciel qui échoue à son test **n'entre pas dans la production** : on note la gêne dans le journal (avec le nom du logiciel), on utilise le plan B (§ 10.6) et on réessaie à sa prochaine version."),
  H2("10.5 Les deux copies d'EffectCraft"),
  P("Il existe maintenant deux copies du même EffectCraft (même version, commit 9db7f3b2) :"),
  B("**~/dev/vid/effectcraft** : la copie de **production**. Elle est compilée, monter.py et les serveurs MCP de Claude l'utilisent. On n'y modifie rien."),
  B("**~/videos/logiciel/effectcraft** : non compilée. Recommandation (D9) : elle devient **le fork** (branche perso, § 9.2) le jour où le journal exige une fonction ; d'ici là, on n'y touche pas. Si tu préfères, on la supprime pour éviter toute confusion."),
  H2("10.6 Règles communes et plan B"),
  B("**Un seul journal** « ce qui m'a gêné », avec une colonne **logiciel** : la règle des 2 vidéos vaut pour les cinq logiciels."),
  B("**Formats ouverts** entre logiciels (PSD, SVG, WAV, SRT, MP4, PNG) : aucun lien propriétaire, donc on peut remplacer un maillon sans casser la chaîne."),
  B("**Versions figées pendant une production** ; mise à jour entre deux vidéos, après avoir refait le test de validation."),
  B("**Fork** d'un logiciel seulement si le journal l'exige, avec ses règles : quality gates au vert, aucun plantage possible, un test par correction."),
  table(["Si ce logiciel bloque…", "Plan B immédiat", "Ce qu'on perd"], [
    ["FilmCraft (transcription)", "Sous-titres depuis le texte du script (monter.py, minutage estimé)", "La précision au mot près"],
    ["FilmCraft (montage long)", "Monter la vidéo longue directement dans EffectCraft (une comp par chapitre)", "Confort de montage, mesure du volume"],
    ["SoundCraft", "Enregistreur du téléphone ; musique BeepBox ; bruitages jsfxr", "Nettoyage de la voix, synthés"],
    ["Aseprite", "Pixelorama (gratuit, lit les mêmes palettes .gpl)", "Export automatique, confort de dessin"],
    ["PhotoCraft", "Décors et miniatures dans Pixelorama, ou miniatures dans la comp Miniature d'EffectCraft", "Calques PSD, styles de texte"],
    ["VectorCraft", "Logo en texte Lilita One directement dans EffectCraft", "Logo dessiné"],
    ["FilmCraft (regarder une vidéo)", "Nos vidéos : images rendues par EffectCraft (render_frame) aux temps voulus ; les autres : captures d'écran", "Détection des coupes, transcription datée"],
    ["agy / Gemini", "On s'en passe : Claude seul, avec la même règle de vérification", "Le regard extérieur"],
  ], [2.6, 4.6, 2.4]),

  H2("10.7 Claude regarde les vidéos"),
  P("Claude ne lit pas un fichier .mp4 comme un lecteur vidéo : il **voit des images** et **lit du texte**. Les logiciels de la suite font la traduction : ils transforment une vidéo en ce que Claude sait regarder. Avec ça, Claude peut vérifier une vidéo avant publication, analyser une référence, comparer deux versions ou chercher pourquoi les spectateurs décrochent à tel moment."),
  table(["Ce que Claude reçoit", "Qui le fabrique (commande vérifiée dans le code)", "Ce que Claude peut en dire"], [
    ["**Fiche technique**", "FilmCraft : file.mediaPropertiesFile (codec, taille, images/s, durée, audio présent ou non)", "Format 9:16 ou 16:9, durée dans la bible, **y a-t-il seulement du son**"],
    ["**Image d'un instant**", "FilmCraft : render_frame (seconds, max_side) sur n'importe quelle vidéo H.264, HEVC, VP9 ou AV1 ; EffectCraft : render_frame / render_preview sur nos comps, **avant même le rendu**", "Cadrage, textes lisibles, zones interdites 9:16, palette, signature présente"],
    ["**Une image par plan**", "FilmCraft : clip.sceneEditDetection (wait: true → liste des temps de coupe), puis une image au milieu de chaque plan", "Nombre et durée des plans, rythme (un changement toutes les 3–4 s ?), structure accroche → développement → chute"],
    ["**Planche contact**", "regarder.py : 16 images horodatées assemblées en une seule (comp grille dans EffectCraft, la même que celle de monter.py v2, journal n° 3)", "La vidéo entière d'un coup d'œil, pour un coût faible"],
    ["**Rafale**", "FilmCraft : file.exportFrame en boucle (une image par appel) sur 1–2 s", "Un saut, un coup, une secousse : le mouvement se lit-il ? image en double, saut d'image"],
    ["**Transcription datée**", "FilmCraft : transcript.generate (Whisper en local, language: fr), puis captions.export en .srt", "Ce qui est dit et quand ; sous-titres décalés ou fautifs ; accroche dite avant 2 s ?"],
    ["**Mesures du son**", "FilmCraft : clip.audioPeak (crête) ; **pas de mesure LUFS sans modifier le clip** : regarder.py calcule lui-même le volume (BS.1770) et les silences sur un export WAV", "Voix trop basse ou trop forte, saturation, silences longs, musique trop forte sous la voix"],
    ["**Score de mouvement** (idée de Gemini)", "regarder.py : part des pixels qui changent d'une image à l'autre", "Plans figés de plus de 3 s, sauf les pauses voulues (chute) déclarées dans episode.toml"],
  ], [2, 4.2, 3.4]),
  GAP(),
  P("**L'outil regarder.py** (à écrire en semaine 2, ~/videos/outils) fait tout ça en une commande, sans ouvrir de fenêtre, et range le résultat dans un dossier. Claude lit ensuite la planche, les images utiles et les mesures, et écrit un **rapport de visionnage** : chaque problème avec son temps, son image et la case de § 11.2 concernée."),
  ...CODE(`python3 -I ~/videos/outils/regarder.py short.mp4                    # fiche + plans + planche + transcription + son
python3 -I ~/videos/outils/regarder.py short.mp4 --rafale 12.5      # images consécutives à partir de 12,5 s
python3 -I ~/videos/outils/regarder.py v1.mp4 --comparer v2.mp4     # mêmes instants, côte à côte
python3 -I ~/videos/outils/regarder.py longue.mp4 --instants 41,95  # instants de décrochage (YouTube Studio)

Sortie : ~/videos/regards/<nom>/  fiche.json  planche.png  plans/plan-01.png…
                                  transcription.srt  son.json  mouvement.json  rapport.md (écrit par Claude)`),
  P("**Les cinq usages**"),
  table(["Usage", "Quand", "Ce que tu reçois"], [
    ["**Contrôle avant publication**", "Après chaque rendu (étape 7c, § 11)", "Rapport de visionnage : cases de § 11.2 vérifiées (accroche, rythme, zones interdites, sous-titres ≤ 2 lignes, son, signature), avec l'image et le temps de chaque alerte. Tu ne regardes que les alertes, puis la vidéo une fois en entier"],
    ["**Autopsie des décrochages**", "Bilan J+7 (§ 13.5)", "Pour chaque chute brusque de la courbe de rétention : la rafale des 3 s qui précèdent, la phrase dite à ce moment, une cause probable et une correction pour les prochains scripts (recettes Claude mises à jour)"],
    ["**Analyse de références**", "Lot « idées » du lundi", "Une fiche dans ~/videos/references/ : durée de l'accroche, nombre de plans, rythme, structure, ce qu'on peut reprendre (la **méthode**, jamais les images)"],
    ["**Comparaison de versions**", "Après une correction", "Ce qui a changé entre v1 et v2, aux mêmes instants"],
    ["**Commandes clients**", "Quand un client envoie un exemple", "Cahier des charges chiffré : plans, durées, tailles, assets déjà dans ~/videos/assets réutilisables"],
  ], [2.2, 2.2, 5.2]),
  GAP(),
  ALERTE("**Droits** : on n'analyse que des fichiers qu'on a le droit d'avoir : nos vidéos, celles sous licence libre, ou celles qu'un client nous envoie. **Télécharger la vidéo YouTube d'un autre créateur est interdit par les conditions d'utilisation de YouTube.** Pour une référence : on la regarde sur YouTube, on fait quelques captures d'écran et on note les temps ; Claude analyse les captures."),
  NOTE("**Ce que Claude ne fait pas** : il voit des **échantillons**, pas le mouvement continu ; entre deux images, il peut rater un défaut (image en trop, scintillement) ou mal juger le timing d'un gag. D'où les rafales sur les moments clés et verifier_pixels.py, qui contrôle **toutes** les images. Il **n'entend pas** : il lit une transcription et des mesures, pas l'ambiance d'une musique ni l'intelligibilité d'une voix sous un bruitage. Ton œil et tes oreilles restent la validation finale (étape 6)."),
  ASTUCE("**Coût** : chaque image prend de la place dans la mémoire de travail de Claude. Une planche de 16 images en une seule coûte bien moins que 16 images séparées : on demande d'abord la planche, puis seulement les images utiles, réduites (max_side 960, la valeur par défaut)."),

  H2("10.8 Deuxième avis : Gemini par agy"),
  P("La CLI **agy** (Antigravity) est installée (~/.local/bin/agy) et donne accès aux modèles Gemini (Gemini 4 Argon, Gemini 3.8 Flash). Claude peut la lancer lui-même, en lecture seule (mode plan), pour avoir **un regard extérieur** : un modèle qui n'a pas construit les scripts n'a pas le même biais. Premier essai le 21/10/2026 : Gemini a relu tout le plan 2.2 ; ses critiques sont devenues les décisions **D10 à D14** (§ 3) et deux idées pour regarder.py (score de mouvement, infos sous chaque vignette de la planche)."),
  ...CODE(`cd ~/videos && agy -p "Lis plans/briefing.md et donne ton avis…" \
    --model gemini-4-argon-high --mode plan --print-timeout 900s > avis-gemini.md`),
  P("**Le test vidéo du 21/10/2026** : on a demandé à Gemini de regarder « Le cloud » directement. Il voit bien les **images** (environ une par seconde) et a relevé de vrais défauts (bouche qui s'ouvre et se ferme sans suivre de voix, clignement fait en écrasant les yeux). Mais il a aussi **décrit une voix qui n'existe pas** : le fichier n'a aucune piste audio, et il a inventé la narration à partir des sous-titres. Et il a pris la pause voulue avant la chute pour un défaut."),
  ALERTE("**Règle de vérification** : une observation de Gemini (ou de Claude) sur une vidéo ne compte que si une mesure la confirme : fiche technique (y a-t-il du son ?), transcription, image extraite au temps cité, ou bible du format (la pause était-elle voulue ?). Sinon elle est notée « à vérifier », jamais corrigée telle quelle."),
  table(["Quand on consulte Gemini (règle des 3 portes)", "Ce qu'on lui donne", "Ce qu'on attend"], [
    ["**Porte script** : lundi, avant d'enregistrer la voix", "Les 5 idées de la semaine, le script de science", "Classement des idées ; erreurs scientifiques ; le gag tombe-t-il ?"],
    ["**Porte rendu** : vidéos longues seulement, avant publication", "Le .mp4 final, le rapport de visionnage de Claude, la miniature", "Ce que Claude a raté ; miniature face à 5 miniatures concurrentes réduites à 10 %"],
    ["**Porte bilan** : mois 3, 6 et 12", "Le tableau de bord (§ 13.5), le journal, ce plan", "Ce qu'il faut couper ou accélérer ; un avis contraire à celui de Claude"],
  ], [3.2, 3.2, 3.2]),
  GAP(),
  P("**En dehors de ces trois portes, on ne le consulte pas** : ni pour le code, ni pour le pilotage des logiciels, ni pour le montage. Un seul agent tient le volant technique ; deux avis sur chaque détail, c'est du bruit et du temps perdu. Gemini ne reçoit **jamais de mot de passe ni d'identifiants**, et tourne toujours en **lecture seule** : on ne lui donne pas l'option qui l'autorise à lancer des commandes sans demander."),
);

// ================================================================ 11
C.push(
  H1("11. Fabriquer une vidéo de A à Z"),
  P("La même chaîne pour toutes les vidéos. Les temps sont des estimations pour un Short pixel de 20–30 s (entre parenthèses : une vidéo longue de 6–8 min), une fois l'usine 2.0 prête."),
  table(["#", "Étape", "Qui", "Comment", "Temps", "Sortie"], [
    ["1", "Idée et angle", "Toi (Claude propose 5 idées)", "« Claude, 5 idées de gag pixel sur le thème X »", "5 min (15)", "Pitch d'une ligne"],
    ["2", "Script et découpage en plans", "Claude, validé par toi", "Recette du format + bible ; tu corriges en une passe", "10 min (45)", "episode.toml v2"],
    ["3", "Assets manquants", "Toi ou Claude", "Liste produite par monter.py --verifier", "0–60 min", "Assets rangés + manifeste"],
    ["4", "Voix (si format avec voix)", "Toi + SoundCraft", "Micro-cravate ; enregistrement, choix des prises et nettoyage dans **SoundCraft**, export WAV normalisé", "— (30)", "voix.wav"],
    ["4b", "Sous-titres depuis la voix", "FilmCraft + toi (relecture)", "**FilmCraft** transcrit (Whisper, en local) ; tu corriges les mots faux ; export .srt", "— (10)", "voix.srt"],
    ["5", "Montage automatique", "Claude", "monter.py v2", "2 min", "Projet + 3 aperçus + planche contact"],
    ["6", "Validation", "Toi", "Regarder aperçus et planche ; corrections dites en une phrase", "5 min (20)", "« OK » ou corrections"],
    ["7", "Rendu", "Machine", "monter.py --rendu (la nuit pour les longues)", "2–5 min (1–3 h)", ".mp4 + contrôle pixels"],
    ["7b", "Assemblage (vidéos longues)", "Claude + FilmCraft", "**FilmCraft** : chapitres, voix, musique atténuée sous la voix, mesure du volume, export « YouTube » + .srt séparé", "— (20)", ".mp4 final + .srt"],
    ["7c", "Visionnage de contrôle", "Claude (FilmCraft)", "**regarder.py** sur le .mp4 rendu → rapport de visionnage ; seules les alertes te sont montrées (§ 10.7)", "2 min (10)", "rapport.md"],
    ["8", "Miniature, titre, description", "Claude propose 3 versions, toi tu choisis", "Comp Miniature d'EffectCraft (Shorts) ou **PhotoCraft** (longues) + modèles de texte (annexe B)", "10 min (20)", "PNG + texte"],
    ["9", "Publication programmée", "Toi", "YouTube Studio, TikTok, Instagram (§ 13.2)", "10 min (15)", "Vidéo programmée"],
    ["10", "Mesure (J+2 et J+7)", "Claude", "Export des stats → tableau de bord (§ 13.5) ; à J+7, Claude regarde les instants où les spectateurs décrochent (regarder.py --instants)", "5 min (15)", "Une ligne dans le tableau"],
  ], [0.4, 1.9, 1.8, 2.9, 1.2, 1.6]),
  GAP(),
  NOTE("**Total pour toi** : environ **45 min par Short** et **3 h par vidéo longue**, hors dessin de nouveaux personnages. C'est ce qui rend le rythme A (≈ 6 h/semaine) tenable."),
  H2("11.1 Travailler par lots (la règle qui fait gagner le plus de temps)"),
  P("Changer de tâche coûte cher. On regroupe donc les étapes du même type pour plusieurs vidéos d'un coup :"),
  table(["Jour (exemple)", "Lot", "Durée"], [
    ["Lundi", "Idées + scripts de toutes les vidéos de la semaine (ou des 2 semaines)", "1 h"],
    ["Mardi", "Dessin des assets manquants ; voix de la vidéo longue", "1 h 30"],
    ["Mercredi", "Validation des aperçus, corrections ; rendus lancés le soir", "1 h"],
    ["Jeudi", "Miniatures, titres, descriptions ; programmation de toutes les publications", "1 h"],
    ["Dimanche", "Bilan : tableau de bord, journal « ce qui m'a gêné », 3 décisions pour la semaine suivante", "30 min"],
  ], [2, 6, 1.6]),
  GAP(),
  H2("11.2 Définition de « vidéo terminée »"),
  P("Une vidéo n'est publiée que si **toutes** les cases sont cochées :"),
  ...[
    "Accroche avant 2 s, une seule idée, fin qui boucle ou renvoie à une autre vidéo.",
    "Un mouvement de caméra (ou un changement de plan) au moins toutes les 3–4 s.",
    "Rien dans les zones interdites du guide 9:16 ; sous-titres ≤ 2 lignes.",
    "verifier_pixels.py au vert ; palette respectée.",
    "Son : volume de la voix constant, musique au moins 15 dB sous la voix, pas de saturation.",
    "Tous les assets dans le manifeste ; crédits CC-BY copiés dans la description.",
    "Miniature lisible à 10 % de sa taille ; titre ≤ 60 caractères.",
    "Signature ico-vid à la fin.",
    "Rapport de visionnage de Claude sans alerte (ou alertes acceptées par toi).",
    "Une ligne ajoutée au journal si quelque chose a gêné.",
  ].map((t) => B("☐ " + t)),
);

// ================================================================ 11
C.push(
  H1("12. Stratégie de contenu"),
  H2("12.1 Positionnement"),
  P("**« ico-vid : le monde expliqué et raconté en pixel art. »** Une identité visuelle unique (pixel cosy, mouvements de caméra soignés) appliquée à des sujets qui intéressent beaucoup de monde. Le pixel art sert de signature : on reconnaît la chaîne en une image."),
  table(["Série", "Format", "Rythme A / B", "Rôle"], [
    ["**Gags pixel** (humour, jeu vidéo rétro, sans voix)", "Shorts 15–40 s en 9:16 ; compilation de 1 min+ pour TikTok", "3 / 5 par semaine", "Découverte, abonnés, vitrine pour les commandes"],
    ["**La science en pixel** (vulgarisation, ta voix)", "Long 6–10 min en 16:9 + 3 Shorts extraits", "1 toutes les 2 sem. / 1 par sem.", "Heures de visionnage, crédibilité"],
    ["**Aventure de Tim** (fantasy pixel, à partir du mois 2)", "Épisodes de 2–4 min + bande-annonce Short", "1 par mois / 2 par mois", "Fidélité : une série qu'on suit"],
    ["**Ambiances pixel** (à partir du mois 2)", "Long 1–3 h en 16:9, scène animée + musique libre", "1 par mois", "Heures de visionnage, produit vendu (fond animé)"],
  ], [3, 2.8, 1.8, 2]),
  GAP(),
  H2("12.2 Pourquoi les ambiances comptent autant"),
  P("Le seuil 2027 de YouTube est de **8 000 heures** en 12 mois. Calcul simple :"),
  table(["Type de vidéo", "Temps vu moyen par vue (hypothèse)", "Vues nécessaires pour 8 000 h"], [
    ["Vulgarisation de 8 min (40 % regardé)", "≈ 3,2 min", "≈ 150 000 vues"],
    ["Épisode de Tim de 3 min (50 %)", "≈ 1,5 min", "≈ 320 000 vues"],
    ["Ambiance de 2 h (on la laisse tourner)", "≈ 15–25 min", "≈ 20 000 à 32 000 vues"],
    ["Shorts", "Ne comptent pas dans les heures", "—"],
  ], [3.6, 3, 3]),
  GAP(),
  P("Les ambiances rapportent donc des heures **5 à 8 fois plus vite par vue**. Ce sont aussi elles qui deviennent des **fonds animés vendus** sur la boutique (même fichier, en boucle propre)."),
  ALERTE("**Contenu « non authentique » de YouTube.** YouTube ne monétise pas les vidéos **génériques, répétitives ou produites en série sur un même gabarit** (règle renommée en juillet 2025, précisée en juillet 2026). Une usine produit justement en série : chaque vidéo doit avoir **sa propre idée, son propre script, ses propres plans**. Pour les ambiances : des scènes **réellement différentes** (pas la même boucle recolorée), une vraie composition, des événements qui arrivent (un oiseau passe, la pluie commence, la nuit tombe), une musique choisie. Les modèles accélèrent le travail ; ils ne doivent pas se voir à l'écran."),
  H2("12.3 Les 10 premières idées (à valider)"),
  table(["#", "Série", "Idée", "Format"], [
    ["1", "Gags pixel", "Le héros meurt juste avant le point de sauvegarde (et le jeu lui rappelle)", "Short 20 s"],
    ["2", "Gags pixel", "Le PNJ qui répète la même phrase… et finit par craquer", "Short 25 s"],
    ["3", "Gags pixel", "La pièce impossible à attraper (elle esquive)", "Short 15 s"],
    ["4", "Gags pixel", "Le coffre au trésor contient… un autre coffre", "Short 20 s"],
    ["5", "Gags pixel", "Le boss final est en pause café", "Short 30 s"],
    ["6", "Science en pixel", "Pourquoi le ciel est bleu (et le coucher de soleil rouge)", "Long 7 min + 3 Shorts"],
    ["7", "Science en pixel", "Le GPS et Einstein (refaire vulga-01 en pixel, version longue)", "Long 8 min + 3 Shorts"],
    ["8", "Science en pixel", "Comment un ordinateur compte avec seulement 0 et 1", "Long 8 min + 3 Shorts"],
    ["9", "Science en pixel", "Pourquoi la Lune nous montre toujours la même face", "Long 6 min + 3 Shorts"],
    ["10", "Ambiances pixel", "Village au bord de la rivière, la nuit tombe, lucioles (1 h)", "Long 1 h"],
  ], [0.5, 2, 5.2, 1.9]),
  GAP(),
  P("Chaque sujet de science est **vérifié** avant le script (2 sources sérieuses minimum, citées en description), comme pour vulga-01."),
  H2("12.4 Structure d'une vidéo longue (8 min)"),
  table(["Moment", "Contenu", "Pourquoi"], [
    ["0:00–0:15", "Accroche : la question + l'image la plus forte de la vidéo", "C'est là que la majorité des spectateurs décident de rester"],
    ["0:15–0:40", "Promesse : ce qu'on va comprendre, en une phrase ; titre animé", "Le spectateur sait pourquoi rester"],
    ["0:40–6:30", "3 chapitres, chacun avec une relance (« mais il y a un problème… ») toutes les 60–90 s", "Éviter les décrochages ; chapitres visibles dans la barre YouTube"],
    ["6:30–7:30", "Réponse finale + récap en une phrase", "Satisfaction, partage"],
    ["7:30–8:00", "Écran de fin (20 s) : vidéo suivante + abonnement ; signature", "Enchaîner sur une autre vidéo = plus d'heures"],
  ], [1.6, 4.8, 3.2]),
);

// ================================================================ 12
C.push(
  H1("13. Marketing YouTube et autres plateformes"),
  H2("13.1 Les plateformes et leurs seuils (vérifiés le 21/10/2026)"),
  table(["Plateforme", "Ce qu'on publie", "Monétisation", "Seuil d'entrée"], [
    ["YouTube (long)", "Science, Tim, ambiances", "Publicités (part des revenus)", "Jusqu'au 31/01/2027 : 1 000 abonnés + 4 000 h sur 12 mois\n**À partir du 01/02/2027 : 1 000 abonnés + 8 000 h**, ou 20 M de vues Shorts sur 90 jours"],
    ["YouTube Shorts", "Gags, extraits", "Part du fonds Shorts", "En plus du programme : **10 M de vues Shorts sur 90 jours** pour toucher le fonds (à partir du 01/02/2027)"],
    ["YouTube, niveau « soutiens »", "—", "Super Thanks, adhésions, Shopping (pas la publicité)", "500 abonnés + 3 vidéos en 90 jours + 3 000 h sur 12 mois ou 3 M de vues Shorts sur 90 jours ; inchangé en 2027 ; disponibilité en France à vérifier dans Studio ▸ Monétiser"],
    ["TikTok", "Gags et extraits de **plus d'une minute**", "Creator Rewards", "10 000 abonnés + 100 000 vues sur 30 jours, 18 ans, compte personnel"],
    ["Instagram Reels", "Les mêmes Shorts", "Indirecte (audience, partenariats)", "—"],
    ["itch.io", "Packs pixel, fonds animés", "Ventes ; part de la plateforme réglable (10 % par défaut)", "Aucun"],
    ["Ko-fi", "Soutiens, petits produits, commandes", "Dons et ventes", "Aucun (frais selon formule : vérifier la page tarifs)"],
    ["Fiverr / Malt", "Animations pixel sur commande", "Prestations (commission de la plateforme)", "Aucun ; statut à déclarer"],
  ], [1.8, 2, 2.4, 3.4]),
  GAP(),
  NOTE("Les chaînes déjà dans le programme partenaire **avant le 1er février 2027** gardent leur statut. Atteindre 4 000 h d'ici là (en 3 mois, en partant de zéro) est très improbable : le plan vise donc directement **8 000 h**, et ne compte pas sur la publicité YouTube avant la fin de la première année."),
  H2("13.2 Lancement (semaine 4) : la liste"),
  ...LIST("m122", [
    "**Identité** : nom ico-vid et pseudo @yehz réservés sur YouTube, TikTok, Instagram, itch.io, Ko-fi (le même partout).",
    "**Avatar** : la mascotte (Tim) en gros plan pixel, lisible en 48×48. **Bannière** YouTube 2560×1440 avec la zone sûre centrale (1546×423) respectée.",
    "**Page de chaîne** : description en 2 phrases (ce qu'on y trouve + rythme), lien boutique, bande-annonce de 30 s pour les non-abonnés.",
    "**Playlists** dès le premier jour : « Gags pixel », « La science en pixel ». Une vidéo vue dans une playlist enchaîne sur la suivante.",
    "**Stock d'avance** : 3 vidéos prêtes (2 Shorts + 1 longue) avant d'ouvrir. On garde ensuite toujours une semaine d'avance.",
    "**Programmation** : mêmes jours, même heure (début de soirée en France, à ajuster avec les statistiques d'audience).",
  ]),
  H2("13.3 Miniatures et titres"),
  B("**Miniature 1280×720** : un personnage agrandi ×8 (net), une émotion lisible, **3 mots maximum**, fort contraste, rien d'important dans le coin bas-droit (durée de la vidéo)."),
  B("**Test** : la miniature doit se comprendre réduite à **10 % de sa taille** (comme sur un téléphone)."),
  B("**Titre** : ≤ 60 caractères, promet une réponse ou une situation (« Pourquoi le ciel est bleu ? (en pixel art) »), jamais trompeur."),
  B("**A/B** : 2 à 3 miniatures testées avec « Tester et comparer » de YouTube Studio quand la fonction est disponible sur la chaîne."),
  H2("13.4 Référencement et recyclage"),
  B("**Description** : 2 premières lignes = le résumé (c'est ce qui s'affiche), puis chapitres, sources, crédits, liens (modèle en annexe B)."),
  B("**Sous-titres intégrés** (beaucoup regardent sans le son) + fichier de sous-titres envoyé à YouTube pour les vidéos avec voix."),
  B("**3 à 5 tags précis** ; les hashtags dans la description (#pixelart #science) plutôt que dans le titre."),
  B("**Recyclage** : chaque Short sur YouTube, TikTok et Instagram, texte adapté à chaque plateforme, **sans filigrane d'une autre plateforme** (exporter depuis EffectCraft, jamais retélécharger)."),
  B("**Communauté** : répondre aux commentaires dans les premières heures, épingler une question, sondages dans l'onglet Posts."),
  B("**Ailleurs** : partager les plus belles scènes sur les communautés pixel art (Reddit r/PixelArt, Bluesky) **en respectant leurs règles d'autopromotion** : montrer le travail, pas seulement le lien."),
  H2("13.5 Ce qu'on mesure chaque semaine (tableau de bord)"),
  table(["Indicateur", "Pourquoi", "Objectif de départ", "Si on est en dessous"], [
    ["Rétention à 3 s (Shorts)", "L'accroche marche-t-elle ?", "> 70 %", "Image d'ouverture plus forte, texte plus tôt"],
    ["Durée moyenne vue (long)", "Le contenu tient-il ?", "> 40 %", "Regarder la courbe : couper là où ça décroche"],
    ["Taux de clic des miniatures", "Titre et miniature donnent-ils envie ?", "> 4 %", "Tester une autre miniature"],
    ["Abonnés par 1 000 vues", "Envie de revenir ?", "> 3", "Fin de vidéo plus claire, série plus identifiable"],
    ["Heures de visionnage cumulées", "Seuil YouTube 2027", "8 000 h en 12 mois", "Plus d'ambiances et de longues"],
    ["Ventes boutique", "Revenu sans seuil", "1 pack au mois 3", "Meilleure page, GIF d'aperçu, prix"],
    ["Demandes de commande", "Revenu sans seuil", "1 par mois à partir du mois 3", "Portfolio itch.io, lien en bio"],
  ], [2.4, 2.4, 2, 2.8]),
);

// ================================================================ 13
C.push(
  H1("14. Objectif 500 $ par mois : les chiffres refaits"),
  P("Les montants par 1 000 vues (RPM) varient énormément selon le pays, le sujet et l'audience. Les chiffres ci-dessous sont des **hypothèses de travail** tirées de guides de 2026, pas des promesses. On les remplace par les vrais chiffres de la chaîne dès qu'ils existent (bilan du mois 3)."),
  H2("14.1 Pourquoi les Shorts seuls ne suffiront pas"),
  table(["Scénario", "Hypothèse", "Volume nécessaire pour 500 $/mois", "Réaliste en année 1 ?"], [
    ["A. Shorts seuls", "RPM 0,03 à 0,10 $ ; et 10 M de vues / 90 j pour toucher le fonds", "5 à 17 millions de vues par mois", "Non"],
    ["B. Vidéos longues seules", "RPM 1 à 4 $ (francophone, à confirmer) ; et 8 000 h pour y avoir droit", "125 000 à 500 000 vues par mois", "Non : le seuil de 8 000 h arrive au mieux vers le mois 12"],
    ["C. Revenus diversifiés (retenu)", "Boutique + commandes + TikTok + soutiens, puis YouTube", "Voir 13.2", "Oui, vers le mois 12, si le rythme est tenu"],
  ], [2.2, 3.2, 2.4, 1.8]),
  GAP(),
  H2("14.2 Le mélange visé au mois 12"),
  table(["Source", "Hypothèse", "Par mois"], [
    ["Boutique (packs pixel, fonds animés pour streamers)", "20 ventes × 9 $ (après la part de la plateforme)", "180 $"],
    ["Commandes (emotes animées, overlays, petites animations)", "2 commandes × 80 $", "160 $"],
    ["TikTok Creator Rewards", "200 000 vues qualifiées × 0,6 $ / 1 000 (très incertain ; exige 10 000 abonnés)", "120 $"],
    ["Soutiens (Ko-fi, Super Thanks, adhésions)", "12 soutiens × 4 $", "50 $"],
    ["**Sous-total sans publicité YouTube**", "", "**≈ 510 $**"],
    ["Publicité YouTube (si 8 000 h atteintes)", "50 000 vues longues × 2 $ / 1 000", "+ 100 $"],
  ], [3.6, 4.4, 1.6]),
  GAP(),
  ASTUCE("**Pourquoi ce mélange est le bon** : la boutique et les commandes ne dépendent d'**aucun seuil** et peuvent rapporter **dès le mois 2 ou 3**. Elles utilisent les mêmes personnages et décors que les vidéos (« un travail, trois usages »). Et les vidéos font la publicité de la boutique gratuitement."),
  H2("14.3 Les produits de la boutique"),
  table(["Produit", "Contenu", "Prix indicatif", "Fabriqué avec"], [
    ["Pack personnage", "1 personnage, 5–8 actions, planche + images séparées + GIF", "3 à 6 $", "Les héros et figurants **dessinés par toi**"],
    ["Pack décor", "Tuiles + 5 plans de parallaxe d'une scène", "5 à 10 $", "Les décors des vidéos"],
    ["Fond animé pour stream", "Boucle de 30–60 s en 1080p et 4K (MP4 + WebM)", "5 à 12 $", "Les ambiances"],
    ["Écrans « Je reviens » / « Début du live »", "3 écrans animés assortis", "8 à 15 $", "Scènes + texte"],
    ["Bundle saison", "Tout ce qui a été fait en 3 mois", "15 à 25 $", "Tout"],
  ], [2.4, 3.6, 1.6, 2]),
  GAP(),
  P("Les prix sont à caler sur un **relevé de 20 produits comparables** sur itch.io au moment du lancement (Claude le prépare). Une page de boutique contient : GIF animé en tête, liste exacte du contenu, licence claire (« usage commercial autorisé, revente des fichiers interdite »)."),
  ALERTE("On ne vend **que ce qu'on a dessiné soi-même** (colonne « vendable » du manifeste). Revendre des assets CC0 de Kenney ou d'un autre pack, même modifiés légèrement, est mal vu, souvent refusé par les boutiques, et nuit à la réputation de la chaîne."),
  H2("14.4 Jalons"),
  table(["Quand", "Jalon", "Revenu visé (brut)"], [
    ["Mois 1", "Usine 2.0 prête, chaîne lancée, 12 à 20 vidéos publiées", "0 $"],
    ["Mois 2", "Premier pack en vente ; page de commandes ouverte", "0–20 $"],
    ["Mois 3", "300 abonnés, 1re commande, 3 packs ; **bilan n° 1**", "20–60 $"],
    ["Mois 6", "1 000 abonnés YouTube, 2 500 h, 5 000 abonnés TikTok ; **bilan n° 2 (pivot possible)**", "120–200 $"],
    ["Mois 9", "Niveau « soutiens » YouTube, TikTok 10 000 abonnés, 8 packs", "250–380 $"],
    ["Mois 12", "Rythme stable, revenus diversifiés ; **bilan n° 3**", "≈ 500 $"],
  ], [1.4, 6, 2.2]),
  GAP(),
  H2("14.5 Frais, cotisations et déclaration"),
  P("500 $ bruts ne sont pas 500 $ en poche. Ordre de grandeur en France (micro-entreprise, taux 2026 relevés sur des sites spécialisés, **à confirmer sur urssaf.fr avant de s'inscrire**) :"),
  table(["Poste", "Ordre de grandeur", "Remarque"], [
    ["Part des plateformes", "itch.io 10 % par défaut (réglable) ; Gumroad ≈ 10 % + 0,50 $ ; Fiverr ≈ 20 %", "Préférer une plateforme qui gère la TVA européenne à ta place"],
    ["Cotisations sociales", "≈ 21 % (prestations de services BIC) ; ≈ 12 % (vente de marchandises) ; ≈ 23–26 % (BNC)", "La vente de fichiers numériques et les commandes sont en général des prestations de services : à faire confirmer"],
    ["Impôt", "Selon ta situation (versement libératoire possible sous conditions)", "—"],
    ["Net estimé", "≈ 70 à 75 % du brut", "500 $ bruts ≈ 350 à 380 $ nets"],
  ], [2, 4.2, 3.4]),
  GAP(),
  ALERTE("**Avant le premier paiement** : s'informer sur le statut (micro-entreprise ou autre), déclarer les revenus, et vérifier l'âge minimum de chaque programme. Ce document n'est pas un conseil fiscal."),
);

// ================================================================ 14
C.push(
  H1("15. Feuille de route détaillée"),
  H2("15.1 Semaines 1 à 4 (construction et lancement)"),
  table(["Semaine", "Livrable", "Qui", "Critère de fin"], [
    ["S1", "Compiler **FilmCraft** et **SoundCraft** ; test de transcription d'une voix française de 30 s ; chaîne voix dans SoundCraft", "Claude (+ toi pour la voix test)", "Moins de 10 % de mots à corriger ; .srt lu par monter.py ; bounce WAV avec son volume (LUFS) affiché"],
    ["S1", "Dépôt git ~/videos (tag v1.0.0), assets/ + manifeste, references/ séparées, a-trier/", "Claude", "git log propre ; verifier_licences.py au vert"],
    ["S1", "Bible v2 : DA pixel (§ 4), palette ico-pixel-32 (.gpl, .hex), interdits", "Claude, validé par toi", "Planche bible v2 rendue et validée"],
    ["S1", "Gabarit de planche + fiche tim.toml ; prototype de Tim en formes simples", "Claude", "Planche ouverte dans Aseprite sans erreur"],
    ["S1–S2", "decouper_planche.py + précomp personnage + marqueurs d'action", "Claude", "Marche de 4 images bouclée à 12 i/s, pieds qui ne glissent pas"],
    ["S2", "Tim dessiné (5 actions)", "Toi", "decouper_planche.py au vert, GIF de contrôle validé"],
    ["S2", "Modèles « Scène pixel 16:9 / 9:16 » + verifier_pixels.py", "Claude", "Rendu de test : 0 bloc fautif, 0 couleur hors palette"],
    ["S2", "Mesure : coût d'un curseur sur un calque nul", "Claude", "Chiffre noté dans le journal"],
    ["S2–S3", "camera.py + 8 mouvements (§ 6.5)", "Claude", "Scène test de 15 s, 3 mouvements, contrôle au vert"],
    ["S3", "monter.py v2 (épisodes plan par plan) + planche contact", "Claude", "L'exemple du § 8.1 monté depuis le fichier texte"],
    ["S2", "**regarder.py** (fiche, plans, planche, transcription, son, mouvement) ; test sur « Le cloud » et « GPS et Einstein »", "Claude", "Test de § 10.4 réussi ; aucune voix inventée sur la vidéo muette"],
    ["S3", "Comp Miniature + modèles de titre et description", "Claude", "Miniature lisible à 10 %"],
    ["S2", "Compiler **PhotoCraft** ; décor test en PSD (5 calques) importé dans EffectCraft", "Claude", "Comp à 5 calques, positions exactes, verifier_pixels.py au vert"],
    ["S3", "Sons : 10 bruitages (jsfxr, SoundCraft) + **jingle ico-vid composé dans SoundCraft**", "Toi + Claude", "Fichiers dans assets/sons avec licence « propriétaire »"],
    ["S3", "Compiler **VectorCraft** ; logo ico-vid en SVG ; montage d'une vidéo longue test dans FilmCraft", "Claude, validé par toi", "Logo importé dans EffectCraft ; export FilmCraft « YouTube 1080p » lu sans erreur"],
    ["S4", "3 vidéos d'avance, chaînes ouvertes partout, playlists, bannière", "Toi + Claude", "Usine **v2.0.0** taguée ; 1re semaine publiée à l'heure"],
  ], [0.9, 4.4, 1.6, 2.7]),
  GAP(),
  H2("15.2 Mois 2 à 12 (production, boutique, bilans)"),
  table(["Période", "Production", "Boutique et commandes", "Usine", "Bilan"], [
    ["Mois 2", "Rythme A ; 1re ambiance ; 1er épisode de Tim", "1er pack itch.io (S6) ; page Ko-fi commandes", "v2.1.0 : corrections du journal", "—"],
    ["Mois 3", "Rythme A ou B selon ton temps", "3 packs ; 1re commande", "Tableau de bord automatique", "**Bilan 1** : vrais RPM, séries qui marchent"],
    ["Mois 4–5", "Rythme B si possible ; TikTok en versions > 1 min", "Écrans de stream ; bundle de saison", "v2.2.0 : publication assistée si utile", "—"],
    ["Mois 6", "Garder ce qui marche, arrêter ce qui ne marche pas", "5 packs", "Fork (v3.0.0) si le journal l'exige", "**Bilan 2** : continuer, ajuster ou pivoter"],
    ["Mois 7–9", "Ambiances mensuelles ; version anglaise des gags (test)", "8 packs ; commandes régulières", "—", "—"],
    ["Mois 10–12", "Rythme stable", "Bundle annuel", "—", "**Bilan 3** : plan v3 pour l'année 2"],
  ], [1.2, 2.6, 2.4, 1.8, 1.6]),
  GAP(),
  H2("15.3 Règles de décision aux bilans"),
  table(["Bilan", "Si…", "Alors…"], [
    ["Mois 3", "Une série a une rétention ou un taux de clic 2 fois meilleur que les autres", "Elle passe en priorité ; la plus faible est mise en pause"],
    ["Mois 3", "Aucune vente de pack", "Revoir pages, prix et GIF ; tester une autre boutique ; demander l'avis de 5 acheteurs potentiels"],
    ["Mois 6", "Moins de 300 abonnés YouTube", "Changer de niche ou de format (pas de rythme) ; garder le moteur et les assets"],
    ["Mois 6", "La boutique et les commandes rapportent plus que prévu", "Leur donner plus de temps, même au détriment du nombre de Shorts"],
    ["Toujours", "Le rythme t'épuise", "Repasser en rythme A sans culpabiliser : 12 mois réguliers valent mieux que 3 mois intenses"],
  ], [1.4, 4, 4.2]),
);

// ================================================================ 15
C.push(
  H1("16. Architecture et organisation des fichiers"),
  H2("16.1 Qui fait quoi"),
  P("Claude prépare et exécute ; toi tu décides et tu valides : idée, script, aperçus, publication. **Claude ne publie rien sans ton accord.**"),
  table(["Dossier", "Contenu", "Versionné (git) ?"], [
    ["~/videos/bible.md, modeles/, presets/, outils/, recettes/", "Les règles et les outils de l'usine", "Oui"],
    ["~/videos/assets/", "Assets + manifest.toml", "Oui, sauf fichiers > 5 Mo (liste dans .gitignore)"],
    ["~/videos/references/, a-trier/", "Inspiration, téléchargements à ranger", "Non"],
    ["~/videos/<format>-NN-mot/", "episode.toml, projet, aperçus, voix", "Oui, sauf .mp4 et .wav lourds"],
    ["~/videos/boutique/", "Produits finis (zip), pages de vente", "Les sources oui, les zip non"],
    ["~/videos/stats/", "Tableau de bord, exports", "Oui"],
    ["~/videos/logiciel/", "Sources des 5 logiciels (dépôts git à part)", "Non (chacun a son propre dépôt ; versions notées dans le CHANGELOG)"],
    ["Rendus .mp4", "Vidéos finales", "Non : copie Bureau + sauvegarde externe"],
  ], [3.6, 3.6, 2.4]),
  GAP(),
  H2("16.2 Les outils (état visé en v2.0.0)"),
  table(["Outil", "Rôle", "Statut"], [
    ["monter.py", "Monte un épisode (v1 : modèles ; v2 : plan par plan)", "v1 fait, v2 à faire"],
    ["rapides.py", "Mouvements gratuits au rendu", "Fait ; + mouvements caméra"],
    ["camera.py", "Moteur caméra pixel", "À faire"],
    ["decouper_planche.py", "Planche → images + précomp personnage", "À faire"],
    ["verifier_pixels.py", "Contrôle blocs entiers + palette", "À faire"],
    ["verifier_licences.py", "Contrôle du manifeste", "À faire"],
    ["regarder.py", "Rend une vidéo lisible par Claude : fiche, une image par plan, planche, rafales, transcription, son, score de mouvement", "À faire (S2)"],
    ["stats.py", "Tableau de bord hebdomadaire à partir des exports YouTube Studio / TikTok", "Mois 2"],
  ], [2.6, 5, 2]),
);

// ================================================================ 16
C.push(
  H1("17. Matériel et temps de rendu"),
  P("La machine actuelle (Intel UHD 620, 16 Go, WSL) fait tourner l'usine. Mais **le rendu se fait sur le processeur**, car WSL n'expose pas la carte graphique (llvmpipe). Les scènes pixel ont un gros avantage : elles se calculent en 480×270, soit **16 fois moins de pixels** qu'en 1080p, puis s'agrandissent presque gratuitement."),
  table(["Vidéo", "Images", "Temps par image (estimé)", "Rendu total (estimé)"], [
    ["Short pixel 30 s", "720", "0,1–0,25 s", "1 à 3 min"],
    ["Long pixel 8 min (1080p)", "11 520", "0,1–0,3 s", "20 min à 1 h"],
    ["Long pixel 8 min (4K)", "11 520", "0,3–0,6 s", "1 à 2 h"],
    ["Ambiance 1 h", "86 400", "0,1–0,2 s", "2 h 30 à 5 h (ou boucle de 2 min répétée à l'export : beaucoup moins)"],
  ], [2.6, 1.4, 2.6, 3]),
  GAP(),
  P("Ces temps sont à **mesurer en semaine 2** et à reporter ici (v2.1.x). Parades si c'est trop lent :"),
  B("**Rendus la nuit** avec le dossier surveillé d'EffectCraft (on dépose les projets, il rend tout)."),
  B("**Aperçus en demi-résolution** et planches contact au lieu de rendus complets."),
  B("**Version Windows native** d'EffectCraft : accès direct à la carte graphique (à tester, journal n° 10b)."),
  B("Un PC plus puissant n'est utile **qu'une fois les revenus là** (jamais avant le bilan du mois 6)."),
  P("**Compiler les 4 autres logiciels** : chacun demande une compilation Rust la première fois (plusieurs dizaines de minutes et plusieurs Go par logiciel sur cette machine, à mesurer). Il reste 846 Go libres : la place n'est pas un problème. On compile **un logiciel à la fois**, en arrière-plan, avec un dossier de compilation séparé, pendant que tu travailles sur autre chose."),
  P("**Transcription** : Whisper tourne sur le processeur. Le modèle « base » (choix par défaut) est un bon compromis ; « small » est plus juste mais plus lent. Le temps pour une minute de voix est à mesurer en semaine 1."),
);

// ================================================================ 17
C.push(
  H1("18. Limites (à lire avant de commencer)"),
  table(["Limite", "Ce que ça veut dire", "Parade"], [
    ["Seuils YouTube 2027", "8 000 h pour la publicité, 10 M de vues Shorts / 90 j pour le fonds Shorts : pas de revenu publicitaire réaliste en année 1", "Revenus sans seuil d'abord (boutique, commandes) ; ambiances pour les heures"],
    ["Matériel", "Rendu sur le processeur : une vidéo longue peut demander une heure ou plus", "Scènes basse résolution, rendus la nuit, test Windows natif"],
    ["Cinq logiciels jeunes", "PhotoCraft est en « alpha précoce », SoundCraft en « pré-alpha » ; les autres bougent vite. Plus on enchaîne de logiciels, plus une panne peut bloquer la chaîne", "Formats ouverts entre logiciels (PSD, SVG, WAV, SRT, MP4) et un **plan B** pour chacun (§ 10.6)"],
    ["Transcription en français", "Whisper n'a été mesuré par FilmCraft qu'en anglais ; la qualité en français est à vérifier", "Test en semaine 1 ; relecture systématique des sous-titres"],
    ["Logiciel jeune", "EffectCraft a moins d'un mois (1er commit le 1er octobre 2026) : 29 gênes déjà notées, d'autres viendront", "Journal, contournements, fork pour l'essentiel, tests avant chaque mise à jour"],
    ["Dessin", "Claude ne dessine pas de sprites de niveau professionnel ; ses scripts font des formes simples", "Héros dessinés par toi, CC0 pour le reste, IA seulement pour chercher un style"],
    ["Voix", "Pas de synthèse vocale française en local ; une voix de synthèse sonne souvent « robot »", "Gags sans voix (choix de style) ; ta voix pour la science"],
    ["Humour et goût", "Claude propose des gags, mais c'est toi qui sais ce qui fait rire ton public", "Validation de chaque script ; tests sur de vrais spectateurs"],
    ["Droits", "Aucune image, musique ou personnage protégé (dont les 4 références du dossier pixel)", "Manifeste obligatoire ; « pas de licence, pas d'usage »"],
    ["Plateformes", "Règles qui changent, contenu « non authentique », algorithmes imprévisibles", "Plusieurs plateformes ; vraie valeur dans chaque vidéo ; revenus hors plateformes"],
    ["Revenus", "Les RPM et les ventes sont des hypothèses ; 500 $/mois n'est pas garanti", "Bilans aux mois 3, 6 et 12 avec règles de décision (§ 15.3)"],
    ["Temps humain", "Validation, voix, dessin et publication restent à toi : 6 à 12 h par semaine", "Travail par lots ; rythme A d'abord"],
    ["Claude et Gemini face à une vidéo", "Ils voient des images extraites, pas le mouvement continu, et n'entendent pas : Gemini a déjà inventé une voix sur une vidéo muette", "Règle de vérification (§ 10.8) : rien n'est retenu sans mesure qui le confirme ; rafales, verifier_pixels.py, ta validation finale"],
    ["Publication automatique", "Claude ne publie rien sans ton accord ; une API demande des identifiants", "Publication manuelle programmée ; automatisation éventuelle en v2.2"],
    ["Administratif", "Les revenus doivent être déclarés", "S'informer avant le premier paiement (§ 14.5)"],
  ], [1.8, 4.2, 3.6]),
);

// ================================================================ 18
C.push(
  H1("19. Versionnage"),
  H2("19.1 Ce document"),
  P("Chaque mise à jour du plan reçoit un numéro (2.1, 2.2…), une date et une ligne dans le tableau de la page de garde. L'ancienne version est gardée dans **~/videos/plans/**. On ne réécrit pas l'histoire : une décision changée est notée avec sa raison."),
  H2("19.2 L'usine (numéros de version)"),
  table(["Version", "Contenu", "Quand"], [
    ["1.0.0", "Bible v1, 4 modèles, 12 presets, 10 rapides, 4 recettes, monter.py v1 (état actuel)", "20/10/2026"],
    ["2.0.0", "Assets + licences, DA pixel, palette 32, planches, modèles Scène pixel, moteur caméra, contrôles, monter.py v2", "Fin de semaine 3–4"],
    ["2.1.0", "Corrections tirées du journal après les 10 premières vidéos", "Mois 2"],
    ["2.2.0", "Tableau de bord des stats, publication assistée (si utile)", "Mois 4"],
    ["3.0.0", "Fork EffectCraft avec les fonctions validées par le journal (§ 9.2)", "Quand le journal l'exige"],
  ], [1.2, 6.2, 2]),
  GAP(),
  P("**Règle de numérotation** : le dernier chiffre pour une correction, le chiffre du milieu pour un ajout qui ne casse rien, le premier chiffre quand les anciens épisodes doivent être adaptés."),
  H2("19.3 En pratique"),
  ...CODE(`cd ~/videos
git init                                   # une seule fois (semaine 1)
git add -A && git commit -m "usine 1.0.0 : état au 20/10/2026"
git tag v1.0.0
# … travail de la semaine …
git commit -m "camera.py : suivi de personnage avec retard"
git tag v2.0.0                             # quand le critère de fin de la v2 est rempli`),
  B("**CHANGELOG.md** : une ligne par changement visible (« ajouté », « corrigé », « changé »), sous le numéro de version."),
  B("**Projets** : Fichier ▸ Incrémenter et enregistrer avant toute grosse retouche ; monter.py garde une copie datée avant d'écraser."),
  B("**Les autres logiciels** : même règle, version et commit notés dans le CHANGELOG (au 20/10/2026 : FilmCraft 0.10.0 · 70f0fc7a, SoundCraft 0.10.0 · 7b339fe, PhotoCraft 0.11.1 · b097800e, VectorCraft 0.14.0 · bc1ae082). On ne met à jour un logiciel qu'entre deux vidéos, jamais au milieu d'une production."),
  B("**EffectCraft** : la version utilisée est notée dans le CHANGELOG (aujourd'hui 0.13.0). Avant de passer à une nouvelle version, on remonte 4 épisodes d'exemple : on ne bascule que si rien ne casse."),
  B("**Recettes Claude** : copie dans ~/videos/recettes/, installée dans ~/.claude/skills/ ; versionnées avec l'usine."),
  B("**Sauvegarde** : le dépôt git est poussé sur un dépôt privé (GitHub ou autre) chaque semaine ; les .mp4 vont sur un disque externe ou un cloud."),
);

// ================================================================ 19
C.push(
  H1("20. Risques et parades"),
  table(["Risque", "Probabilité", "Impact", "Parade"], [
    ["Démonétisation pour contenu répétitif", "Moyenne", "Fort", "Idée, script et plans uniques par vidéo ; ambiances réellement différentes"],
    ["Seuil de 8 000 h non atteint en 12 mois", "Forte", "Moyen", "Le plan ne compte pas sur la publicité en année 1 ; ambiances et longues"],
    ["Peu de vues au départ", "Forte", "Moyen", "Tenir 12 semaines avant de juger ; A/B des miniatures ; Shorts pour la découverte"],
    ["Aucune vente de pack", "Moyenne", "Moyen", "Relevé de prix, GIF d'aperçu, plusieurs boutiques, bundles"],
    ["Rendus trop lents", "Moyenne", "Moyen", "Scènes basse résolution, nuit, Windows natif"],
    ["Bug bloquant d'EffectCraft", "Moyenne", "Moyen", "Journal, contournement, signalement au projet, correctif dans le fork"],
    ["Problème de droits sur un asset", "Faible si la règle est suivie", "Fort", "Manifeste, verifier_licences.py, références séparées"],
    ["Perte de fichiers", "Faible", "Fort", "git poussé chaque semaine + sauvegarde externe des rendus"],
    ["Épuisement", "Moyenne", "Fort", "Lots, rythme A, l'usine fait le répétitif, pauses prévues"],
    ["Objectif financier non atteint au mois 12", "Moyenne", "Moyen", "Bilans 3, 6, 12 ; pivot (niche, format, plus de boutique ou de commandes)"],
  ], [3, 1.6, 1, 4]),
);

// ================================================================ 20
C.push(
  H1("21. La semaine 1, jour par jour"),
  table(["Jour", "Toi", "Claude", "Fin de journée"], [
    ["J1", "Lire § 1 et § 3 ; répondre aux décisions D1 à D4, D8 et D9 (5 min)", "Compilation de FilmCraft lancée en arrière-plan ; dépôt git ~/videos, tag v1.0.0, dossiers assets/, references/, a-trier/ ; les 4 images « pixel » rangées dans references/", "Historique propre"],
    ["J2", "Valider la palette ico-pixel-32 ; enregistrer 30 s de voix test (n'importe quel texte du script vulga-01)", "Compilation de SoundCraft ; transcription de la voix test dans FilmCraft (mesure des erreurs) ; Bible v2 (DA pixel, interdits), fichiers .gpl/.hex, planche bible v2 ; manifeste + verifier_licences.py", "Planche bible v2 validée"],
    ["J3", "Installer Aseprite (version Windows) ; ouvrir le gabarit", "Gabarit de planche 32×32 + fiche tim.toml ; prototype de Tim en formes simples", "Gabarit ouvert chez toi"],
    ["J4", "Commencer à dessiner Tim (repos + marche)", "decouper_planche.py + précomp personnage + marqueurs d'action, testés avec le prototype", "Prototype qui marche et saute à 12 i/s"],
    ["J5", "Continuer Tim ; générer 5 bruitages sur jsfxr", "Modèle « Scène pixel 9:16 » (SCENE, CAM, 5 plans, sortie) + verifier_pixels.py", "Rendu de test au vert"],
    ["J6–J7", "Repos, ou finir Tim", "Premiers mouvements caméra (travelling, secousse) ; mise à jour du journal", "Point de la semaine en 5 lignes"],
  ], [0.8, 3, 4, 1.8]),
  GAP(),
  NOTE("**Pour démarrer** : réponds aux décisions **D1 à D4** (même en une ligne : « D1 ok, D2 rythme A, D3 ok, D4 ok »), puis dis à Claude **« on attaque la semaine 1 de l'usine 2.1 »**."),
);

// ================================================================ annexes
C.push(
  H1("Annexe A. Glossaire"),
  table(["Mot", "Sens"], [
    ["Asset", "Fichier utilisé dans une vidéo sans être fabriqué dans le projet (sprite, décor, son, police)."],
    ["CC0", "Licence « domaine public » : usage libre, même commercial, sans obligation de crédit."],
    ["CC-BY / -SA / -NC / -ND", "Licences Creative Commons : BY = créditer ; SA = partager sous la même licence ; NC = pas d'usage commercial ; ND = pas de modification."],
    ["Comp / précomp", "Composition (une « scène » d'EffectCraft) ; une précomp est une comp utilisée comme un calque dans une autre."],
    ["Draft / plus proche voisin", "Qualité d'agrandissement qui copie chaque pixel sans le lisser : indispensable au pixel art."],
    ["Expression", "Petite formule attachée à une propriété (position, échelle…) qui calcule sa valeur à chaque image."],
    ["Marqueur", "Repère posé sur un calque à un instant précis ; nos expressions s'y déclenchent."],
    ["Parallaxe", "Les plans lointains bougent moins vite que les plans proches : illusion de profondeur."],
    ["Planche de sprites", "Image qui contient toutes les images d'animation d'un personnage, rangées en grille."],
    ["RPM", "Revenu pour 1 000 vues, après la part de la plateforme."],
    ["YPP", "YouTube Partner Program : le programme qui permet de toucher la publicité."],
    ["Heures de visionnage", "Total des heures regardées sur les vidéos longues publiques (les Shorts ne comptent pas)."],
    ["Zone sûre", "Partie de l'image que les boutons et textes des applis ne recouvrent pas."],
    ["MCP", "Protocole qui permet à Claude de piloter un logiciel (ses commandes deviennent des outils de Claude)."],
    ["LUFS", "Unité de volume perçu ; YouTube et les autres plateformes ramènent les vidéos à un volume cible."],
    ["Whisper", "Modèle de reconnaissance vocale (licence MIT) que FilmCraft fait tourner en local pour transcrire la voix."],
    ["PSD / SVG / SRT", "Formats d'échange : image en calques (PhotoCraft) ; dessin vectoriel (VectorCraft) ; sous-titres minutés (FilmCraft)."],
  ], [2.4, 7.2]),
  H1("Annexe B. Modèles de textes de publication"),
  H2("B.1 Description d'une vidéo longue"),
  ...CODE(`<Une phrase qui répond à « qu'est-ce que je vais apprendre ? »>
<Une phrase qui donne envie de rester jusqu'au bout.>

00:00 La question
00:40 <Chapitre 1>
02:30 <Chapitre 2>
04:30 <Chapitre 3>
06:30 La réponse

Sources :
- <source 1 (auteur, titre, année, lien)>
- <source 2>

Crédits : <textes exigés par les licences CC-BY, copiés du manifeste>
Musique : <titre, auteur, licence>

🎮 Packs pixel et fonds animés : <lien boutique>
☕ Soutenir la chaîne : <lien Ko-fi>

#pixelart #science #vulgarisation`),
  H2("B.2 Short"),
  ...CODE(`<Titre ≤ 60 caractères, sans spoiler de la chute>
<1 ligne de contexte> · la version longue : <lien>
#pixelart #shorts #<thème>`),
  H2("B.3 Page d'un pack (boutique)"),
  ...CODE(`<Nom du pack> — <ce que c'est en 5 mots>
[GIF animé de démonstration]
Contenu : <N> personnages · <N> actions · planches 32×32 + images séparées + GIF
Palette : ico-pixel-32 (fichier .gpl fourni)
Licence : usage personnel et commercial autorisé dans vos jeux, vidéos et streams ;
revente ou redistribution des fichiers interdite.
Fait par @yehz · ico-vid`),
  H1("Annexe C. Sources"),
  B("YouTube, page d'aide officielle « Changes to the YouTube Partner Programme » (support.google.com/youtube/answer/12843009), consultée le 21/10/2026 : seuils du 01/02/2027 (8 000 h ou 20 M de vues Shorts ; 10 M de vues Shorts / 90 j pour le fonds Shorts ; critères d'activité ; niveau « soutiens » inchangé)."),
  B("YouTube, « Présentation du Programme Partenaire YouTube et conditions d'éligibilité » (support.google.com/youtube/answer/72851) et « Commerce Products monetization policies » (answer/13195878)."),
  B("TechCrunch, « YouTube clarifies policies around AI slop and upsetting videos », 20/07/2026 (contenu non authentique)."),
  B("AIR Media-Tech, données de RPM Shorts 2026 et guide des conditions YPP 2026 (air.io)."),
  B("Guides TikTok Creator Rewards 2026 (metricool.com, swello.com, toptal.com, shortsync.app) : conditions concordantes (10 000 abonnés, 100 000 vues / 30 j, vidéos > 1 min, 18 ans) ; rémunération estimée entre 0,40 et 1,20 $ pour 1 000 vues qualifiées selon les sources."),
  B("Frais de plateformes : itch.io (part réglable, 10 % par défaut), Gumroad (10 % + 0,50 $) d'après des comparatifs 2026 ; à vérifier sur les pages tarifs officielles."),
  B("Documentation des logiciels, lue le 21/10/2026 dans ~/videos/logiciel : README de chaque logiciel ; FilmCraft docs/captions.md, docs/transcripts.md, docs/agents.md ; PhotoCraft et SoundCraft docs/mcp.md ; EffectCraft docs/file-format-parity.md (import PSD, AI/PDF, SVG)."),
  B("Taux micro-entreprise 2026 (lecoindesentrepreneurs.fr, hayot-expertise.fr, advizexperts.fr) : sources concordantes sur les taux, divergentes sur les plafonds ; **à confirmer sur urssaf.fr**."),
);

const doc = new Document({
  creator: "ico-vid", title: "ico-vid · Usine 2.3 — plan détaillé", description: "Plan de construction détaillé de l'usine vidéo pixel",
  styles: {
    default: { document: { run: { font: "Calibri", size: 21 } } },
    paragraphStyles: [
      { id: "Heading1", name: "Heading 1", basedOn: "Normal", next: "Normal", quickFormat: true,
        run: { size: 34, bold: true, color: NAVY }, paragraph: { spacing: { before: 360, after: 200 }, outlineLevel: 0,
        border: { bottom: { style: BorderStyle.SINGLE, size: 8, color: AMBER, space: 4 } } } },
      { id: "Heading2", name: "Heading 2", basedOn: "Normal", next: "Normal", quickFormat: true,
        run: { size: 26, bold: true, color: BLUE }, paragraph: { spacing: { before: 260, after: 120 }, outlineLevel: 1 } },
      { id: "Heading3", name: "Heading 3", basedOn: "Normal", next: "Normal", quickFormat: true,
        run: { size: 22, bold: true, color: GREY }, paragraph: { spacing: { before: 200, after: 80 }, outlineLevel: 2 } },
    ],
  },
  numbering: {
    config: [
      { reference: "puces", levels: [
        { level: 0, format: LevelFormat.BULLET, text: "•", alignment: AlignmentType.LEFT, style: { paragraph: { indent: { left: 500, hanging: 260 } } } },
        { level: 1, format: LevelFormat.BULLET, text: "–", alignment: AlignmentType.LEFT, style: { paragraph: { indent: { left: 900, hanging: 260 } } } }] },
      ...[...LISTES].map((r) => ({ reference: r, levels: [
        { level: 0, format: LevelFormat.DECIMAL, text: "%1.", alignment: AlignmentType.LEFT, style: { paragraph: { indent: { left: 500, hanging: 300 } } } }] })),
    ],
  },
  sections: [{
    properties: { page: { size: { width: 11906, height: 16838 }, margin: { top: 1134, bottom: 1134, left: 1134, right: 1134 } } },
    footers: { default: new Footer({ children: [new Paragraph({ alignment: AlignmentType.RIGHT, children: [
      new TextRun({ text: "ico-vid · Usine 2.3 · plan détaillé · page ", color: GREY, size: 16 }),
      new TextRun({ children: [PageNumber.CURRENT], color: GREY, size: 16 })] })] }) },
    children: C,
  }],
});

Packer.toBuffer(doc).then((buf) => { fs.writeFileSync(process.argv[2], buf); console.log("écrit", process.argv[2], buf.length, "octets"); });
