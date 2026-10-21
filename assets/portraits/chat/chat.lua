-- ico-vid : portrait de chat « monochrome corail », 96x96, construit dans Aseprite
-- 5 calques (fond / oreilles / tete / yeux / moustaches), palette indexee de 18 couleurs.
-- Technique relevee sur une reference (cadrage serre, une seule teinte en 14 valeurs,
-- pas de contour noir, fourrure en traits d'1 px, une seule touche froide) ;
-- le dessin, la pose et la rampe sont les notres.
--   Aseprite.exe -b --script chat.lua

local SORTIE = "C:\\Users\\Yehezkelou\\ico-pixel\\portraits\\chat\\chat.aseprite"
local L = 96
math.randomseed(11)

-- palette : 1..14 = rampe corail (ombre -> lumiere), 15 = fond, 16/17 = reflet froid, 18 = rose
local COULEURS = {
  "210B07","36120B","481910","5A1F16","6B261C","7C2C23","8D332B",
  "9D3A35","AD423F","BE4A4A","CD575A","DD646C","ED737F","FC8393",
  "292524",            -- 15 fond (presque noir, chaud et desature)
  "9CC7F0","5E8FD6",   -- 16/17 reflet de l'oeil : la seule touche froide
  "8C4A4E",            -- 18 interieur des oreilles et nez
}
local NIV = 14         -- la rampe va de 1 a 14
local FOND, FROID1, FROID2, ROSE = 15, 16, 17, 18

-- une grille de niveaux par calque
local NOMS = { "fond", "oreilles", "tete", "yeux", "moustaches" }
local g = {}
for _, n in ipairs(NOMS) do
  g[n] = {}
  for y = 0, L - 1 do g[n][y] = {} end
end

local function mettre(c, x, y, v)
  if x >= 0 and x < L and y >= 0 and y < L then g[c][y][x] = v end
end

local function lire(x, y)   -- niveau du chat (oreilles ou tete) a cet endroit
  if x < 0 or x >= L or y < 0 or y >= L then return nil, nil end
  if g.tete[y][x] then return g.tete[y][x], "tete" end
  if g.oreilles[y][x] then return g.oreilles[y][x], "oreilles" end
  return nil, nil
end

local function eclaircir(x, y, d)
  local v, c = lire(x, y)
  if v and v >= 1 and v <= NIV then
    local n = v + d
    if n < 1 then n = 1 elseif n > NIV then n = NIV end
    g[c][y][x] = n
  end
end

---------------------------------------------------------------- silhouette
local CX, CY, RX, RY = 48, 60, 44, 41

local TOUFFE = {}
for i = 0, 359 do
  local a = math.rad(i)
  TOUFFE[i] = 1.0 + 0.055 * math.sin(a * 7.0 + 1.3) + 0.040 * math.sin(a * 17.0)
                  + 0.030 * math.sin(a * 29.0 + 2.1)
end

local function dans_tete(x, y)
  local nx, ny = (x - CX) / RX, (y - CY) / RY
  local d = math.sqrt(nx * nx + ny * ny)
  local a = math.deg(math.atan(ny, nx)) % 360
  return d <= TOUFFE[math.floor(a)], d
end

local OREILLES = {
  { { 10, -14 }, { 40, 22 }, { 4, 30 } },
  { { 86, -14 }, { 56, 22 }, { 92, 30 } },
}

local function dans_triangle(x, y, p, a, b)
  local function cote(u, v) return (v[1] - u[1]) * (y - u[2]) - (v[2] - u[2]) * (x - u[1]) end
  local s1, s2, s3 = cote(p, a), cote(a, b), cote(b, p)
  return (s1 >= 0 and s2 >= 0 and s3 >= 0) or (s1 <= 0 and s2 <= 0 and s3 <= 0)
end

local function retreci(p, a, b, k)
  local cx, cy = (p[1] + a[1] + b[1]) / 3, (p[2] + a[2] + b[2]) / 3
  local function r(q) return { cx + (q[1] - cx) * k, cy + (q[2] - cy) * k } end
  return r(p), r(a), r(b)
end

---------------------------------------------------------------- volume
for y = 0, L - 1 do
  for x = 0, L - 1 do
    local tete, d = dans_tete(x, y)
    local oreille = false
    for _, o in ipairs(OREILLES) do
      if dans_triangle(x, y, o[1], o[2], o[3]) then
        oreille = true
        local p = o[1]
        if not tete and math.sqrt((x - p[1]) ^ 2 + (y - p[2]) ^ 2) < 3.2 then
          oreille = false                              -- pointe adoucie
        end
        break
      end
    end
    if tete or oreille then
      -- source de lumiere placee en haut a gauche du visage : la clarte decroit
      -- avec la distance a ce point, et le pourtour retombe dans l'ombre
      local dist = math.sqrt((x - 32) ^ 2 + (y - 36) ^ 2) / 95
      local lum = 1 - math.min(1, dist) ^ 1.3
      local bord = (d > 0.74) and (d - 0.74) * 3.8 or 0
      local v
      if tete then
        v = 2.4 + 13.6 * lum - 3.4 * bord
      else
        v = 1.2 + 11.0 * lum                           -- oreilles : plus plates, plus sombres
      end
      v = math.floor(v + 0.5)
      if v < 1 then v = 1 elseif v > NIV then v = NIV end
      mettre(tete and "tete" or "oreilles", x, y, v)
    end
  end
end

-- interieur des oreilles
for _, o in ipairs(OREILLES) do
  local p, a, b = retreci(o[1], o[2], o[3], 0.42)
  for y = 0, 40 do
    for x = 0, L - 1 do
      if dans_triangle(x, y, p, a, b) and g.oreilles[y][x] then
        if math.sqrt((x - p[1]) ^ 2 + (y - p[2]) ^ 2) >= 2.6 then
          g.oreilles[y][x] = ROSE
        end
      end
    end
  end
end

-- liseré sombre du bord des oreilles, touffes a la base
for _, o in ipairs(OREILLES) do
  local p, a, b = o[1], o[2], o[3]
  for t = 0, 59 do
    local k = t / 59
    for _, uv in ipairs({ { p, a }, { p, b } }) do
      eclaircir(math.floor(uv[1][1] + (uv[2][1] - uv[1][1]) * k + 0.5),
                math.floor(uv[1][2] + (uv[2][2] - uv[1][2]) * k + 0.5), -2)
    end
  end
  for t = 0, 13 do
    local k = t / 13
    eclaircir(math.floor(a[1] + (b[1] - a[1]) * k + 0.5) + math.random(-1, 1),
              math.floor(a[2] + (b[2] - a[2]) * k + 0.5) + math.random(0, 2), 2)
  end
end

---------------------------------------------------------------- fourrure
-- traits courts d'1 px, surtout sur le pourtour (au milieu du visage ils tueraient le volume)
for _ = 1, 900 do
  local ang = math.random() * 2 * math.pi
  local r = 0.52 + 0.50 * math.sqrt(math.random())
  local x0, y0 = CX + math.cos(ang) * r * RX, CY + math.sin(ang) * r * RY
  local lg = ({ 2, 2, 3 })[math.random(3)]
  local delta = ({ -1, -1, 1 })[math.random(3)] * (r < 0.9 and 1 or 2)
  local a2 = ang + (math.random() - 0.5) * 0.7
  local dx, dy = math.cos(a2), math.sin(a2)
  for k = 0, lg - 1 do
    eclaircir(math.floor(x0 + dx * k + 0.5), math.floor(y0 + dy * k + 0.5), delta)
  end
end

-- structure : arcades sombres, arete du nez claire, pommettes dans l'ombre
for y = 0, L - 1 do
  for x = 0, L - 1 do
    if lire(x, y) then
      -- modelé doux : l'effet s'éteint au bord de la zone, sinon on voit une tache plate
      for _, z in ipairs({ { 27, 42, 16, 7, -2 }, { 69, 42, 16, 7, -2 },      -- arcades
                           { 11, 68, 11, 14, -2 }, { 85, 68, 11, 14, -2 },    -- pommettes
                           { 48, 52, 7, 20, 2 } }) do                         -- arête du nez
        local dd = ((x - z[1]) / z[3]) ^ 2 + ((y - z[2]) / z[4]) ^ 2
        if dd < 1 then
          local k = 1 - math.sqrt(dd)                  -- plein au centre, nul au bord
          local delta = z[5] * k
          delta = (delta > 0) and math.floor(delta + 0.35) or -math.floor(-delta + 0.35)
          if delta ~= 0 then eclaircir(x, y, delta) end
        end
      end
    end
  end
end

-- rayures du front
for i, s in ipairs({ { 48, 12, 4 }, { 36, 10, 3 }, { 60, 10, 3 }, { 27, 7, 2 }, { 69, 7, 2 } }) do
  for k = 0, s[2] - 1 do
    local y = 17 + k
    local x = math.floor(s[1] + math.sin(k * 0.22 + i * 1.7) * 2.0 + k * (s[1] - 48) * 0.035 + 0.5)
    eclaircir(x, y, -s[3]); eclaircir(x + 1, y, -s[3])
  end
end

---------------------------------------------------------------- yeux
local function oeil(ox, oy)
  local RXE, RYE = 13.5, 11.5
  for y = oy - 17, oy + 16 do
    for x = ox - 17, ox + 16 do
      local v, c = lire(x, y)
      if v then
        local nx, ny = (x - ox) / RXE, (y - oy) / RYE
        if ny < 0 then ny = ny * 1.18 end               -- amande : paupiere plus plate
        local d = nx * nx + ny * ny
        if d <= 1.0 then
          g[c][y][x] = nil                              -- l'oeil quitte le calque du corps
          local n
          if d > 0.87 then
            n = (ny < 0.15) and 1 or 3                  -- cerne
          else
            n = math.floor(9.8 - 6.0 * (d / 0.87) + 2.2 * ny + 0.5)
            if n < 2 then n = 2 elseif n > NIV then n = NIV end
          end
          mettre("yeux", x, y, n)
        end
      end
    end
  end
  for y = oy - 11, oy + 11 do                             -- pupille fendue
    local t = math.abs(y - oy) / 11.0
    local larg = math.floor(2.9 * (1 - t ^ 1.7) + 0.5)
    for x = ox - larg, ox + larg do
      if g.yeux[y][x] then g.yeux[y][x] = 1 end
    end
  end
  for _, p in ipairs({ { -4, -5, FROID1 }, { -3, -5, FROID1 }, { -4, -4, FROID1 },
                       { -3, -4, FROID2 }, { -4, -6, FROID2 } }) do
    if g.yeux[oy + p[2]] and g.yeux[oy + p[2]][ox + p[1]] then
      g.yeux[oy + p[2]][ox + p[1]] = p[3]
    end
  end
  if g.yeux[oy + 4] and g.yeux[oy + 4][ox + 5] then g.yeux[oy + 4][ox + 5] = 13 end
end

oeil(27, 57)
oeil(69, 57)

---------------------------------------------------------------- museau
for y = 68, 93 do
  for x = 26, 70 do
    if g.tete[y][x] then
      for _, cx2 in ipairs({ 39, 57 }) do
        if ((x - cx2) / 13.0) ^ 2 + ((y - 81) / 10.0) ^ 2 < 1 then eclaircir(x, y, 1); break end
      end
    end
  end
end

for k, lg in ipairs({ 3, 2, 1 }) do                     -- nez
  for x = 48 - lg, 48 + lg do
    if g.tete[71 + k] then g.tete[71 + k][x] = ROSE end
  end
end
for k = 0, 1 do if g.tete[75 + k][48] then g.tete[75 + k][48] = 2 end end
for _, sens in ipairs({ -1, 1 }) do                     -- bouche
  for k = 0, 3 do
    eclaircir(48 + sens * (1 + k), 77 + (k > 1 and 1 or 0), -3)
  end
  for i = 0, 2 do                                       -- points des moustaches
    for j = 0, 1 do eclaircir(48 + sens * (7 + j * 5), 78 + i * 3, -2) end
  end
end

---------------------------------------------------------------- moustaches
for _, sens in ipairs({ -1, 1 }) do
  for i, m in ipairs({ { -5, -0.016, 26 }, { 0, 0.004, 28 }, { 6, 0.022, 23 } }) do
    for k = 0, m[3] - 1 do
      local x = 48 + sens * (17 + k)
      local y = math.floor(80 + m[1] + m[2] * k * k + (i == 1 and -0.18 or 0.10) * k + 0.5)
      if x >= 0 and x < L and y >= 0 and y < L then
        local v = lire(x, y)
        local clair = (k < m[3] * 0.55) and 12 or 10
        if not v then
          if k % 4 ~= 3 then mettre("moustaches", x, y, clair - 3) end   -- discontinu sur le fond
        elseif v < clair then
          mettre("moustaches", x, y, clair)
        end
      end
    end
  end
end

---------------------------------------------------------------- fond
for y = 0, L - 1 do
  for x = 0, L - 1 do g.fond[y][x] = FOND end
end

---------------------------------------------------------------- sprite
local spr = Sprite(L, L, ColorMode.INDEXED)
local pal = Palette(#COULEURS + 1)
pal:setColor(0, Color{ r = 0, g = 0, b = 0, a = 0 })
for i, hex in ipairs(COULEURS) do
  pal:setColor(i, Color{ r = tonumber(hex:sub(1, 2), 16),
                         g = tonumber(hex:sub(3, 4), 16),
                         b = tonumber(hex:sub(5, 6), 16) })
end
spr:setPalette(pal)
spr.transparentColor = 0

local calque = {}
spr.layers[1].name = NOMS[1]
calque[NOMS[1]] = spr.layers[1]
for i = 2, #NOMS do
  local l = spr:newLayer()
  l.name = NOMS[i]
  calque[NOMS[i]] = l
end

for _, nom in ipairs(NOMS) do
  local img = Image(L, L, ColorMode.INDEXED)
  for y = 0, L - 1 do
    for x = 0, L - 1 do
      local v = g[nom][y][x]
      if v then img:drawPixel(x, y, v) end
    end
  end
  spr:newCel(calque[nom], 1, img, Point(0, 0))
end

spr:saveAs(SORTIE)
print("chat.aseprite : " .. L .. "x" .. L .. ", " .. #spr.layers .. " calques, palette de "
      .. #spr.palettes[1] .. " couleurs")
