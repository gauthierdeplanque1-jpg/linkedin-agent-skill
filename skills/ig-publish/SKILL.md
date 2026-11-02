---
name: ig-publish
description: >-
  Publie (ou programme via une tâche planifiée) un post, carrousel, reel ou
  story sur le compte Instagram professionnel du dépôt, par l'API officielle
  de Meta. Toujours en aperçu d'abord ; publie seulement après un « oui »
  explicite. Utiliser pour « publie », « poste-le », « programme pour vendredi ».
---

# ig-publish

## Pourquoi l'API officielle

Instagram autorise la publication automatique **uniquement** par son API
(Instagram Graph API, « Content Publishing ») sur un compte professionnel.
Les bots qui pilotent un navigateur ou l'API privée (instagrapi,
Playwright + cookies…) violent les conditions d'utilisation et font
bloquer les comptes. Pour un compte d'enseigne, c'est exclu.

## Mise en place (une fois)

1. Compte Instagram du dépôt en **compte professionnel** (Business).
2. Feu vert du siège (service Réseaux sociaux) pour un compte local et pour
   l'accès API : le compte porte la marque.
3. Sur developers.facebook.com : créer une app, ajouter le produit
   « Instagram » (connexion Instagram), ajouter le compte comme testeur,
   générer un jeton avec `instagram_business_basic` et
   `instagram_business_content_publish`. Pour un usage sur son propre compte,
   le mode développement suffit ; l'App Review n'est nécessaire que pour
   publier sur des comptes tiers.
4. Exporter :

   ```bash
   export IG_USER_ID=...        # renvoyé par GET /me?fields=user_id
   export IG_ACCESS_TOKEN=...   # jeton longue durée, à renouveler avant 60 jours
   ```

   Ne jamais committer le jeton.
5. Héberger les médias à une URL publique (Meta va les chercher).

## Le geste

```bash
python3 publish.py reel --url https://.../reel.mp4 --legende legende.txt          # aperçu
python3 publish.py reel --url https://.../reel.mp4 --legende legende.txt --oui    # publie
python3 publish.py quota                                                          # quota 24 h
```

1. Toujours lancer l'aperçu, le montrer, et demander « je publie ? ».
2. `--oui` seulement après un oui explicite dans la conversation. Un oui pour
   un post ne vaut pas pour le suivant.
3. Renvoyer le lien de la publication.

## Programmer

L'API publie immédiatement. Pour « vendredi 8 h », créer une tâche planifiée
qui lance la commande `--oui` à l'heure dite, après validation du contenu.
Alternative sans code : Meta Business Suite (programmation native, gratuite)
ou un planificateur open source comme Postiz.
