"""Essai : Tim dessiné pixel par pixel (cellule 32×32, palette ico-pixel-32).

    python tim.py <dossier de sortie>   → tim-planche.png (32×32 par case), tim-apercu.png et tim.gif (×8)
"""
import os, sys
from PIL import Image

PAL = {
    "K": "1D1B2E",  # contour
    "H": "7A4E1E", "h": "B9802B",  # cheveux, reflet
    "S": "C9A57A", "s": "9C7451",  # peau, ombre
    "r": "F59A7A",                  # joues
    "W": "F2EDE4",                  # blanc des yeux
    "R": "E5533D",                  # écharpe
    "T": "3FB56B", "t": "2E7D4F",  # tunique, ombre
    "B": "6B4A35",                  # ceinture
    "P": "3E5BA9", "p": "1F2E5C",  # pantalon, ombre
    "O": "3B2A22",                  # bottes
}

HAUT = [  # tête et corps (16 de large)
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
]
YEUX_FERMES = [".KSSSSSSSSSSSSK.", ".KSKKSSSSSKKSSK."]  # lignes 7 et 8
JAMBES = {
    "neutre": ["...KPPPKKPPPK...", "...KPPPKKPPPK...", "...KpPPKKpPPK...", "..KOOOOKKOOOOK..", "..KKKKKKKKKKKK.."],
    "gauche": ["...KPPPKKPPPK...", "...KpPPKKPPPK...", "..KOOOOKKpPPK...", "..KKKKKKKOOOOK..", "........KKKKKK.."],
    "droite": ["...KPPPKKPPPK...", "...KPPPKKpPPK...", "...KpPPKKOOOOK..", "..KOOOOKKKKKKK..", "..KKKKKK........"],
}
SOL = 28  # dernière ligne des pieds dans la case


def image(jambes="neutre", cligne=False, respire=0):
    haut = list(HAUT)
    if cligne:
        haut[7], haut[8] = YEUX_FERMES
    bas = JAMBES[jambes]
    rows = haut + bas
    for r in rows:
        assert len(r) == 16, r
    img = Image.new("RGBA", (32, 32), (0, 0, 0, 0))
    top = SOL - len(rows) + 1
    for y, row in enumerate(rows):
        yy = top + y + (respire if y < len(haut) else 0)  # le haut du corps descend d'1 px
        for x, c in enumerate(row):
            if c != ".":
                v = PAL[c]
                img.putpixel((8 + x, yy), (int(v[:2], 16), int(v[2:4], 16), int(v[4:], 16), 255))
    return img


ACTIONS = {
    "repos": [image(), image(respire=1), image(), image(cligne=True)],
    "marche": [image("gauche"), image(respire=1), image("droite"), image(respire=1)],
}
DUREES = {"repos": [400, 300, 400, 150], "marche": [120, 120, 120, 120]}  # ms par image

out = sys.argv[1] if len(sys.argv) > 1 else "."
os.makedirs(out, exist_ok=True)
planche = Image.new("RGBA", (32 * 4, 32 * len(ACTIONS)), (0, 0, 0, 0))
for j, (nom, imgs) in enumerate(ACTIONS.items()):
    for i, im in enumerate(imgs):
        planche.paste(im, (32 * i, 32 * j))
planche.save(os.path.join(out, "tim-planche.png"))

# aperçu ×8 sur fond crème, et GIF animé (repos puis marche)
Z = 8
fond = (242, 237, 228, 255)
ap = Image.new("RGBA", planche.size, fond)
ap.alpha_composite(planche)
ap.resize((planche.width * Z, planche.height * Z), Image.NEAREST).save(os.path.join(out, "tim-apercu.png"))
frames, durs = [], []
for nom in ("repos", "repos", "marche", "marche", "marche"):
    for im, d in zip(ACTIONS[nom], DUREES[nom]):
        f = Image.new("RGBA", (32, 32), fond)
        f.alpha_composite(im)
        frames.append(f.resize((32 * Z, 32 * Z), Image.NEAREST).convert("P", palette=Image.ADAPTIVE))
        durs.append(d)
frames[0].save(os.path.join(out, "tim.gif"), save_all=True, append_images=frames[1:], duration=durs, loop=0, disposal=2)
print("ok", out)
