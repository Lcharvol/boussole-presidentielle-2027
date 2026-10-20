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

## Audit de neutralité

Le script [`scripts/audit_biais.py`](skills/boussole-presidentielle-2027/scripts/audit_biais.py) vérifie que le résultat ne favorise pas mécaniquement un camp. Il tourne à chaque pull request : le rapport complet est publié dans le résumé du job de CI, sans jamais la faire échouer. Pour le lancer :

```bash
python3 skills/boussole-presidentielle-2027/scripts/audit_biais.py
```

Il fait trois choses :

1. **Un axe calculé, sans étiquette.** À partir des seules positions des candidats, il calcule l'axe qui les sépare le plus (première composante principale). Aucune question ni aucun candidat n'est classé à la main ; seul le sens de l'axe est orienté, pour l'affichage. L'axe est ensuite découpé en trois tiers : « gauche », « centre », « droite ».
2. **Le sens des formulations.** Pour chaque affirmation, il mesure si « d'accord » rapproche plutôt des candidats d'un pôle ou de l'autre (corrélation avec l'axe recalculé sans cette question). Si beaucoup d'affirmations penchent du même côté, une personne qui répond souvent « d'accord » est poussée vers ce pôle.
3. **Des profils au hasard.** Il tire 2 000 profils sans opinion (réponses au hasard, 10 % de « je passe »), les passe dans le calcul de `score.py` et compte qui sort premier ou dans les trois premiers, en mode long et en mode rapide. Un calcul neutre donnerait à chaque candidat classé la même chance ; l'attendu tient compte des candidats exclus faute de positions connues.

**Résultats actuels** (20 octobre 2026, graine 2027 ; le résumé de la CI donne les chiffres à jour) :

- L'axe calculé explique la moitié des écarts entre candidats et place à un bout les candidats habituellement classés à gauche, à l'autre ceux classés à droite, sans qu'on le lui ait indiqué.
- **Mode long : pas de biais de camp.** Avec des réponses au hasard, les tiers gauche et droit sortent premiers presque aussi souvent l'un que l'autre (ratios 0,69 et 0,65). Les affirmations sont à peu près équilibrées : 14 orientent « d'accord » vers le pôle gauche, 18 vers le pôle droit, 6 sont transversales ; un profil qui répond plus souvent « d'accord » ne gagne que 3 points côté droit. Le mode moyen est équilibré aussi (11 contre 10).
- **Le centre est avantagé** (ratio 1,87 en mode long) : un score qui mesure l'écart favorise les positions modérées face à des réponses au hasard, et les fiches les moins remplies (Dominique de Villepin, Bernard Cazeneuve) donnent des scores plus variables, donc plus souvent en tête. Les candidats aux positions les plus tranchées et les mieux documentées (Jean-Luc Mélenchon, Marine Tondelier, Marine Le Pen) sortent moins souvent premiers. Avec des vraies réponses, qui ne sont pas aléatoires, cet effet est bien plus faible, mais il existe.
- **Mode rapide : déséquilibre des formulations.** Sur ses 8 questions, 6 orientent « d'accord » vers le pôle droit et une seule vers le pôle gauche : un profil qui acquiesce souvent gagne 32 points côté droit, un profil qui conteste souvent va presque toujours à gauche. Le mode rapide reste une tendance ; le mode long est à privilégier.
- **Couverture inégale.** 8 candidats ont moins de la moitié de leurs positions renseignées ; plusieurs ne sont jamais classés en mode long. C'est la cause la plus probable des écarts entre candidats, avant le calcul lui-même. L'audit liste les fiches et les questions à compléter en priorité.

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
