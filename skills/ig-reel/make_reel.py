#!/usr/bin/env python3
"""Monte un Reel vertical 1080x1920 à partir d'un storyboard JSON :
photos (effet zoom lent) et vidéos prises en dépôt, texte en bandeaux
au style dépôt, carton de fin, musique optionnelle.

Usage :
    python3 make_reel.py storyboard.json --out reel.mp4

Storyboard :
{
  "segments": [
    {"media": "rayon.jpg",  "duree": 2.5, "texte": "IL FAIT FROID ?"},
    {"media": "radiateur.mp4", "duree": 3, "texte": "RADIATEUR À INERTIE", "sous_texte": "Céramique 1000 W"},
    {"media": "etiquette.jpg", "duree": 2.5, "texte": "LE PRIX EN VRAI", "sous_texte": "en rayon à Andilly"}
  ],
  "fin": {"texte": "ALLEZ, AUX TRAVAUX !", "sous_texte": "Brico Dépôt Andilly", "duree": 2.5},
  "musique": "musique_libre_de_droits.mp3"
}

Les chemins sont relatifs au fichier storyboard.
Dépendances : ffmpeg dans le PATH, Pillow.
"""
from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

from PIL import Image, ImageDraw

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "ig-post"))
from make_visual import BLANC, NOIR, ROUGE, ajuster, bandeau, police  # noqa: E402

W, H, FPS = 1080, 1920, 30
VIDEO_EXT = {".mp4", ".mov", ".m4v", ".webm", ".avi"}


def overlay(texte: str | None, sous_texte: str | None, path: Path, plein=False):
    img = Image.new("RGBA", (W, H), ROUGE + (255,) if plein else (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    lignes = [l.strip().upper() for l in (texte or "").split("|") if l.strip()]
    if lignes:
        f = ajuster(d, lignes, W - 120, 104, None)
        hauteur = len(lignes) * 140 + (80 if sous_texte else 0)
        y = (H - hauteur) // 2 if plein else int(H * 0.62)
        for l in lignes:
            y = bandeau(d, 60, y, l, f) + 10
        if sous_texte:
            y = bandeau(d, 60, y + 10, sous_texte, police(50), fond=BLANC, couleur=NOIR)
    img.save(path)


def run(cmd):
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        sys.stderr.write(r.stderr[-2000:])
        raise SystemExit(f"ffmpeg a échoué : {' '.join(cmd[:6])} …")


def segment(media: Path | None, duree: float, ov: Path, out: Path):
    frames = int(duree * FPS)
    if media is None:
        src = ["-loop", "1", "-t", str(duree), "-i", str(ov)]
        filtre = f"[0:v]scale={W}:{H},format=yuv420p[v]"
        run(["ffmpeg", "-y", *src, "-filter_complex", filtre, "-map", "[v]",
             "-r", str(FPS), "-c:v", "libx264", "-preset", "veryfast", "-an", str(out)])
        return
    if media.suffix.lower() in VIDEO_EXT:
        src = ["-t", str(duree), "-i", str(media)]
        base = f"[0:v]scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H},fps={FPS},setsar=1[b]"
    else:
        src = ["-loop", "1", "-t", str(duree), "-i", str(media)]
        base = (f"[0:v]scale={W*2}:{H*2}:force_original_aspect_ratio=increase,crop={W*2}:{H*2},"
                f"zoompan=z='min(zoom+0.0012,1.15)':d={frames}:x='iw/2-(iw/zoom/2)':"
                f"y='ih/2-(ih/zoom/2)':s={W}x{H}:fps={FPS},setsar=1[b]")
    filtre = f"{base};[b][1:v]overlay=0:0,format=yuv420p[v]"
    run(["ffmpeg", "-y", *src, "-loop", "1", "-t", str(duree), "-i", str(ov),
         "-filter_complex", filtre, "-map", "[v]", "-t", str(duree),
         "-r", str(FPS), "-c:v", "libx264", "-preset", "veryfast", "-an", str(out)])


def monter(storyboard: Path, out: Path):
    if not shutil.which("ffmpeg"):
        raise SystemExit("ffmpeg introuvable : installe-le (brew install ffmpeg / apt install ffmpeg).")
    sb = json.loads(storyboard.read_text(encoding="utf-8"))
    racine = storyboard.parent
    with tempfile.TemporaryDirectory() as tmp:
        tmp = Path(tmp)
        morceaux = []
        for i, s in enumerate(sb["segments"]):
            ov, seg = tmp / f"ov{i}.png", tmp / f"seg{i}.mp4"
            overlay(s.get("texte"), s.get("sous_texte"), ov)
            segment(racine / s["media"], float(s.get("duree", 2.5)), ov, seg)
            morceaux.append(seg)
        if sb.get("fin"):
            f = sb["fin"]
            ov, seg = tmp / "ovfin.png", tmp / "fin.mp4"
            overlay(f.get("texte"), f.get("sous_texte"), ov, plein=True)
            segment(None, float(f.get("duree", 2.5)), ov, seg)
            morceaux.append(seg)
        liste = tmp / "liste.txt"
        liste.write_text("".join(f"file '{m}'\n" for m in morceaux))
        muet = tmp / "muet.mp4"
        run(["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", str(liste), "-c", "copy", str(muet)])
        out.parent.mkdir(parents=True, exist_ok=True)
        if sb.get("musique"):
            run(["ffmpeg", "-y", "-i", str(muet), "-i", str(racine / sb["musique"]),
                 "-map", "0:v", "-map", "1:a", "-c:v", "copy", "-c:a", "aac", "-b:a", "192k",
                 "-af", "afade=t=out:st=0:d=0.1", "-shortest", "-movflags", "+faststart", str(out)])
        else:
            run(["ffmpeg", "-y", "-i", str(muet), "-f", "lavfi", "-i", "anullsrc=r=44100:cl=stereo",
                 "-map", "0:v", "-map", "1:a", "-c:v", "copy", "-c:a", "aac", "-shortest",
                 "-movflags", "+faststart", str(out)])
    return out


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("storyboard")
    p.add_argument("--out", required=True)
    a = p.parse_args(argv)
    print(f"écrit : {monter(Path(a.storyboard), Path(a.out))}")


if __name__ == "__main__":
    main()
