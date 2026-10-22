-- ico-vid : poses « potion » de Tim pour pixel-02-potion (32x32, palette ico-pixel-32 indexee).
-- Part de tim.aseprite (construit par tim.lua) : image de repos 1 reprise telle quelle, avec des
-- retouches pixel par pixel. 4 images :
--   1-2 fouille (main dans la poche, puis qui en ressort) · 3 tend (bras tendu vers la droite)
--   4 regarde en haut (sans baton)
-- lance par Claude :
--   Aseprite.exe -b --script-param planche=<chemin>/tim-potion-planche.png --script tim-potion.lua

local BASE   = app.fs.joinPath(os.getenv("USERPROFILE") or os.getenv("HOME"), "ico-pixel", "persos", "tim")
local SOURCE = app.fs.joinPath(BASE, "tim.aseprite")
local SORTIE = app.fs.joinPath(BASE, "tim-potion.aseprite")
local PLANCHE = app.params["planche"]

if not app.fs.isFile(SOURCE) then error("lancer d'abord tim.lua : " .. SOURCE .. " introuvable") end
local src = app.open(SOURCE)

-- index de la palette ico-pixel-32 (0 = transparent), comme tim.lua
local K, W, S, T, t = 2, 8, 28, 15, 14         -- contour, blanc des yeux, peau, tunique, tunique ombre

-- main droite au repos : (20, 21), entre deux contours (19 et 21)
local MAIN_DANS_POCHE = { { 20, 21, t }, { 21, 22, K }, { 21, 23, K } }
local MAIN_SORT       = { { 20, 21, t }, { 21, 21, K }, { 22, 21, S }, { 22, 20, K }, { 23, 21, K }, { 22, 22, K } }
-- bras tendu a hauteur d'epaule (lignes 17-19), la main en (25, 18) ; la miette se pose en (27, 18)
local BRAS_TENDU = {
  { 20, 21, K }, { 21, 21, 0 }, { 21, 18, T },
  { 22, 17, K }, { 23, 17, K }, { 24, 17, K }, { 25, 17, K },
  { 22, 18, T }, { 23, 18, T }, { 24, 18, T }, { 25, 18, S }, { 26, 18, K },
  { 22, 19, K }, { 23, 19, K }, { 24, 19, K }, { 25, 19, K },
}
-- yeux vers le haut (comme tim-sort.lua) : une pupille d'1 px dans le coin haut
local YEUX_HAUT = {
  { 12, 10, W }, { 13, 10, K }, { 12, 11, W }, { 13, 11, W },
  { 18, 10, W }, { 19, 10, K }, { 18, 11, W }, { 19, 11, W },
}

-- une image = { retouches, duree }
local IMAGES = {
  { MAIN_DANS_POCHE, 0.17 }, { MAIN_SORT, 0.17 },
  { BRAS_TENDU, 1.00 },
  { YEUX_HAUT, 0.80 },
}
local ETIQUETTES = { { "fouille", 1, 2 }, { "tend", 3, 3 }, { "regarde-haut", 4, 4 } }

----------------------------------------------------------------------
-- controle : la main et les yeux sont bien la ou on les retouche (sinon tim.lua a change)
do
  local img = Image(src.spec); img:drawSprite(src, 1)
  if img:getPixel(20, 21) ~= S then error("main droite attendue en 20,21") end
  for _, p in ipairs({ { 13, 10 }, { 13, 11 }, { 19, 10 }, { 19, 11 } }) do
    if img:getPixel(p[1], p[2]) ~= K then error("pupille attendue en " .. p[1] .. "," .. p[2]) end
  end
end

local spr = Sprite(32, 32, ColorMode.INDEXED)
spr:setPalette(src.palettes[1])
spr.transparentColor = 0
spr.layers[1].name = "tim"
for i = 2, #IMAGES do spr:newEmptyFrame() end

local planche = Image(32 * #IMAGES, 32, ColorMode.INDEXED)

for f, def in ipairs(IMAGES) do
  local corps = Image(src.spec); corps:drawSprite(src, 1)
  for _, p in ipairs(def[1]) do corps:drawPixel(p[1], p[2], p[3]) end
  spr:newCel(spr.layers[1], f, corps, Point(0, 0))
  spr.frames[f].duration = def[2]
  for y = 0, 31 do
    for x = 0, 31 do
      local c = corps:getPixel(x, y)
      if c ~= 0 then planche:drawPixel(32 * (f - 1) + x, y, c) end
    end
  end
end

for _, e in ipairs(ETIQUETTES) do
  local tg = spr:newTag(e[2], e[3]); tg.name = e[1]; tg.aniDir = AniDir.FORWARD
end

src:close()
spr:saveAs(SORTIE)
if PLANCHE and PLANCHE ~= "" then planche:saveAs{ filename = PLANCHE, palette = spr.palettes[1] } end
print("tim-potion.aseprite : " .. #spr.frames .. " images, " .. #spr.tags .. " etiquettes")
