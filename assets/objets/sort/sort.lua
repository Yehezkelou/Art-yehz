-- ico-vid : effets du « sort rate » (pixel-01-sort) : etincelles, boule de feu, poule.
-- Cases de 16x16, palette ico-pixel-32 indexee, 7 images :
--   1-3 etincelle (3 tailles) · 4-5 boule de feu (2 flammes) · 6 poule qui tombe · 7 poule assise
-- lance par Claude :
--   Aseprite.exe -b --script-param planche=<chemin>/sort-planche.png --script sort.lua

local SORTIE = app.fs.joinPath(os.getenv("USERPROFILE") or os.getenv("HOME"), "ico-pixel", "objets", "sort", "sort.aseprite")
local PLANCHE = app.params["planche"]

-- palette ico-pixel-32 (index 0 = transparent, puis 8 rampes de 4), comme tim.lua
local RAMPES = {
  "0E0D18","1D1B2E","2F2C45","4A4663",  -- nuits et contours
  "6E6A80","9A96A6","C9C4C8","F2EDE4",  -- neutres et creme
  "1F2E5C","3E5BA9","5E8FD6","9CC7F0",  -- bleus
  "1E4D3A","2E7D4F","3FB56B","8FDB86",  -- verts
  "7A4E1E","B9802B","F4C542","FBE58C",  -- ors
  "5A1E2B","9E2F33","E5533D","F59A7A",  -- rouges
  "3B2A22","6B4A35","9C7451","C9A57A",  -- terres
  "3D2550","6B3F87","A066B8","E0A6D9",  -- violets
}

-- lettre du dessin -> index de la palette
local C = {
  K = 2,              -- contour
  W = 8, w = 7,       -- plumes creme, ombre grise
  R = 23,             -- crete rouge
  Y = 19, y = 20,     -- or (bec, pattes), or clair
  o = 22, O = 23,     -- flamme : rouge sombre, rouge
}

local DESSINS = {
  { nom = "etincelle-grande", lignes = {
    "................", "................", "................", "................",
    "................", ".......y........", ".......Y........", ".....yYWYy......",
    ".......Y........", ".......y........", "................", "................",
    "................", "................", "................", "................" } },
  { nom = "etincelle-moyenne", lignes = {
    "................", "................", "................", "................",
    "................", "................", "......Y.Y.......", ".......W........",
    "......Y.Y.......", "................", "................", "................",
    "................", "................", "................", "................" } },
  { nom = "etincelle-petite", lignes = {
    "................", "................", "................", "................",
    "................", "................", "................", ".......W........",
    "................", "................", "................", "................",
    "................", "................", "................", "................" } },
  { nom = "boule-a", lignes = {
    "................", "................", "................", "................",
    "......oooo......", ".....oOOOOo.....", "....oOYYYYOo....", "....oOYyyYOo....",
    "....oOYyyYOo....", "....oOYYYYOo....", ".....oOOOOo.....", "......oooo......",
    "................", "................", "................", "................" } },
  { nom = "boule-b", lignes = {
    "................", "................", "................", ".......o........",
    ".....oOoOo......", "....oOOOOOo.....", "....oOYYYYOo....", "...oOYyyyYOo....",
    "....oOYyyYOo....", "....oOYYYYOo....", ".....oOOOOo.....", "......oooo......",
    "................", "................", "................", "................" } },
  { nom = "poule-chute", lignes = {
    ".K...........K..", "KWK...RR....KWK.", "KWWK.RRR...KWWK.", ".KWWKKKKK.KWWK..",
    "..KWKWWWWKWWK...", "..YKWKWWWWWK....", "..YYWWWWWWWK....", "...KWWWWWWWWK...",
    "...KWWwWWWwWK...", "...KWWwwwwwWK...", "....KWWWWWWK....", ".....KKKKKK.....",
    "......Y..Y......", "......Y..Y......", "................", "................" } },
  { nom = "poule-assise", lignes = {
    "................", "......RR........", ".....RRR........", "....KKKKK.......",
    "...KWWWWWK......", "..YKWKWWWWK.....", "..YYWWWWWWWK....", "...KWWWWWWWWKK..",
    "...KWWWWWWWWWWK.", "...KWWwWWWWwWWK.", "...KWWwwwwwwWK..", "....KWWWWWWWK...",
    ".....KKKKKKK....", "......Y...Y.....", ".....YY..YY.....", "................" } },
}

----------------------------------------------------------------------
local spr = Sprite(16, 16, ColorMode.INDEXED)
local pal = Palette(#RAMPES + 1)
pal:setColor(0, Color{ r = 0, g = 0, b = 0, a = 0 })
for i, hex in ipairs(RAMPES) do
  pal:setColor(i, Color{ r = tonumber(hex:sub(1, 2), 16), g = tonumber(hex:sub(3, 4), 16), b = tonumber(hex:sub(5, 6), 16) })
end
spr:setPalette(pal)
spr.transparentColor = 0
spr.layers[1].name = "effets"
for i = 2, #DESSINS do spr:newEmptyFrame() end

local planche = Image(16 * #DESSINS, 16, ColorMode.INDEXED)
for f, d in ipairs(DESSINS) do
  if #d.lignes ~= 16 then error(d.nom .. " : " .. #d.lignes .. " lignes au lieu de 16") end
  local img = Image(16, 16, ColorMode.INDEXED)
  for y, ligne in ipairs(d.lignes) do
    if #ligne ~= 16 then error(d.nom .. " ligne " .. y .. " : " .. #ligne .. " colonnes") end
    for x = 1, 16 do
      local c = ligne:sub(x, x)
      if c ~= "." then
        local idx = C[c]
        if not idx then error("lettre inconnue : " .. c) end
        img:drawPixel(x - 1, y - 1, idx)
        planche:drawPixel(16 * (f - 1) + x - 1, y - 1, idx)
      end
    end
  end
  spr:newCel(spr.layers[1], f, img, Point(0, 0))
  spr.frames[f].duration = 0.1
  local t = spr:newTag(f, f); t.name = d.nom
end

app.fs.makeAllDirectories(app.fs.filePath(SORTIE))
spr:saveAs(SORTIE)
if PLANCHE and PLANCHE ~= "" then planche:saveAs{ filename = PLANCHE, palette = pal } end
print("sort.aseprite : " .. #spr.frames .. " images, " .. #spr.tags .. " etiquettes")
