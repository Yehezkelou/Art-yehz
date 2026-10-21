// Plan « Usine 2.0 » ico-vid — génère le .docx (node plan.js <sortie.docx>)
const fs = require("fs");
const {
  Document, Packer, Paragraph, TextRun, HeadingLevel, Table, TableRow, TableCell, WidthType,
  ShadingType, BorderStyle, AlignmentType, LevelFormat, Footer, PageNumber, PageBreak,
  TableOfContents,
} = require("docx");

const W = 9638; // largeur utile A4 avec marges de 2 cm (DXA)
const NAVY = "1B2340", BLUE = "2E5AA0", GREY = "5B6475", LIGHT = "F2F4F8", AMBER = "FFB020", CREAM = "FFF6D6";

// **gras** dans le texte
function runs(text, opts = {}) {
  return text.split("**").map((t, i) => new TextRun({ text: t, bold: i % 2 === 1 || opts.bold, color: opts.color, size: opts.size, italics: opts.italics }));
}
const P = (t, o = {}) => new Paragraph({ children: runs(t, o), spacing: { after: 120, line: 288 }, alignment: o.align });
const H1 = (t) => new Paragraph({ heading: HeadingLevel.HEADING_1, children: [new TextRun(t)], pageBreakBefore: true });
const H2 = (t) => new Paragraph({ heading: HeadingLevel.HEADING_2, children: [new TextRun(t)] });
const H3 = (t) => new Paragraph({ heading: HeadingLevel.HEADING_3, children: [new TextRun(t)] });
const B = (t, lvl = 0) => new Paragraph({ numbering: { reference: "puces", level: lvl }, children: runs(t), spacing: { after: 60, line: 276 } });
const N = (t, ref = "num") => new Paragraph({ numbering: { reference: ref, level: 0 }, children: runs(t), spacing: { after: 60, line: 276 } });
const BR = () => new Paragraph({ children: [new PageBreak()] });
const NOTE = (t) => new Paragraph({
  children: runs(t), spacing: { before: 120, after: 160, line: 288 },
  shading: { type: ShadingType.CLEAR, fill: CREAM, color: "auto" },
  border: { left: { style: BorderStyle.SINGLE, size: 24, color: AMBER, space: 8 } },
  indent: { left: 170, right: 170 },
});

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
      new TableRow({ tableHeader: true, children: headers.map((h, i) => cell(h, i, true)) }),
      ...rows.map((r, j) => new TableRow({ children: r.map((c, i) => cell(c, i, false, j % 2 === 1)) })),
    ],
  });
}
const GAP = () => new Paragraph({ children: [], spacing: { after: 80 } });

const C = []; // contenu

// ---------------------------------------------------------------- page de garde
C.push(
  new Paragraph({ children: [], spacing: { before: 2400 } }),
  new Paragraph({ children: [new TextRun({ text: "ico-vid · Usine 2.0", bold: true, size: 64, color: NAVY })], spacing: { after: 160 } }),
  new Paragraph({ children: [new TextRun({ text: "Plan de construction : personnages et motion design pixel, moteur caméra, production, marketing YouTube et plateformes, objectif 500 $ par mois", size: 30, color: BLUE })], spacing: { after: 480 } }),
  new Paragraph({ children: runs("Version **2.0** · 21 octobre 2026 · chaîne **ico-vid** · **@yehz**", { color: GREY, size: 24 }), spacing: { after: 120 } }),
  new Paragraph({ children: runs("Fait suite à « EffectCraft sur mesure » (v1.0, même date) : étapes 0 à 5 terminées, étape 6 commencée.", { color: GREY, size: 22 }), spacing: { after: 1200 } }),
  table(["Version", "Date", "Contenu", "Statut"], [
    ["1.0", "20/10/2026", "Plan initial « EffectCraft sur mesure » : étapes 0 à 8", "Étapes 0–5 faites"],
    ["2.0", "21/10/2026", "Ce document : usine 2.0 pixel, moteur caméra, marketing, objectif 500 $/mois, limites, versionnage", "À valider"],
    ["2.x", "à venir", "Mises à jour après chaque phase (chiffres réels, décisions)", "—"],
  ], [1, 1.4, 5, 1.6]),
);

// ---------------------------------------------------------------- sommaire
C.push(
  new Paragraph({ children: [new TextRun({ text: "Sommaire", bold: true, size: 32, color: NAVY })], spacing: { after: 200 }, pageBreakBefore: true }),
  new TableOfContents("Sommaire", { hyperlink: true, headingStyleRange: "1-2" }),
);

// ---------------------------------------------------------------- 1
C.push(
  H1("1. En une page"),
  P("**Où on en est.** L'usine 1.0 tourne : une bible de chaîne, 4 modèles de projet, 12 presets et 10 mouvements « rapides », 4 recettes Claude et un outil qui monte un épisode complet en **2 secondes** à partir d'un petit fichier texte. Deux vidéos de test sont sorties (sketch « Le cloud », vulgarisation « GPS et Einstein »)."),
  P("**Ce qu'on construit maintenant.** Une usine 2.0 spécialisée **pixel art et motion design pixel** : de vrais personnages animés (planches de sprites), des scènes en plusieurs plans, et un **moteur caméra pixel** (travellings, suivi, zoom par paliers, secousse, parallaxe) pour des mouvements de caméra crédibles. La chaîne ne fait pas seulement des Shorts : elle produit aussi des formats longs, parce que ce sont eux qui rapportent."),
  P("**Le but chiffré.** **500 $ par mois** au bout d'environ 12 mois, en additionnant plusieurs revenus : publicité YouTube (surtout les vidéos longues), TikTok (vidéos de plus d'une minute), vente de packs pixel et de fonds animés, petites commandes. Les Shorts seuls n'y arriveront pas : il faudrait 5 à 17 millions de vues par mois (§ 9)."),
  P("**La méthode, dans l'ordre :**"),
  N("**Fondations (semaines 1–2)** : dépôt versionné, bibliothèque d'assets avec licences, direction artistique pixel, découpage des planches de sprites, modèles pixel v2."),
  N("**Moteur caméra pixel (semaines 2–4)** : une caméra pilotée par un seul calque de contrôle, qui fait bouger 4 à 6 plans à des vitesses différentes, toujours au pixel entier."),
  N("**Production régulière (à partir de la semaine 4)** : 5 Shorts et 1 vidéo longue par semaine, publiés sur YouTube, TikTok et Instagram."),
  N("**Mesure et ajustement (mois 2 à 12)** : analytics, miniatures testées, boutique de packs, puis monétisation dès que les seuils sont atteints."),
  NOTE("**Règle d'or conservée** : on ne code une nouvelle fonction dans EffectCraft que si elle a manqué sur **au moins 2 vraies vidéos** (journal « ce qui m'a gêné », 28 entrées à ce jour). Sinon on construit un logiciel parfait… et zéro vidéo."),
);

// ---------------------------------------------------------------- 2
C.push(
  H1("2. Bilan de l'usine 1.0"),
  table(["Brique", "État au 21/10/2026", "Où"], [
    ["Bible de la chaîne", "Formats, zones sûres 9:16 et 16:9, polices OFL, 4 palettes, sous-titres, signature ico-vid", "~/videos/bible.md"],
    ["Modèles de projet", "Sketch, Pixel art, Aventure fantasy, Vulgarisation (.ectemplate, galerie de l'app)", "~/videos/modeles/"],
    ["Presets", "12 .ecpreset (pop, rebond, secousse, zoom, iris…) + 10 mouvements rapides (gratuits au rendu)", "~/videos/presets/"],
    ["Recettes Claude", "video-sketch, video-pixel, video-fantasy, video-vulga", "~/.claude/skills/"],
    ["Outil de montage", "monter.py : episode.toml → projet + 3 aperçus (~2 s), puis rendu .mp4 + copie Bureau", "~/videos/outils/"],
    ["Vidéos sorties", "sketch-01 (17 s), vulga-01-gps (62 s, rendu en 3 min 42)", "~/videos/…"],
    ["Journal des gênes", "28 entrées (performances, commandes manquantes, sous-titres…)", "~/videos/ce-qui-m-a-gene.md"],
  ], [2, 5, 2.4]),
  GAP(),
  P("**Ce que le test a prouvé** : la chaîne idée → script → projet → aperçus → vidéo fonctionne de bout en bout, sans ouvrir l'app. **Ce qu'il manque pour de « vraies » vidéos pixel** : des personnages dessinés et animés, des décors en plans séparés, des mouvements de caméra, une voix et du son."),
);

// ---------------------------------------------------------------- 3
C.push(
  H1("3. Références visuelles et droits"),
  P("Le dossier **Bureau ▸ pixel** contient 4 images. Elles donnent une direction claire, mais **aucune ne peut apparaître dans une vidéo publiée** : ce sont des fonds d'écran d'autres artistes, et l'une représente un personnage de jeu protégé."),
  table(["Fichier", "Ce qu'on en retient (style)", "Utilisable en vidéo ?"], [
    ["artistic-pixel_art-1002548", "Ruines en vue plongeante, herbe en aplats, ombres longues, palette verte et douce : ambiance « cosy »", "Non : auteur inconnu, droits réservés"],
    ["artistic-pixel_art-1023270", "Terre et Lune dans l'espace, nébuleuse en tons bleus, étoiles scintillantes", "Non : signé @exilecast"],
    ["artistic-pixel_art-981491", "Village « Owl's nest » : chaumière, rivière, pont, personnages minuscules, cadre par la végétation au premier plan", "Non : droits réservés"],
    ["…final_fantasy…381064", "Mage noir 16 bits : contour noir épais, 4–5 couleurs, silhouette lisible", "Non : personnage de Square Enix"],
  ], [2.6, 4.6, 2.2]),
  GAP(),
  H2("3.1 Direction artistique retenue (« ico-vid pixel »)"),
  B("**Ambiance** : scènes cosy et lumineuses (nature, village, espace), personnages petits dans de grands décors, végétation au premier plan pour cadrer."),
  B("**Personnages** : sprites de 32×32 px (gros plans : 64×64), contour sombre, 4 à 6 couleurs par personnage, silhouette lisible en miniature."),
  B("**Décors** : tuiles de 16×16 px, chaque décor découpé en 4 à 6 plans (ciel, loin, milieu, action, premier plan, effets)."),
  B("**Palette** : 32 couleurs maximum par série, enregistrée dans la bible (palette « pixel » actuelle à étendre)."),
  B("**Animation** : 12 images par seconde ; 4 images pour une marche, 2 à 4 pour la respiration, 6 à 8 pour un saut."),
  H2("3.2 D'où viendront les personnages et les décors (légalement)"),
  table(["Source", "Coût", "Qualité", "Droits", "Rôle dans l'usine"], [
    ["Dessin maison (Pixelorama, licence MIT ; ou Aseprite, payant)", "0 à ~20 $", "La meilleure à terme, identité unique", "100 % à toi", "Héros récurrents, mascotte, miniatures"],
    ["Packs CC0 (Kenney, OpenGameArt filtré CC0)", "0 $", "Bonne, mais déjà vue ailleurs", "Libres, même commercial", "Décors, objets, figurants"],
    ["Packs payants itch.io (licence commerciale)", "5–30 $ le pack", "Très bonne", "Vérifier la licence de chaque pack", "Tilesets complets, effets"],
    ["Sprites générés par script (Claude)", "0 $", "Simple (formes, couleurs, animations de base)", "À toi", "Prototypes, objets, particules"],
    ["Générateurs d'images IA", "variable", "Inégale en pixel art (grille irrégulière, il faut retoucher)", "Selon l'outil ; à déclarer sur YouTube si réaliste", "Recherche de style uniquement, au début"],
  ], [3, 1.3, 2.2, 2.2, 2.4]),
  NOTE("**Règle** : chaque fichier entre dans la bibliothèque avec sa ligne de licence (source, auteur, licence, date). Pas de licence vérifiée, pas d'utilisation. Les 4 images du dossier « pixel » vont dans **références/**, jamais dans **assets/**."),
);

// ---------------------------------------------------------------- 4
C.push(
  H1("4. Personnalisation du logiciel"),
  H2("4.1 Sans toucher au code (semaines 1–2)"),
  table(["Personnalisation", "Détail", "Statut"], [
    ["Espace de travail « ico-vid pixel »", "Panneaux disposés pour le pixel : Timeline large, viewer en 200 % ou 400 %, Effets et presets à droite", "À faire"],
    ["Modèles pixel v2", "« Scène pixel 16:9 » (480×270 ×4 = 1920×1080) et « Scène pixel 9:16 » (270×480 ×4), avec plans, caméra et guide", "À faire (§ 5)"],
    ["Bibliothèque de personnages", "Un personnage = une précomp avec ses actions (repos, marche, saut, parle) prêtes à glisser", "À faire"],
    ["Presets caméra", "Travelling, suivi, secousse, zoom par paliers, en mouvements rapides (expressions)", "À faire (§ 5)"],
    ["Modèle d'export", "« Short 9:16 H.264 » (fait) + « Long 16:9 H.264 » + « Boucle GIF / WebM » pour la boutique", "1 sur 3"],
    ["Raccourcis", "Ajouter un marqueur, Draft/Best, appliquer les mouvements rapides", "À faire"],
  ], [2.6, 5, 1.4]),
  GAP(),
  H2("4.2 Avec du code (fork, seulement si validé par le journal)"),
  P("On travaille sur **un fork** du dépôt EffectCraft, branche **perso**, et on garde le dépôt officiel comme « upstream » pour récupérer ses mises à jour. Chaque fonction ajoutée est une commande (id, paramètres) : elle apparaît alors dans les menus, la ligne de commande et pour Claude. Tout ce qui est utile à tous est proposé au projet officiel. Les candidats, classés par impact d'après le journal :"),
  table(["#", "Fonction", "Pourquoi (gêne du journal)", "Priorité"], [
    ["1", "Contrôles d'expression gratuits au rendu", "Un simple curseur coûte ~200 ms par image ; un preset multiplie le rendu par 5 (n° 24)", "Haute"],
    ["2", "Mode « pixel parfait » : texte sans lissage, accrochage aux pixels entiers", "Texte anticrénelé dans la comp 270×480 (n° 18) ; indispensable pour la v2 pixel", "Haute"],
    ["3", "Commande pour régler l'entrée et la sortie d'un calque", "Il faut passer par un script à chaque sous-titre (n° 1)", "Moyenne"],
    ["4", "Import de sous-titres .srt", "Les sous-titres sont le plus gros travail manuel (n° 2)", "Moyenne"],
    ["5", "Option --config-dir pour la ligne de commande", "Impossible d'enregistrer un modèle en headless (n° 15)", "Basse"],
    ["6", "Presets qui n'écrasent pas la valeur des propriétés", "Appliquer un preset déplaçait le calque (n° 21)", "Basse (contourné)"],
  ], [0.5, 3.4, 4.4, 1.3]),
  NOTE("Avant chaque modification : `cargo xtask ci` au vert, zéro plantage possible (pas de unwrap ni de panic), un test par correction. Ce sont les règles du projet EffectCraft ; elles s'appliquent aussi au fork."),
);

// ---------------------------------------------------------------- 5
C.push(
  H1("5. Le moteur caméra pixel"),
  P("Un « vrai » mouvement de caméra en pixel art ne peut pas utiliser la caméra 3D classique : elle agrandit et tourne les images à des tailles non entières, et les pixels « bavent ». On construit donc **un moteur caméra 2.5D** à partir de ce qu'EffectCraft sait déjà faire très bien et gratuitement au rendu : des **expressions** et des **précomps**."),
  H2("5.1 Principe"),
  N("La scène est une comp en basse résolution (480×270 ou 270×480) qui contient **4 à 6 plans** : ciel, loin, milieu, action (personnages), premier plan, effets (pluie, lucioles, poussière).", "num2"),
  N("Un calque de contrôle **CAM** porte quelques curseurs : position X/Y, zoom, secousse, calque à suivre, retard du suivi.", "num2"),
  N("Chaque plan suit CAM selon sa **profondeur** (ciel ×0,1 ; loin ×0,3 ; milieu ×0,6 ; action ×1 ; premier plan ×1,4) : c'est la parallaxe qui donne l'illusion de relief.", "num2"),
  N("Toutes les positions sont **arrondies au pixel entier** ; le zoom ne prend que des **paliers entiers** (×1, ×2, ×3) ou passe par un raccord (coupe).", "num2"),
  N("La comp de sortie agrandit la scène ×4 en qualité Draft (plus proche voisin, déjà validé : 3 couleurs autour du héros, aucun flou).", "num2"),
  H2("5.2 Bibliothèque de mouvements"),
  table(["Mouvement", "Usage", "Réalisme ajouté"], [
    ["Travelling latéral", "Suivre une marche, découvrir un décor", "Démarrage et arrêt amortis (ease in/out), parallaxe"],
    ["Panoramique vertical", "Révéler un ciel, une tour, une planète", "Vitesse non constante, léger dépassement à l'arrêt"],
    ["Suivi de personnage", "Le héros reste cadré quand il bouge", "Retard réglable (la caméra « rattrape » le perso)"],
    ["Zoom par paliers", "Insister sur une réaction (gag)", "×1 → ×2 en coupe franche, ou sur 2 images"],
    ["Secousse d'impact", "Chute, explosion, porte qui claque", "Décroissance rapide, amplitude en pixels entiers"],
    ["Caméra « à la main »", "Scènes calmes, ambiance vivante", "Micro-dérive de 1 px, très lente"],
    ["Plan d'ensemble → rapproché", "Raconter (où, puis qui)", "Coupe sur le mouvement, raccord dans l'axe"],
    ["Fondu iris / volet", "Fin de scène, transition", "Iris au pixel (cercle dessiné en marches)"],
  ], [2.4, 3.2, 4]),
  GAP(),
  H2("5.3 Et les caméras 3D ?"),
  P("Pour les formats qui ne sont pas en pixel (fantasy, vulgarisation), on utilise la **caméra 3D d'EffectCraft** : calques en 3D, profondeur de champ, flou de mouvement. Le projet Remotion « serie-aventure » peut fournir des plans 3D, qu'EffectCraft compose ensuite (titres, effets, sous-titres). Ces deux voies restent séparées de la voie pixel, pour ne pas mélanger les styles."),
  H2("5.4 Livrables"),
  B("**camera.py** : génère les expressions de la caméra et des plans (comme rapides.py)."),
  B("**Modèles « Scène pixel 16:9 / 9:16 »** avec CAM et les plans déjà reliés."),
  B("**monter.py v2** : un épisode décrit **plan par plan** (décor, personnages, action, mouvement de caméra, répliques)."),
  B("**decouper_planche.py** : découpe une planche de sprites en images numérotées, importées en séquence à 12 i/s."),
  B("**Critère de fin** : une scène de 15 s avec 2 personnages, 5 plans de profondeur et 3 mouvements de caméra, rendue sans un seul pixel baveux, montée depuis un fichier texte."),
);

// ---------------------------------------------------------------- 6
C.push(
  H1("6. Architecture de l'usine 2.0"),
  P("Chaque étape a un responsable clair. Claude prépare et exécute, toi tu décides et tu valides : idée, script, aperçus, publication."),
  table(["#", "Étape", "Qui", "Outil", "Sortie"], [
    ["1", "Idée et angle", "Toi (Claude propose)", "Recette du format", "Pitch d'une ligne"],
    ["2", "Script et découpage en plans", "Claude, validé par toi", "Recette + bible", "episode.toml v2"],
    ["3", "Assets (persos, décors, sons)", "Bibliothèque ; dessin si besoin", "assets/ + manifeste des licences", "Liste des assets utilisés"],
    ["4", "Voix", "Toi (téléphone) ou synthèse vocale externe", "voix.wav", "Bouche et sous-titres calés"],
    ["5", "Montage automatique", "Claude", "monter.py v2 + camera.py", "Projet .ecproj + 3 aperçus"],
    ["6", "Validation", "Toi", "Aperçus, ou l'app", "« OK » ou corrections"],
    ["7", "Rendu", "Machine (la nuit si long)", "monter.py --rendu, dossier surveillé", ".mp4 9:16 et 16:9"],
    ["8", "Miniature, titre, description, tags", "Claude propose, toi tu choisis", "Comp « Miniature » + modèle de texte", "Miniature PNG + texte"],
    ["9", "Publication", "Toi (au début)", "YouTube Studio, TikTok, Instagram", "Vidéo en ligne"],
    ["10", "Mesure", "Claude (export des stats)", "Analytics → tableau", "Ce qui marche ou pas"],
  ], [0.4, 2.4, 2.2, 2.4, 2.2]),
  GAP(),
  H2("6.1 Organisation des fichiers"),
  table(["Dossier", "Contenu", "Versionné (git) ?"], [
    ["~/videos/bible.md, modeles/, presets/, outils/", "Les règles et les outils de l'usine", "Oui"],
    ["~/videos/assets/pixel/{persos,decors,fx,sons}/", "Assets + manifest.toml (licences)", "Oui, sauf fichiers > 5 Mo"],
    ["~/videos/references/", "Images d'inspiration (non utilisables)", "Non"],
    ["~/videos/<format>-NN-mot/", "episode.toml, projet, aperçus", "Oui, sauf .mp4"],
    ["Rendus .mp4", "Vidéos finales", "Non : copie Bureau + sauvegarde externe"],
  ], [3.6, 3.8, 2.2]),
  GAP(),
  H2("6.2 Matériel"),
  P("La machine actuelle (Intel UHD 620, 16 Go, WSL) fait tourner l'usine. Mais **le rendu se fait sur le processeur**, car WSL n'expose pas le GPU (llvmpipe) : environ 0,25 s par image pour un sketch, 1 s pour la fantasy. Parades : rendre la nuit avec le dossier surveillé d'EffectCraft, prévisualiser en demi-résolution, tester une **version Windows native** (accès direct à la carte graphique). Un PC plus puissant n'est utile qu'une fois les revenus là."),
);

// ---------------------------------------------------------------- 7
C.push(
  H1("7. Stratégie de contenu"),
  H2("7.1 Positionnement"),
  P("**« ico-vid : le monde expliqué et raconté en pixel art. »** Une identité visuelle unique (pixel cosy, mouvements de caméra soignés) appliquée à des sujets qui intéressent beaucoup de monde. Le pixel art sert de signature : on reconnaît la chaîne en une image."),
  table(["Série", "Format", "Rythme", "Rôle"], [
    ["**La science en pixel** (vulgarisation)", "Long 6–10 min en 16:9 + 3 Shorts extraits", "1 long / semaine", "Revenus publicitaires, heures de visionnage"],
    ["**Gags pixel** (humour, jeu vidéo rétro)", "Shorts 15–45 s en 9:16, et version 1 min+ pour TikTok", "3–4 / semaine", "Découverte, abonnés"],
    ["**Aventure de Tim** (fantasy pixel)", "Épisodes de 2–4 min + bande-annonce Short", "1 / 2 semaines", "Fidélité, série qu'on suit"],
    ["**Ambiances pixel** (scènes animées en boucle + musique libre)", "Long 1–3 h en 16:9", "1 / mois", "Heures de visionnage, produit à vendre (fond animé)"],
  ], [3.2, 3, 1.6, 2.2]),
  NOTE("**Attention au contenu « non authentique » de YouTube.** Depuis juillet 2025, et précisé en juillet 2026, YouTube ne monétise pas les vidéos **génériques, répétitives ou fabriquées en série sur un même gabarit**. Une usine est justement ce qui produit en série : chaque vidéo doit donc avoir sa propre idée, son propre script, ses propres plans et une vraie valeur. Les modèles accélèrent le travail, ils ne doivent pas se voir à l'écran. Les « ambiances » doivent montrer des scènes réellement différentes, pas la même boucle recolorée."),
  H2("7.2 Règles de fabrication qui font vendre"),
  B("**Accroche en 2 secondes** (bible § 3), miniature lisible en tout petit, titre qui promet une réponse."),
  B("**Une idée par vidéo** ; les longues ont un chapitrage et une boucle de fin vers la vidéo suivante."),
  B("**Mouvements de caméra** à chaque plan : c'est ce qui sépare le motion design de la simple image animée."),
  B("**Son** : voix claire, bruitages 8 bits, musique libre (bibliothèque audio YouTube, Freesound avec licence vérifiée)."),
  B("**Recyclage intelligent** : 1 vidéo longue donne 3 Shorts, 1 GIF pour la boutique et 1 miniature-affiche."),
);

// ---------------------------------------------------------------- 8
C.push(
  H1("8. Marketing YouTube et autres plateformes"),
  table(["Plateforme", "Ce qu'on publie", "Monétisation", "Seuil d'entrée (vérifié en oct. 2026)"], [
    ["YouTube (long)", "Science en pixel, fantasy, ambiances", "Publicités (part des revenus)", "1 000 abonnés + 4 000 h de visionnage sur 12 mois"],
    ["YouTube Shorts", "Gags, extraits de vulgarisation", "Part du fonds publicitaire Shorts", "1 000 abonnés + 10 M de vues Shorts sur 90 jours (ou les 4 000 h)"],
    ["TikTok", "Versions de plus d'une minute", "Creator Rewards (vidéos > 1 min)", "10 000 abonnés + 100 000 vues sur 30 jours, 18 ans"],
    ["Instagram Reels", "Les mêmes Shorts", "Indirecte (audience, partenariats)", "—"],
    ["itch.io / Gumroad / Ko-fi", "Packs pixel, fonds animés pour streamers, modèles", "Ventes (frais de 5 à 10 %)", "Aucun"],
    ["Malt / Fiverr", "Animations pixel sur commande", "Prestations", "Aucun (statut à déclarer)"],
  ], [1.8, 2.6, 2.4, 3]),
  NOTE("**Changement annoncé** : la page d'aide officielle de YouTube indique que le Programme Partenaire change le **1er février 2027**, sans détailler comment. Un guide tiers parle de seuils plus élevés pour les nouveaux candidats (8 000 h ou 20 M de vues Shorts), ce qui n'est **pas confirmé** officiellement. Le plan suppose donc des seuils plus durs, et vérifie la page officielle au mois 3."),
  H2("8.1 Lancement"),
  B("**Identité** : même nom (ico-vid) et même pseudo (@yehz) partout, bannière et avatar pixel (un personnage mascotte)."),
  B("**Calendrier** : 5 Shorts et 1 long par semaine, publiés aux mêmes heures ; 3 vidéos prêtes d'avance avant le lancement."),
  B("**Référencement** : titres et descriptions en français, chapitres pour les longues, 3 à 5 tags précis, sous-titres intégrés (beaucoup regardent sans le son)."),
  B("**Miniatures** : tester 2 à 3 versions avec l'outil « Tester et comparer » de YouTube Studio quand il est disponible sur la chaîne."),
  B("**Communauté** : répondre aux commentaires les premières heures, poser une question à la fin, sondages dans l'onglet Posts."),
  B("**Recyclage** : chaque Short sur YouTube, TikTok et Instagram, avec le texte adapté à chaque plateforme (pas de filigrane d'une autre plateforme)."),
  H2("8.2 Ce qu'on mesure chaque semaine"),
  table(["Indicateur", "Pourquoi", "Objectif de départ"], [
    ["Rétention à 3 s (Shorts)", "L'accroche marche-t-elle ?", "> 70 %"],
    ["Durée moyenne vue (long)", "Le contenu tient-il ?", "> 40 % de la vidéo"],
    ["Taux de clic des miniatures", "Titre et miniature donnent-ils envie ?", "> 4 %"],
    ["Abonnés par 1 000 vues", "La chaîne donne-t-elle envie de revenir ?", "> 3"],
    ["Heures de visionnage cumulées", "Seuil du Programme Partenaire", "4 000 h en 12 mois"],
    ["Ventes boutique", "Revenu hors plateformes", "1 pack au mois 3"],
  ], [3, 3.6, 2.4]),
);

// ---------------------------------------------------------------- 9
C.push(
  H1("9. Objectif 500 $ par mois : les chiffres"),
  P("Les montants par 1 000 vues (RPM) varient énormément selon le pays, le sujet et l'audience. Les chiffres ci-dessous sont des **hypothèses de travail** tirées de guides de 2026, pas des promesses ; on les remplacera par les vrais chiffres de la chaîne dès qu'ils existent."),
  table(["Scénario", "Hypothèse", "Volume nécessaire pour 500 $/mois", "Réaliste ?"], [
    ["A. Shorts seuls", "RPM 0,03 à 0,10 $", "5 à 17 millions de vues par mois", "Non, pas la première année"],
    ["B. Vidéos longues seules", "RPM 1 à 4 $ (francophone, à confirmer)", "125 000 à 500 000 vues par mois", "Difficile seul"],
    ["C. Mélange (recommandé)", "Plusieurs sources de revenus", "Voir le détail ci-dessous", "Oui, vers le mois 12"],
  ], [2.2, 2.6, 3, 1.8]),
  GAP(),
  table(["Source (scénario C, mois 12)", "Hypothèse", "Par mois"], [
    ["YouTube, vidéos longues", "100 000 vues × 2 $ / 1 000", "200 $"],
    ["YouTube Shorts", "1,5 M vues × 0,05 $ / 1 000", "75 $"],
    ["TikTok Creator Rewards", "150 000 vues qualifiées × ~0,40 $ / 1 000 (très incertain)", "60 $"],
    ["Boutique (packs pixel, fonds animés)", "15 ventes × 8 $", "120 $"],
    ["Commandes (animation pixel sur mesure)", "1 petite commande", "75 $"],
    ["**Total**", "", "**≈ 530 $**"],
  ], [3.4, 4.4, 1.6]),
  NOTE("La boutique et les commandes ne dépendent d'aucun seuil : elles peuvent rapporter **dès le mois 2 ou 3**, bien avant la monétisation YouTube. Ce sont elles qui rendent l'objectif atteignable. L'usine fabrique ces packs avec les mêmes assets que les vidéos."),
  H2("9.1 Jalons"),
  table(["Quand", "Jalon", "Revenu visé"], [
    ["Mois 1", "Usine 2.0 prête, chaîne lancée, 20 vidéos publiées", "0 $"],
    ["Mois 3", "1er pack en vente, 300 abonnés, 1re commande", "20–50 $"],
    ["Mois 6", "1 000 abonnés YouTube, 2 000 h de visionnage, 3 packs", "100–150 $"],
    ["Mois 9", "Programme Partenaire YouTube obtenu, TikTok 10 000 abonnés", "250–350 $"],
    ["Mois 12", "Rythme stable, revenus diversifiés", "≈ 500 $"],
  ], [1.4, 5.6, 2]),
);

// ---------------------------------------------------------------- 10
C.push(
  H1("10. Feuille de route détaillée"),
  table(["Semaine", "Livrable", "Critère de fin"], [
    ["S1", "Dépôt git ~/videos (v1.0.0), bibliothèque assets/ + manifeste des licences, références/ séparées", "git log propre, chaque asset a sa licence"],
    ["S1", "Direction artistique pixel dans la bible (§ 3.1) + palette 32 couleurs", "Planche bible v2 rendue"],
    ["S1–S2", "decouper_planche.py + 1er personnage (repos, marche, saut, parle)", "Marche de 4 images importée et bouclée à 12 i/s"],
    ["S2", "Modèles « Scène pixel 16:9 / 9:16 » avec 5 plans", "Rendu sans pixel baveux (contrôle automatique des couleurs)"],
    ["S2–S3", "camera.py + 8 mouvements (§ 5.2)", "Scène test de 15 s, 3 mouvements de caméra"],
    ["S3", "monter.py v2 : épisodes plan par plan", "Un épisode de 3 plans monté depuis un fichier texte"],
    ["S3", "Comp Miniature + modèle titre/description", "Miniature lisible à 10 % de sa taille"],
    ["S4", "Lancement : 3 vidéos d'avance, chaînes créées partout", "1re semaine publiée à l'heure"],
    ["S4–S12", "Production : 5 Shorts + 1 long / semaine ; journal tenu", "≥ 40 vidéos à S12"],
    ["S6", "1er pack itch.io (personnages + décor + fond animé)", "Page en ligne, licence claire"],
    ["S8", "Bilan : journal relu, 2–3 fonctions codées si le journal l'exige (§ 4.2)", "Version usine 2.1"],
    ["S12", "Bilan trimestriel : chiffres réels, plan v2.1 du document", "Décision : continuer, ajuster ou pivoter"],
  ], [1, 5.4, 3.2]),
);

// ---------------------------------------------------------------- 11
C.push(
  H1("11. Limites (à lire avant de commencer)"),
  table(["Limite", "Ce que ça veut dire", "Parade"], [
    ["Matériel", "Rendu sur le processeur : environ 1 s par image en 1080p pour une scène chargée ; une vidéo longue de 10 min peut demander plusieurs heures", "Rendus la nuit, demi-résolution pour vérifier, version Windows native, plans légers"],
    ["Logiciel jeune", "EffectCraft a moins d'un mois (1er commit le 1er octobre 2026) : 28 gênes déjà notées, d'autres viendront", "Journal, contournements, fork pour l'essentiel, tests avant chaque mise à jour"],
    ["Dessin", "Claude ne dessine pas de sprites de niveau professionnel ; les scripts font des formes simples", "Packs CC0 ou payants, dessin maison sur Pixelorama, IA seulement pour chercher un style"],
    ["Voix", "Pas de synthèse vocale française en local ; une voix de synthèse sonne souvent « robot »", "Ta voix au téléphone, ou un service externe payant (clé API à toi)"],
    ["Humour et goût", "Claude propose des gags, mais c'est toi qui sais ce qui fait rire ton public", "Validation systématique du script, tests sur de vrais spectateurs"],
    ["Droits", "Aucune image, musique ou personnage protégé (dont les 4 références du dossier pixel)", "Manifeste des licences obligatoire, « pas de licence, pas d'usage »"],
    ["Plateformes", "Règles de monétisation qui changent (contenu non authentique, changement YouTube du 01/02/2027), algorithmes imprévisibles", "Plusieurs plateformes, revenus hors plateformes, vraie valeur dans chaque vidéo"],
    ["Revenus", "Les RPM sont des estimations ; 500 $/mois n'est pas garanti, même avec un bon rythme", "Jalons trimestriels, décision de pivot au mois 6 et au mois 12"],
    ["Temps humain", "Validation, voix, dessin et publication restent à toi : 5 à 8 h par semaine au minimum", "Lots de production (un jour script, un jour voix, un jour validation)"],
    ["Publication automatique", "Claude ne publie rien sans ton accord ; une API demande des identifiants et une configuration", "Publication manuelle au début ; automatisation éventuelle en v2.2"],
    ["Administratif", "Les revenus doivent être déclarés (micro-entreprise en France, par exemple)", "S'informer avant le premier paiement"],
  ], [1.8, 4.2, 3.6]),
);

// ---------------------------------------------------------------- 12
C.push(
  H1("12. Versionnage"),
  H2("12.1 Ce document"),
  P("Chaque mise à jour du plan reçoit un numéro (2.0, 2.1…), une date et une ligne dans le tableau de la page de garde. On ne réécrit pas l'historique : une décision changée est notée avec sa raison."),
  H2("12.2 L'usine (numéros de version)"),
  table(["Version", "Contenu", "Quand"], [
    ["1.0.0", "Bible v1, 4 modèles, 12 presets, 10 rapides, 4 recettes, monter.py v1 (état actuel)", "20/10/2026"],
    ["2.0.0", "Assets + licences, DA pixel, découpe des planches, modèles Scène pixel, moteur caméra, monter.py v2", "Semaine 3"],
    ["2.1.0", "Miniatures, textes de publication, corrections tirées du journal", "Semaine 8"],
    ["2.2.0", "Tableau de stats, publication assistée (si utile)", "Mois 4"],
    ["3.0.0", "Fork EffectCraft avec les fonctions validées par le journal (§ 4.2)", "Quand le journal l'exige"],
  ], [1.2, 6.2, 2]),
  GAP(),
  P("**Règle de numérotation** : le dernier chiffre pour une correction, le chiffre du milieu pour un ajout qui ne casse rien, le premier chiffre quand les anciens épisodes doivent être adaptés (par exemple un nouveau format d'episode.toml)."),
  H2("12.3 Comment on versionne en pratique"),
  B("**Git sur ~/videos** : tout ce qui est texte et outil (bible, outils, modèles, presets, recettes, episode.toml), avec une étiquette par version (v1.0.0, v2.0.0) et un fichier **CHANGELOG.md**."),
  B("**Hors git** : les rendus .mp4 et les gros assets (copie Bureau + sauvegarde externe ou cloud)."),
  B("**Projets** : Fichier ▸ Incrémenter et enregistrer avant toute grosse retouche ; monter.py garde une copie datée avant d'écraser."),
  B("**EffectCraft** : la version utilisée est notée dans le CHANGELOG (aujourd'hui 0.13.0). Avant de passer à une nouvelle version, on remonte les 4 épisodes d'exemple : on ne bascule que si rien ne casse."),
  B("**Recettes Claude** : versionnées avec l'usine (copie dans ~/videos/recettes/, installée dans ~/.claude/skills/)."),
);

// ---------------------------------------------------------------- 13
C.push(
  H1("13. Risques et parades"),
  table(["Risque", "Probabilité", "Impact", "Parade"], [
    ["Démonétisation pour contenu répétitif", "Moyenne", "Fort", "Idée et plans uniques par vidéo, pas de vidéos « clones »"],
    ["Peu de vues au départ", "Forte", "Moyen", "Rythme tenu 12 semaines avant de juger, A/B des miniatures, Shorts pour la découverte"],
    ["Rendus trop lents", "Forte", "Moyen", "Plans légers, rendus la nuit, mouvements rapides plutôt que presets"],
    ["Bug bloquant d'EffectCraft", "Moyenne", "Moyen", "Journal, contournement, signalement au projet, correctif dans le fork"],
    ["Problème de droits sur un asset", "Faible si on suit la règle", "Fort", "Manifeste des licences, références séparées"],
    ["Épuisement (trop de vidéos)", "Moyenne", "Fort", "Production par lots, rythme réduit possible, l'usine fait le répétitif"],
    ["Objectif financier non atteint au mois 12", "Moyenne", "Moyen", "Bilans aux mois 6 et 12, pivot (niche, format, plus de boutique ou de commandes)"],
  ], [3, 1.4, 1.2, 4]),
);

// ---------------------------------------------------------------- 14
C.push(
  H1("14. À faire cette semaine"),
  N("Valider ce plan (ou dire quoi changer), et choisir la série de lancement (proposition : « La science en pixel » + « Gags pixel »).", "num3"),
  N("Créer le dépôt git ~/videos, la bibliothèque assets/ et le dossier références/ (Claude).", "num3"),
  N("Choisir la source du premier personnage : dessin maison sur Pixelorama, pack CC0, ou pack payant.", "num3"),
  N("Construire decouper_planche.py et le modèle « Scène pixel 16:9 » (Claude).", "num3"),
  N("Première scène test de 15 s avec 3 mouvements de caméra.", "num3"),
  NOTE("Prochaine étape : dis à Claude « on attaque la semaine 1 de l'usine 2.0 »."),
  H2("Sources"),
  B("YouTube, page d'aide officielle « Présentation du Programme Partenaire YouTube et conditions d'éligibilité » (support.google.com/youtube/answer/72851), consultée le 21/10/2026."),
  B("TechCrunch, « YouTube clarifies policies around AI slop and upsetting videos », 20/07/2026."),
  B("AIR Media-Tech, données de RPM Shorts 2026 (274 chaînes) et guide des conditions YPP 2026 (air.io)."),
  B("Guides Creator Rewards TikTok 2026 (ttcalculator.net, metricool.com) : conditions concordantes, chiffres de rémunération contradictoires."),
);

const doc = new Document({
  creator: "ico-vid", title: "ico-vid · Usine 2.0 — plan v2.0", description: "Plan de construction de l'usine vidéo pixel",
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
      ...["num", "num2", "num3"].map((r) => ({ reference: r, levels: [
        { level: 0, format: LevelFormat.DECIMAL, text: "%1.", alignment: AlignmentType.LEFT, style: { paragraph: { indent: { left: 500, hanging: 300 } } } }] })),
    ],
  },
  sections: [{
    properties: { page: { size: { width: 11906, height: 16838 }, margin: { top: 1134, bottom: 1134, left: 1134, right: 1134 } } },
    footers: { default: new Footer({ children: [new Paragraph({ alignment: AlignmentType.RIGHT, children: [
      new TextRun({ text: "ico-vid · Usine 2.0 · plan v2.0 · page ", color: GREY, size: 16 }),
      new TextRun({ children: [PageNumber.CURRENT], color: GREY, size: 16 })] })] }) },
    children: C,
  }],
});

Packer.toBuffer(doc).then((buf) => { fs.writeFileSync(process.argv[2], buf); console.log("écrit", process.argv[2], buf.length, "octets"); });
