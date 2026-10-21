-- ico-vid : construit tim.aseprite (32x32, palette ico-pixel-32 indexee,
-- 4 calques : vetements / peau / cheveux / contour, 2 actions etiquetees)
-- lance par Claude : Aseprite.exe -b --script tim.lua

local SORTIE = "C:\\Users\\Yehezkelou\\ico-pixel\\persos\\tim\\tim.aseprite"

-- palette ico-pixel-32 (index 0 = transparent, puis 8 rampes de 4)
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

-- lettre du dessin -> { index dans la palette, calque }
local C = {
  K = { 2,  "contour"   },
  H = { 17, "cheveux"   }, h = { 18, "cheveux" },
  S = { 28, "peau"      }, s = { 27, "peau"    }, r = { 24, "peau" }, W = { 8, "peau" },
  R = { 23, "vetements" },
  T = { 15, "vetements" }, t = { 14, "vetements" },
  B = { 26, "vetements" },
  P = { 10, "vetements" }, p = { 9,  "vetements" },
  O = { 25, "vetements" },
}

-- haut du corps (16 px de large)
local HAUT = {
  ".....KKKKKK.....",
  "...KKHHHHHHKK...",
  "..KHHhHHHHHHHK..",
  ".KHHhHHHHHHHHHK.",
  ".KHHHHHHHHHHHHK.",
  ".KHSSHHHHSSHHSK.",
  ".KSSSSSSSSSSSSK.",
  ".KSSWKSSSSWKSSK.",
  ".KSSWKSSSSWKSSK.",
  ".KSrSSSSSSSSrSK.",
  ".KSSSSSKKSSSSSK.",
  "..KsSSSSSSSSsK..",
  "...KKKKKKKKKK...",
  "....KRRRRRRK....",
  "...KTTRRRRTTK...",
  "..KTTTTRRTTTTK..",
  "..KtTTTTTTTTtK..",
  "..KtTTTTTTTTtK..",
  "..KSKBBBBBBKSK..",
  "...KTTTTTTTTK...",
  "...KtTTTTTTtK...",
}
local YEUX_FERMES = { ".KSSSSSSSSSSSSK.", ".KSKKSSSSSKKSSK." }  -- remplacent les lignes 8 et 9

local JAMBES = {
  neutre = { "...KPPPKKPPPK...", "...KPPPKKPPPK...", "...KpPPKKpPPK...", "..KOOOOKKOOOOK..", "..KKKKKKKKKKKK.." },
  gauche = { "...KPPPKKPPPK...", "...KpPPKKPPPK...", "..KOOOOKKpPPK...", "..KKKKKKKOOOOK..", "........KKKKKK.." },
  droite = { "...KPPPKKPPPK...", "...KPPPKKpPPK...", "...KpPPKKOOOOK..", "..KOOOOKKKKKKK..", "..KKKKKK........" },
}
local SOL = 28   -- derniere ligne des pieds dans la case de 32

-- une image = { jambes, cligne, respire }
local IMAGES = {
  { "neutre", false, 0 }, { "neutre", false, 1 }, { "neutre", false, 0 }, { "neutre", true,  0 },  -- repos
  { "gauche", false, 0 }, { "neutre", false, 1 }, { "droite", false, 0 }, { "neutre", false, 1 },  -- marche
}
local DUREES = { 0.40, 0.30, 0.40, 0.15, 0.12, 0.12, 0.12, 0.12 }
local ETIQUETTES = { { "repos", 1, 4 }, { "marche", 5, 8 } }

----------------------------------------------------------------------
local spr = Sprite(32, 32, ColorMode.INDEXED)

local pal = Palette(#RAMPES + 1)
pal:setColor(0, Color{ r = 0, g = 0, b = 0, a = 0 })          -- transparent
for i, hex in ipairs(RAMPES) do
  pal:setColor(i, Color{ r = tonumber(hex:sub(1, 2), 16),
                         g = tonumber(hex:sub(3, 4), 16),
                         b = tonumber(hex:sub(5, 6), 16) })
end
spr:setPalette(pal)
spr.transparentColor = 0

-- calques, du bas vers le haut
local NOMS = { "vetements", "peau", "cheveux", "contour" }
local calque = {}
spr.layers[1].name = NOMS[1]
calque[NOMS[1]] = spr.layers[1]
for i = 2, #NOMS do
  local l = spr:newLayer()
  l.name = NOMS[i]
  calque[NOMS[i]] = l
end

for i = 2, #IMAGES do spr:newEmptyFrame() end

for f, def in ipairs(IMAGES) do
  local jambes, cligne, respire = def[1], def[2], def[3]

  -- lignes de cette image
  local lignes = {}
  for i, l in ipairs(HAUT) do lignes[i] = l end
  if cligne then lignes[8], lignes[9] = YEUX_FERMES[1], YEUX_FERMES[2] end
  local nhaut = #lignes
  for _, l in ipairs(JAMBES[jambes]) do lignes[#lignes + 1] = l end

  -- une image par calque
  local img = {}
  for _, nom in ipairs(NOMS) do img[nom] = Image(32, 32, ColorMode.INDEXED) end

  local haut = SOL - #lignes + 1
  for y, ligne in ipairs(lignes) do
    local yy = haut + y - 1
    if y <= nhaut then yy = yy + respire end   -- le buste descend d'1 px
    for x = 1, 16 do
      local c = ligne:sub(x, x)
      if c ~= "." then
        local def2 = C[c]
        if not def2 then error("lettre inconnue : " .. c) end
        img[def2[2]]:drawPixel(8 + x - 1, yy, def2[1])
      end
    end
  end

  for _, nom in ipairs(NOMS) do spr:newCel(calque[nom], f, img[nom], Point(0, 0)) end
  spr.frames[f].duration = DUREES[f]
end

for _, e in ipairs(ETIQUETTES) do
  local t = spr:newTag(e[2], e[3])
  t.name = e[1]
  t.aniDir = AniDir.FORWARD
end

spr:saveAs(SORTIE)
print("tim.aseprite : " .. #spr.layers .. " calques, " .. #spr.frames .. " images, "
      .. #spr.tags .. " etiquettes, palette de " .. #spr.palettes[1] .. " couleurs")
