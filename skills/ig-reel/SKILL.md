---
name: ig-reel
description: >-
  Monte un Reel Instagram vertical (1080x1920) à partir des photos et vidéos
  prises en dépôt : écrit le storyboard, pose les textes en bandeaux au style
  Brico Dépôt, ajoute le carton de fin et la musique, puis assemble avec
  make_reel.py (ffmpeg). Utiliser pour « reel », « vidéo », « montage »,
  « TikTok », ou une ligne REEL du rétro-planning.
---

# ig-reel

## Étapes

1. Lire `~/.claude/instagram/depot.md` et l'opération du `bic/AAAA-MM.json`.
2. **Écrire le storyboard d'abord**, le faire valider, puis seulement monter.
   Structure qui marche pour un dépôt (15 à 25 secondes) :

   | Temps | Plan | Texte |
   | --- | --- | --- |
   | 0-2 s | Le problème, en mouvement | « IL FAIT FROID ? » |
   | 2-8 s | Le produit dans le rayon d'Andilly | Nom du produit |
   | 8-14 s | Le geste : un vendeur montre, explique | Le conseil en 5 mots |
   | 14-18 s | L'étiquette prix en vrai | Prix + dates |
   | 18-20 s | Carton de fin | « ALLEZ, AUX TRAVAUX ! » |

3. Donner à l'utilisateur la **liste de tournage** : plans à filmer au
   téléphone, à la verticale, 3 à 5 secondes chacun, lumière du rayon.
4. Écrire `storyboard.json` à côté des médias (format en tête de
   `make_reel.py`), puis :

   ```bash
   python3 make_reel.py chemin/storyboard.json --out reel.mp4
   ```

5. Vérifier une image au milieu et à la fin (`ffmpeg -ss 5 -i reel.mp4 -frames:v 1 check.png`),
   corriger les textes qui débordent.
6. Écrire la légende comme `/ig-post`, puis passer à `/ig-publish`.

## Règles

- Musique : uniquement libre de droits ou ajoutée ensuite depuis la
  bibliothèque Instagram. Un son commercial dans le fichier = reel muté.
- Texte lisible en 1 seconde : 4 mots max par bandeau, ne rien mettre dans
  les 250 px du bas (interface Instagram).
- Visages : autorisation écrite de chaque collègue ou client filmé.
- Pas de logo redessiné : `--logo` avec le fichier officiel seulement.
