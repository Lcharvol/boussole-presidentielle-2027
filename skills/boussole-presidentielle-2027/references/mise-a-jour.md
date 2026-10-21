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

Pour chaque fiche à rafraîchir, et pour chacun des enjeux de `data/enjeux.json` :

1. Cherche d'abord dans le programme officiel (`programme_url`) ; s'il vient d'être publié, c'est la priorité absolue.
2. Sinon, des déclarations récentes (entretiens, discours, votes au Parlement).
3. Sinon, la position du parti ou le programme de 2022, avec `confiance: "deduite"` et en le disant dans le résumé.
4. Rien de trouvé → `null`. Ne jamais déduire une position de l'étiquette politique : c'est précisément ce qui biaiserait le test.

Chaque position non nulle a une URL source précise, une `date_source` et une `citation` : la phrase exacte de la source qui justifie la valeur (300 caractères au plus), recopiée après avoir ouvert la page. Si aucune phrase de la source ne justifie la valeur, corrige la valeur ou passe-la à `null`. Les agrégateurs (votons-2027.fr, elyseescope, monvote2027…) ne comptent jamais comme source. Toute position créée ou modifiée garde (ou repasse à) `relu: false`. Le résumé décrit la position en une phrase, sans adjectif évaluatif. Mets à jour `mis_a_jour` avec la date du jour.

La valeur se lit entre les deux pôles de l'enjeu : -2 = pôle A nettement (`pole_a`), +2 = pôle B nettement (`pole_b`), 0 = position intermédiaire. Code d'après les deux pôles et non d'après une formulation particulière : les variantes d'un même enjeu sont équivalentes.

Avec beaucoup de fiches, répartis le travail entre plusieurs agents (4 ou 5 candidats chacun), en leur donnant ce fichier et `data/FORMAT.md` comme consignes.

### Règles de codage

Ces règles viennent de la relecture humaine des fiches. Elles évitent de surestimer une position à partir d'un indice indirect :

- **Vote contre (ou pour) un texte entier** : un cran de moins que la valeur extrême (±1 au lieu de ±2), sauf si le candidat s'est aussi exprimé sur la mesure précise. Un texte contient d'autres dispositions que celle de la question.
- **Position ancienne tenue comme membre du gouvernement** (ministre, Premier ministre) et jamais réaffirmée depuis : un cran de moins. Elle reflète aussi la ligne du gouvernement de l'époque.
- **Restriction partielle** (par exemple limitée à Mayotte) : la soutenir vaut ±1 (cela ne dit pas qu'on veut l'étendre) ; s'y opposer vaut ±2 (qui refuse une restriction limitée refuse a fortiori une restriction générale).
- **Refus de l'austérité sans mention d'impôts** : +1 sur `eco_depenses` (plutôt le pôle B, « augmenter les impôts ») ; +2 seulement si la source évoque des hausses de recettes fiscales.
- **Heures supplémentaires** : les défiscaliser ou les rendre plus rémunératrices sans toucher à la durée légale vaut 0 sur `eco_35h` ; −1 (plutôt le pôle A, garder les 35 heures) si le candidat exclut explicitement d'augmenter la durée légale.
- **Condition de résidence pour les étrangers** (durée minimale de séjour ou de travail pour accéder aux prestations ou au logement social) : +1 sur `imm_preference` (plutôt le pôle B) ; +2 seulement pour une priorité ou une réservation fondée sur la nationalité.
- **CEDH et droit de l'UE** : `eur_primaute` porte sur le droit de l'Union européenne (pôle B : faire primer le droit français). Une remise en cause limitée à la CEDH (Conseil de l'Europe) vaut 0 ; si elle vise aussi la CJUE ou les traités de l'UE, appliquer l'échelle habituelle.
- **Principe général** : une règle générale qui couvre explicitement le cas de la question (par exemple une interdiction « pour tous » ou « dans tout l'espace public », ou une neutralité qui « ne s'impose pas aux usagers ») vaut comme une position sur ce cas, même s'il n'est pas nommé.
- **Dilemme à deux mesures** (par exemple `sec_prisons` : construire des places / développer les peines alternatives) : soutenir les deux pôles vaut 0 ; rejeter un pôle sans défendre l'autre vaut ±1 vers l'autre pôle ; ±2 seulement si le candidat défend un pôle de préférence à l'autre, ou l'un en rejetant l'autre.
- **Ligne du parti ou de son journal** (pas une déclaration du candidat) : acceptable en confiance `deduite`, à condition de le dire dans le résumé et de citer une phrase qui exprime la position, pas seulement un titre ou une description.

## 4. Vérifier

Relance `python3 scripts/check_data.py` : il doit sortir sans erreur. Il signale en alerte les positions sans citation et affiche, par candidat, combien de positions ont été relues par un humain.

Puis fais relire les positions par un humain : `python3 scripts/a_relire.py > a-relire.md` produit une liste à cocher, valeurs extrêmes (2 ou -2) et positions « deduite » en tête. Le relecteur ouvre la source, vérifie que la citation y figure mot pour mot et justifie la valeur, puis passe `relu` à `true`. Seul un humain passe `relu` à `true`.

## Tirage des questions

Il n'y a plus de niveaux à recalculer : `scripts/tirage.py` pondère le tirage du mode rapide (et du socle du mode adaptatif) par le pouvoir de départage de chaque enjeu (écart-type des positions des candidats × part des positions connues), calculé à chaque appel à partir des fiches. Après une mise à jour importante, relance seulement l'audit : `python3 scripts/audit_biais.py`.

## Modifier les enjeux et leurs formulations

Évite de changer les enjeux en cours de campagne : chaque changement de pôle oblige à recoder l'enjeu pour tous les candidats. Si c'est nécessaire (sujet devenu central, enjeu qui ne départage plus personne), change `version` dans `enjeux.json` et remplis le nouvel enjeu pour **tous** les candidats avant de publier, sinon les scores ne sont plus comparables.

Une nouvelle formulation (variante) d'un enjeu existant ne demande pas de recodage, à condition d'opposer exactement les mêmes pôles. Elle suit ces règles :

- deux options légitimes, de même dignité : pas d'intensif (« massivement », « fortement », « quitte à »…), pas de vocabulaire propre à un camp, une longueur et une concrétude comparables ; si une option est justifiée (« pour… »), l'autre aussi ;
- pas de prémisse qui fait pencher la question (« pour réduire le trafic… » favorise l'option qui prétend le réduire) ;
- `a` exprime toujours le pôle A, `b` le pôle B.

Avant de l'ajouter, fais-la passer au test « devine le camp » (`outils/devine_le_camp.py`, à la racine du dépôt) : des agents jouant des électeurs de bords différents disent quel camp a rédigé la question et quelle option elle présente le plus favorablement. Elle n'est retenue que si ces deux taux restent entre 35 et 65 %. Ajoute-la ensuite avec `"validee": false` : seul Lcharvol la passe à `true` après relecture.
