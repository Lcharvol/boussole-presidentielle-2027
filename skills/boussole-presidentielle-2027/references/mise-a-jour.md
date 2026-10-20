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

Pour chaque fiche à rafraîchir, et pour chacune des 40 questions de `data/questions.json` :

1. Cherche d'abord dans le programme officiel (`programme_url`) ; s'il vient d'être publié, c'est la priorité absolue.
2. Sinon, des déclarations récentes (entretiens, discours, votes au Parlement).
3. Sinon, la position du parti ou le programme de 2022, avec `confiance: "deduite"` et en le disant dans le résumé.
4. Rien de trouvé → `null`. Ne jamais déduire une position de l'étiquette politique : c'est précisément ce qui biaiserait le test.

Chaque position non nulle a une URL source précise, une `date_source` et une `citation` : la phrase exacte de la source qui justifie la valeur (300 caractères au plus), recopiée après avoir ouvert la page. Si aucune phrase de la source ne justifie la valeur, corrige la valeur ou passe-la à `null`. Les agrégateurs (votons-2027.fr, elyseescope, monvote2027…) ne comptent jamais comme source. Toute position créée ou modifiée garde (ou repasse à) `relu: false`. Le résumé décrit la position en une phrase, sans adjectif évaluatif. Mets à jour `mis_a_jour` avec la date du jour.

Avec beaucoup de fiches, répartis le travail entre plusieurs agents (4 ou 5 candidats chacun), en leur donnant ce fichier et `_FORMAT.md` comme consignes.

### Règles de codage

Ces règles viennent de la relecture humaine des fiches. Elles évitent de surestimer une position à partir d'un indice indirect :

- **Vote contre (ou pour) un texte entier** : un cran de moins que la valeur extrême (±1 au lieu de ±2), sauf si le candidat s'est aussi exprimé sur la mesure précise. Un texte contient d'autres dispositions que celle de la question.
- **Position ancienne tenue comme membre du gouvernement** (ministre, Premier ministre) et jamais réaffirmée depuis : un cran de moins. Elle reflète aussi la ligne du gouvernement de l'époque.
- **Restriction partielle** (par exemple limitée à Mayotte) : la soutenir vaut ±1 (cela ne dit pas qu'on veut l'étendre) ; s'y opposer vaut ±2 (qui refuse une restriction limitée refuse a fortiori une restriction générale).
- **Refus de l'austérité sans mention d'impôts** : ±1 sur `eco_depenses` (« augmenter les impôts plutôt que baisser les dépenses ») ; ±2 seulement si la source évoque des hausses de recettes fiscales.
- **Ligne du parti ou de son journal** (pas une déclaration du candidat) : acceptable en confiance `deduite`, à condition de le dire dans le résumé et de citer une phrase qui exprime la position, pas seulement un titre ou une description.

## 4. Vérifier

Relance `python3 scripts/check_data.py` : il doit sortir sans erreur. Il signale en alerte les positions sans citation et affiche, par candidat, combien de positions ont été relues par un humain.

Puis fais relire les positions par un humain : `python3 scripts/a_relire.py > a-relire.md` produit une liste à cocher, valeurs extrêmes (2 ou -2) et positions « deduite » en tête. Le relecteur ouvre la source, vérifie que la citation y figure mot pour mot et justifie la valeur, puis passe `relu` à `true`. Seul un humain passe `relu` à `true`.

## Recalculer les modes rapide et moyen

Après une mise à jour importante des fiches, lance `python3 scripts/choisir_niveaux.py` : il affiche, thème par thème, le pouvoir de départage de chaque question. Si le classement a changé, enregistre les nouveaux niveaux avec `--ecrire`, et signale-le dans le message de commit.

## Modifier les questions

Évite de changer les questions en cours de campagne : chaque modification oblige à recoder la question pour tous les candidats. Si c'est nécessaire (sujet devenu central, question qui ne départage plus personne), change `version` dans `questions.json` et remplis la nouvelle question pour **tous** les candidats avant de publier, sinon les scores ne sont plus comparables. Relance ensuite `choisir_niveaux.py --ecrire` pour lui attribuer un niveau.
