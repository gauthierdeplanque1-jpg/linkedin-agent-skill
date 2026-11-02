#!/usr/bin/env python3
"""Génère un visuel Instagram au style « dépôt » : fond rouge, titres en
bandeaux noirs, bloc prix blanc, comme les supports du B.I.C.

Usage :
    python3 make_visual.py --titre "RADIATEUR À INERTIE" --sous-titre "Céramique 1000 W" \\
        --prix 89 --photo rayon.jpg --out post.png
    python3 make_visual.py --titre "1 MINUTE AVEC|KARIM" --badge "CE QU'ON NE VOIT PAS" \\
        --photo karim.jpg --format story --out story.png

Formats : post (1080x1350, 4:5), carre (1080x1080), story (1080x1920).
Un « | » dans le titre force un retour à la ligne (un bandeau par ligne).
Dépendance : Pillow (pip install pillow).
"""
from __future__ import annotations

import argparse
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont, ImageOps

ROUGE = (227, 6, 19)
NOIR = (17, 17, 17)
BLANC = (255, 255, 255)
JAUNE = (255, 221, 0)

FORMATS = {"post": (1080, 1350), "carre": (1080, 1080), "story": (1080, 1920)}

POLICES = [
    "/usr/share/fonts/opentype/inter/Inter-ExtraBold.otf",
    "/usr/share/fonts/opentype/inter/InterDisplay-Bold.otf",
    "/Library/Fonts/Arial Black.ttf",
    "/System/Library/Fonts/Supplemental/Arial Black.ttf",
    "C:/Windows/Fonts/ariblk.ttf",
    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
]


def police(taille: int, chemin: str | None = None) -> ImageFont.FreeTypeFont:
    for p in ([chemin] if chemin else []) + POLICES:
        if p and Path(p).exists():
            return ImageFont.truetype(p, taille)
    return ImageFont.load_default(taille)


def bandeau(draw, x, y, texte, f, fond=NOIR, couleur=BLANC, pad=(22, 12)):
    l, t, r, b = draw.textbbox((0, 0), texte, font=f)
    w, h = r - l, b - t
    draw.rectangle([x, y, x + w + 2 * pad[0], y + h + 2 * pad[1]], fill=fond)
    draw.text((x + pad[0] - l, y + pad[1] - t), texte, font=f, fill=couleur)
    return y + h + 2 * pad[1]


def ajuster(draw, lignes, largeur_max, taille, chemin):
    while taille > 30:
        f = police(taille, chemin)
        if all(draw.textbbox((0, 0), l, font=f)[2] + 44 <= largeur_max for l in lignes):
            return f
        taille -= 4
    return police(taille, chemin)


def bloc_prix(img, draw, prix: str, cx, cy, chemin, taille=230, droite=None):
    """Étiquette prix. Centrée sur (cx, cy), ou bord droit calé sur `droite`."""
    euros, _, cents = prix.replace(".", ",").partition(",")
    f_e, f_c = police(taille, chemin), police(int(taille * 0.4), chemin)
    le, te, re, be = draw.textbbox((0, 0), euros, font=f_e)
    lc, tc, rc, bc = draw.textbbox((0, 0), "€", font=f_c)
    w = (re - le) + max(rc - lc, draw.textbbox((0, 0), cents or "€", font=f_c)[2]) + 90
    h = (be - te) + 70
    x0, y0 = (droite - w if droite else cx - w // 2), cy - h // 2
    draw.rectangle([x0, y0, x0 + w, y0 + h], fill=BLANC)
    draw.text((x0 + 30 - le, y0 + 35 - te), euros, font=f_e, fill=ROUGE)
    xs = x0 + 30 + (re - le) + 15
    draw.text((xs - lc, y0 + 40 - tc), "€", font=f_c, fill=ROUGE)
    if cents:
        draw.text((xs, y0 + 40 + (bc - tc) + 10), cents, font=f_c, fill=ROUGE)


def generer(a) -> Path:
    W, H = FORMATS[a.format]
    img = Image.new("RGB", (W, H), ROUGE)
    draw = ImageDraw.Draw(img)
    marge = 60

    zone_photo = 0
    if a.photo:
        zone_photo = int(H * (0.58 if a.format != "carre" else 0.5))
        ph = ImageOps.fit(Image.open(a.photo).convert("RGB"), (W, zone_photo), Image.LANCZOS)
        img.paste(ph, (0, 0))

    y = (zone_photo - 60) if a.photo else int(H * 0.18)
    if a.badge:
        y = bandeau(draw, marge, y - 70 if a.photo else y, a.badge.upper(),
                    police(38, a.police), fond=JAUNE, couleur=NOIR) + 20
    lignes = [l.strip().upper() for l in a.titre.split("|") if l.strip()]
    f_titre = ajuster(draw, lignes, W - 2 * marge, 96 if a.format != "story" else 110, a.police)
    for l in lignes:
        y = bandeau(draw, marge, y, l, f_titre) + 8
    if a.sous_titre:
        y += 14
        f_s = police(46, a.police)
        draw.text((marge, y), a.sous_titre, font=f_s, fill=BLANC)
        y += draw.textbbox((0, 0), a.sous_titre, font=f_s)[3] + 10

    pied = 110
    if a.prix and a.photo:
        # étiquette posée sur la photo, coin haut droit : ne gêne jamais le titre
        bloc_prix(img, draw, a.prix, 0, 60 + 130, a.police, taille=200, droite=W - marge)
    elif a.prix:
        cy = y + ((H - pied - 60) - y) // 2
        bloc_prix(img, draw, a.prix, W // 2, cy, a.police)
    if a.mention:
        f_m = police(26, a.police)
        draw.text((marge, H - pied - 50), a.mention, font=f_m, fill=BLANC)

    draw.rectangle([0, H - pied, W, H], fill=NOIR)
    f_p = police(40, a.police)
    draw.text((marge, H - pied + 32), a.signature.upper(), font=f_p, fill=BLANC)
    if a.logo and Path(a.logo).exists():
        logo = Image.open(a.logo).convert("RGBA")
        logo.thumbnail((180, pied - 20))
        img.paste(logo, (W - marge - logo.width, H - pied + (pied - logo.height) // 2), logo)

    out = Path(a.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    img.save(out, quality=95)
    return out


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--titre", required=True, help="texte des bandeaux, « | » pour couper")
    p.add_argument("--sous-titre", dest="sous_titre")
    p.add_argument("--prix", help="ex. 89 ou 14,90")
    p.add_argument("--mention", help="mention légale sous le prix (dates, dans la limite des stocks)")
    p.add_argument("--badge", help="petit bandeau jaune au-dessus du titre")
    p.add_argument("--photo", help="photo prise en dépôt")
    p.add_argument("--logo", help="logo PNG fourni par l'enseigne (optionnel)")
    p.add_argument("--signature", default="Brico Dépôt Andilly")
    p.add_argument("--format", choices=FORMATS, default="post")
    p.add_argument("--police", help="chemin d'une police .ttf/.otf grasse")
    p.add_argument("--out", required=True)
    print(f"écrit : {generer(p.parse_args(argv))}")


if __name__ == "__main__":
    main()
