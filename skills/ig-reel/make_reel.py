#!/usr/bin/env python3
"""Monte un Reel 1080x1920 au style Brico Dépôt Andilly à partir d'un
storyboard JSON : plans filmés en dépôt avec bandeaux, cartons pleins
(rouge / blanc), étiquette prix, conseils numérotés, carton de fin.

Usage :
    python3 make_reel.py storyboard.json --out reel.mp4

Storyboard :
{
  "musique": "musique_libre_de_droits.mp3",       # optionnel
  "segments": [
    {"duree": 2,   "fond": "rouge", "blocs": [{"texte": "IL FAIT|FROID ?", "style": "titre"},
                                              {"texte": "VOTRE POÊLE A FAIM", "style": "blanc"}]},
    {"duree": 2.5, "media": "rayon.mp4", "position": "bas",
                   "blocs": [{"texte": "BAINS D'HUILE", "style": "rouge"},
                             {"texte": "UNE CHALEUR DOUCE", "style": "noir"}]},
    {"duree": 2.5, "fond": "blanc", "blocs": [{"prix": "5,29", "libelle": "Granulés|de bois",
                   "detail": "Sac de 15 kg", "tag": "STOCK XXL"}, {"espace": 30},
                   {"texte": "PRIX DÉPÔT", "style": "jaune"}]},
    {"duree": 2.5, "fin": true}
  ]
}
« media » = photo ou vidéo prise en dépôt (sinon « fond » : rouge, blanc).
Les blocs et options (flou, ruban, deco, position) sont ceux de
skills/ig-post/style.py. Les chemins sont relatifs au storyboard.
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

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "ig-post"))
from style import composer  # noqa: E402

W, H, FPS = 1080, 1920, 30
VIDEO_EXT = {".mp4", ".mov", ".m4v", ".webm", ".avi"}
APPARITION = 0.25  # fondu d'entrée des bandeaux, en secondes


def run(cmd):
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        sys.stderr.write(r.stderr[-2000:])
        raise SystemExit("ffmpeg a échoué.")


X264 = ["-r", str(FPS), "-c:v", "libx264", "-preset", "veryfast", "-crf", "20", "-pix_fmt", "yuv420p", "-an"]


def segment(seg: dict, racine: Path, tmp: Path, i: int) -> Path:
    duree = float(seg.get("duree", 2.5))
    out = tmp / f"seg{i:02d}.mp4"
    media = seg.get("media")
    frames = int(duree * FPS)

    if media and Path(racine / media).suffix.lower() in VIDEO_EXT:
        ov = tmp / f"ov{i}.png"
        composer(seg, W, H, transparent=True).save(ov)
        flou = ",boxblur=20:2" if seg.get("flou") else ""
        filtre = (f"[0:v]scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H},fps={FPS},setsar=1{flou}[b];"
                  f"[1:v]format=rgba,fade=t=in:st=0:d={APPARITION}:alpha=1[o];[b][o]overlay=0:0[v]")
        run(["ffmpeg", "-y", "-ss", str(seg.get("debut", 0)), "-t", str(duree), "-i", str(racine / media),
             "-loop", "1", "-t", str(duree), "-i", str(ov), "-filter_complex", filtre, "-map", "[v]",
             "-t", str(duree), *X264, str(out)])
        return out

    # photo ou carton plein : fond rendu par Pillow, léger zoom, bandeaux en fondu
    sc = dict(seg)
    if media:
        sc["fond"] = str(racine / media)
    fond = tmp / f"fond{i}.png"
    ov = tmp / f"ov{i}.png"
    composer({k: v for k, v in sc.items() if k not in ("blocs", "ruban", "fin")}, W, H).convert("RGB").save(fond)
    composer(sc, W, H, transparent=not sc.get("fin")).save(ov)
    zoom = "1.0015" if media else "1.0004"
    filtre = (f"[0:v]scale={W*2}:{H*2},zoompan=z='min(zoom+{float(zoom)-1},1.12)':d={frames}:"
              f"x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':s={W}x{H}:fps={FPS},setsar=1[b];"
              f"[1:v]format=rgba,fade=t=in:st=0:d={APPARITION}:alpha=1[o];[b][o]overlay=0:0[v]")
    run(["ffmpeg", "-y", "-loop", "1", "-t", str(duree), "-i", str(fond), "-loop", "1", "-t", str(duree),
         "-i", str(ov), "-filter_complex", filtre, "-map", "[v]", "-t", str(duree), *X264, str(out)])
    return out


def monter(storyboard: Path, out: Path):
    if not shutil.which("ffmpeg"):
        raise SystemExit("ffmpeg introuvable : installe-le (brew install ffmpeg / apt install ffmpeg).")
    sb = json.loads(storyboard.read_text(encoding="utf-8"))
    racine = storyboard.parent
    with tempfile.TemporaryDirectory() as tmp:
        tmp = Path(tmp)
        morceaux = [segment(s, racine, tmp, i) for i, s in enumerate(sb["segments"])]
        liste = tmp / "liste.txt"
        liste.write_text("".join(f"file '{m}'\n" for m in morceaux))
        muet = tmp / "muet.mp4"
        run(["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", str(liste), "-c", "copy", str(muet)])
        out.parent.mkdir(parents=True, exist_ok=True)
        audio = (["-i", str(racine / sb["musique"])] if sb.get("musique")
                 else ["-f", "lavfi", "-i", "anullsrc=r=44100:cl=stereo"])
        run(["ffmpeg", "-y", "-i", str(muet), *audio, "-map", "0:v", "-map", "1:a", "-c:v", "copy",
             "-c:a", "aac", "-b:a", "192k", "-shortest", "-movflags", "+faststart", str(out)])
    return out


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("storyboard")
    p.add_argument("--out", required=True)
    a = p.parse_args(argv)
    print(f"écrit : {monter(Path(a.storyboard), Path(a.out))}")


if __name__ == "__main__":
    main()
