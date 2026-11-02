"""Charte « Brico Dépôt Andilly » : le style des reels et visuels du compte.

Une scène = un fond + une pile de blocs centrés. Utilisé par make_visual.py
(images) et make_reel.py (overlays vidéo).

Scène (JSON) :
{
  "fond": "rouge" | "blanc" | "chemin/photo.jpg",
  "flou": true,                 # photo floutée derrière le texte
  "ruban": true,                # rubans de chantier jaune/noir
  "deco": "points" | "damier",  # décor des cartons pleins
  "position": "centre" | "bas", # où poser la pile de blocs
  "cadrage": [0.5, 0.5],        # point de la photo à garder au recadrage 9:16
  "blocs": [
    {"texte": "IL FAIT|FROID ?", "style": "titre"},
    {"texte": "VOTRE POÊLE A FAIM", "style": "blanc"},
    {"texte": "PRIX DÉPÔT", "style": "jaune", "angle": -4},
    {"prix": "5,29", "libelle": "Granulés|de bois", "detail": "Sac de 15 kg", "tag": "STOCK XXL"},
    {"numero": "01"},
    {"texte": "Grands carreaux : mettez aussi de la colle au dos.", "style": "carte"}
  ]
}
Styles de bloc : titre (gros texte sans fond), rouge, noir, blanc, jaune,
carte (texte courant sur fond blanc), info, info-rouge.
Une scène {"fin": true} donne le carton de fin avec les infos du dépôt.
"""
from __future__ import annotations

import json
import os
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont, ImageOps

ROUGE = (227, 6, 19)
NOIR = (17, 17, 17)
BLANC = (255, 255, 255)
JAUNE = (255, 228, 0)
GRIS = (236, 236, 236)

FORMATS = {"post": (1080, 1350), "carre": (1080, 1080), "story": (1080, 1920)}

RACINE = Path(__file__).resolve().parents[2]
POLICES = {
    "black": RACINE / "fonts" / "Montserrat-Black.ttf",
    "extrabold": RACINE / "fonts" / "Montserrat-ExtraBold.ttf",
    "bold": RACINE / "fonts" / "Montserrat-Bold.ttf",
}
SECOURS = [
    "/usr/share/fonts/opentype/inter/Inter-ExtraBold.otf",
    "/System/Library/Fonts/Supplemental/Arial Black.ttf",
    "C:/Windows/Fonts/ariblk.ttf",
    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
]


def police(taille: int, graisse: str = "extrabold") -> ImageFont.FreeTypeFont:
    for p in [POLICES.get(graisse)] + SECOURS:
        if p and Path(p).exists():
            return ImageFont.truetype(str(p), taille)
    return ImageFont.load_default(taille)


def depot() -> dict:
    """Infos du carton de fin : ~/.claude/instagram/depot.json, sinon le modèle du dépôt."""
    for p in (Path(os.path.expanduser("~/.claude/instagram/depot.json")), RACINE / "templates" / "depot.json"):
        if p.exists():
            return json.loads(p.read_text(encoding="utf-8"))
    return {"enseigne": "BRICO DÉPÔT", "ville": "ANDILLY", "lignes": []}


# ---------------------------------------------------------------- blocs

def _texte(draw, xy, txt, f, fill):
    l, t, _, _ = draw.textbbox((0, 0), txt, font=f)
    draw.text((xy[0] - l, xy[1] - t), txt, font=f, fill=fill)


def _taille(txt, f):
    l, t, r, b = ImageDraw.Draw(Image.new("L", (1, 1))).textbbox((0, 0), txt, font=f)
    return r - l, b - t


def _ajuste(lignes, largeur, taille, graisse):
    while taille > 24:
        f = police(taille, graisse)
        if max(_taille(l, f)[0] for l in lignes) <= largeur:
            return f
        taille -= 2
    return police(taille, graisse)


def bloc_boite(txt, fond, encre, taille, largeur_max, graisse="black", pad=(26, 14)):
    """Un bandeau par ligne (« | » pour couper), empilés et centrés."""
    lignes = [l.strip() for l in txt.split("|") if l.strip()]
    f = _ajuste(lignes, largeur_max - 2 * pad[0], taille, graisse)
    tuiles = []
    for l in lignes:
        w, h = _taille(l, f)
        hb = int(f.size * 0.74)  # hauteur des capitales : bandeaux réguliers
        im = Image.new("RGBA", (w + 2 * pad[0], max(h, hb) + 2 * pad[1]), fond + (255,) if fond else (0, 0, 0, 0))
        d = ImageDraw.Draw(im)
        _texte(d, (pad[0], pad[1] + (max(h, hb) - h) // 2), l, f, encre)
        tuiles.append(im)
    W = max(t.width for t in tuiles)
    H = sum(t.height for t in tuiles)
    out = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    y = 0
    for t in tuiles:
        out.alpha_composite(t, ((W - t.width) // 2, y))
        y += t.height
    return out


def bloc_carte(txt, largeur, taille=34):
    f = police(taille, "bold")
    mots, lignes, cur = txt.split(), [], ""
    for m in mots:
        essai = f"{cur} {m}".strip()
        if _taille(essai, f)[0] > largeur - 60 and cur:
            lignes.append(cur)
            cur = m
        else:
            cur = essai
    lignes.append(cur)
    lh = int(taille * 1.35)
    im = Image.new("RGBA", (largeur, lh * len(lignes) + 44), BLANC + (255,))
    d = ImageDraw.Draw(im)
    for i, l in enumerate(lignes):
        w, _ = _taille(l, f)
        _texte(d, ((largeur - w) // 2, 22 + i * lh), l, f, NOIR)
    return im


def bloc_info(txt, encre, taille=36):
    f = police(taille, "bold")
    w, h = _taille(txt, f)
    im = Image.new("RGBA", (w + 4, int(taille * 1.4)), (0, 0, 0, 0))
    _texte(ImageDraw.Draw(im), (2, (im.height - h) // 2), txt, f, encre)
    return im


def bloc_prix(b, echelle=1.0):
    """Étiquette rouge : libellé à gauche, prix géant à droite, tag noir au-dessus."""
    s = lambda v: int(v * echelle)
    euros, _, cents = b["prix"].replace(".", ",").partition(",")
    fe, fc, fl, fd = police(s(230), "black"), police(s(84), "black"), police(s(46), "extrabold"), police(s(30), "bold")
    lib = [l for l in b.get("libelle", "").split("|") if l]
    we, he = _taille(euros, fe)
    wc = max(_taille(cents or "00", fc)[0], _taille("€", fc)[0])
    wl = max([_taille(l, fl)[0] for l in lib] + [_taille(b.get("detail", ""), fd)[0], 0])
    W = s(60) + wl + s(50) + we + s(14) + wc + s(50)
    H = he + s(110)
    im = Image.new("RGBA", (W, H + s(70)), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    y0 = s(70)
    d.rectangle([0, y0, W, y0 + H], fill=ROUGE)
    yl = y0 + H // 2 - (len(lib) * s(56) + s(40)) // 2
    for l in lib:
        _texte(d, (s(50), yl), l, fl, BLANC)
        yl += s(56)
    if b.get("detail"):
        _texte(d, (s(50), yl + s(6)), b["detail"], fd, BLANC)
    xe = s(60) + wl + s(50)
    _texte(d, (xe, y0 + (H - he) // 2), euros, fe, BLANC)
    xc = xe + we + s(14)
    _texte(d, (xc, y0 + (H - he) // 2), "€", fc, BLANC)
    if cents:
        _texte(d, (xc, y0 + (H - he) // 2 + s(96)), cents, fc, BLANC)
    if b.get("tag"):
        tag = bloc_boite(b["tag"], NOIR, BLANC, s(40), W, pad=(s(20), s(10))).rotate(3, expand=True, resample=Image.BICUBIC)
        im.alpha_composite(tag, ((W - tag.width) // 2, max(0, y0 - tag.height + s(22))))
    return im


STYLES = {
    "rouge": (ROUGE, BLANC, 96),
    "noir": (NOIR, BLANC, 44),
    "blanc": (BLANC, ROUGE, 50),
    "jaune": (JAUNE, NOIR, 56),
}


def rendre_bloc(b, W, fond_scene):
    if "prix" in b:
        return bloc_prix(b, b.get("echelle", 1.0))
    if "numero" in b:
        return bloc_boite(b["numero"], BLANC, ROUGE, b.get("taille", 130), W, pad=(24, 16))
    style = b.get("style", "rouge")
    txt = b.get("texte", "")
    if style == "titre":
        encre = ROUGE if fond_scene == "blanc" else BLANC
        return bloc_boite(txt.upper(), None, encre, b.get("taille", 150), W - 120, pad=(0, 6))
    if style == "carte":
        return bloc_carte(txt, min(W - 200, 760))
    if style in ("info", "info-rouge"):
        return bloc_info(txt, ROUGE if style == "info-rouge" else NOIR, b.get("taille", 36))
    fond, encre, taille = STYLES[style]
    return bloc_boite(txt.upper(), fond, encre, b.get("taille", taille), W - 100)


# ---------------------------------------------------------------- décors

def ruban(W, epaisseur=120, angle=-6):
    L = int(W * 1.4)
    r = Image.new("RGBA", (L, epaisseur), NOIR + (255,))
    d = ImageDraw.Draw(r)
    pas = epaisseur
    for x in range(-epaisseur, L + epaisseur, pas * 2):
        d.polygon([(x, epaisseur), (x + pas, epaisseur), (x + 2 * pas, 0), (x + pas, 0)], fill=JAUNE)
    return r.rotate(angle, expand=True, resample=Image.BICUBIC)


def decor(img, deco):
    W, H = img.size
    d = ImageDraw.Draw(img)
    if deco == "points":
        for (x, y, r, c) in [(.13, .18, 70, ROUGE), (.85, .14, 55, NOIR), (.82, .8, 85, ROUGE), (.15, .84, 45, NOIR)]:
            d.ellipse([x * W - r, y * H - r, x * W + r, y * H + r], fill=c)
    elif deco == "damier":
        c = 150
        for i in range(0, W // c + 1):
            for j in range(0, H // c + 1):
                if (i + j) % 3 == 0 and (i in (0, W // c) or j % 4 == 0):
                    d.rectangle([i * c + 8, j * c + 8, i * c + c - 8, j * c + c - 8], fill=GRIS)


def fond_image(scene, W, H):
    fond = scene.get("fond", "rouge")
    if fond in ("rouge", "blanc"):
        img = Image.new("RGBA", (W, H), (ROUGE if fond == "rouge" else BLANC) + (255,))
        if scene.get("deco"):
            decor(img, scene["deco"])
        return img
    ph = ImageOps.exif_transpose(Image.open(fond)).convert("RGB")
    ph = ImageOps.fit(ph, (W, H), Image.LANCZOS, centering=tuple(scene.get("cadrage", (0.5, 0.5))))
    if scene.get("flou"):
        ph = ph.filter(ImageFilter.GaussianBlur(14))
    return ph.convert("RGBA")


# ---------------------------------------------------------------- scène

def scene_fin():
    info = depot()
    blocs = [
        {"texte": info.get("enseigne", "BRICO DÉPÔT"), "style": "rouge", "taille": 84},
        {"texte": info.get("ville", "ANDILLY"), "style": "noir", "taille": 56},
        {"espace": 30},
    ]
    for i, l in enumerate(info.get("lignes", [])):
        blocs.append({"texte": l, "style": "info-rouge" if i == len(info["lignes"]) - 1 else "info"})
    return {"fond": "blanc", "blocs": blocs, "colle": True}


def composer(scene, W, H, transparent=False):
    """Rend la scène. transparent=True : uniquement les blocs (overlay vidéo)."""
    if scene.get("fin"):
        scene = {**scene_fin(), **{k: v for k, v in scene.items() if k != "fin"}}
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0)) if transparent else fond_image(scene, W, H)
    fond_scene = scene.get("fond", "rouge") if scene.get("fond") in ("rouge", "blanc") else "photo"

    if scene.get("ruban"):
        r = ruban(W)
        img.alpha_composite(r, ((W - r.width) // 2, int(H * 0.06)))
        r2 = ruban(W, angle=5)
        img.alpha_composite(r2, ((W - r2.width) // 2, int(H * 0.86) - r2.height // 2))

    tuiles = []
    for b in scene.get("blocs", []):
        if "espace" in b:
            tuiles.append(Image.new("RGBA", (1, b["espace"]), (0, 0, 0, 0)))
            continue
        t = rendre_bloc(b, W, fond_scene)
        ang = b.get("angle", 0)
        if ang:
            t = t.rotate(ang, expand=True, resample=Image.BICUBIC)
        tuiles.append(t)
    if not tuiles:
        return img
    ecart = 0 if scene.get("colle", True) else 18
    total = sum(t.height for t in tuiles) + ecart * (len(tuiles) - 1)
    pos = scene.get("position", "centre")
    y = int(H * 0.66) - total // 2 if pos == "bas" else (H - total) // 2
    y = max(40, min(y, H - total - 260 if H > 1500 else H - total - 40))
    for t in tuiles:
        img.alpha_composite(t, ((W - t.width) // 2, y))
        y += t.height + ecart
    return img
