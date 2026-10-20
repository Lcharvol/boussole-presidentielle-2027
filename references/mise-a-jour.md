# Mettre à jour les programmes et la liste des candidats

La campagne bouge vite : des candidats se déclarent, se retirent ou se rallient, et les programmes sont publiés par morceaux jusqu'au printemps 2027. Cette procédure garde les fiches à jour sans casser la comparabilité entre candidats.

## 1. Faire l'état des lieux

Lance `python3 scripts/check_data.py`. Note les fiches anciennes, celles qui ont beaucoup de positions `null` ou `deduite`, et celles dont le statut est « pressenti ».

## 2. Mettre la liste des candidats à jour

Cherche sur le web la liste actuelle (sources conseillées : la page Wikipédia « Candidatures à l'élection présidentielle française de 2027 », Public Sénat, France 24, Toute l'Europe ; après la clôture des parrainages, la liste officielle du Conseil constitutionnel, qui fait foi).

- Nouveau candidat crédible → crée sa fiche (étape 3).
- Candidat retiré ou rallié → passe `statut` à `"retiré"` et écris dans `notes` qui il soutient. Garde le fichier : le score l'ignore, mais l'historique reste.
- Une fois la liste officielle publiée, passe en `"retiré"` ceux qui n'y figurent pas.

## 3. Mettre à jour les positions

Pour chaque fiche à rafraîchir, et pour chacune des 25 questions de `data/questions.json` :

1. Cherche d'abord dans le programme officiel (`programme_url`) ; s'il vient d'être publié, c'est la priorité absolue.
2. Sinon, des déclarations récentes (entretiens, discours, votes au Parlement).
3. Sinon, la position du parti ou le programme de 2022, avec `confiance: "deduite"` et en le disant dans le résumé.
4. Rien de trouvé → `null`. Ne jamais déduire une position de l'étiquette politique : c'est précisément ce qui biaiserait le test.

Chaque position non nulle a une URL source précise et une `date_source`. Le résumé décrit la position en une phrase, sans adjectif évaluatif. Mets à jour `mis_a_jour` avec la date du jour.

Avec beaucoup de fiches, répartis le travail entre plusieurs agents (4 ou 5 candidats chacun), en leur donnant ce fichier et `_FORMAT.md` comme consignes.

## 4. Vérifier

Relance `python3 scripts/check_data.py` : il doit sortir sans erreur. Puis relis quelques positions au hasard en ouvrant la source, surtout les valeurs extrêmes (2 ou -2) et les positions « deduite ».

## Recalculer les modes rapide et moyen

Après une mise à jour importante des fiches, lance `python3 scripts/choisir_niveaux.py` : il affiche, thème par thème, le pouvoir de départage de chaque question. Si le classement a changé, enregistre les nouveaux niveaux avec `--ecrire`, et signale-le dans le message de commit.

## Modifier les questions

Évite de changer les questions en cours de campagne : chaque modification oblige à recoder la question pour tous les candidats. Si c'est nécessaire (sujet devenu central, question qui ne départage plus personne), change `version` dans `questions.json` et remplis la nouvelle question pour **tous** les candidats avant de publier, sinon les scores ne sont plus comparables. Relance ensuite `choisir_niveaux.py --ecrire` pour lui attribuer un niveau.
