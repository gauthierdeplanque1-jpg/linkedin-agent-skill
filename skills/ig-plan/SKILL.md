---
name: ig-plan
description: >-
  Construit le rétro-planning Instagram du mois à partir du B.I.C. structuré
  (bic/AAAA-MM.json) : pour chaque opération, brief, tournage, montage,
  validation et programmation remontés depuis la date de lancement, puis les
  publications pendant l'opération et les rubriques « ce qu'on ne voit pas ».
  Utiliser pour « planning du mois », « rétro-planning », « qu'est-ce qu'on
  poste cette semaine », ou juste après /ig-bic.
---

# ig-plan

## Étapes

1. Vérifier que `bic/AAAA-MM.json` existe. Sinon, lancer `/ig-bic` d'abord.
2. Lancer le calcul (rien d'inventé, tout vient des dates du B.I.C.) :

   ```bash
   python3 retroplanning.py bic/AAAA-MM.json --out plans/AAAA-MM.md --csv plans/AAAA-MM.csv
   ```

3. Relire le résultat avec l'utilisateur et ajuster à la main :
   - **EN RETARD** : la tâche est ramenée à aujourd'hui. S'il y en a plus de
     trois le même jour, proposer de couper (story au lieu de reel, un seul
     hero product au lieu de deux).
   - Rubriques « Coulisses » (mardi) et « 1 minute avec… » (jeudi) : les
     décaler si elles tombent sur un jour de lancement.
   - Ajouter les jours de fermeture et les événements locaux du dépôt
     (`~/.claude/instagram/depot.md`).
4. Pour la semaine en cours, transformer chaque ligne PUBLI en une ligne
   d'action : qui filme quoi, dans quel rayon, avec quel produit.
5. Proposer d'enchaîner sur `/ig-reel` ou `/ig-post` pour la prochaine publication.

## Le gabarit de rétro-planning (J0 = lancement de l'opération)

| Jour | Étape |
| --- | --- |
| J-6 | Brief : 2 hero products + 1 angle « ce qu'on ne voit pas » |
| J-4 | Tournage en dépôt (autorisations droit à l'image signées) |
| J-3 | Montage du reel + carrousel |
| J-2 | Validation directeur (prix, dates, mentions) |
| J-1 | Programmation |
| J0 | Reel de lancement + story |
| J+2 | Carrousel conseil / produits en rayon |
| J+4 | Story sondage ou quiz |
| Fin-1 | Story « derniers jours » |

Temps forts (pont, Black Friday, Fondation) : préparation J-3, teaser J-1, story J0.
Le gabarit se modifie en haut de `retroplanning.py`.

## Rythme cible

3 à 4 publications feed par semaine + stories quotidiennes. Mieux vaut
3 publications tenues que 7 prévues et abandonnées.
