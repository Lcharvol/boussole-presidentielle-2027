<div align="center">

![Icône de la Boussole présidentielle 2027 : une boussole devant l'Élysée aux couleurs du drapeau français](assets/icon.png)

</div>

# Boussole présidentielle 2027

Un [skill Claude](https://docs.claude.com/en/docs/agents-and-tools/agent-skills/overview) qui vous pose de 12 à 62 questions sur les grands enjeux de la présidentielle française de 2027, puis vous montre de quels candidats vous êtes le plus proche, thème par thème, avec les sources de chaque position.

Le résultat mesure une **proximité avec des programmes**. Ce n'est pas une consigne de vote.

## Ce que fait le skill

1. Il vérifie que les données sur les candidats sont récentes.
2. Vous choisissez un mode : **rapide** (12 questions, une tendance), **adaptatif** (12 questions, puis des lots choisis pour départager les candidats dont vous êtes le plus proche, jusqu'à ce que le résultat soit assez précis) ou **complet** (tous les enjeux, le plus fiable). On peut continuer à la fin sans recommencer.
3. Il pose des dilemmes sur 8 thèmes : économie, écologie, sécurité, immigration, Europe, santé et protection sociale, éducation, institutions. Chaque question oppose deux options légitimes (« Face à la surpopulation carcérale, que faut-il privilégier ? Construire de nouvelles places de prison / Développer les peines alternatives ») ; vous indiquez de laquelle vous êtes le plus proche, sur cinq crans, ou vous passez. Les enjeux, leur ordre, leur formulation et le côté où chaque option est affichée sont tirés au hasard à chaque passage.
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

- **Enjeux** ([`data/enjeux.json`](skills/boussole-presidentielle-2027/data/enjeux.json), format décrit dans [`data/FORMAT.md`](skills/boussole-presidentielle-2027/data/FORMAT.md)) : chaque enjeu oppose deux pôles, A et B, et a deux ou trois formulations équivalentes. Les deux options ont la même dignité : pas d'intensif, pas de vocabulaire propre à un camp, une longueur et une concrétude comparables.
- **Positions** : chaque candidat a une fiche dans [`data/candidats/`](skills/boussole-presidentielle-2027/data/candidats/). Pour chaque enjeu, sa position est notée de -2 (pôle A) à +2 (pôle B), avec un résumé, une URL source, une date et un niveau de confiance :
  - `programme` : écrit dans le programme officiel 2027 ;
  - `declaration` : entretien, discours ou vote récent ;
  - `deduite` : position du parti ou programme de 2022, non démentie.
  Sans source, la position reste vide (`null`) : on ne devine jamais à partir de l'étiquette politique.
- **Calcul** ([`scripts/score.py`](skills/boussole-presidentielle-2027/scripts/score.py)) : pour chaque question où vous et le candidat avez une position, l'accord brut vaut `1 - |écart| / 4`, de 1 (identique) à 0 (opposé). Le score est la moyenne pondérée de ces accords, après deux corrections décrites plus bas. Le poids d'une question est l'importance que vous donnez à son thème (1 à 3) multipliée par la confiance dans la position du candidat : 1 pour `programme`, 0,85 pour `declaration`, 0,6 pour `deduite`. Une position déduite compte donc, mais moins qu'un engagement écrit. Le score est affiché de 0 à 100 % : 50 % veut dire « pas plus proche que des réponses au hasard », 100 % « mêmes réponses partout ». Un candidat dont la position n'est connue que sur moins de la moitié de vos réponses est classé à part. Le classement suit le score exact, avant arrondi : deux candidats affichés au même pourcentage ne sont pas départagés par le nombre de leurs positions connues, ce qui avantageait les fiches les plus remplies (voir [l'analyse de l'audit](docs/audit-62-enjeux.md)).
- **Correction du hasard** : avec l'accord brut, une position nuancée (0) est en moyenne plus proche d'une réponse quelconque (accord moyen 0,7) qu'une position tranchée (0,5 pour ±2). Face à des réponses sans opinion, les candidats aux positions modérées sortaient donc premiers bien plus souvent que les autres, quel que soit leur camp (voir l'audit). Chaque accord est donc corrigé du hasard, comme un kappa de Cohen : `(accord - accord_hasard) / (1 - accord_hasard)`, où `accord_hasard` est l'accord moyen de la position du candidat avec une réponse tirée au hasard (0,7 à 0 ; 0,65 à ±1 ; 0,5 à ±2). L'accord corrigé vaut 1 pour une réponse identique, 0 pour un accord égal au hasard, et il est négatif en dessous. Toutes les positions ont ainsi la même espérance face au hasard ; une personne aux opinions nuancées reste bien sûr plus proche des candidats nuancés.
- **Positions inconnues** : une question à laquelle vous avez répondu mais sur laquelle on ne connaît pas la position du candidat compte comme un accord égal au hasard (0), avec un poids de √2 - 1 ≈ 0,41 fois l'importance du thème (multiplié par la confiance moyenne des positions connues du candidat, pour que des positions surtout déduites ne soient pas davantage rapprochées de 50 %). Sans cela, le score d'un candidat peu renseigné repose sur moins de questions, varie davantage, et le place plus souvent tout en haut (ou tout en bas) du classement : les fiches les moins remplies étaient avantagées. Ce poids n'est pas réglé à la main : c'est la valeur pour laquelle la dispersion du score face à des réponses au hasard est la même à 50 % et à 100 % de couverture (et à 2 % près entre les deux). Un poids de 1 pénaliserait les fiches incomplètes, un poids nul les avantagerait. Un candidat peu renseigné voit donc son score rapproché de 50 %, d'autant plus qu'il lui manque de positions, et sa marge en tient compte.
- **Marge d'incertitude** : chaque score est affiché avec une marge (« 72 ± 8 % »). Elle est obtenue par rééchantillonnage (bootstrap) : 1 000 fois, on tire au hasard, avec remise, autant de questions que vous en avez répondu, et on recalcule le score. La marge est la moitié de l'intervalle qui contient 90 % des scores obtenus ; elle mesure à quel point le résultat dépend du choix des questions. La graine est fixe : les mêmes réponses donnent toujours le même résultat. Quand l'intervalle d'un candidat recouvre celui du premier, le skill le signale : leur ordre n'est pas significatif. Avec peu de réponses, les marges sont larges et ce recouvrement est fréquent ; le mode complet les resserre.
- **Tirage** ([`scripts/tirage.py`](skills/boussole-presidentielle-2027/scripts/tirage.py)) : le mode rapide tire 12 enjeux, au moins un par thème, en favorisant ceux qui départagent le plus les candidats (écart-type de leurs positions × part des positions connues) sans exclure les autres. Le mode adaptatif part de ces 12, puis ajoute des lots de 4 enjeux choisis pour départager les candidats dont la marge recouvre celle du premier, et s'arrête quand le premier se détache, quand les enjeux restants ne départagent plus ces candidats, ou à 32 questions. L'ordre alterne les thèmes ; la formulation et le côté de chaque option sont tirés au hasard. Tout dépend d'une graine : avec la même graine et les mêmes réponses, le tirage est identique (tests, reprise).
- **Neutralité** : les formulations sont posées telles quelles, sans reformulation, et les positions des candidats ne sont pas montrées pendant le questionnaire. Chaque formulation passe le test « devine le camp » ([rapport](docs/devine-le-camp.md)) avant d'être validée par un humain.

## Audit de neutralité

Le script [`scripts/audit_biais.py`](skills/boussole-presidentielle-2027/scripts/audit_biais.py) vérifie que le résultat ne favorise pas mécaniquement un camp. Il tourne à chaque pull request : le rapport complet est publié dans le résumé du job de CI, sans jamais la faire échouer. Pour le lancer :

```bash
python3 skills/boussole-presidentielle-2027/scripts/audit_biais.py
```

Il fait trois choses :

1. **Un axe calculé, sans étiquette.** À partir des seules positions des candidats, il calcule l'axe qui les sépare le plus (première composante principale). Aucune question ni aucun candidat n'est classé à la main ; seul le sens de l'axe est orienté, pour l'affichage. L'axe est ensuite découpé en trois tiers : « gauche », « centre », « droite ».
2. **Les pôles.** Pour chaque enjeu, il mesure quel pôle rapproche de quel côté de l'axe (corrélation avec l'axe recalculé sans cet enjeu).
3. **Des profils au hasard, sur le vrai tirage.** Il tire des profils sans opinion (réponses au hasard, 10 % de « je passe ») et les fait passer par `tirage.py` puis `score.py`, avec une graine par profil, dans les trois modes ; il compte qui sort premier ou dans les trois premiers. Un calcul neutre donnerait à chaque candidat classé la même chance ; l'attendu tient compte des candidats exclus faute de positions connues. Il vérifie aussi qu'un profil qui choisit plus souvent l'option affichée d'un côté de l'écran n'est poussé vers aucun camp.

**Résultats actuels** (21 octobre 2026, 62 enjeux, 872 positions toutes relues par un humain ; 10 000 profils en modes complet et rapide, 500 en mode adaptatif, graine 2027 ; le résumé de la CI donne les chiffres à jour, sur 2 000 profils) :

- L'axe calculé place à un bout les candidats habituellement classés à gauche, à l'autre ceux classés à droite, sans qu'on le lui ait indiqué. Son tiers central regroupe des candidats variés (Ruffin, Villepin, Branco, Asselineau, Attal…) : il ne correspond pas à un « centre » politique au sens habituel.
- **Équilibre des tiers.** Ratios des premières places observées / attendues (graine 2027) : 1,07 à gauche, 1,00 au centre, 0,94 à droite en mode complet ; 1,06 / 1,03 / 0,93 en mode rapide ; 0,97 / 1,13 / 0,94 en mode adaptatif (500 profils, plus de bruit). Un seul tirage varie de ±0,015 environ d'une graine à l'autre (±0,03 à 0,06 en mode adaptatif) : en moyenne sur 7 graines, le mode complet donne 1,07 / 0,98 / 0,95. Le tiers central était à 0,885 avant le tri sur le score exact : les ex aequo à l'arrondi (22 % des profils) revenaient au candidat le plus couvert. Le mode adaptatif favorise un peu le tiers central (1,11 en moyenne sur 7 graines de 2 000 profils), un effet propre à ce mode qui reste à analyser. Détails : [analyse de l'audit à 62 enjeux](docs/audit-62-enjeux.md).
- **Écarts individuels.** Par candidat, les ratios vont de 0,73 (Florian Philippot, classé seulement 83 % du temps : il n'a de position connue que sur 7 des 22 nouveaux enjeux) à 1,31 (Édouard Philippe). Ces écarts ne viennent pas du calcul : avec des réponses au hasard, un candidat aux positions modérées et sans voisin proche (Philippe) sort plus souvent premier, tandis que des candidats aux positions très proches se partagent les premières places (Le Pen et Dupont-Aignan, Mélenchon et Tondelier, Retailleau et Lisnard). Seule la complétion des fiches réduit l'effet de la couverture.
- **Pas d'effet de côté.** Le pôle proche de la gauche de l'axe est le pôle A pour 25 enjeux et le pôle B pour 27 (9 transversaux, 1 indéterminé), et le côté où chaque option est affichée est tiré au hasard : un profil qui choisit plus souvent l'option affichée à gauche (ou à droite) ne déplace l'écart droite - gauche des premières places que de 3 à 5 points.
- **Couverture inégale.** Plusieurs candidats (Bouamrane, Polony, Lassalle, Batho, Cazeneuve, Bertrand) ont moins de la moitié de leurs positions renseignées et ne sont jamais classés en mode complet. La correction des positions inconnues empêche qu'ils soient avantagés, mais seule la complétion des fiches leur donne une place juste.

## Confidentialité

Vos réponses sont des opinions politiques : le skill les traite comme une donnée sensible.

- Elles restent dans votre conversation avec Claude. Le calcul se fait localement, avec les fichiers du plugin : les réponses sont transmises au script de calcul par l'entrée standard, sans être écrites dans un fichier.
- Le skill ne demande ni nom, ni e-mail, ni adresse, et n'envoie aucune donnée à un service extérieur. L'auteur ne reçoit et ne conserve rien.
- Seule la mise à jour des fiches fait des recherches web, et elles portent sur les candidats, jamais sur vos réponses.

## Limites

- La liste officielle des candidats ne sera connue qu'après la validation des parrainages par le Conseil constitutionnel. D'ici là, la liste suit les candidatures déclarées ou pressenties.
- Beaucoup de programmes ne sont pas encore publiés : une partie des positions est donc déduite.
- 62 enjeux ne résument pas un projet présidentiel. Lisez les programmes des candidats qui vous intéressent.
- Les fiches ont été constituées par recherche documentaire assistée par IA, puis **relues une à une par un humain** (octobre 2026) : chaque position a une citation vérifiée et le champ `relu`. Les arbitrages de codage sont décrits dans [`references/mise-a-jour.md`](skills/boussole-presidentielle-2027/references/mise-a-jour.md). Des erreurs restent possibles : signalez-les (voir ci-dessous).

## Contribuer

Une position est fausse, ou un programme vient de sortir ? Ouvrez une issue ou une pull request en citant la source. La procédure de mise à jour est décrite dans [`references/mise-a-jour.md`](skills/boussole-presidentielle-2027/references/mise-a-jour.md), et `python3 skills/boussole-presidentielle-2027/scripts/check_data.py` vérifie les fiches.

## Licence

[MIT](LICENSE)
