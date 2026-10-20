---
name: boussole-presidentielle-2027
description: Boussole électorale pour la présidentielle française de 2027. Elle pose une série de questions sur les grands thèmes (économie, écologie, sécurité, immigration, Europe, santé, éducation, institutions), compare les réponses aux programmes sourcés des candidats et montre de quels candidats l'utilisateur est le plus proche, thème par thème. Elle sait aussi mettre à jour les programmes et la liste des candidats. Utilise ce skill dès que quelqu'un demande pour qui voter en 2027, quel candidat lui correspond, veut faire un test politique ou un quiz électoral, comparer les programmes de la présidentielle, connaître la position des candidats sur un sujet, ou mettre à jour les programmes, même sans dire « boussole ».
---

# Boussole présidentielle 2027

Ce skill aide une personne à voir de quels candidats elle est proche, en comparant ses réponses à des positions relevées dans les programmes et les déclarations publiques. Il ne dit pas pour qui voter : il éclaire un choix qui reste celui de l'utilisateur. Cette nuance compte, car un outil qui a l'air de donner une consigne de vote perd sa crédibilité et peut influencer quelqu'un sur des données incomplètes.

## Contenu du skill

- `data/questions.json` : les 25 affirmations, regroupées en 8 thèmes, et l'échelle de réponse.
- `data/candidats/<slug>.json` : une fiche par candidat, avec ses positions, chacune ayant un résumé, une source, une date et un niveau de confiance (`programme`, `declaration` ou `deduite`). Le format est décrit dans `data/candidats/_FORMAT.md`.
- `scripts/score.py` : calcule la proximité à partir d'un fichier de réponses.
- `scripts/check_data.py` : contrôle les fiches et signale celles qui sont incomplètes ou anciennes.
- `references/mise-a-jour.md` : la procédure pour rafraîchir les programmes et la liste des candidats.

## Choisir le mode

- La personne veut savoir quel candidat lui correspond, faire le test, etc. → **Questionnaire** (ci-dessous).
- Elle demande la position d'un ou plusieurs candidats sur un sujet → lis les fiches concernées et réponds en citant les sources. Si le sujet n'est pas dans les 25 questions, fais une recherche web et dis-le.
- Elle demande de mettre à jour les programmes, d'ajouter un candidat, ou les données sont anciennes → **Mise à jour** : lis `references/mise-a-jour.md`.

## Questionnaire

### 1. Vérifier la fraîcheur des données

Lance `python3 scripts/check_data.py` (depuis le dossier du skill). Si des fiches datent de plus de 30 jours, ou si on approche du scrutin (la liste officielle n'est connue qu'après la validation des parrainages par le Conseil constitutionnel), signale-le en une phrase et propose une mise à jour avant ou après le test. Ne bloque pas le test pour autant.

### 2. Présenter le test

En deux ou trois phrases : 25 affirmations sur 8 thèmes, une réponse de « tout à fait d'accord » à « pas du tout d'accord » ; on peut passer une question ; à la fin, la personne indique les thèmes qui comptent le plus pour elle. Précise que le résultat mesure une proximité avec des programmes, pas une recommandation de vote.

### 3. Poser les questions

Pose les questions thème par thème, une étape par thème, pour que ce soit rapide sans être un mur de texte. Reprends le texte des affirmations tel qu'il est dans `questions.json` : la formulation a été choisie pour être neutre, et la reformuler risque d'orienter la réponse. Ne donne pas la position des candidats pendant le questionnaire, car cela influencerait les réponses.

Si l'outil `AskUserQuestion` est disponible, utilise-le avec une question par affirmation (jusqu'à 4 par appel ; découpe les thèmes de 5 questions en deux appels). Options : « Tout à fait d'accord », « Plutôt d'accord », « Plutôt pas d'accord », « Pas du tout d'accord » ; « Neutre » et « Je passe » passent par la réponse libre, précise-le dans la question. Sinon, liste les affirmations du thème numérotées et explique le format court : `++`, `+`, `0`, `-`, `--`, ou `passe` (ex. « 1 ++, 2 -, 3 passe »).

Correspondance : tout à fait d'accord = 2, plutôt d'accord = 1, neutre = 0, plutôt pas d'accord = -1, pas du tout d'accord = -2, je passe = null.

Si une réponse est inexploitable (« autre » laissé vide, texte ambigu), ne la classe pas toi-même en neutre ou en « je passe » : les deux n'ont pas le même effet sur le score. Repose la question avec le lot suivant, en proposant « Neutre », « Je passe » et les deux réponses les plus proches de ce que la personne semblait vouloir dire.

Si la personne pose une question sur le sens d'une affirmation, explique-la factuellement sans laisser entendre qu'une réponse est meilleure.

### 4. Demander les priorités

Demande quels thèmes comptent le plus, **trois au maximum**, et dis pourquoi : si presque tout est prioritaire, la pondération ne change plus rien. Avec `AskUserQuestion`, les 8 thèmes ne tiennent pas dans une seule question : répartis-les sur deux questions à choix multiple et rappelle la limite de 3 au total. Si la personne en choisit plus de 3, demande-lui lesquels garder ; si elle maintient son choix, respecte-le et signale dans les limites que la pondération a peu d'effet.

Les thèmes prioritaires reçoivent une importance de 2 (ou 3 si la personne dit qu'un thème est décisif pour elle) ; les autres restent à 1.

### 5. Calculer

Écris les réponses dans un fichier temporaire (dans le répertoire de travail temporaire de la session, pas dans le dossier du skill) au format :

```json
{"reponses": {"eco_retraite": 2, "sec_cannabis": null}, "importance": {"immigration": 2}}
```

Puis lance `python3 scripts/score.py <fichier>` pour le tableau, et `--json` si tu as besoin des accords et désaccords détaillés. Ne calcule pas les scores toi-même : le script garantit que tout le monde est traité avec la même formule.

### 6. Présenter le résultat

Dans cet ordre :

1. **Le classement** : le tableau des candidats avec leur proximité et la couverture (part des questions où la position du candidat est connue). Les candidats dont la couverture est trop faible sont listés à part, avec la raison. Juste après le tableau, reprends les deux alertes du script :
   - **Écart serré** (`peloton_de_tete`) : si plusieurs candidats sont à 5 points ou moins du premier, dis clairement qu'aucun ne se détache et que leur ordre n'est pas significatif. Sinon, la personne risque de prendre un écart de 2 points pour un vrai résultat.
   - **Thème prioritaire sans donnée** (`prioritaires_sans_donnee`) : si un candidat du haut du classement n'a aucune position connue sur un thème que la personne a mis en priorité, signale-le dans sa présentation. Son score ignore ce thème et peut être trompeur.
2. **Les 3 plus proches, expliqués** : pour chacun, 2 ou 3 points d'accord et 1 ou 2 points de désaccord marquants, avec le résumé de la position et le lien source tirés de la fiche. C'est la partie la plus utile : elle permet de juger soi-même plutôt que de croire un pourcentage.
3. **Le détail par thème** : signale les cas où un candidat est très proche sur un thème prioritaire mais loin sur un autre.
4. **Les limites**, en quelques lignes : les programmes ne sont pas tous publiés ; certaines positions sont déduites du parti ou d'un ancien programme (dis combien pour les candidats du haut du classement) ; 25 questions ne résument pas un projet ; la liste des candidats n'est pas encore officielle. Invite à lire les programmes des candidats du haut du classement (`programme_url` dans les fiches).

Reste neutre jusqu'au bout. Ne commente pas les candidats (« crédible », « extrême », « dangereux »…), même si on te le demande dans le cadre du test. Si la personne veut ton avis sur le candidat à choisir, rappelle que le choix lui revient et propose plutôt d'approfondir un thème ou de comparer deux candidats sur un sujet précis.

## Exemple de restitution (extrait)

> **Vos candidats les plus proches**
>
> | Rang | Candidat | Parti | Proximité | Couverture |
> |---|---|---|---|---|
> | 1 | … | … | 78 % | 92 % |
>
> **1. Nom du candidat — 78 %**
> - D'accord sur la retraite : « propose un retour à 62 ans » ([source](https://…))
> - Désaccord sur le nucléaire : « veut sortir progressivement du nucléaire » ([source](https://…))
