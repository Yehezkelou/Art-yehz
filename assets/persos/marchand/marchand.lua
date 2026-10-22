-- ico-vid : le marchand (gobelin en capuche, regarde a gauche) pour pixel-02-potion.
-- 32x32, palette ico-pixel-32 indexee. Il se tient derriere un comptoir : seules les lignes 0-27
-- sont visibles (le haut du comptoir est a la ligne 28). 5 images :
--   1 repos (mains sur le comptoir) · 2-3 caisse (main droite qui tape, haut / bas)
--   4 yeux ronds (bouche en O) · 5 prend (main gauche tendue vers Tim)
-- lance par Claude :
--   Aseprite.exe -b --script-param planche=<chemin>/marchand-planche.png --script marchand.lua

local SORTIE = app.fs.joinPath(os.getenv("USERPROFILE") or os.getenv("HOME"), "ico-pixel", "persos", "marchand", "marchand.aseprite")
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
  V = 30, v = 29,     -- capuche et robe violettes, ombre
  G = 15, g = 14,     -- peau verte, ombre (nez)
  W = 8,              -- blanc des yeux
  Y = 19,             -- boutons dores
}

-- corps de base (les lignes plus courtes que 32 sont completees par du vide a droite)
local CORPS = {
  "",
  "",
  "............KKKKKKKK",
  "..........KKVVVVVVVVKK",
  ".........KVVVVVVVVVVVVK",
  "........KVVVVVVVVVVVVVVK",
  "........KVKKKKKKKKKKKKVK",
  "....KK..KVGGGGGGGGGGGGVK..KK",
  "...KGGGKKVGGGGGGGGGGGGVKKGGGK",
  "..KGGGGGKVGWWWGGGWWWGGVKGGGGGK",
  "...KKGGGKVGKWWGGGKWWGGVKGGGKK",
  ".....KKKKVGKWWGGGKWWGGVKKKK",
  "........KVGGGGGGGGGGGGVK",
  "........KVGggGGGGGGGGGVK",
  "........KVGGGKKKKKGGGGVK",
  "........KVKGGGGGGGGGGKVK",
  "........KVVKKKKKKKKKKVVK",
  "......KvVVVVVVVVVVVVVVVvK",
  ".....KvVVVVVVVVVVVVVVVVVvK",
  ".....KvVVVVVVVVYVVVVVVVVvK",
  ".....KvVVVVVVVVVVVVVVVVVvK",
  ".....KvVVVVVVVVVVVVVVVVVvK",
  ".....KvVVVVVVVVYVVVVVVVVvK",
  ".....KvVVVVVVVVVVVVVVVVVvK",
  ".....KvVVVVVVVVVVVVVVVVVvK",
  ".....KvVVVVVVVVYVVVVVVVVvK",
  ".....KvVVVVVVVVVVVVVVVVVvK",
  ".....KvVVVVVVVVVVVVVVVVVvK",
  ".....KvVVVVVVVVVVVVVVVVVvK",
  ".....KvVVVVVVVVVVVVVVVVVvK",
  ".....KvVVVVVVVVVVVVVVVVVvK",
  ".....KvVVVVVVVVVVVVVVVVVvK",
}

-- retouches : { x, y, lettre } (x, y depuis 0 ; "." = vide)
local function main(x)                         -- une main posee sur le comptoir (lignes 25-27)
  return { { x, 25, "K" }, { x + 1, 25, "K" }, { x - 1, 26, "K" }, { x, 26, "G" }, { x + 1, 26, "G" },
           { x + 2, 26, "K" }, { x - 1, 27, "K" }, { x, 27, "G" }, { x + 1, 27, "G" }, { x + 2, 27, "K" } }
end
local function ajoute(...)
  local r = {}
  for _, l in ipairs({ ... }) do for _, p in ipairs(l) do r[#r + 1] = p end end
  return r
end
local function bras_droit(y)                   -- bras vers la caisse (a droite), main en x = 29-30
  return { { 25, y - 1, "K" }, { 26, y - 1, "K" }, { 27, y - 1, "K" }, { 28, y - 1, "K" }, { 29, y - 1, "K" },
           { 26, y, "V" }, { 27, y, "V" }, { 28, y, "K" }, { 29, y, "G" }, { 30, y, "G" }, { 31, y, "K" },
           { 25, y + 1, "K" }, { 26, y + 1, "K" }, { 27, y + 1, "K" }, { 28, y + 1, "K" }, { 29, y + 1, "G" },
           { 30, y + 1, "G" }, { 31, y + 1, "K" }, { 29, y + 2, "K" }, { 30, y + 2, "K" } }
end
local BRAS_GAUCHE = {                          -- tendu vers Tim, la main au bord gauche (x = 1-2, y = 24-25)
  { 1, 23, "K" }, { 2, 23, "K" }, { 3, 23, "K" }, { 4, 23, "K" }, { 5, 23, "K" },
  { 0, 24, "K" }, { 1, 24, "G" }, { 2, 24, "G" }, { 3, 24, "K" }, { 4, 24, "V" }, { 5, 24, "V" },
  { 0, 25, "K" }, { 1, 25, "G" }, { 2, 25, "G" }, { 3, 25, "K" }, { 4, 25, "K" }, { 5, 25, "K" },
  { 1, 26, "K" }, { 2, 26, "K" },
}
local YEUX_RONDS = {
  { 11, 9, "W" }, { 12, 9, "W" }, { 13, 9, "W" }, { 17, 9, "W" }, { 18, 9, "W" }, { 19, 9, "W" },
  { 11, 10, "W" }, { 12, 10, "K" }, { 13, 10, "W" }, { 17, 10, "W" }, { 18, 10, "K" }, { 19, 10, "W" },
  { 11, 11, "W" }, { 12, 11, "W" }, { 13, 11, "W" }, { 17, 11, "W" }, { 18, 11, "W" }, { 19, 11, "W" },
  { 10, 8, "K" }, { 11, 8, "K" }, { 12, 8, "K" }, { 13, 8, "K" }, { 14, 8, "K" },
  { 16, 8, "K" }, { 17, 8, "K" }, { 18, 8, "K" }, { 19, 8, "K" }, { 20, 8, "K" },
  -- bouche en O (lignes 14-15)
  { 13, 14, "G" }, { 14, 14, "K" }, { 15, 14, "K" }, { 16, 14, "K" }, { 17, 14, "G" },
  { 14, 15, "K" }, { 15, 15, "v" }, { 16, 15, "K" },
}

local MAINS = ajoute(main(7), main(22))
local IMAGES = {
  { "repos",      MAINS,                            0.40 },
  { "caisse-a",   ajoute(main(7), bras_droit(23)), 0.17 },
  { "caisse-b",   ajoute(main(7), bras_droit(25)), 0.17 },
  { "yeux-ronds", ajoute(MAINS, YEUX_RONDS),        0.80 },
  { "prend",      ajoute(main(22), BRAS_GAUCHE),    0.40 },
}

----------------------------------------------------------------------
local spr = Sprite(32, 32, ColorMode.INDEXED)
local pal = Palette(#RAMPES + 1)
pal:setColor(0, Color{ r = 0, g = 0, b = 0, a = 0 })
for i, hex in ipairs(RAMPES) do
  pal:setColor(i, Color{ r = tonumber(hex:sub(1, 2), 16), g = tonumber(hex:sub(3, 4), 16), b = tonumber(hex:sub(5, 6), 16) })
end
spr:setPalette(pal)
spr.transparentColor = 0
spr.layers[1].name = "marchand"
for i = 2, #IMAGES do spr:newEmptyFrame() end

local function couleur(c)
  if c == "." then return 0 end
  local idx = C[c]
  if not idx then error("lettre inconnue : " .. c) end
  return idx
end

if #CORPS ~= 32 then error("CORPS : " .. #CORPS .. " lignes au lieu de 32") end
local planche = Image(32 * #IMAGES, 32, ColorMode.INDEXED)
for f, def in ipairs(IMAGES) do
  local img = Image(32, 32, ColorMode.INDEXED)
  for y, ligne in ipairs(CORPS) do
    if #ligne > 32 then error("ligne " .. y .. " : " .. #ligne .. " colonnes") end
    for x = 1, #ligne do img:drawPixel(x - 1, y - 1, couleur(ligne:sub(x, x))) end
  end
  for _, p in ipairs(def[2]) do img:drawPixel(p[1], p[2], couleur(p[3])) end
  spr:newCel(spr.layers[1], f, img, Point(0, 0))
  spr.frames[f].duration = def[3]
  local tg = spr:newTag(f, f); tg.name = def[1]
  for y = 0, 31 do for x = 0, 31 do
    local c = img:getPixel(x, y)
    if c ~= 0 then planche:drawPixel(32 * (f - 1) + x, y, c) end
  end end
end

app.fs.makeAllDirectories(app.fs.filePath(SORTIE))
spr:saveAs(SORTIE)
if PLANCHE and PLANCHE ~= "" then planche:saveAs{ filename = PLANCHE, palette = pal } end
print("marchand.aseprite : " .. #spr.frames .. " images, " .. #spr.tags .. " etiquettes")
