---
name: ig-post
description: >-
  Crée une publication Instagram pour un dépôt Brico Dépôt : légende, hashtags,
  et visuels au style de l'enseigne (post 4:5, carré, story, carrousel) générés
  par make_visual.py à partir des photos prises en dépôt. Utiliser pour « fais
  un post », « carrousel », « story », « visuel promo », ou une ligne PUBLI du
  rétro-planning.
---

# ig-post

## Avant d'écrire

1. Lire `~/.claude/instagram/depot.md` (copie de `templates/depot.md`). S'il
   n'existe pas, le créer avec l'utilisateur avant tout : ton, hashtags,
   personne qui valide.
2. Lire `bic/AAAA-MM.json` pour l'opération en cours : thème, dates, hero products.
3. Demander les **photos réelles** du dépôt. Une photo du rayon d'Andilly bat
   n'importe quel visuel générique : c'est ce que le compte national n'a pas.
4. Un prix n'apparaît que si l'utilisateur le donne ou s'il figure dans le
   B.I.C. côté client (étiquette, catalogue). Sinon : `{{prix}}` et un drapeau.

## Les formats

| Format | Quand | Commande |
| --- | --- | --- |
| Post 4:5 | Un produit, un prix | `--format post` |
| Carrousel | 3 à 6 produits, un conseil en étapes | un visuel par slide |
| Story | Rappel, sondage, derniers jours | `--format story` |

```bash
python3 make_visual.py --titre "RADIATEUR|À INERTIE" --sous-titre "Céramique 1000 W" \
  --prix 89 --mention "Du 06/11 au 12/11, dans la limite des stocks" \
  --badge "Chauffage & isolation" --photo rayon.jpg --logo logo_officiel.png --out post.png
```

Carrousel : slide 1 = la promesse (« 3 radiateurs pour passer l'hiver »),
slides 2 à n-1 = un produit chacun, dernière slide = « Allez, aux travaux ! »
+ adresse du dépôt.

## La légende

```
Ligne 1   l'accroche, visible avant « plus » (≤ 125 caractères)
Corps     2 à 4 lignes courtes : le produit, le prix, pour qui, pourquoi maintenant
Local     « Dispo à Brico Dépôt Andilly » + dates de l'offre
Action    une seule : « Enregistre pour ton chantier », « Dis-nous en commentaire… »
Hashtags  5 à 8, en fin de légende
```

Toujours : dates de validité, « dans la limite des stocks disponibles ».
Jamais : chiffres internes du B.I.C., jargon (OP, KBS, TDR, Animaco).

## Fin

Afficher le visuel et la légende dans un bloc prêt à copier. Ne rien publier :
la publication passe par `/ig-publish`, après un « oui » explicite.
