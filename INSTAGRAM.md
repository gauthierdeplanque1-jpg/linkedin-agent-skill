# Agent Instagram · Brico Dépôt Andilly

Cinq skills Claude qui transforment le B.I.C. du mois en publications
Instagram au style de l'enseigne, avec en plus ce que le compte national ne
montre pas : les coulisses, l'équipe, les prix en vrai dans les rayons d'Andilly.

```
 B.I.C. (PDF)  ──/ig-bic──▶  bic/2026-11.json  ──/ig-plan──▶  rétro-planning du mois
                                    │
          photos & vidéos du dépôt ─┼──/ig-post──▶  visuels + légende
                                    └──/ig-reel──▶  reel 1080x1920
                                                         │
                                         « oui »  ──/ig-publish──▶  Instagram (API Meta)
```

| Commande | Rôle |
| --- | --- |
| `/ig-bic` | Lit le PDF du B.I.C., garde ce qui sert aux clients, écrit `bic/AAAA-MM.json` |
| `/ig-plan` | Rétro-planning : brief J-6, tournage J-4, montage J-3, validation J-2, programmation J-1, publication J0, relances |
| `/ig-post` | Post, carrousel, story au style du compte (bandeaux Montserrat, étiquette prix, rubans de chantier, carton de fin) + légende + hashtags |
| `/ig-reel` | Storyboard, liste de tournage, montage vidéo (`make_reel.py`, ffmpeg) ; 3 exemples dans `skills/ig-reel/exemples/` |
| `/ig-publish` | Publication par l'API officielle Instagram, aperçu d'abord, `--oui` ensuite |

## Installation

```bash
git clone <ce dépôt> && cd linkedin-agent-skill
cp -r skills/ig-* ~/.claude/skills/
# les scripts trouvent la police Montserrat dans fonts/ : lance-les depuis ce dépôt
mkdir -p ~/.claude/instagram && cp templates/depot.md templates/depot.json ~/.claude/instagram/
pip install pillow            # visuels
brew install ffmpeg           # ou apt install ffmpeg : montage vidéo
```

Puis remplir `~/.claude/instagram/depot.md` (10 minutes) et, dans Claude Code :
« voilà le BIC de décembre » + le PDF.

## Chaque mois

1. Le B.I.C. arrive → `/ig-bic` → `/ig-plan`.
2. Chaque lundi : relire la semaine du rétro-planning, faire la liste de tournage.
3. Tournage au téléphone pendant les heures calmes (10 minutes par sujet).
4. `/ig-reel` et `/ig-post` sur les médias → validation du directeur.
5. `/ig-publish` (ou tâche planifiée) le jour J.

Le rétro-planning tient compte du retard : si le B.I.C. arrive à J-4, les
étapes déjà dépassées sont ramenées à aujourd'hui et marquées EN RETARD.

## Ce qui existe déjà sur GitHub (et pourquoi on ne s'en sert pas tel quel)

| Projet | Ce qu'il fait | Limite pour un compte d'enseigne |
| --- | --- | --- |
| [xtea/auto-instagram](https://github.com/xtea/auto-instagram) | Publie posts, carrousels, reels | Pilote instagram.com avec les cookies du navigateur, pas l'API : contraire aux conditions d'Instagram |
| [alsk1992/instagram-ai-agent](https://github.com/alsk1992/instagram-ai-agent) | Agent complet : planification, reels sous-titrés | À vérifier : API officielle ou session navigateur ? Pas pensé pour un calendrier commercial |
| [Avnsh1111/Instagram-Reels-Scraper-Auto-Poster](https://github.com/Avnsh1111/Instagram-Reels-Scraper-Auto-Poster) | Reposte des vidéos récupérées ailleurs | Republier le contenu des autres : exclu |
| [dhohirpradana/Instagram-Automation](https://github.com/dhohirpradana/Instagram-Automation) | Publication planifiée via GitHub Actions | Feed et stories seulement |
| Postiz (open source) | Planificateur multi-réseaux | Bon pour programmer ; ne lit pas le B.I.C. et ne fait pas les visuels |

Aucun ne part d'un B.I.C. ni ne connaît le calendrier des opérations. D'où
ces skills : elles construisent le contenu, et la publication passe par
l'API officielle ou par Meta Business Suite.

## Les règles du jeu

- **Feu vert du siège.** Le compte porte la marque Brico Dépôt : le service
  Réseaux sociaux (Activation & Médias) doit valider le compte local, le
  logo et les accès API.
- **Le B.I.C. est interne.** `bic/*.json` et `plans/` sont ignorés par git.
  Sur Instagram, seulement ce qu'un client voit déjà en dépôt.
- **Droit à l'image.** Autorisation écrite de chaque collègue ou client filmé.
- **Prix et promotions.** Dates de validité, « dans la limite des stocks »,
  prix identique à l'étiquette en dépôt.
- **Rien ne part sans « oui ».** `publish.py` n'envoie rien sans `--oui`.
