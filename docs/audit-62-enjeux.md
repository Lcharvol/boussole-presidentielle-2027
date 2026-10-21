# Audit de neutralité à 62 enjeux : d'où vient l'écart ?

Analyse du 21 octobre 2026 sur la branche `v2/completion` (PR #23). Aucune position n'a été modifiée. Les corrections ci-dessous sont **proposées, pas appliquées**.

> **Mise à jour** : les propositions 1 (tri sur le score non arrondi) et 2 (audit sur plusieurs graines, pentes, candidats jamais classés signalés dans les tiers) sont appliquées dans la branche `fix/departage-score-brut`. Mesuré par `audit_biais.py --graines 7` (graines 2027 à 2033, 10 000 profils) : complet 1,07 / 0,99 / 0,95, rapide 1,04 / 1,03 / 0,95.

## En bref

1. **La référence « 40 enjeux = 1,04 / 0,96 / 0,99 » était un tirage favorable.** Avec d'autres graines, les mêmes données (main) donnent un tiers central entre 0,90 et 0,91. Mesuré sur 7 graines, l'écart entre 40 et 62 enjeux est petit : centre 0,914 → 0,885.
2. **Aucun des 22 nouveaux enjeux n'en est responsable à lui seul.** Retirer n'importe lequel d'entre eux remonte le centre de 0,00 à 0,04.
3. **La cause principale tient au calcul, pas aux enjeux.** `score.py` arrondit le score à l'entier puis départage les ex aequo par la couverture. Or 22 % des profils ont un ex aequo pour la première place. Ce départage avantage les fiches les plus complètes, et le tiers central est le moins couvert. Classer sur le score non arrondi donne 1,07 / 0,98 / 0,95 au lieu de 1,08 / 0,885 / 1,01.
4. **L'axe reste pertinent, le découpage en tiers est fragile.** Les coordonnées à 40 et à 62 enjeux sont corrélées à 0,998. Mais 3 des 8 candidats du « centre » ne sont jamais classés, et Ruffin, Glucksmann et Philippot sont à la frontière.

**Recommandation** :
- trier le classement sur le score non arrondi (2 lignes dans `score.py`, à reporter dans `score.ts` du site) ;
- faire la moyenne de l'audit sur plusieurs graines ;
- ne toucher ni à `POIDS_INCONNUE`, ni à `COUVERTURE_MIN`, ni à la liste des enjeux.

## 1. Bruit Monte-Carlo

Vrai déroulé (`audit_biais.simuler`, mode complet, 10 000 profils), ratios gauche / centre / droite :

| Graine | main (40 enjeux) | branche (62 enjeux) |
|---|---|---|
| 2027 (celle du README) | 1,04 / **0,96** / 0,99 | 1,07 / 0,91 / 1,01 |
| 1 à 6 | centre de 0,899 à 0,913 | centre de 0,861 à 0,901 |
| **Moyenne sur 7 graines** | **1,063 / 0,914 / 0,998** | **1,080 / 0,885 / 1,014** |
| Écart-type entre graines | ±0,012 / 0,021 / 0,008 | ±0,010 / 0,016 / 0,009 |

- Un ratio de tiers fluctue d'environ ±0,015 à 10 000 profils, et d'environ ±0,03 aux 2 000 profils de la CI. Un ratio de candidat fluctue de ±0,03 à 0,06.
- Comparer deux tirages uniques revient donc à comparer du bruit. Mesuré proprement, le centre a perdu 0,03, pas 0,05.
- Mode rapide (7 graines) : main 1,033 / 1,001 / 0,967 ; branche 1,048 / 0,996 / 0,960. Pas de dégradation.

## 2. Effet des nouveaux enjeux et de la couverture

Simulateur allégé : même formule que `score.py`, vérifiée identique sur 400 profils, et mêmes moyennes que le vrai script. Mode complet, 10 graines × 10 000 profils, tiers de l'axe à 62 enjeux gardés fixes pour isoler l'effet des enjeux.

| Configuration | gauche | centre | droite |
|---|---|---|---|
| 62 enjeux | 1,081 | 0,880 | 1,016 |
| 40 premiers enjeux (fiches de la branche) | 1,015 | 0,966 | 1,009 |
| 62 moins un nouvel enjeu (22 cas) | 1,05 à 1,08 | 0,88 à 0,92 | 1,00 à 1,03 |
| 40 plus un nouvel enjeu (22 cas) | 1,01 à 1,04 | 0,94 à 0,98 | 0,99 à 1,02 |
| 62 moins les nouveaux enjeux d'un thème (8 cas) | 1,05 à 1,09 | 0,88 à 0,90 | 1,00 à 1,03 |
| 40 enjeux tirés au hasard parmi 62 (6 tirages) | 0,99 à 1,16 | 0,83 à 0,94 | 0,98 à 1,06 |

- L'enjeu qui pèse le plus est `eco_libre_echange` : sans lui, le centre passe à 0,920. Viennent ensuite `eco_nationalisation`, `ecol_eau_agricole` et `eur_service_militaire` (+0,02 environ chacun). Aucun ne justifie un retrait.
- Le problème ne vient ni du contenu ni du nombre d'enjeux : 40 enjeux tirés au hasard parmi les 62 font aussi mal que les 62. Il vient de la **couverture** : les 40 premiers enjeux sont les mieux renseignés.
- Couverture des nouveaux enjeux par les candidats classés :
  - gauche 54 % ;
  - **centre 42 %** (Attal 5/22, Ruffin 9/22, Asselineau 9/22) ;
  - droite 55 %.

  Sur les 40 premiers : 75 / 67 / 81 %.

Paramètres de couverture (62 enjeux) :

| Variante | Calcul actuel (arrondi) | Score non arrondi |
|---|---|---|
| `POIDS_INCONNUE` = 0 | 1,06 / 1,07 / 0,90 | — |
| `POIDS_INCONNUE` = 0,25 | 1,07 / 0,95 / 0,97 | 1,06 / 1,04 / 0,92 |
| `POIDS_INCONNUE` = 0,35 | — | 1,07 / 1,00 / 0,94 |
| **`POIDS_INCONNUE` = √2-1 (actuel)** | **1,08 / 0,88 / 1,02** | **1,07 / 0,98 / 0,95** |
| `POIDS_INCONNUE` = 0,5 | 1,09 / 0,85 / 1,04 | — |
| `COUVERTURE_MIN` = 0,4 | 1,03 / 0,92 / 1,03 | 1,03 / 1,00 / 0,97 |
| `COUVERTURE_MIN` = 0,6 | 1,18 / 0,79 / 0,97 | — |
| Sans « je passe » | 1,09 / 0,87 / 1,02 | 1,08 / 0,97 / 0,95 |

- `√2-1` remplit son rôle : sous profils aléatoires, l'écart-type du score des candidats classés va de 4,7 à 5,0 points, quelle que soit leur couverture (52 à 89 %).
- Le baisser jusqu'à atteindre un centre à 1,00 reviendrait à régler un paramètre sur l'audit : je ne le recommande pas.

## 3. Le mécanisme : arrondi et départage par la couverture

- `calculer()` arrondit le score à l'entier, puis trie par (score, couverture).
- À 62 enjeux, les deux premiers ont le même score arrondi dans **22 %** des profils (19 % à 40 enjeux).
- Ces ex aequo reviennent au candidat le plus couvert : Tondelier, Mélenchon, Le Pen, Dupont-Aignan (87 à 89 %).
- L'attendu de l'audit suppose au contraire des chances égales.

Ce qui se passe quand on change le tri :

| Mode complet, 62 enjeux | Ratios des tiers | Pente « extrêmes / centre » | Pente « gauche → droite » |
|---|---|---|---|
| Actuel | 1,081 / 0,880 / 1,016 | **+0,24 ± 0,03** | −0,01 ± 0,01 |
| Tri sur le score non arrondi | 1,071 / 0,978 / 0,954 | +0,04 ± 0,03 | −0,02 ± 0,01 |
| Ex aequo départagés au hasard | 1,066 / 0,984 / 0,954 | — | — |

Lecture des colonnes :
- **Pentes** : régression du log du ratio de chaque candidat classé sur sa coordonnée normalisée (« gauche → droite ») ou sur sa valeur absolue (« extrêmes / centre »), pondérée par l'attendu.
- **Corrélation ratio–couverture** : +0,47 aujourd'hui, −0,27 avec le tri non arrondi.
- **Pente « extrêmes / centre »** : significative aujourd'hui (+0,24 ± 0,03), elle ne l'est plus avec la correction (+0,04 ± 0,03).

Ratios individuels (simulateur, 10 graines) :

| Candidat | Coordonnée | Classé | Actuel | Non arrondi |
|---|---|---|---|---|
| Marine Tondelier | −12,1 | 100 % | 1,26 | 1,08 |
| Jean-Luc Mélenchon | −10,6 | 100 % | 1,06 | 0,81 |
| Anasse Kazib | −10,0 | 96 % | 1,01 | 1,22 |
| Nathalie Arthaud | −8,6 | 100 % | 1,20 | 1,27 |
| Fabien Roussel | −8,0 | 100 % | 0,86 | 0,83 |
| Raphaël Glucksmann | −6,8 | 100 % | 1,09 | 1,23 |
| François Ruffin | −6,3 | 100 % | 0,74 | 0,79 |
| Dominique de Villepin | −2,2 | 99 % | 0,94 | 1,08 |
| Juan Branco | −0,4 | 100 % | 0,95 | 0,93 |
| François Asselineau | +2,7 | 99 % | 0,79 | 0,92 |
| Gabriel Attal | +4,8 | 99 % | 0,99 | 1,17 |
| Florian Philippot | +5,1 | 84 % | 0,54 | 0,71 |
| Marine Le Pen | +7,4 | 100 % | 1,19 | 0,97 |
| Édouard Philippe | +7,8 | 100 % | 1,20 | 1,20 |
| Nicolas Dupont-Aignan | +8,3 | 100 % | 0,96 | 0,79 |
| Éric Zemmour | +9,2 | 100 % | 0,90 | 0,94 |
| David Lisnard | +9,9 | 100 % | 1,14 | 1,10 |
| Bruno Retailleau | +11,0 | 100 % | 1,10 | 0,94 |

**Ce qui reste après correction (0,71 à 1,27) ne vient pas du calcul.**
- Avec des réponses au hasard, la chance de sortir premier dépend de la place qu'un candidat occupe seul dans l'espace des positions. Certains duos ont des scores très corrélés (r = 0,66 à 0,73) : Le Pen et Dupont-Aignan, Retailleau et Lisnard, Mélenchon et Tondelier.
- Aucune formule ne neutralise cet effet sans déformer les positions.
- Le cas de Philippot est résolu à moitié : 0,54 → 0,71. Il perdait les ex aequo (couverture 52 %) et n'est classé que 84 % du temps, juste au-dessus du seuil.

Deux autres pistes testées n'apportent rien :
- **Accord standardisé** (même variance pour une position à 0 qu'à ±2) : aucun effet (1,07 / 0,97 / 0,96).
- **Poids de confiance égaux** : gauche 1,07 → 1,05. Faible effet, et cela change le sens de la méthode.

## 4. L'axe et les tiers

**L'axe tient.**
- Variance expliquée : 50 % à 62 enjeux (54 % à 40).
- Corrélation des coordonnées entre 40 et 62 enjeux : 0,998.
- Un axe calculé sur les 22 nouveaux enjeux seuls donne le même ordre (r = 0,96).

**Le découpage en tiers est fragile.**
- Les tiers sont des parts égales des 24 candidats placés, y compris 6 jamais classés (Labib, Batho, Cazeneuve, Lassalle, Polony, Bertrand). Le « centre » ne compte donc que 5 candidats en compétition (Ruffin, Villepin, Branco, Asselineau, Attal) : son ratio dépend de deux ou trois personnes.
- Sur 200 sous-ensembles aléatoires d'enjeux, Ruffin tombe au centre 48 % du temps et Glucksmann 30 % du temps. Philippot, à droite sur les 62 enjeux, tombe au centre 92 % du temps. Un changement de frontière déplace le ratio du centre de ±0,05 : avec l'axe recalculé, retirer `eco_libre_echange` donne 0,873 au lieu de 0,920.
- Découper en tiers parmi les seuls 18 candidats classés (6 par tiers, Philippot au centre) donne :
  - calcul actuel : 1,08 / 0,83 / 1,08 ;
  - tri non arrondi : 1,07 / 0,94 / 0,99.

  Le chiffre dépend du découpage autant que du calcul.
- Comme l'indique déjà le README, le tiers central regroupe des profils hétérogènes (Ruffin, Villepin, Asselineau, Attal) : c'est une position sur un axe, pas un « centre » politique.

## 5. Corrections proposées (non appliquées)

| # | Proposition | Effet mesuré (vrai déroulé, 7 graines) | Avis |
|---|---|---|---|
| 1 | **Trier le classement sur le score non arrondi** (`score_brut`). L'affichage et le peloton de tête restent arrondis. | Complet : 1,080 / 0,885 / 1,014 → **1,072 / 0,981 / 0,951**, écart maximal 0,115 → 0,072. Rapide : 1,048 / 0,996 / 0,960 → 1,044 / 1,033 / 0,939. Sur main : 1,063 / 0,914 / 0,998 → 1,053 / 1,020 / 0,934. Les 38 tests passent. | **Recommandée** : supprime un avantage sans justification, ne règle rien sur l'audit. À reporter dans `src/lib/score.ts` du site, sinon le test de concordance échoue. |
| 2 | **Audit sur plusieurs graines** : moyenne et écart-type, ou 50 000 profils. Ajouter les deux pentes (avec leur incertitude) comme indicateurs principaux, et signaler les candidats jamais classés dans les tiers. | Supprime les écarts de ±0,03 entre deux passages, comme celui de la graine 2027. | **Recommandée** : sans elle, le critère « au moins aussi bon qu'avant » compare du bruit. |
| 3 | Baisser `POIDS_INCONNUE` à 0,35 | Avec la proposition 1 : 1,07 / 1,00 / 0,94 | Déconseillée : réglage sur l'audit ; √2-1 est justifié et vérifié. |
| 4 | Baisser `COUVERTURE_MIN` à 0,4 | Avec la proposition 1 : 1,03 / 1,00 / 0,97 | À décider côté produit : on afficherait des scores fondés sur 40 % des réponses. |
| 5 | Retirer des enjeux | 0,04 au plus sur le centre (`eco_libre_echange`) | Déconseillée : aucun responsable isolé. |
| 6 | Modifier le tirage | Le mode complet ne fait qu'ordonner les enjeux ; le rapide bouge peu. | Rien à changer. |

**Le critère, mesuré sur 7 graines**, en écart maximal au neutre :

| Données | Calcul actuel | Avec la proposition 1 |
|---|---|---|
| main (40 enjeux) | 0,086 | 0,066 |
| branche (62 enjeux) | 0,115 | 0,072 |

Sans correction, la branche est un peu moins bonne que main. Avec la proposition 1, elle est meilleure que main tel qu'il est aujourd'hui, et équivalente à main corrigé.

**Ce qui reste** (gauche +0,05 à +0,07, droite −0,05) tient à la géométrie des positions et à la couverture inégale des nouveaux enjeux. Seule la complétion des fiches peut le réduire, en priorité pour le tiers central : Attal, Ruffin, Asselineau et Villepin sur les 22 nouveaux enjeux.

---
Scripts de l'analyse : non versionnés (simulateur allégé validé contre `score.py`, balayages, bootstrap de l'axe). Ils sont disponibles sur demande et seront intégrés à `audit_biais.py` si la proposition 2 est retenue.
