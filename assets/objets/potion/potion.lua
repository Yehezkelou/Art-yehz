-- ico-vid : la boutique de pixel-02-potion (palette ico-pixel-32 indexee). Trois planches :
--   potion-planche.png   cases 16x16 : potion bleue, potion rouge, caisse, piece
--   chiffres-planche.png cases 4x6   : chiffres 3x5 « 0 » a « 9 » puis la virgule (1 px de large)
--   comptoir.png         80x10       : comptoir en bois (assez bas pour que Tim tende le bras par-dessus)
-- lance par Claude :
--   Aseprite.exe -b --script-param dossier=<chemin>/assets/objets/potion --script potion.lua

local SORTIE = app.fs.joinPath(os.getenv("USERPROFILE") or os.getenv("HOME"), "ico-pixel", "objets", "potion", "potion.aseprite")
local DOSSIER = app.params["dossier"]

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

local COMMUN = { K = 2, D = 3, W = 8, w = 7, B = 27, O = 18, Y = 19 }
local function lettres(extra)
  local c = {}
  for k, v in pairs(COMMUN) do c[k] = v end
  for k, v in pairs(extra or {}) do c[k] = v end
  return c
end

local FLACON = {
  "", "",
  "", "......KKKK", "......KBBK", "......KKKK", "......KwwK", ".....KwwwwK",
  "....KwPPPPPK", "...KwPPPPPPPK", "...KWPPPPPPPK", "...KPPPPPPPpK",
  "...KPPPPPPPpK", "....KPPPPPpK", ".....KKKKKK", "",
}
local DESSINS = {
  { nom = "potion-bleue", c = lettres({ P = 11, p = 10 }), lignes = FLACON },
  { nom = "potion-rouge", c = lettres({ P = 23, p = 22 }), lignes = FLACON },
  { nom = "caisse", c = lettres(), lignes = {
    "", "", "", "",
    "......KKKK", "..KKKKKKKKKKKK", "..KYYYYYYYYYYK", "..KYKKKKKKKKYK",
    "..KYKDDDDDDKYK", "..KYKKKKKKKKYK", ".KOOOOOOOOOOOOK", ".KOWOWOWOWOWOOK",
    ".KOOOOOOOOOOOOK", ".KOWOWOWOWOWOOK", ".KOOOOOOOOOOOOK", ".KKKKKKKKKKKKKK" } },
  { nom = "piece", c = lettres(), lignes = { ".KKK.", "KYYOK", "KYWOK", "KOOOK", ".KKK." } },
}

-- chiffres 3x5 (la virgule : 1 colonne, lignes 3-5)
local CHIFFRES = {
  { "KKK", "K.K", "K.K", "K.K", "KKK" }, { ".K.", "KK.", ".K.", ".K.", "KKK" },
  { "KKK", "..K", "KKK", "K..", "KKK" }, { "KKK", "..K", ".KK", "..K", "KKK" },
  { "K.K", "K.K", "KKK", "..K", "..K" }, { "KKK", "K..", "KKK", "..K", "KKK" },
  { "KKK", "K..", "KKK", "K.K", "KKK" }, { "KKK", "..K", "..K", ".K.", ".K." },
  { "KKK", "K.K", "KKK", "K.K", "KKK" }, { "KKK", "K.K", "KKK", "..K", "KKK" },
  { "", "", "", "K", "K", "K" },
}

----------------------------------------------------------------------
local pal = Palette(#RAMPES + 1)
pal:setColor(0, Color{ r = 0, g = 0, b = 0, a = 0 })
for i, hex in ipairs(RAMPES) do
  pal:setColor(i, Color{ r = tonumber(hex:sub(1, 2), 16), g = tonumber(hex:sub(3, 4), 16), b = tonumber(hex:sub(5, 6), 16) })
end

local function dessine(img, ox, oy, lignes, c)
  for y, ligne in ipairs(lignes) do
    for x = 1, #ligne do
      local ch = ligne:sub(x, x)
      if ch ~= "." then
        local idx = c[ch]
        if not idx then error("lettre inconnue : " .. ch) end
        img:drawPixel(ox + x - 1, oy + y - 1, idx)
      end
    end
  end
end

-- objets (un sprite Aseprite, une image par objet)
local spr = Sprite(16, 16, ColorMode.INDEXED)
spr:setPalette(pal)
spr.transparentColor = 0
spr.layers[1].name = "objets"
for i = 2, #DESSINS do spr:newEmptyFrame() end
local planche = Image(16 * #DESSINS, 16, ColorMode.INDEXED)
for f, d in ipairs(DESSINS) do
  if #d.lignes > 16 then error(d.nom .. " : trop de lignes") end
  local img = Image(16, 16, ColorMode.INDEXED)
  dessine(img, 0, 0, d.lignes, d.c)
  dessine(planche, 16 * (f - 1), 0, d.lignes, d.c)
  spr:newCel(spr.layers[1], f, img, Point(0, 0))
  local tg = spr:newTag(f, f); tg.name = d.nom
end
app.fs.makeAllDirectories(app.fs.filePath(SORTIE))
spr:saveAs(SORTIE)

if DOSSIER and DOSSIER ~= "" then
  planche:saveAs{ filename = app.fs.joinPath(DOSSIER, "potion-planche.png"), palette = pal }

  local chiffres = Image(4 * #CHIFFRES, 6, ColorMode.INDEXED)
  for i, g in ipairs(CHIFFRES) do dessine(chiffres, 4 * (i - 1), 0, g, COMMUN) end
  chiffres:saveAs{ filename = app.fs.joinPath(DOSSIER, "chiffres-planche.png"), palette = pal }

  -- comptoir 80x10 : planche du dessus (28 / 27), facade 26 avec une latte sombre (25) tous les 16 px
  local comptoir = Image(80, 10, ColorMode.INDEXED)
  for y = 0, 9 do
    for x = 0, 79 do
      local c = 26
      if x == 0 or x == 79 or y == 0 or y == 3 or y == 9 then c = 2
      elseif y == 1 then c = 28
      elseif y == 2 then c = 27
      elseif x % 16 == 0 then c = 25
      elseif y == 4 then c = 27 end
      comptoir:drawPixel(x, y, c)
    end
  end
  comptoir:saveAs{ filename = app.fs.joinPath(DOSSIER, "comptoir.png"), palette = pal }
end
print("potion.aseprite : " .. #spr.frames .. " objets ; " .. #CHIFFRES .. " chiffres ; comptoir 80x10")
