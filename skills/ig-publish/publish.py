#!/usr/bin/env python3
"""Publie sur Instagram via l'API officielle de Meta (Instagram Graph API,
« Content Publishing »). Compte professionnel (Business ou Créateur) requis.

Sans --oui, le script n'envoie RIEN : il affiche ce qui serait publié.

Usage :
    python3 publish.py image   --url https://.../post.jpg --legende legende.txt
    python3 publish.py carrousel --url https://.../1.jpg --url https://.../2.jpg --legende legende.txt
    python3 publish.py reel    --url https://.../reel.mp4 --legende legende.txt [--couverture https://.../cover.jpg]
    python3 publish.py story   --url https://.../story.jpg
    python3 publish.py quota                               # posts restants sur 24 h
    ... --oui                                              # publie vraiment

Les médias doivent être accessibles par une URL publique (Meta va les
chercher) : hébergement du dépôt, Google Cloud Storage, S3, Cloudinary…

Variables d'environnement :
    IG_USER_ID       identifiant du compte Instagram professionnel
    IG_ACCESS_TOKEN  jeton d'accès (permissions instagram_business_basic +
                     instagram_business_content_publish)
    IG_GRAPH_HOST    graph.instagram.com (connexion Instagram, défaut)
                     ou graph.facebook.com (connexion via Page Facebook)
    IG_GRAPH_VERSION version de l'API (défaut v23.0 : mets la plus récente)

Aucune dépendance. Python 3.9+.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path


def cfg():
    manquants = [v for v in ("IG_USER_ID", "IG_ACCESS_TOKEN") if not os.environ.get(v)]
    if manquants:
        raise SystemExit(f"Variables manquantes : {', '.join(manquants)} (voir skills/ig-publish/SKILL.md)")
    host = os.environ.get("IG_GRAPH_HOST", "graph.instagram.com")
    version = os.environ.get("IG_GRAPH_VERSION", "v23.0")
    return f"https://{host}/{version}", os.environ["IG_USER_ID"], os.environ["IG_ACCESS_TOKEN"]


def appel(methode: str, url: str, params: dict) -> dict:
    data = urllib.parse.urlencode(params).encode()
    if methode == "GET":
        req = urllib.request.Request(f"{url}?{data.decode()}")
    else:
        req = urllib.request.Request(url, data=data, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            return json.loads(r.read())
    except urllib.error.HTTPError as e:
        raise SystemExit(f"Erreur API {e.code} : {e.read().decode(errors='replace')}")


def conteneur(base, uid, token, **params) -> str:
    params = {k: v for k, v in params.items() if v is not None}
    return appel("POST", f"{base}/{uid}/media", {**params, "access_token": token})["id"]


def attendre(base, token, cid: str, max_s=600):
    """Les vidéos sont traitées côté Meta : on attend FINISHED avant de publier."""
    debut = time.time()
    while time.time() - debut < max_s:
        st = appel("GET", f"{base}/{cid}", {"fields": "status_code,status", "access_token": token})
        code = st.get("status_code")
        if code == "FINISHED":
            return
        if code in ("ERROR", "EXPIRED"):
            raise SystemExit(f"Traitement refusé par Meta : {st}")
        time.sleep(5)
    raise SystemExit("Délai dépassé pendant le traitement de la vidéo.")


def est_video(url: str) -> bool:
    return urllib.parse.urlparse(url).path.lower().endswith((".mp4", ".mov"))


def publier(a):
    legende = Path(a.legende).read_text(encoding="utf-8").strip() if a.legende else None
    if a.type != "quota":
        print(f"Type      : {a.type}")
        print(f"Médias    : {len(a.url or [])}")
        for u in a.url or []:
            print(f"  - {u}")
        if legende:
            print(f"Légende   : {len(legende)} caractères\n---\n{legende}\n---")
        if len(legende or "") > 2200:
            raise SystemExit("Légende trop longue (2 200 caractères max).")
        if not a.oui:
            print("\nAPERÇU SEULEMENT. Rien n'a été envoyé. Ajoute --oui pour publier.")
            return

    base, uid, token = cfg()
    if a.type == "quota":
        print(appel("GET", f"{base}/{uid}/content_publishing_limit",
                    {"fields": "config,quota_usage", "access_token": token}))
        return

    if a.type == "image":
        cid = conteneur(base, uid, token, image_url=a.url[0], caption=legende)
    elif a.type == "reel":
        cid = conteneur(base, uid, token, media_type="REELS", video_url=a.url[0], caption=legende,
                        cover_url=a.couverture, share_to_feed="true")
        attendre(base, token, cid)
    elif a.type == "story":
        champ = "video_url" if est_video(a.url[0]) else "image_url"
        cid = conteneur(base, uid, token, media_type="STORIES", **{champ: a.url[0]})
        if champ == "video_url":
            attendre(base, token, cid)
    else:
        if not 2 <= len(a.url) <= 10:
            raise SystemExit("Un carrousel prend de 2 à 10 médias.")
        enfants = []
        for u in a.url:
            if est_video(u):
                c = conteneur(base, uid, token, media_type="VIDEO", video_url=u, is_carousel_item="true")
                attendre(base, token, c)
            else:
                c = conteneur(base, uid, token, image_url=u, is_carousel_item="true")
            enfants.append(c)
        cid = conteneur(base, uid, token, media_type="CAROUSEL", children=",".join(enfants), caption=legende)
        attendre(base, token, cid)

    res = appel("POST", f"{base}/{uid}/media_publish", {"creation_id": cid, "access_token": token})
    media = appel("GET", f"{base}/{res['id']}", {"fields": "permalink", "access_token": token})
    print(f"Publié : {media.get('permalink', res['id'])}")


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("type", choices=["image", "carrousel", "reel", "story", "quota"])
    p.add_argument("--url", action="append", help="URL publique du média (répéter pour un carrousel)")
    p.add_argument("--legende", help="fichier texte de la légende")
    p.add_argument("--couverture", help="URL de l'image de couverture du reel")
    p.add_argument("--oui", action="store_true", help="publier vraiment (sinon aperçu)")
    a = p.parse_args(argv)
    if a.type != "quota" and not a.url:
        p.error("--url est obligatoire")
    publier(a)


if __name__ == "__main__":
    sys.exit(main())
