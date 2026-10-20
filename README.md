<div align="center">

![Icône de la Boussole présidentielle 2027 : une boussole devant l'Élysée aux couleurs du drapeau français](assets/icon.png)

</div>

# Boussole présidentielle 2027

Un [skill Claude](https://docs.claude.com/en/docs/agents-and-tools/agent-skills/overview) qui vous pose de 8 à 40 questions sur les grands thèmes de la présidentielle française de 2027, puis vous montre de quels candidats vous êtes le plus proche, thème par thème, avec les sources de chaque position.

Le résultat mesure une **proximité avec des programmes**. Ce n'est pas une consigne de vote.

## Ce que fait le skill

1. Il vérifie que les données sur les candidats sont récentes.
2. Vous choisissez un mode : **rapide** (8 questions, une tendance), **moyen** (24 questions) ou **long** (40 questions, le plus fiable). Les modes courts gardent, dans chaque thème, les questions qui départagent le plus les candidats. On peut passer au mode supérieur à la fin sans recommencer.
3. Il pose les affirmations, réparties en 8 thèmes : économie, écologie, sécurité, immigration, Europe, santé et protection sociale, éducation, institutions. Vous répondez de « tout à fait d'accord » à « pas du tout d'accord », ou vous passez.
4. Il vous demande quels thèmes comptent le plus pour vous (3 au maximum).
5. Il calcule votre proximité avec chaque candidat et explique les principaux accords et désaccords, avec un lien vers la source.

Il peut aussi répondre à « quelle est la position de X sur Y ? » et mettre à jour les programmes quand la campagne avance.

## Installation

**Claude Code (plugin)** : ce dépôt est aussi une marketplace de plugins.

```
/plugin marketplace add Lcharvol/boussole-presidentielle-2027
/plugin install boussole-presidentielle-2027@lcharvol-skills
```

**Claude Code (skill seul)** : copiez le dossier du skill dans vos skills.

```bash
git clone https://github.com/Lcharvol/boussole-presidentielle-2027 /tmp/boussole && cp -r /tmp/boussole/skills/boussole-presidentielle-2027 ~/.claude/skills/
```

**Claude.ai** : zippez le dossier `skills/boussole-presidentielle-2027`, puis ajoutez-le dans *Settings → Capabilities → Skills*.

Ensuite, demandez simplement : « Pour qui voter en 2027 ? » ou « Fais-moi le test de la présidentielle ».

## Méthode

- **Positions** : chaque candidat a une fiche dans [`data/candidats/`](skills/boussole-presidentielle-2027/data/candidats/). Pour chaque question, sa position est notée de -2 à +2, avec un résumé, une URL source, une date et un niveau de confiance :
  - `programme` : écrit dans le programme officiel 2027 ;
  - `declaration` : entretien, discours ou vote récent ;
  - `deduite` : position du parti ou programme de 2022, non démentie.
  Sans source, la position reste vide (`null`) : on ne devine jamais à partir de l'étiquette politique.
- **Calcul** ([`scripts/score.py`](skills/boussole-presidentielle-2027/scripts/score.py)) : pour chaque question où vous et le candidat avez une position, l'accord vaut `1 - |écart| / 4`, de 1 (identique) à 0 (opposé). Le score est la moyenne de ces accords, pondérée par l'importance que vous donnez à chaque thème. Un candidat dont la position n'est connue que sur moins de la moitié de vos réponses est classé à part.
- **Modes** ([`scripts/choisir_niveaux.py`](skills/boussole-presidentielle-2027/scripts/choisir_niveaux.py)) : dans chaque thème, les questions sont classées selon leur pouvoir de départage (écart-type des positions des candidats × part des positions connues). La meilleure va en mode rapide, les deux suivantes en mode moyen, les autres en mode long.
- **Neutralité** : les affirmations sont posées telles quelles, sans reformulation, et les positions des candidats ne sont pas montrées pendant le questionnaire.

## Confidentialité

Vos réponses sont des opinions politiques : le skill les traite comme une donnée sensible.

- Elles restent dans votre conversation avec Claude. Le calcul se fait localement, avec les fichiers du plugin : les réponses sont transmises au script de calcul par l'entrée standard, sans être écrites dans un fichier.
- Le skill ne demande ni nom, ni e-mail, ni adresse, et n'envoie aucune donnée à un service extérieur. L'auteur ne reçoit et ne conserve rien.
- Seule la mise à jour des fiches fait des recherches web, et elles portent sur les candidats, jamais sur vos réponses.

## Limites

- La liste officielle des candidats ne sera connue qu'après la validation des parrainages par le Conseil constitutionnel. D'ici là, la liste suit les candidatures déclarées ou pressenties.
- Beaucoup de programmes ne sont pas encore publiés : une partie des positions est donc déduite.
- 40 questions ne résument pas un projet présidentiel. Lisez les programmes des candidats qui vous intéressent.
- Les fiches ont été constituées par recherche documentaire assistée par IA : des erreurs sont possibles. Signalez-les (voir ci-dessous).

## Contribuer

Une position est fausse, ou un programme vient de sortir ? Ouvrez une issue ou une pull request en citant la source. La procédure de mise à jour est décrite dans [`references/mise-a-jour.md`](skills/boussole-presidentielle-2027/references/mise-a-jour.md), et `python3 skills/boussole-presidentielle-2027/scripts/check_data.py` vérifie les fiches.

## Licence

[MIT](LICENSE)
