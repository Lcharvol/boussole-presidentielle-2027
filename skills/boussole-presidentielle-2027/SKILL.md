---
name: boussole-presidentielle-2027
description: Boussole électorale pour la présidentielle française de 2027. Elle pose une série de questions sur les grands thèmes (économie, écologie, sécurité, immigration, Europe, santé, éducation, institutions), compare les réponses aux programmes sourcés des candidats et montre de quels candidats l'utilisateur est le plus proche, thème par thème. Elle sait aussi mettre à jour les programmes et la liste des candidats. Utilise ce skill dès que quelqu'un demande pour qui voter en 2027, quel candidat lui correspond, veut faire un test politique ou un quiz électoral, comparer les programmes de la présidentielle, connaître la position des candidats sur un sujet, ou mettre à jour les programmes, même sans dire « boussole ».
---

# Boussole présidentielle 2027

Ce skill aide une personne à voir de quels candidats elle est proche, en comparant ses réponses à des positions relevées dans les programmes et les déclarations publiques. Il ne dit pas pour qui voter : il éclaire un choix qui reste celui de l'utilisateur. Cette nuance compte, car un outil qui a l'air de donner une consigne de vote perd sa crédibilité et peut influencer quelqu'un sur des données incomplètes.

## Contenu du skill

- `data/enjeux.json` : les enjeux, répartis en 8 thèmes. Chaque enjeu oppose deux options légitimes, le pôle A et le pôle B, et a deux ou trois formulations équivalentes (variantes).
- `data/candidats/<slug>.json` : une fiche par candidat, avec sa position sur chaque enjeu (de -2, pôle A, à +2, pôle B), un résumé, une source, une citation, une date et un niveau de confiance (`programme`, `declaration` ou `deduite`). Le format est décrit dans `data/FORMAT.md`.
- `scripts/tirage.py` : choisit les questions à poser (enjeux, ordre, formulation, côté de chaque pôle) et, en mode adaptatif, les suivantes.
- `scripts/score.py` : calcule la proximité, avec une marge d'incertitude, à partir des réponses reçues sur l'entrée standard.
- `scripts/check_data.py` : contrôle les données et signale les fiches incomplètes ou anciennes.
- `references/mise-a-jour.md` : la procédure pour rafraîchir les programmes et la liste des candidats.

## Choisir le mode

- La personne veut savoir quel candidat lui correspond, faire le test, etc. → **Questionnaire** (ci-dessous).
- Elle demande la position d'un ou plusieurs candidats sur un sujet → lis les fiches concernées et réponds en citant les sources ; une position se lit entre les deux pôles de l'enjeu (`pole_a` à -2, `pole_b` à +2). Si le sujet n'est pas dans les enjeux, fais une recherche web et dis-le.
- Elle demande de mettre à jour les programmes, d'ajouter un candidat, ou les données sont anciennes → **Mise à jour** : lis `references/mise-a-jour.md`.

## Questionnaire

### 1. Vérifier la fraîcheur des données

Lance `python3 scripts/check_data.py` (depuis le dossier du skill). Si des fiches datent de plus de 30 jours, ou si on approche du scrutin (la liste officielle n'est connue qu'après la validation des parrainages par le Conseil constitutionnel), signale-le en une phrase et propose une mise à jour avant ou après le test. Ne bloque pas le test pour autant.

### 2. Présenter le test et choisir le mode

En deux ou trois phrases : chaque question oppose deux options, et la personne indique de laquelle elle se sent la plus proche, sur cinq crans (nettement l'une, plutôt l'une, entre les deux, plutôt l'autre, nettement l'autre) ; on peut passer une question ; les thèmes arrivent dans le désordre ; à la fin, la personne indique les thèmes qui comptent le plus pour elle. Précise que le résultat mesure une proximité avec des programmes, pas une recommandation de vote.

Puis fais choisir le mode (avec `AskUserQuestion` s'il est disponible) :

| Mode | Questions | Durée | Fiabilité |
|---|---|---|---|
| Rapide | 12 (au moins une par thème) | ~3 min | Donne une tendance. Les écarts entre candidats proches ne sont pas significatifs. |
| Adaptatif | 12, puis par lots de 4 jusqu'à ce que le résultat soit assez précis (32 au plus) | 5 à 8 min | Bon compromis : les questions ajoutées sont celles qui départagent les candidats dont la personne est la plus proche. |
| Complet | tous les enjeux | ~12 min | Le plus fiable. |

Si la personne ne choisit pas, propose le mode adaptatif.

Le tirage change à chaque passage : enjeux du mode rapide, ordre, formulation et côté où chaque option est affichée. C'est voulu : cela évite de revoir toujours les mêmes questions et d'associer une option à une place à l'écran. Pour un nouveau passage, demande une graine au hasard ; garde le nombre renvoyé (champ `graine`) pour tous les appels suivants du même passage, y compris si la personne passe ensuite à un autre mode.

```bash
python3 scripts/tirage.py --mode adaptatif --graine hasard < /dev/null
```

### 3. Poser les questions

`tirage.py` renvoie la liste ordonnée des questions à poser (`questions`). Pose-les **dans cet ordre**, par lots de 4 au plus, sans les regrouper par thème et sans annoncer de thème. Pour chaque question, affiche le `contexte` s'il existe, puis la `question` et les deux options exactement comme elles sont données, **dans l'ordre donné** : `gauche` en premier, `droite` en second. Ne reformule rien, n'ajoute ni exemple ni argument, ne dis pas quelle option correspond à quel camp : les formulations ont été testées pour ne pas trahir de camp, et l'ordre des options est tiré au hasard pour la même raison. Ne donne pas la position des candidats pendant le questionnaire.

Si l'outil `AskUserQuestion` est disponible, une question par dilemme (4 par appel). Dans le texte de la question, écris la question puis les deux options sur deux lignes : « ① <texte de gauche> » et « ② <texte de droite> ». Options, dans cet ordre : « ① nettement », « Plutôt ① », « Plutôt ② », « ② nettement » ; « Entre les deux » et « Je passe » passent par la réponse libre, précise-le dans la question. Sinon, liste les questions du lot numérotées, chacune avec ses options ① et ②, et explique le format court : `①`, `plutôt ①`, `=`, `plutôt ②`, `②` ou `passe` (ex. « 1 ①, 2 =, 3 passe »).

**Conversion** : chaque question porte, dans `options`, les cinq réponses dans l'ordre d'affichage (① nettement, plutôt ①, entre les deux, plutôt ②, ② nettement) avec leur `valeur`. Enregistre pour l'enjeu (`enjeu`) la `valeur` de l'option choisie, ou `null` pour « je passe ». Ne recalcule jamais toi-même le sens : selon le tirage, ① peut être le pôle A ou le pôle B.

Si une réponse est inexploitable (« autre » laissé vide, texte ambigu), ne la classe pas toi-même en « entre les deux » ou en « je passe » : les deux n'ont pas le même effet sur le score. Repose la question avec le lot suivant, en proposant « Entre les deux », « Je passe » et les deux réponses les plus proches de ce que la personne semblait vouloir dire.

Si la personne demande ce que recouvre une option, explique-la factuellement sans laisser entendre qu'une réponse est meilleure, et sans dire quel camp la défend.

**Mode adaptatif** : après les 12 premières questions, rappelle `tirage.py` avec le même mode, la même graine et toutes les réponses déjà données (y compris les `null`), **par l'entrée standard** :

```bash
python3 scripts/tirage.py --mode adaptatif --graine 713121 <<'FIN'
{"reponses": {"sec_prisons": -1, "eco_retraite": 2, "sec_cannabis": null}}
FIN
```

Il renvoie le lot suivant, choisi pour départager les candidats encore proches de la personne. Pose-le, puis recommence, jusqu'à ce qu'il renvoie `"fin": true` ; sa `raison` dit pourquoi il s'arrête (le premier se détache, les enjeux restants ne départagent plus les candidats en tête, ou 32 questions posées). Annonce simplement « encore quelques questions » entre deux lots, sans dire quels candidats sont en tête.

### 4. Demander les priorités

Demande quels thèmes comptent le plus, **trois au maximum**, et dis pourquoi : si presque tout est prioritaire, la pondération ne change plus rien. Avec `AskUserQuestion`, les 8 thèmes ne tiennent pas dans une seule question : répartis-les sur deux questions à choix multiple et rappelle la limite de 3 au total. Si la personne en choisit plus de 3, demande-lui lesquels garder ; si elle maintient son choix, respecte-le et signale dans les limites que la pondération a peu d'effet.

Les thèmes prioritaires reçoivent une importance de 2 (ou 3 si la personne dit qu'un thème est décisif pour elle) ; les autres restent à 1.

### 5. Calculer

Passe les réponses au script **par l'entrée standard**, sans les écrire dans un fichier : ce sont des opinions politiques, une donnée sensible, et rien ne doit en rester sur la machine une fois le calcul fait.

```bash
python3 scripts/score.py <<'FIN'
{"reponses": {"eco_retraite": 2, "sec_cannabis": null}, "importance": {"immigration": 2}}
FIN
```

Les clés de `reponses` sont les identifiants d'enjeux, les valeurs celles des options choisies (-2 = pôle A nettement, +2 = pôle B nettement). Ajoute `--json` (`python3 scripts/score.py --json <<'FIN' … FIN`) si tu as besoin des accords et désaccords détaillés, ou du nombre de positions de chaque niveau de confiance (`par_confiance`). Ne calcule pas les scores toi-même : le script garantit que tout le monde est traité avec la même formule. Ne conserve pas les réponses ailleurs (fichier, mémoire, note) une fois le résultat présenté.

### 6. Présenter le résultat

Dans cet ordre :

1. **Le classement** : le tableau des candidats avec leur proximité, **toujours accompagnée de sa marge** (« 72 ± 8 % »), et la couverture (part des questions où la position du candidat est connue). Précise que 50 % signifie « pas plus proche que des réponses au hasard » et 100 % « mêmes réponses partout ». Les candidats dont la couverture est trop faible sont listés à part, avec la raison. Explique la marge en une phrase : elle indique de combien le score pourrait varier avec un autre jeu de questions (intervalle à 90 %, calculé en rééchantillonnant les réponses) ; elle est plus large quand on a répondu à peu de questions ou que le candidat a peu de positions connues. Juste après le tableau, reprends les deux alertes du script :
   - **Marges qui se recouvrent** (`peloton_de_tete`) : les candidats dont l'intervalle (score ± marge) recouvre celui du premier. S'il y en a plusieurs, dis clairement qu'aucun ne se détache et que leur ordre n'est pas significatif : ne présente pas le premier comme « le plus proche » sans cette réserve. Sinon, la personne risque de prendre un écart de 2 points pour un vrai résultat.
   - **Thème prioritaire sans donnée** (`prioritaires_sans_donnee`) : si un candidat du haut du classement n'a aucune position connue sur un thème que la personne a mis en priorité, signale-le dans sa présentation. Sur ce thème, son score ne repose sur rien de connu (les questions sans position comptent comme un accord égal au hasard) et peut être trompeur.
2. **Les 3 plus proches, expliqués** : pour chacun, 2 ou 3 points d'accord et 1 ou 2 points de désaccord marquants, avec le résumé de la position et le lien source tirés de la fiche. C'est la partie la plus utile : elle permet de juger soi-même plutôt que de croire un pourcentage.
3. **Le détail par thème** : signale les cas où un candidat est très proche sur un thème prioritaire mais loin sur un autre.
4. **Les limites**, en quelques lignes : le mode choisi et le nombre de questions répondues (en mode adaptatif, que les questions ont été choisies pour départager les candidats en tête) ; les programmes ne sont pas tous publiés ; certaines positions sont déduites du parti ou d'un ancien programme (dis combien pour les candidats du haut du classement, avec `par_confiance`) et comptent donc moins dans le score (poids 0,6 contre 1 pour le programme et 0,85 pour une déclaration) ; quelques dizaines d'enjeux ne résument pas un projet ; la liste des candidats n'est pas encore officielle. Invite à lire les programmes des candidats du haut du classement (`programme_url` dans les fiches).

Après un mode rapide ou adaptatif, propose de **continuer** sans recommencer : rappelle `tirage.py` avec le mode adaptatif (après un mode rapide) ou complet, la même graine et toutes les réponses déjà données ; seuls les enjeux pas encore posés sont tirés, puis le calcul est relancé sur l'ensemble. C'est particulièrement utile quand plusieurs marges se recouvrent : plus de réponses resserrent les marges.

Reste neutre jusqu'au bout. Ne commente pas les candidats (« crédible », « extrême », « dangereux »…), même si on te le demande dans le cadre du test. Si la personne veut ton avis sur le candidat à choisir, rappelle que le choix lui revient et propose plutôt d'approfondir un thème ou de comparer deux candidats sur un sujet précis.

## Exemple de restitution (extrait)

> **Vos candidats les plus proches**
>
> | Rang | Candidat | Parti | Proximité | Couverture |
> |---|---|---|---|---|
> | 1 | … | … | 78 ± 7 % | 92 % |
>
> **1. Nom du candidat — 78 % (± 7)**
> - D'accord sur la retraite : « propose un retour à 62 ans » ([source](https://…))
> - Désaccord sur le nucléaire : « veut sortir progressivement du nucléaire » ([source](https://…))
