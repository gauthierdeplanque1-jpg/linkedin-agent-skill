#!/usr/bin/env python3
"""Rétro-planning Instagram calculé à partir d'un B.I.C. structuré.

Usage :
    python3 retroplanning.py bic/2026-11.json                 # tableau Markdown
    python3 retroplanning.py bic/2026-11.json --today 2026-11-02 --out plans/2026-11.md
    python3 retroplanning.py bic/2026-11.json --csv plans/2026-11.csv

Principe : chaque opération du B.I.C. a une date de lancement (J0). On
remonte le temps à partir de J0 pour poser le brief, le tournage, le
montage, la validation et la programmation, puis on pose les publications
de relance pendant l'opération. Toute tâche dont la date est déjà passée
est marquée EN RETARD et ramenée à aujourd'hui, pour que le plan reste
faisable même quand le B.I.C. arrive tard.

Aucune dépendance. Python 3.9+.
"""
from __future__ import annotations

import argparse
import csv
import datetime as dt
import json
import sys
from pathlib import Path

JOURS = ["lun.", "mar.", "mer.", "jeu.", "ven.", "sam.", "dim."]

# (décalage par rapport à J0, type, tâche). Les décalages négatifs sont la
# préparation, les positifs les publications pendant l'opération.
GABARIT_OPERATION = [
    (-6, "PREPA", "Brief : relire le B.I.C., choisir 2 hero products + 1 angle « ce qu'on ne voit pas »"),
    (-4, "PREPA", "Tournage en dépôt : rayon, prix en vrai, conseil vendeur (autorisations droit à l'image)"),
    (-3, "PREPA", "Montage : reel de lancement (/ig-reel) + carrousel (/ig-post)"),
    (-2, "PREPA", "Validation directeur de dépôt (prix, dates, mentions légales)"),
    (-1, "PREPA", "Programmation : légendes finales, hashtags locaux, heure de publication"),
    (0, "PUBLI", "REEL lancement de l'opération + story « c'est parti »"),
    (2, "PUBLI", "CARROUSEL conseil / hero products en rayon"),
    (4, "PUBLI", "STORY sondage ou quiz sur la thématique"),
]
GABARIT_FIN = (-1, "PUBLI", "STORY « derniers jours » de l'opération")

GABARIT_TEMPS_FORT = [
    (-3, "PREPA", "Préparer le contenu du temps fort"),
    (-1, "PUBLI", "POST teaser du temps fort"),
    (0, "PUBLI", "STORY jour J"),
]

# Rythme du compte : lundi réel conseil, mercredi carrousel/produit,
# vendredi réel coulisses ou offre. Tournage en lot le jeudi d'avant.
RUBRIQUES_HEBDO = {
    0: ("PUBLI", "RÉEL CONSEIL « 1 rayon, 1 astuce » (18 h 30)"),
    2: ("PUBLI", "CARROUSEL conseil ou produit en situation (12 h 15)"),
    3: ("PREPA", "Tournage en lot de la semaine suivante (1 h, heures creuses)"),
    4: ("PUBLI", "RÉEL coulisses / équipe ou offre du week-end (12 h 15)"),
}


def parse_date(s: str) -> dt.date:
    return dt.date.fromisoformat(s)


def fmt(d: dt.date) -> str:
    return f"{JOURS[d.weekday()]} {d.strftime('%d/%m')}"


def construire(bic: dict, today: dt.date) -> list[dict]:
    lignes: list[dict] = []

    def ajouter(date: dt.date, sujet: str, typ: str, tache: str, details: str = ""):
        retard = typ == "PREPA" and date < today
        lignes.append({
            "date_prevue": date,
            "date": today if retard else date,
            "sujet": sujet,
            "type": typ,
            "tache": tache,
            "details": details,
            "statut": "EN RETARD" if retard else ("PASSÉ" if date < today else "À FAIRE"),
        })

    for op in bic.get("operations", []):
        j0, fin = parse_date(op["debut"]), parse_date(op["fin"])
        sujet = f"{op['code']} · {op['theme']}"
        heros = ", ".join(p["libelle"] for p in op.get("hero_products", [])[:3])
        for decal, typ, tache in GABARIT_OPERATION:
            d = j0 + dt.timedelta(days=decal)
            if typ == "PUBLI" and d > fin:
                continue
            ajouter(d, sujet, typ, tache, heros if decal in (-6, 0, 2) else "")
        d_fin = fin + dt.timedelta(days=GABARIT_FIN[0])
        if (fin - j0).days >= 4:
            ajouter(d_fin, sujet, GABARIT_FIN[1], GABARIT_FIN[2])

    for tf in bic.get("temps_forts", []):
        j0 = parse_date(tf["date"])
        for decal, typ, tache in GABARIT_TEMPS_FORT:
            ajouter(j0 + dt.timedelta(days=decal), tf["nom"], typ, tache, tf.get("angle", ""))

    debut_mois = parse_date(bic["mois"] + "-01")
    d = debut_mois
    while d.month == debut_mois.month:
        if d.weekday() in RUBRIQUES_HEBDO:
            typ, tache = RUBRIQUES_HEBDO[d.weekday()]
            ajouter(d, "Rubrique dépôt", typ, tache)
        d += dt.timedelta(days=1)

    lignes.sort(key=lambda l: (l["date"], l["type"] != "PREPA", l["sujet"]))
    return [l for l in lignes if l["statut"] != "PASSÉ"]


def en_markdown(bic: dict, lignes: list[dict], today: dt.date) -> str:
    out = [
        f"# Rétro-planning Instagram · {bic.get('depot', 'dépôt')} · {bic['mois']}",
        "",
        f"Calculé le {today.isoformat()} à partir du B.I.C. "
        f"Les tâches en retard sont ramenées à aujourd'hui.",
        "",
    ]
    themes = bic.get("thematiques", [])
    if themes:
        out.append("**Fils rouges du mois :** " + " · ".join(
            f"{t['nom']} ({t.get('message', '')})".replace(" ()", "") for t in themes))
        out.append("")
    out += ["| Date | Statut | Sujet | Type | Tâche | Produits / angle |",
            "| --- | --- | --- | --- | --- | --- |"]
    for l in lignes:
        statut = l["statut"]
        if statut == "EN RETARD":
            statut += f" (prévu {fmt(l['date_prevue'])})"
        out.append(f"| {fmt(l['date'])} | {statut} | {l['sujet']} | {l['type']} | "
                   f"{l['tache']} | {l['details']} |")
    nb_retard = sum(l["statut"] == "EN RETARD" for l in lignes)
    nb_publi = sum(l["type"] == "PUBLI" for l in lignes)
    out += ["", f"{nb_publi} publications prévues, {nb_retard} tâches de préparation en retard."]
    return "\n".join(out) + "\n"


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("bic", help="fichier JSON du B.I.C. (voir skills/ig-bic/schema.json)")
    p.add_argument("--today", help="date de référence AAAA-MM-JJ (défaut : aujourd'hui)")
    p.add_argument("--out", help="écrire le Markdown dans ce fichier")
    p.add_argument("--csv", help="exporter aussi en CSV (Excel, Google Sheets, Trello)")
    a = p.parse_args(argv)

    bic = json.loads(Path(a.bic).read_text(encoding="utf-8"))
    today = parse_date(a.today) if a.today else dt.date.today()
    lignes = construire(bic, today)
    md = en_markdown(bic, lignes, today)

    if a.out:
        Path(a.out).parent.mkdir(parents=True, exist_ok=True)
        Path(a.out).write_text(md, encoding="utf-8")
        print(f"écrit : {a.out}")
    else:
        sys.stdout.write(md)

    if a.csv:
        Path(a.csv).parent.mkdir(parents=True, exist_ok=True)
        with open(a.csv, "w", newline="", encoding="utf-8-sig") as f:
            w = csv.writer(f, delimiter=";")
            w.writerow(["date", "statut", "sujet", "type", "tache", "details"])
            for l in lignes:
                w.writerow([l["date"].isoformat(), l["statut"], l["sujet"], l["type"], l["tache"], l["details"]])
        print(f"écrit : {a.csv}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
