#!/usr/bin/env python3
"""Visuel Instagram au style du compte Brico Dépôt Andilly.

Usage :
    python3 make_visual.py scene.json --format post  --out post.png
    python3 make_visual.py scene.json --format story --out story.png
    python3 make_visual.py --fin --format story --out fin.png        # carton adresse

Raccourci sans fichier (bandeau rouge + sous-titre + tag jaune) :
    python3 make_visual.py --titre "VOTRE DÉPÔT|FAIT PEAU NEUVE" --sur-titre "TRAVAUX EN COURS" \\
        --sous-titre "ON REMONTE LES RACKS POUR VOUS" --tag "RENDEZ-VOUS EN 2027" \\
        --photo rayon.jpg --flou --ruban --format post --out travaux.png

Le format de scène est décrit en tête de style.py.
Dépendance : Pillow.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from style import FORMATS, composer, depot


def scene_depuis_args(a) -> dict:
    blocs = []
    if a.sur_titre:
        blocs.append({"texte": a.sur_titre, "style": "noir", "angle": 2})
    blocs.append({"texte": a.titre, "style": "rouge"})
    if a.sous_titre:
        blocs.append({"texte": a.sous_titre, "style": "blanc"})
    if a.prix:
        blocs += [{"espace": 30}, {"prix": a.prix, "libelle": a.libelle or "", "detail": a.detail or "", "tag": a.tag_prix}]
    if a.tag:
        blocs += [{"espace": 30}, {"texte": a.tag, "style": "jaune", "angle": 2}]
    blocs += [{"espace": 24}, {"texte": f"{depot().get('enseigne', 'BRICO DÉPÔT')} {depot().get('ville', '')}".strip(), "style": "noir", "taille": 40}]
    return {"fond": a.photo or "rouge", "flou": a.flou, "ruban": a.ruban, "blocs": blocs}


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("scene", nargs="?", help="fichier JSON de la scène")
    p.add_argument("--fin", action="store_true", help="carton de fin avec les infos du dépôt")
    p.add_argument("--titre")
    p.add_argument("--sur-titre", dest="sur_titre")
    p.add_argument("--sous-titre", dest="sous_titre")
    p.add_argument("--tag", help="bandeau jaune")
    p.add_argument("--prix")
    p.add_argument("--libelle")
    p.add_argument("--detail")
    p.add_argument("--tag-prix", dest="tag_prix", default="PRIX DÉPÔT")
    p.add_argument("--photo")
    p.add_argument("--flou", action="store_true")
    p.add_argument("--ruban", action="store_true", help="rubans de chantier")
    p.add_argument("--format", choices=FORMATS, default="post")
    p.add_argument("--out", required=True)
    a = p.parse_args(argv)

    if a.fin:
        scene = {"fin": True}
    elif a.scene:
        scene = json.loads(Path(a.scene).read_text(encoding="utf-8"))
        fond = scene.get("fond")
        if fond and fond not in ("rouge", "blanc"):
            scene["fond"] = str((Path(a.scene).parent / fond))
    elif a.titre:
        scene = scene_depuis_args(a)
    else:
        p.error("donne un fichier de scène, --titre ou --fin")

    W, H = FORMATS[a.format]
    out = Path(a.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    composer(scene, W, H).convert("RGB").save(out, quality=95)
    print(f"écrit : {out}")


if __name__ == "__main__":
    main()
