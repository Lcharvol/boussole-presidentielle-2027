# Audit de neutralité à 62 enjeux : d'où vient l'écart ?

Analyse du 21 octobre 2026 sur la branche `v2/completion` (PR #23). Aucune position n'a été modifiée. **Mise à jour** : Lcharvol a validé la proposition 1 (tri sur le score non arrondi), appliquée dans `score.py` sur cette branche. La proposition 2 (audit sur plusieurs graines, pentes, candidats jamais classés signalés dans les tiers) est appliquée dans `audit_biais.py --graines N` : sur 7 graines (2027 à 2033, 10 000 profils), complet 1,07 / 0,99 / 0,95, rapide 1,04 / 1,03 / 0,95. Les autres propositions ne sont pas appliquées.

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
- Mode adaptatif (branche, 2 000 profils × 7 graines) : 0,990 / 1,046 / 0,977, avec ±0,03 à 0,04 d'une graine à l'autre. Aux 500 profils du README, l'écart-type atteint environ ±0,06, et à 300 profils environ ±0,09.

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

### Philippe (1,31) et Philippot (0,56)

Simulateur, mode complet, 10 graines. Ratio de Philippe / ratio de Philippot :

| Facteur | Philippe | Philippot |
|---|---|---|
| 62 enjeux (actuel) | 1,20 | 0,54 (classé 84 %) |
| 40 premiers enjeux | 1,26 | 0,64 (classé 100 %) |
| (a) 62 moins un nouvel enjeu (22 cas) | 1,14 à 1,24 | 0,52 à 0,57 |
| (a) 62 moins un thème (8 cas) | 1,15 à 1,24 | 0,53 à 0,61 |
| (b) Tri non arrondi | 1,20 | **0,71** |
| (b) `POIDS_INCONNUE` = 0,25 / 0 | 1,21 / 1,19 | 0,68 / **0,96** |
| (b) `COUVERTURE_MIN` = 0,4 | 1,25 | 0,57 |
| (c) Part de ±2 dans ses positions | 0,40 (modéré) | 0,59 |

**Philippe.** Son ratio ne bouge presque dans aucune variante : son avantage ne tient ni aux nouveaux enjeux, ni à la couverture, ni à l'arrondi.
- Ses positions sont modérées (40 % de ±2, l'une des parts les plus basses), et son seul voisin proche est Attal (r = 0,68).
- Sur l'ensemble des candidats, la part de ±2 est faiblement corrélée au ratio (r = −0,32 avec le tri non arrondi) : une position modérée est un peu plus souvent proche d'une réponse au hasard.
- C'est un vrai profil de positions, à expliquer dans le README, pas à corriger.

**Philippot.** Son déficit tient à la couverture :
- Il ne couvre que 7 des 22 nouveaux enjeux. Sa couverture passe de 62,5 % à 52 %, juste au-dessus du seuil.
- Il perd la plupart des ex aequo, d'où la remontée à 0,71 avec le tri non arrondi.
- Ses scores sont presque toujours atténués par les positions inconnues, d'où 0,96 sans aucune atténuation. Supprimer l'atténuation ne serait pas une correction : cela avantagerait mécaniquement toutes les fiches peu remplies (centre à 1,07).
- Le reste du déficit est géométrique : son plus proche voisin est Le Pen (r = 0,66), et Asselineau et Dupont-Aignan sont proches aussi.
- La correction légitime est de **compléter sa fiche** sur les nouveaux enjeux, par recherche documentaire relue, sans viser une valeur.

**Tiers central (0,91).**
- (a) Aucun nouvel enjeu ni aucun thème ne dépasse +0,04 : l'effet est diffus.
- (b) La cause principale est la couverture, via le départage des ex aequo (section 3).
- (c) Le centre est le tiers le plus modéré (Villepin 0,21 de ±2, Attal 0,24, Asselineau 0,41). Cet effet joue plutôt *en sa faveur* (r = −0,32) : il ne l'explique pas.

### (d) Sens des formulations des nouveaux enjeux

Section 2 d'`audit_biais.py`, sur les 22 nouveaux enjeux :

| Pôle le plus proche de la gauche de l'axe | Nombre d'enjeux |
|---|---|
| Pôle A | 8 |
| Pôle B | 9 |
| Transversal | 4 (`eco_libre_echange`, `sec_controle_identite`, `eur_dissuasion`, `soc_allocations_familiales`) |
| Indéterminé (5 positions) | 1 (`ins_cumul`) |

- C'est équilibré, et le côté d'affichage est de toute façon tiré au hasard : un penchant pour un côté de l'écran ne déplace l'écart droite − gauche que de 4 à 5 points.
- **Aucun retournement de pôles n'est justifié.**

Enjeux qui départagent peu (pouvoir de départage le plus bas) :
- `ins_mandat_unique` : 0,16, 6 positions dont 5 au pôle A ;
- `edu_remuneration` : 0,27 ;
- `sec_controle_identite` : 0,32 ;
- `ins_cumul` : 0,32, 5 positions.

Effet de leur retrait (mode complet) :

| Variante | Calcul actuel | Tri non arrondi |
|---|---|---|
| 62 enjeux | 1,081 / 0,880 / 1,016 | 1,071 / 0,978 / 0,954 |
| Sans `ins_mandat_unique` et `ins_cumul` | 1,082 / 0,895 / 1,004 | 1,068 / 0,992 / 0,947 |
| Sans les 6 enjeux de pouvoir < 0,35 | 1,069 / 0,920 / 0,996 | 1,065 / 1,003 / 0,940 |

- Le gain est faible (+0,015 à +0,04 sur le centre) et ne change presque rien pour Philippe et Philippot.
- Il vient de la couverture : ces enjeux ajoutent surtout des positions inconnues.
- Le mode rapide les tire déjà rarement (tirage pondéré par le pouvoir de départage).
- Un retrait ne se justifierait donc que pour des raisons de contenu, pas pour l'audit. Les compléter est préférable.

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
| 1 | **Trier le classement sur le score non arrondi** (appliquée). L'affichage et le peloton de tête restent arrondis. | Complet : 1,080 / 0,885 / 1,014 → **1,072 / 0,981 / 0,951**, écart maximal 0,115 → 0,072. Rapide : 1,048 / 0,996 / 0,960 → 1,044 / 1,033 / 0,939. Adaptatif (2 000 profils) : 0,990 / 1,046 / 0,977 → 0,984 / **1,109** / 0,939. Sur main : 1,063 / 0,914 / 0,998 → 1,053 / 1,020 / 0,934. Les tests passent (39 avec le nouveau test des ex aequo). | **Recommandée** : supprime un avantage sans justification, ne règle rien sur l'audit. Elle améliore nettement le mode complet, mais dégrade un peu le mode rapide et le mode adaptatif (voir ci-dessous). À reporter dans `src/lib/score.ts` du site, sinon le test de concordance échoue. |
| 2 | **Audit sur plusieurs graines** : moyenne et écart-type, ou 50 000 profils. Ajouter les deux pentes (avec leur incertitude) comme indicateurs principaux, et signaler les candidats jamais classés dans les tiers. | Supprime les écarts de ±0,03 entre deux passages, comme celui de la graine 2027. | **Recommandée** : sans elle, le critère « au moins aussi bon qu'avant » compare du bruit. |
| 3 | Baisser `POIDS_INCONNUE` à 0,35 | Avec la proposition 1 : 1,07 / 1,00 / 0,94 | Déconseillée : réglage sur l'audit ; √2-1 est justifié et vérifié. |
| 4 | Baisser `COUVERTURE_MIN` à 0,4 | Avec la proposition 1 : 1,03 / 1,00 / 0,97 | À décider côté produit : on afficherait des scores fondés sur 40 % des réponses. |
| 5 | Retirer des enjeux | 0,04 au plus sur le centre (`eco_libre_echange`). Retirer les 6 enjeux de pouvoir < 0,35 : +0,04 au centre. | Déconseillée pour l'audit : aucun responsable isolé. |
| 6 | Modifier le tirage | Le mode complet ne fait qu'ordonner les enjeux ; le rapide bouge peu. | Rien à changer. |
| 7 | Retourner ou reformuler des pôles | Sens des pôles équilibré (A 8, B 9, transversaux 4) ; le côté d'affichage est tiré au hasard. | Pas justifié. |
| 8 | **Compléter des fiches** sur les nouveaux enjeux, par recherche documentaire relue, sans viser une valeur : Philippot (7/22), Attal (5/22), Ruffin et Asselineau (9/22), Villepin (11/22) | Non simulable sans inventer des positions. C'est le levier sur le reste des écarts (couverture). | **Recommandée** (travail de recherche, relecture par Lcharvol). |
| 9 | README : expliquer les écarts individuels qui reflètent un vrai profil (Philippe : positions modérées, peu de voisins proches ; duos très corrélés qui se partagent les premières places) | — | **Recommandée**. |

**Effet de la proposition 1 selon le mode**, en écart maximal au neutre (branche, 7 graines) :

| Mode | Avant | Après |
|---|---|---|
| Complet | 0,115 | **0,072** |
| Rapide | 0,048 | 0,061 |
| Adaptatif | 0,054 | 0,109 (centre 1,11) |

Avec le tri par couverture, les candidats les plus couverts, plutôt aux deux bouts de l'axe, gagnaient les ex aequo. Supprimer ce tri enlève cet avantage dans tous les modes. Dans les modes courts, il compensait un léger excès du tiers central. Le mode adaptatif sert ce tiers pour une raison propre à ce mode, à analyser à part : il choisit les enjeux qui départagent le peloton de tête, et les fiches moins couvertes y ont moins de positions connues. Je n'ai pas cherché à compenser cet excès par un réglage.

**Le critère, mesuré sur 7 graines**, en écart maximal au neutre :

| Données | Calcul actuel | Avec la proposition 1 |
|---|---|---|
| main (40 enjeux) | 0,086 | 0,066 |
| branche (62 enjeux) | 0,115 | 0,072 |

Sans correction, la branche est un peu moins bonne que main. Avec la proposition 1, elle est meilleure que main tel qu'il est aujourd'hui, et équivalente à main corrigé.

**Ce qui reste** (gauche +0,05 à +0,07, droite −0,05) tient à la géométrie des positions et à la couverture inégale des nouveaux enjeux. Seule la complétion des fiches peut le réduire, en priorité pour le tiers central : Attal, Ruffin, Asselineau et Villepin sur les 22 nouveaux enjeux.

---
Scripts de l'analyse : non versionnés (simulateur allégé validé contre `score.py`, balayages, bootstrap de l'axe). Ils sont disponibles sur demande et seront intégrés à `audit_biais.py` si la proposition 2 est retenue.

## 6. Mode adaptatif après le tri sur le score exact

Vrai déroulé (`tirage.py` et `score.py` de la branche), 2 000 profils × 7 graines par variante. Variantes obtenues en remplaçant des fonctions dans le script d'analyse : rien n'est modifié dans le dépôt. Bruit d'une graine à l'autre : ±0,02 à 0,05 par tiers. Aux 500 profils du README, il est d'environ ±0,06 à 0,08 : un seul passage à 500 profils ne permet pas de juger ce mode.

**Les critères d'arrêt ne jouent pas.** Avec des réponses au hasard, 99,96 % des parcours vont jusqu'à 32 questions. Le peloton de tête ne se détache jamais, et « plus d'enjeu utile » n'arrive presque jamais. L'audit ne teste donc ni l'un ni l'autre critère.

**Le socle n'y est pour rien.** Après les 12 premières questions, les tiers valent 1,04 / 1,02 / 0,95, comme en mode rapide. L'écart se crée pendant les 20 questions suivantes.

| Sélection des lots (après le socle) | gauche | centre | droite | Écart maximal |
|---|---|---|---|---|
| Actuelle : les 4 meilleurs gains de `departage()`, un par thème | 1,006 | **1,096** | 0,928 | 0,096 |
| Actuelle, avec l'ancien tri (arrondi puis couverture) | 1,011 | 1,046 | 0,958 | 0,054 |
| Gain calculé sur tous les candidats au lieu du peloton | 1,004 | 1,110 | 0,920 | 0,110 |
| `departage()` sans le facteur « part des positions connues » | 0,976 | 1,068 | 0,978 | 0,068 |
| Lots tirés au hasard, sans gain | 1,069 | 0,976 | 0,957 | 0,069 |
| **Lots tirés au hasard, pondérés par le gain** | 1,026 | 1,035 | 0,951 | **0,049** |
| Pondérés par le gain, sans le facteur de couverture | 1,052 | 0,993 | 0,958 | 0,058 |

**Cause.** Il n'y en a qu'une : la sélection prend toujours les enjeux de plus fort gain.
- Le gain calculé sur tous les candidats donne le même excès. Ce n'est donc pas l'adaptation au peloton, mais le fait de toujours poser les enjeux les plus clivants et les mieux renseignés (`eur_ukraine`, `eco_retraite`, `imm_baisse`…).
- **Couverture** : sur ces enjeux, des fiches peu remplies dépassent 50 % de couverture et entrent dans le classement. Cazeneuve est classé dans 47 % des parcours (5 % avec des lots au hasard), Bertrand dans 91 % (9 %). Cazeneuve, au tiers central, y obtient un ratio de 1,42 et pèse pour environ 0,03 des 0,10 d'excès.
- **Géométrie** : le reste vient d'Asselineau (1,11 contre 0,92 au hasard), de Branco (1,01 contre 0,87) et de Villepin (1,22 contre 1,11). Sur des enjeux très clivés, les candidats de chaque bout ont des réponses proches et se partagent les premières places, alors que les profils atypiques du tiers central se distinguent.
- L'ancien tri par couverture masquait en partie cet effet : il donnait les ex aequo aux fiches les plus remplies, situées aux deux bouts de l'axe.

**Correction proposée** (non appliquée) : dans `suivantes()`, **tirer les enjeux du lot au hasard parmi les enjeux utiles (gain ≥ `GAIN_MIN`), avec une probabilité proportionnelle à leur gain** (`tirage_pondere`, déjà utilisé par le socle), au lieu de prendre les 4 meilleurs.
- On garde un enjeu par thème et les mêmes critères d'arrêt.
- Justification : c'est la règle du mode rapide. Un enjeu presque aussi utile garde sa chance, et la sélection ne se fige plus sur les mêmes enjeux clivants.
- Effet sur le mode adaptatif : 1,006 / 1,096 / 0,928 → 1,026 / 1,035 / 0,951 (écart maximal 0,096 → 0,049, meilleur qu'avant le tri exact).
- Effet sur les modes complet et rapide : aucun, car ils n'appellent pas `suivantes()`.
- **Coût pour une vraie personne** (profils cohérents : positions d'un candidat classé, avec une part de réponses au hasard ; 700 profils) :

  | Bruit | Variante | Cible 1re | Cible dans le top 3 | Questions |
  |---|---|---|---|---|
  | 30 % | Actuel | 99,1 % | 100 % | 28,6 |
  | 30 % | Lots pondérés | 98,6 % | 99,3 % | 28,9 |
  | 50 % | Actuel | 88,1 % | 97,6 % | 31,3 |
  | 50 % | Lots pondérés | 87,0 % | 97,3 % | 31,5 |

  Les écarts sont dans le bruit de l'échantillon (±0,4 à 1,2 point).
- **À reporter dans le site** : la même règle dans `src/lib/tirage.ts`, avec le même générateur aléatoire et la même graine, pour que le site et le skill posent les mêmes questions (concordance). `score.ts` n'est pas concerné.
- Autres pistes écartées :
  - retirer le facteur de couverture de `departage()` : moins bon (0,068) et moins justifié, puisqu'un enjeu inconnu pour un candidat ne peut pas le départager ;
  - lots purement au hasard : 0,069, et le mode perd son intérêt ;
  - toucher aux critères d'arrêt : sans effet sur l'audit.
- **Pour l'audit** : passer le mode adaptatif à 2 000 profils au moins, ou faire la moyenne sur plusieurs graines (PR #25).
