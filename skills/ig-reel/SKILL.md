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
   Les structures qui marchent sur le compte (13 à 18 secondes, 4 à 6 plans) :

   | Type | Enchaînement | Exemple |
   | --- | --- | --- |
   | Produit saison | carton rouge accroche → plans rayon avec bandeaux → étiquette prix → fin | `exemples/granules.json` |
   | Conseil | carton « 3 ERREURS » (damier) → 01, 02, 03 sur rouge + carte « bonne pratique » → fin | `exemples/conseil-carrelage.json` |
   | Pros / arrivage | « CHANTIER EN VUE ? » sur la machine → nom + marque → « ARRIVAGE, quantités limitées » → fin | |
   | Événement | carton blanc à points « SOIRÉE PRIVILÈGE » + date → « JUSQU'À -70 % » → fin avec horaires de la soirée | |
   | Annonce dépôt | vidéo floutée + rubans de chantier + bandeaux empilés → fin | `exemples/travaux.json` |
   | Nouveautés | carton « DU NEUF » → photos avec tag NOUVEAUTÉ → étiquettes prix des modèles exposés → « ET EN RAYON » → fin | `exemples/nouveautes-sas.json` |

3. Donner à l'utilisateur la **liste de tournage** : plans à filmer au
   téléphone, à la verticale, 3 à 5 secondes chacun, sans texte incrusté.
4. Écrire `storyboard.json` à côté des médias (format en tête de
   `make_reel.py`, blocs décrits dans `skills/ig-post/style.py`), puis :

   ```bash
   python3 make_reel.py chemin/storyboard.json --out reel.mp4
   ```

   Le carton de fin (`{"fin": true}`) reprend l'adresse, les horaires et le
   téléphone de `~/.claude/instagram/depot.json` (modèle : `templates/depot.json`).
   Pour une soirée, remplacer les horaires par ceux de l'événement dans une
   scène dédiée.

5. Vérifier une image au milieu et à la fin (`ffmpeg -ss 5 -i reel.mp4 -frames:v 1 check.png`),
   corriger les textes qui débordent.
6. Écrire la légende comme `/ig-post`, puis passer à `/ig-publish`.

## Règles

- Musique : uniquement libre de droits ou ajoutée ensuite depuis la
  bibliothèque Instagram. Un son commercial dans le fichier = reel muté.
- Texte lisible en 1 seconde : 4 mots max par bandeau ; les blocs restent
  au-dessus des 260 px du bas (interface Instagram).
- Un « {{...}} » dans un exemple = une info à demander, jamais à inventer.
- Visages : autorisation écrite de chaque collègue ou client filmé.
- Pas de logo redessiné : le carton de fin écrit « BRICO DÉPÔT » en bandeau, comme sur le compte.
