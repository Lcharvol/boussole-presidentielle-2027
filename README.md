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
- **Calcul** ([`scripts/score.py`](skills/boussole-presidentielle-2027/scripts/score.py)) : pour chaque question où vous et le candidat avez une position, l'accord brut vaut `1 - |écart| / 4`, de 1 (identique) à 0 (opposé). Le score est la moyenne pondérée de ces accords, après deux corrections décrites plus bas. Le poids d'une question est l'importance que vous donnez à son thème (1 à 3) multipliée par la confiance dans la position du candidat : 1 pour `programme`, 0,85 pour `declaration`, 0,6 pour `deduite`. Une position déduite compte donc, mais moins qu'un engagement écrit. Le score est affiché de 0 à 100 % : 50 % veut dire « pas plus proche que des réponses au hasard », 100 % « mêmes réponses partout ». Un candidat dont la position n'est connue que sur moins de la moitié de vos réponses est classé à part.
- **Correction du hasard** : avec l'accord brut, une position nuancée (0) est en moyenne plus proche d'une réponse quelconque (accord moyen 0,7) qu'une position tranchée (0,5 pour ±2). Face à des réponses sans opinion, les candidats aux positions modérées sortaient donc premiers bien plus souvent que les autres, quel que soit leur camp (voir l'audit). Chaque accord est donc corrigé du hasard, comme un kappa de Cohen : `(accord - accord_hasard) / (1 - accord_hasard)`, où `accord_hasard` est l'accord moyen de la position du candidat avec une réponse tirée au hasard (0,7 à 0 ; 0,65 à ±1 ; 0,5 à ±2). L'accord corrigé vaut 1 pour une réponse identique, 0 pour un accord égal au hasard, et il est négatif en dessous. Toutes les positions ont ainsi la même espérance face au hasard ; une personne aux opinions nuancées reste bien sûr plus proche des candidats nuancés.
- **Positions inconnues** : une question à laquelle vous avez répondu mais sur laquelle on ne connaît pas la position du candidat compte comme un accord égal au hasard (0), avec un poids de √2 - 1 ≈ 0,41 fois l'importance du thème (multiplié par la confiance moyenne des positions connues du candidat, pour que des positions surtout déduites ne soient pas davantage rapprochées de 50 %). Sans cela, le score d'un candidat peu renseigné repose sur moins de questions, varie davantage, et le place plus souvent tout en haut (ou tout en bas) du classement : les fiches les moins remplies étaient avantagées. Ce poids n'est pas réglé à la main : c'est la valeur pour laquelle la dispersion du score face à des réponses au hasard est la même à 50 % et à 100 % de couverture (et à 2 % près entre les deux). Un poids de 1 pénaliserait les fiches incomplètes, un poids nul les avantagerait. Un candidat peu renseigné voit donc son score rapproché de 50 %, d'autant plus qu'il lui manque de positions, et sa marge en tient compte.
- **Marge d'incertitude** : chaque score est affiché avec une marge (« 72 ± 8 % »). Elle est obtenue par rééchantillonnage (bootstrap) : 1 000 fois, on tire au hasard, avec remise, autant de questions que vous en avez répondu, et on recalcule le score. La marge est la moitié de l'intervalle qui contient 90 % des scores obtenus ; elle mesure à quel point le résultat dépend du choix des questions. La graine est fixe : les mêmes réponses donnent toujours le même résultat. Quand l'intervalle d'un candidat recouvre celui du premier, le skill le signale : leur ordre n'est pas significatif. Avec peu de réponses, les marges sont larges et ce recouvrement est fréquent ; le mode long les resserre.
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

**Résultats actuels** (21 octobre 2026, après la relecture humaine des 565 positions, graine 2027 ; le résumé de la CI donne les chiffres à jour) :

- L'axe calculé explique la moitié des écarts entre candidats et place à un bout les candidats habituellement classés à gauche, à l'autre ceux classés à droite, sans qu'on le lui ait indiqué.
- **Pas d'avantage au centre ni de biais de camp.** Avec des réponses au hasard, les trois tiers de l'axe sortent premiers aussi souvent qu'attendu en mode long (ratios 1,05 à gauche, 1,01 au centre, 0,94 à droite). Avant la correction du hasard et des positions inconnues (voir Méthode), le centre sortait premier 1,8 fois plus souvent qu'attendu, et Dominique de Villepin 5 fois plus. Aucun candidat classé n'est plus nettement sur- ou sous-représenté.
- **Formulations équilibrées.** En mode long, 16 affirmations orientent « d'accord » vers le pôle gauche, 16 vers le pôle droit, 6 sont transversales ; en mode rapide, 3 contre 4 (une transversale) ; en mode moyen, 12 contre 9. Quatre affirmations ont été retournées pour y arriver (`eco_depenses`, `sec_mineurs`, `soc_medecins`, `eur_defense3`), en gardant le même enjeu ; les positions des candidats ont été inversées en conséquence. Un profil qui répond plus souvent « d'accord » ne se déplace plus que de quelques points (-5 en mode long, +4 en mode rapide, contre +31 auparavant en mode rapide).
- **Mode rapide : un écart résiduel.** Le tiers droit y sort premier un peu moins souvent qu'attendu (ratio 0,87, contre 1,07 à gauche et 1,05 au centre). Sur ces 8 questions, les candidats de ce tiers ont des positions très proches entre eux (écart moyen 0,80 contre 0,94 à gauche) et se partagent donc les premières places. Le mode rapide reste une tendance ; le mode long est à privilégier.
- **Couverture inégale.** 8 candidats ont moins de la moitié de leurs positions renseignées ; plusieurs ne sont jamais classés en mode long. La correction des positions inconnues empêche qu'ils soient avantagés, mais seule la complétion des fiches leur donne une place juste. L'audit liste les fiches et les questions à compléter en priorité.

## Confidentialité

Vos réponses sont des opinions politiques : le skill les traite comme une donnée sensible.

- Elles restent dans votre conversation avec Claude. Le calcul se fait localement, avec les fichiers du plugin : les réponses sont transmises au script de calcul par l'entrée standard, sans être écrites dans un fichier.
- Le skill ne demande ni nom, ni e-mail, ni adresse, et n'envoie aucune donnée à un service extérieur. L'auteur ne reçoit et ne conserve rien.
- Seule la mise à jour des fiches fait des recherches web, et elles portent sur les candidats, jamais sur vos réponses.

## Limites

- La liste officielle des candidats ne sera connue qu'après la validation des parrainages par le Conseil constitutionnel. D'ici là, la liste suit les candidatures déclarées ou pressenties.
- Beaucoup de programmes ne sont pas encore publiés : une partie des positions est donc déduite.
- 40 questions ne résument pas un projet présidentiel. Lisez les programmes des candidats qui vous intéressent.
- Les fiches ont été constituées par recherche documentaire assistée par IA, puis **relues une à une par un humain** (octobre 2026) : chaque position a une citation vérifiée et le champ `relu`. Les arbitrages de codage sont décrits dans [`references/mise-a-jour.md`](skills/boussole-presidentielle-2027/references/mise-a-jour.md). Des erreurs restent possibles : signalez-les (voir ci-dessous).

## Contribuer

Une position est fausse, ou un programme vient de sortir ? Ouvrez une issue ou une pull request en citant la source. La procédure de mise à jour est décrite dans [`references/mise-a-jour.md`](skills/boussole-presidentielle-2027/references/mise-a-jour.md), et `python3 skills/boussole-presidentielle-2027/scripts/check_data.py` vérifie les fiches.

## Licence

[MIT](LICENSE)
