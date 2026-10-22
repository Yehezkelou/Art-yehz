-- ico-vid : poses « sort » de Tim pour pixel-01-sort (32x32, palette ico-pixel-32 indexee).
-- Part de tim.aseprite (construit par tim.lua) : les images de Tim sont reprises telles quelles,
-- on ajoute un baton (calque a part) et deux retouches d'yeux. 9 images :
--   1-4 repos (baton plante) · 5-6 charge (baton leve, gemme qui clignote) · 7 lancer
--   8 regarde en haut · 9 sonne (yeux fermes)
-- lance par Claude :
--   Aseprite.exe -b --script-param planche=<chemin>/tim-sort-planche.png --script tim-sort.lua

local BASE   = app.fs.joinPath(os.getenv("USERPROFILE") or os.getenv("HOME"), "ico-pixel", "persos", "tim")
local SOURCE = app.fs.joinPath(BASE, "tim.aseprite")
local SORTIE = app.fs.joinPath(BASE, "tim-sort.aseprite")
local PLANCHE = app.params["planche"]

if not app.fs.isFile(SOURCE) then error("lancer d'abord tim.lua : " .. SOURCE .. " introuvable") end
local src = app.open(SOURCE)

-- index de la palette ico-pixel-32 (0 = transparent)
local K, W, S = 2, 8, 28                      -- contour, blanc des yeux, peau (comme tim.lua)
local BOIS, GEMME_BLEUE, OR, OR_CLAIR, CREME = 26, 10, 19, 20, 8

-- baton : liste de pixels { x, y, couleur } dans la case de 32 (origine 0,0)
local function vertical(x, y1, y2, gemme)
  local p = {}
  for y = y1, y2 do p[#p + 1] = { x, y, BOIS } end
  for _, d in ipairs({ { 0, 0 }, { 1, 0 }, { 0, 1 }, { 1, 1 } }) do
    p[#p + 1] = { x + d[1], y1 - 2 + d[2], gemme }
  end
  return p
end
local function diagonal(gemme)
  local p = {}
  for i = 0, 6 do p[#p + 1] = { 22 + i, 22 - i, BOIS } end
  for _, d in ipairs({ { 0, 0 }, { 1, 0 }, { 0, 1 }, { 1, 1 } }) do
    p[#p + 1] = { 29 + d[1], 14 + d[2], gemme }
  end
  return p
end

local BATON = {
  plante = vertical(22, 15, 27, GEMME_BLEUE),
  leveA  = vertical(22, 3, 24, OR),
  leveB  = vertical(22, 3, 24, OR_CLAIR),
  lance  = diagonal(CREME),
}

-- yeux vers le haut (image de repos 1, buste non descendu) : une pupille d'1 px dans le coin haut
local YEUX_HAUT = {
  { 12, 10, W }, { 13, 10, K }, { 12, 11, W }, { 13, 11, W },
  { 18, 10, W }, { 19, 10, K }, { 18, 11, W }, { 19, 11, W },
}

-- une image = { image source de Tim, baton, retouches, duree }
local IMAGES = {
  { 1, "plante", nil, 0.40 }, { 2, "plante", nil, 0.30 }, { 3, "plante", nil, 0.40 }, { 4, "plante", nil, 0.15 },
  { 1, "leveA", nil, 0.17 }, { 1, "leveB", nil, 0.17 },
  { 1, "lance", nil, 0.50 },
  { 1, "plante", YEUX_HAUT, 0.80 },
  { 4, "plante", nil, 1.00 },
}
local ETIQUETTES = { { "repos", 1, 4 }, { "charge", 5, 6 }, { "lancer", 7, 7 }, { "regarde-haut", 8, 8 }, { "sonne", 9, 9 } }

----------------------------------------------------------------------
-- controle : les yeux sont bien la ou on les retouche (sinon tim.lua a change)
do
  local img = Image(src.spec); img:drawSprite(src, 1)
  for _, p in ipairs({ { 13, 10 }, { 13, 11 }, { 19, 10 }, { 19, 11 } }) do
    if img:getPixel(p[1], p[2]) ~= K then error("pupille attendue en " .. p[1] .. "," .. p[2]) end
  end
end

local pal = src.palettes[1]
local spr = Sprite(32, 32, ColorMode.INDEXED)
spr:setPalette(pal)
spr.transparentColor = 0
spr.layers[1].name = "tim"
local lbaton = spr:newLayer(); lbaton.name = "baton"
for i = 2, #IMAGES do spr:newEmptyFrame() end

local planche = Image(32 * #IMAGES, 32, ColorMode.INDEXED)

for f, def in ipairs(IMAGES) do
  local corps = Image(src.spec); corps:drawSprite(src, def[1])
  if def[3] then for _, p in ipairs(def[3]) do corps:drawPixel(p[1], p[2], p[3]) end end
  local baton = Image(32, 32, ColorMode.INDEXED)
  for _, p in ipairs(BATON[def[2]]) do baton:drawPixel(p[1], p[2], p[3]) end
  spr:newCel(spr.layers[1], f, corps, Point(0, 0))
  spr:newCel(lbaton, f, baton, Point(0, 0))
  spr.frames[f].duration = def[4]
  for y = 0, 31 do
    for x = 0, 31 do
      local c = baton:getPixel(x, y)
      if c == 0 then c = corps:getPixel(x, y) end
      if c ~= 0 then planche:drawPixel(32 * (f - 1) + x, y, c) end
    end
  end
end

for _, e in ipairs(ETIQUETTES) do
  local t = spr:newTag(e[2], e[3]); t.name = e[1]; t.aniDir = AniDir.FORWARD
end

src:close()
spr:saveAs(SORTIE)
if PLANCHE and PLANCHE ~= "" then planche:saveAs{ filename = PLANCHE, palette = spr.palettes[1] } end
print("tim-sort.aseprite : " .. #spr.layers .. " calques, " .. #spr.frames .. " images, "
      .. #spr.tags .. " etiquettes" .. (PLANCHE and (" ; planche " .. PLANCHE) or ""))
