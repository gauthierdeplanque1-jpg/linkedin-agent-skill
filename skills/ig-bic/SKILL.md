---
name: ig-bic
description: >-
  Lit le B.I.C. (Book d'Implantation Commerciale) mensuel de Brico Dépôt en
  PDF et en extrait ce qui sert à Instagram : opérations hebdo, dates, hero
  products, thématiques, temps forts, opérations fournisseurs. Écrit
  bic/AAAA-MM.json. Utiliser dès que l'utilisateur dépose un B.I.C., un book
  d'implantation, un planning des opérations ou dit « voilà le BIC du mois ».
---

# ig-bic

Le B.I.C. est la source unique du mois. Cette skill le transforme en un
fichier structuré que `/ig-plan`, `/ig-post` et `/ig-reel` lisent ensuite.

## Étapes

1. **Lire le PDF entier**, par tranches de pages. Les pages utiles sont en
   général : Ambitions, Planning des opérations, Enjeux des opérations, Hero
   product, Produits de Noël / Fondation, Médiatisation, Calendrier PLV,
   Anti-inflation, Parcours client.
2. **Remplir `bic/AAAA-MM.json`** selon `schema.json` (dans ce dossier) :
   - `operations` : code (OP S45), thème, date de début et de fin (lire le
     tableau « Planning des opérations », colonne Date), catégories
     prioritaires, hero products (EAN + libellé lisible, pas en majuscules).
   - `thematiques` : fils rouges du mois (anti-inflation, Black Week…) avec
     le message client tel qu'il apparaît sur la PLV.
   - `temps_forts` : jours fériés, ponts, Black Friday, lancement Fondation,
     relais radio/TV nationaux.
   - `fournisseurs`, `pros` : seulement l'angle client.
3. **Filtrer.** Ne recopier AUCUNE donnée interne : CA, engagement, % vs N-1,
   noms et contacts du siège, liens SharePoint/Power BI, codes internes
   (Easier, Legacy). Si un champ manque, le laisser vide, ne pas l'inventer.
4. **Signaler les incohérences** au lieu de trancher seul. Exemple fréquent :
   le thème d'une semaine diffère entre le tableau des dates et le résumé.
   Prendre les dates du tableau, et poser la question en une ligne.
5. **Enchaîner** : proposer de lancer `/ig-plan` sur le fichier produit.

## Où ranger

`bic/` est ignoré par git (sauf `bic/README.md`) : le B.I.C. est un document
interne, il ne doit pas finir dans un dépôt public.
