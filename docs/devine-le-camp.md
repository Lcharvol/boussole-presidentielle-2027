# Test « devine le camp » : rapport par enjeu

Outil : [`outils/devine_le_camp.py`](../outils/devine_le_camp.py) ; résultats bruts agrégés : [`devine-le-camp.json`](devine-le-camp.json).

## Protocole

Six agents (Claude Sonnet) jouent des électeurs de bords différents : gauche radicale, gauche modérée, centre, droite, droite nationale, sans camp. Chacun reçoit les formulations mélangées, sous un code aléatoire, avec les deux options dans un ordre tiré au hasard, et répond pour chacune :

- **rédacteur** : d'après la seule formulation, la personne qui l'a rédigée est-elle de gauche, de droite, ou impossible à dire ?
- **favorisée** : quelle option la formulation présente-t-elle sous le jour le plus favorable (ou à égalité) ?
- **orientation** : quelle option un électeur de gauche choisirait-il ?

Les taux sont rapportés au camp de l'ancienne affirmation (celui de son pôle, calculé à partir des positions des candidats, sans étiquette posée à la main). 50 % = hasard ; « impossible à dire » et « à égalité » comptent pour moitié. **Une formulation est retenue si les taux « rédacteur » et « favorisée » restent entre 35 et 65 %.** Les 40 anciennes affirmations, passées au même test (6 agents), servent de témoin.

Trois tours : 86 formulations au premier tour (n = 6 réponses chacune) ; les 29 refusées ont été réécrites (ou retirées, pour 2) et repassées au deuxième tour (n = 12, deux tirages indépendants) ; les 15 encore refusées, au troisième (n = 12). Une formulation réécrite ne garde que les réponses portant sur son texte actuel.

## Résultats globaux

| | Rédacteur | Favorisée | Orientation | Retenues |
|---|---|---|---|---|
| Anciennes affirmations (témoin) | 60 % | 66 % (« d'accord ») | 91 % | — |
| Dilemmes (version actuelle) | 50 % | 47 % | 92 % | 76/83 |

**Ce que disent ces chiffres.** Le taux « favorisée » est le plus parlant : les anciennes affirmations présentaient l'option « d'accord » plus favorablement deux fois sur trois (66 %) ; les dilemmes sont à l'équilibre en moyenne (47 %), et 76 formulations sur 84 restent dans la fourchette (une, `soc_findevie.1`, est à retester : sa question a été raccourcie après le troisième tour). Le taux « rédacteur » est proche de 50 % partout, y compris pour les témoins (60 %) : les agents répondent le plus souvent « impossible à dire », ce qui en fait un critère peu discriminant.

**Orientation des pôles : une limite assumée.** Le taux « orientation » reste à 93 % : quelle que soit sa rédaction, un dilemme sur l'impôt sur la fortune ou le droit du sol laisse deviner quelle option défend la gauche. C'est le fond de l'enjeu, pas la formulation ; une boussole dont les options ne correspondraient à aucun camp ne départagerait personne. Ce que les dilemmes changent, c'est que la question ne porte plus la mesure d'un seul camp : les deux options sont présentées à égalité, à la même place à l'écran une fois sur deux. Le critère retenu est donc l'équilibre de la formulation (rédacteur, favorisée), et l'orientation est rapportée pour information.

**Formulations encore refusées.** Sept formulations restent hors de la fourchette après trois tours. Elles portent sur des enjeux de valeurs (aide à mourir, préférence nationale, AME, droit du sol) où les agents jugent une option plus favorable presque quelle que soit la rédaction, ou bien elles basculent de l'autre côté d'un tour à l'autre (`ecol_thermique2035.2` : 96 % puis 0 %). Elles demandent un arbitrage humain plutôt qu'un quatrième tour.

## Détail par enjeu

### `eco_retraite` — Économie, travail et fiscalité

Ancienne affirmation : « L'âge légal de départ à la retraite doit être ramené à 62 ans ou moins. » (témoin : rédacteur 58 %, « d'accord » favorisé 67 %)

Pôle A : **Revenir à 62 ans** — pôle B : **Garder 64 ans ou plus**  
Contexte : La réforme de 2023 relève l'âge légal de départ de 62 à 64 ans ; sa mise en œuvre a été suspendue fin 2025.

| Variante | Question | Option A | Option B | n | Rédacteur | Favorisée (pôle de l'ancienne affirmation) | Orientation | Retenue |
|---|---|---|---|---|---|---|---|---|
| `eco_retraite.1` | Quel âge légal de départ à la retraite faut-il viser ? | Revenir à 62 ans ou moins | Rester à 64 ans ou plus | 6 | 50 % | 50 % | 100 % | oui |
| `eco_retraite.2` | Pour l'équilibre des retraites, quel levier privilégier ? | Un départ à 62 ans, avec des cotisations plus élevées | Un départ à 64 ans ou plus, avec des cotisations inchangées | 12 | 50 % | 50 % | 100 % | oui |
| `eco_retraite.3` | Âge légal de départ à la retraite : | 62 ans ou moins | 64 ans ou plus | 6 | 50 % | 50 % | 100 % | oui |

### `eco_smic` — Économie, travail et fiscalité

Ancienne affirmation : « L'État doit augmenter nettement le SMIC, au-delà de la revalorisation automatique. » (témoin : rédacteur 58 %, « d'accord » favorisé 67 %)

Pôle A : **SMIC selon la seule revalorisation automatique** — pôle B : **SMIC relevé par décision de l'État**  
Contexte : Le SMIC est revalorisé chaque année selon une formule automatique ; l'État peut décider d'aller au-delà (« coup de pouce »).

| Variante | Question | Option A | Option B | n | Rédacteur | Favorisée (pôle de l'ancienne affirmation) | Orientation | Retenue |
|---|---|---|---|---|---|---|---|---|
| `eco_smic.1` | Comment faire évoluer le SMIC ? | Selon la seule revalorisation automatique | Au-delà de la revalorisation automatique | 6 | 50 % | 50 % | 100 % | oui |
| `eco_smic.2` | Pour les salariés payés au SMIC, que faut-il privilégier ? | La revalorisation automatique, pour ne pas freiner l'embauche | Une hausse décidée par l'État, pour soutenir leur pouvoir d'achat | 6 | 50 % | 50 % | 100 % | oui |

### `eco_depenses` — Économie, travail et fiscalité

Ancienne affirmation : « Pour réduire le déficit, il faut d'abord augmenter les impôts plutôt que baisser fortement les dépenses publiques. » (témoin : rédacteur 58 %, « d'accord » favorisé 58 %)

Pôle A : **Baisser les dépenses publiques** — pôle B : **Augmenter les impôts**

| Variante | Question | Option A | Option B | n | Rédacteur | Favorisée (pôle de l'ancienne affirmation) | Orientation | Retenue |
|---|---|---|---|---|---|---|---|---|
| `eco_depenses.1` | Pour réduire le déficit public, que faut-il faire d'abord ? | Réduire les dépenses publiques | Augmenter les recettes fiscales | 6 | 50 % | 50 % | 100 % | oui |
| `eco_depenses.2` | Pour rééquilibrer les comptes publics, quel levier privilégier ? | Des économies ciblées sur les dépenses de l'État et des collectivités | Des hausses d'impôts ciblées sur certains ménages ou certaines entreprises | 6 | 50 % | 50 % | 100 % | oui |
| `eco_depenses.3` | Face au déficit public : | Réduire les dépenses | Augmenter les impôts | 12 | 50 % | 46 % | 100 % | oui |

### `eco_patrimoine` — Économie, travail et fiscalité

Ancienne affirmation : « Il faut taxer davantage les très hauts patrimoines (rétablissement de l'ISF, taxe de type Zucman…). » (témoin : rédacteur 67 %, « d'accord » favorisé 67 %)

Pôle A : **Taxer davantage les grandes fortunes** — pôle B : **Garder la fiscalité actuelle du patrimoine**  
Contexte : Depuis 2018, seul le patrimoine immobilier est soumis à un impôt sur la fortune (IFI).

| Variante | Question | Option A | Option B | n | Rédacteur | Favorisée (pôle de l'ancienne affirmation) | Orientation | Retenue |
|---|---|---|---|---|---|---|---|---|
| `eco_patrimoine.1` | Sur l'imposition des plus grandes fortunes, que privilégier ? | Un impôt supplémentaire sur leur patrimoine | Le niveau d'imposition actuel | 6 | 50 % | 50 % | 100 % | oui |
| `eco_patrimoine.2` | Impôt sur le patrimoine des ménages les plus fortunés : | L'augmenter (retour de l'ISF, taxe Zucman…) | Le maintenir ou le baisser (impôt sur la fortune immobilière…) | 12 | 50 % | 58 % | 100 % | oui |

### `eco_35h` — Économie, travail et fiscalité

Ancienne affirmation : « Il faut assouplir la durée légale du travail (35 heures) pour permettre de travailler plus. » (témoin : rédacteur 67 %, « d'accord » favorisé 75 %)

Pôle A : **Garder les 35 heures** — pôle B : **Assouplir la durée légale**

| Variante | Question | Option A | Option B | n | Rédacteur | Favorisée (pôle de l'ancienne affirmation) | Orientation | Retenue |
|---|---|---|---|---|---|---|---|---|
| `eco_35h.1` | Durée légale du travail : | La garder à 35 heures par semaine | La porter au-delà de 35 heures par semaine | 12 | 50 % | 50 % | 100 % | oui |
| `eco_35h.2` | Pour le temps de travail, que faut-il privilégier ? | Les 35 heures comme référence commune | Une durée plus longue, négociée dans chaque entreprise | 6 | 50 % | 50 % | 100 % | oui |

### `ecol_nucleaire` — Écologie et énergie

Ancienne affirmation : « La France doit construire de nombreux nouveaux réacteurs nucléaires. » (témoin : rédacteur 50 %, « d'accord » favorisé 58 %)

Pôle A : **Construire de nouveaux réacteurs** — pôle B : **Réduire la part du nucléaire**

| Variante | Question | Option A | Option B | n | Rédacteur | Favorisée (pôle de l'ancienne affirmation) | Orientation | Retenue |
|---|---|---|---|---|---|---|---|---|
| `ecol_nucleaire.1` | Pour produire l'électricité, quelle voie privilégier ? | Construire de nouveaux réacteurs nucléaires | Réduire progressivement la part du nucléaire | 6 | 50 % | 50 % | 92 % | oui |
| `ecol_nucleaire.2` | Les réacteurs nucléaires actuels vieillissent. Que faut-il faire ? | Les remplacer par de nouveaux réacteurs | Les remplacer progressivement par d'autres sources | 6 | 50 % | 50 % | 100 % | oui |

### `ecol_renouvelables` — Écologie et énergie

Ancienne affirmation : « Il faut accélérer fortement le développement de l'éolien et du solaire. » (témoin : rédacteur 58 %, « d'accord » favorisé 67 %)

Pôle A : **Limiter l'éolien et le solaire** — pôle B : **Accélérer l'éolien et le solaire**

| Variante | Question | Option A | Option B | n | Rédacteur | Favorisée (pôle de l'ancienne affirmation) | Orientation | Retenue |
|---|---|---|---|---|---|---|---|---|
| `ecol_renouvelables.1` | Pour l'éolien et le solaire, que faut-il faire ? | Limiter les nouvelles installations | Accélérer les nouvelles installations | 6 | 50 % | 58 % | 100 % | oui |
| `ecol_renouvelables.2` | Face aux projets d'éoliennes et de parcs solaires, que privilégier ? | Le cadre de vie des riverains et les paysages | La production d'électricité renouvelable | 6 | 50 % | 50 % | 100 % | oui |

### `ecol_normes` — Écologie et énergie

Ancienne affirmation : « Il faut renforcer les normes environnementales, même si cela pèse sur les agriculteurs et les entreprises. » (témoin : rédacteur 58 %, « d'accord » favorisé 58 %)

Pôle A : **Renforcer les normes environnementales** — pôle B : **Alléger les normes environnementales**

| Variante | Question | Option A | Option B | n | Rédacteur | Favorisée (pôle de l'ancienne affirmation) | Orientation | Retenue |
|---|---|---|---|---|---|---|---|---|
| `ecol_normes.1` | Normes environnementales pour les entreprises et les agriculteurs : | Les renforcer pour mieux protéger l'environnement | Les alléger pour soulager ceux qui produisent | 6 | 50 % | 50 % | 100 % | oui |
| `ecol_normes.2` | Agriculture : quelle priorité ? | Réduire l'usage des pesticides et des engrais chimiques | Réduire les contraintes réglementaires sur les exploitations | 6 | 50 % | 58 % | 100 % | oui |
| `ecol_normes.3` | Pour les entreprises et les exploitations agricoles : | Plus d'exigences environnementales | Moins d'exigences environnementales | 6 | 50 % | 50 % | 100 % | oui |

### `ecol_thermique2035` — Écologie et énergie

Ancienne affirmation : « L'interdiction de vendre des voitures thermiques neuves à partir de 2035 doit être maintenue. » (témoin : rédacteur 58 %, « d'accord » favorisé 58 %)

Pôle A : **Revenir sur l'échéance de 2035** — pôle B : **Garder la fin des voitures thermiques neuves en 2035**  
Contexte : L'Union européenne a fixé à 2035 la fin de la vente de voitures neuves émettant du CO2 ; cette échéance est débattue.

| Variante | Question | Option A | Option B | n | Rédacteur | Favorisée (pôle de l'ancienne affirmation) | Orientation | Retenue |
|---|---|---|---|---|---|---|---|---|
| `ecol_thermique2035.1` | Fin de la vente des voitures thermiques neuves en 2035 : | Repousser ou supprimer cette échéance | Garder cette échéance | 6 | 50 % | 58 % | 100 % | oui |
| `ecol_thermique2035.2` | Pour les voitures neuves vendues à partir de 2035, que privilégier ? | Des voitures électriques, hybrides ou thermiques, au choix | Des voitures électriques uniquement | 12 | 50 % | 0 % | 100 % | **non** |

### `ecol_aerien` — Écologie et énergie

Ancienne affirmation : « Il faut taxer davantage le transport aérien (billets, kérosène) pour financer la transition écologique. » (témoin : rédacteur 58 %, « d'accord » favorisé 83 %)

Pôle A : **Taxer davantage l'aérien** — pôle B : **Garder la fiscalité actuelle de l'aérien**

| Variante | Question | Option A | Option B | n | Rédacteur | Favorisée (pôle de l'ancienne affirmation) | Orientation | Retenue |
|---|---|---|---|---|---|---|---|---|
| `ecol_aerien.1` | Billets d'avion et kérosène : | Les taxer davantage pour financer la transition écologique | Garder leur fiscalité actuelle pour ne pas renchérir les voyages | 6 | 50 % | 50 % | 100 % | oui |
| `ecol_aerien.2` | Taxes sur le transport aérien : | Les augmenter | Les laisser à leur niveau actuel | 6 | 50 % | 50 % | 100 % | oui |

### `sec_peines` — Sécurité et justice

Ancienne affirmation : « Il faut durcir les peines, par exemple avec des peines planchers ou minimales. » (témoin : rédacteur 67 %, « d'accord » favorisé 75 %)

Pôle A : **Peines plus lourdes, avec un minimum légal** — pôle B : **Peine fixée par le juge au cas par cas**

| Variante | Question | Option A | Option B | n | Rédacteur | Favorisée (pôle de l'ancienne affirmation) | Orientation | Retenue |
|---|---|---|---|---|---|---|---|---|
| `sec_peines.1` | Pour sanctionner les délits, que faut-il privilégier ? | Des peines plus lourdes, avec un minimum fixé par la loi | Des peines fixées par le juge au cas par cas | 6 | 50 % | 50 % | 100 % | oui |
| `sec_peines.2` | En cas de récidive, que privilégier ? | Une peine minimale fixée par la loi | Une peine fixée par le juge, au cas par cas | 12 | 50 % | 46 % | 100 % | oui |

### `sec_prisons` — Sécurité et justice

Ancienne affirmation : « Il faut construire massivement de nouvelles places de prison. » (témoin : rédacteur 58 %, « d'accord » favorisé 67 %)

Pôle A : **Construire des places de prison** — pôle B : **Développer les peines alternatives**  
Contexte : Les prisons françaises comptent plus de détenus que de places.

| Variante | Question | Option A | Option B | n | Rédacteur | Favorisée (pôle de l'ancienne affirmation) | Orientation | Retenue |
|---|---|---|---|---|---|---|---|---|
| `sec_prisons.1` | Face à la surpopulation carcérale, que faut-il privilégier ? | Construire de nouvelles places de prison | Développer les peines alternatives | 6 | 50 % | 50 % | 100 % | oui |
| `sec_prisons.2` | Les prisons sont surpeuplées. Quelle réponse privilégier ? | Augmenter le nombre de places de prison | Exécuter davantage de peines hors de prison (bracelet, travail d'intérêt général…) | 6 | 50 % | 42 % | 100 % | oui |

### `sec_cannabis` — Sécurité et justice

Ancienne affirmation : « La consommation de cannabis doit être légalisée et encadrée par l'État. » (témoin : rédacteur 58 %, « d'accord » favorisé 75 %)

Pôle A : **Maintenir l'interdiction du cannabis** — pôle B : **Légaliser et encadrer le cannabis**

| Variante | Question | Option A | Option B | n | Rédacteur | Favorisée (pôle de l'ancienne affirmation) | Orientation | Retenue |
|---|---|---|---|---|---|---|---|---|
| `sec_cannabis.1` | Cannabis récréatif : | Maintenir l'interdiction | Légaliser | 12 | 50 % | 50 % | 100 % | oui |
| `sec_cannabis.2` | Cannabis récréatif, que privilégier ? | Interdire la vente et la consommation | Autoriser la vente et la consommation | 12 | 50 % | 50 % | 100 % | oui |

### `sec_mineurs` — Sécurité et justice

Ancienne affirmation : « Les mineurs de 16 ans et plus doivent toujours être jugés selon les règles de la justice des mineurs. » (témoin : rédacteur 58 %, « d'accord » favorisé 67 %)

Pôle A : **Justice des mineurs pour les 16-18 ans** — pôle B : **Pouvoir juger les 16-18 ans comme des majeurs**

| Variante | Question | Option A | Option B | n | Rédacteur | Favorisée (pôle de l'ancienne affirmation) | Orientation | Retenue |
|---|---|---|---|---|---|---|---|---|
| `sec_mineurs.1` | Pour les mineurs de 16 à 18 ans auteurs de délits, que faut-il ? | Les juger selon les règles de la justice des mineurs | Pouvoir les juger comme des majeurs, selon les faits | 6 | 50 % | 58 % | 100 % | oui |
| `sec_mineurs.2` | Délinquance des 16-18 ans : que privilégier ? | Une justice spécialisée, centrée sur l'éducation | Les règles des majeurs, selon la gravité des faits | 6 | 50 % | 58 % | 100 % | oui |

### `sec_videosurveillance` — Sécurité et justice

Ancienne affirmation : « Il faut généraliser la vidéosurveillance algorithmique (détection automatique, reconnaissance faciale) dans l'espace public. » (témoin : rédacteur 58 %, « d'accord » favorisé 67 %)

Pôle A : **Généraliser l'analyse automatique des images** — pôle B : **Interdire ou limiter l'analyse automatique**  
Contexte : La vidéosurveillance algorithmique analyse les images des caméras par logiciel (détection de comportements, voire reconnaissance faciale).

| Variante | Question | Option A | Option B | n | Rédacteur | Favorisée (pôle de l'ancienne affirmation) | Orientation | Retenue |
|---|---|---|---|---|---|---|---|---|
| `sec_videosurveillance.1` | Caméras avec analyse automatique des images dans l'espace public : | Les généraliser | Les interdire | 12 | 50 % | 42 % | 100 % | oui |
| `sec_videosurveillance.2` | Dans l'espace public, que privilégier ? | La détection automatique des risques par les caméras | La protection de la vie privée face à ces caméras | 6 | 50 % | 42 % | 100 % | oui |

### `imm_baisse` — Immigration

Ancienne affirmation : « Il faut réduire fortement l'immigration légale (quotas, restriction du regroupement familial…). » (témoin : rédacteur 67 %, « d'accord » favorisé 75 %)

Pôle A : **Réduire l'immigration légale** — pôle B : **Maintenir ou ouvrir l'immigration légale**

| Variante | Question | Option A | Option B | n | Rédacteur | Favorisée (pôle de l'ancienne affirmation) | Orientation | Retenue |
|---|---|---|---|---|---|---|---|---|
| `imm_baisse.1` | Immigration légale (travail, famille, études) : | Fixer des quotas annuels plus bas qu'aujourd'hui | Garder ou élargir les possibilités actuelles | 12 | 50 % | 46 % | 100 % | oui |
| `imm_baisse.2` | Nombre de titres de séjour délivrés chaque année : | Le réduire | Le maintenir ou l'augmenter | 6 | 50 % | 50 % | 100 % | oui |
| `imm_baisse.3` | Regroupement familial (venue de la famille d'un étranger installé en France) : | Le restreindre | Le garder dans ses conditions actuelles ou l'assouplir | 6 | 50 % | 42 % | 100 % | oui |

### `imm_ame` — Immigration

Ancienne affirmation : « L'Aide médicale d'État (AME) pour les étrangers en situation irrégulière doit être supprimée ou réduite à l'urgence. » (témoin : rédacteur 67 %, « d'accord » favorisé 58 %)

Pôle A : **Maintenir l'AME** — pôle B : **Limiter l'AME aux soins urgents**  
Contexte : L'Aide médicale d'État (AME) prend en charge les soins des étrangers en situation irrégulière à faibles ressources.

| Variante | Question | Option A | Option B | n | Rédacteur | Favorisée (pôle de l'ancienne affirmation) | Orientation | Retenue |
|---|---|---|---|---|---|---|---|---|
| `imm_ame.1` | Aide médicale d'État (soins des étrangers en situation irrégulière) : | La maintenir dans sa forme actuelle | La limiter aux soins urgents | 6 | 50 % | 50 % | 100 % | oui |
| `imm_ame.2` | Soins des étrangers en situation irrégulière, que privilégier ? | Garder la couverture des soins courants | Réduire la couverture aux soins urgents | 12 | 50 % | 17 % | 100 % | **non** |

### `imm_regularisation` — Immigration

Ancienne affirmation : « Il faut faciliter la régularisation des travailleurs sans papiers, notamment dans les métiers en tension. » (témoin : rédacteur 75 %, « d'accord » favorisé 83 %)

Pôle A : **Restreindre les régularisations** — pôle B : **Faciliter les régularisations**

| Variante | Question | Option A | Option B | n | Rédacteur | Favorisée (pôle de l'ancienne affirmation) | Orientation | Retenue |
|---|---|---|---|---|---|---|---|---|
| `imm_regularisation.1` | Régularisation des étrangers sans papiers qui travaillent en France : | En accorder moins qu'aujourd'hui | En accorder plus qu'aujourd'hui | 12 | 50 % | 50 % | 100 % | oui |
| `imm_regularisation.2` | Étrangers sans titre de séjour qui travaillent en France : | Réduire le nombre de régularisations | Faciliter leur accès à un titre de séjour | 6 | 50 % | 50 % | 100 % | oui |

### `imm_droitdusol` — Immigration

Ancienne affirmation : « Le droit du sol doit être supprimé ou fortement restreint. » (témoin : rédacteur 67 %, « d'accord » favorisé 67 %)

Pôle A : **Maintenir le droit du sol** — pôle B : **Supprimer ou restreindre le droit du sol**  
Contexte : Un enfant né en France de parents étrangers peut devenir français à sa majorité (droit du sol).

| Variante | Question | Option A | Option B | n | Rédacteur | Favorisée (pôle de l'ancienne affirmation) | Orientation | Retenue |
|---|---|---|---|---|---|---|---|---|
| `imm_droitdusol.1` | Nationalité des enfants nés en France de parents étrangers : | Elle s'obtient automatiquement à 18 ans, comme aujourd'hui | Elle s'obtient sur demande, sous conditions | 12 | 50 % | 0 % | 100 % | **non** |
| `imm_droitdusol.2` | Droit du sol : | Le conserver | Le supprimer ou le restreindre | 6 | 50 % | 42 % | 100 % | oui |

### `imm_preference` — Immigration

Ancienne affirmation : « Certaines prestations sociales et l'accès au logement social doivent être réservés en priorité aux Français. » (témoin : rédacteur 83 %, « d'accord » favorisé 67 %)

Pôle A : **Mêmes règles pour Français et étrangers** — pôle B : **Priorité selon la nationalité française**

| Variante | Question | Option A | Option B | n | Rédacteur | Favorisée (pôle de l'ancienne affirmation) | Orientation | Retenue |
|---|---|---|---|---|---|---|---|---|
| `imm_preference.1` | Accès au logement social et à certaines aides sociales : | Les mêmes conditions pour les Français et les étrangers en situation régulière | Des conditions plus favorables pour les Français | 12 | 50 % | 21 % | 100 % | **non** |
| `imm_preference.2` | Attribution d'un logement social, à situation égale : | Selon les critères sociaux uniquement | Selon les critères sociaux et la nationalité | 12 | 50 % | 17 % | 100 % | **non** |

### `eur_integration` — Europe et international

Ancienne affirmation : « Il faut renforcer l'intégration européenne (défense commune, emprunt commun, davantage de décisions à la majorité). » (témoin : rédacteur 50 %, « d'accord » favorisé 67 %)

Pôle A : **Plus de décisions européennes communes** — pôle B : **Plus de décisions laissées aux États**

| Variante | Question | Option A | Option B | n | Rédacteur | Favorisée (pôle de l'ancienne affirmation) | Orientation | Retenue |
|---|---|---|---|---|---|---|---|---|
| `eur_integration.1` | Union européenne : quelle direction ? | Plus de décisions prises en commun (défense, emprunt commun, vote à la majorité) | Plus de décisions laissées à chaque État (budget, défense, droit de veto) | 12 | 50 % | 50 % | 92 % | oui |
| `eur_integration.2` | Pour peser face aux États-Unis et à la Chine, que privilégier ? | Une Europe plus intégrée, avec des politiques communes | Une coopération entre États qui gardent la main | 6 | 50 % | 58 % | 75 % | oui |

### `eur_primaute` — Europe et international

Ancienne affirmation : « Le droit français doit primer sur le droit européen, quitte à renégocier ou sortir des traités. » (témoin : rédacteur 67 %, « d'accord » favorisé 58 %)

Pôle A : **Appliquer le droit européen** — pôle B : **Faire primer le droit français**

| Variante | Question | Option A | Option B | n | Rédacteur | Favorisée (pôle de l'ancienne affirmation) | Orientation | Retenue |
|---|---|---|---|---|---|---|---|---|
| `eur_primaute.1` | En cas de conflit entre le droit français et le droit de l'Union européenne : | Appliquer le droit européen | Appliquer le droit français | 12 | 50 % | 50 % | 88 % | oui |
| `eur_primaute.2` | Les traités européens : | Les appliquer, y compris quand ils priment sur la loi française | Les renégocier pour que la loi française prime sur eux | 12 | 50 % | 50 % | 83 % | oui |

### `eur_ukraine` — Europe et international

Ancienne affirmation : « La France doit continuer à soutenir militairement l'Ukraine. » (témoin : rédacteur 50 %, « d'accord » favorisé 58 %)

Pôle A : **Poursuivre l'aide militaire à l'Ukraine** — pôle B : **Cesser l'aide militaire à l'Ukraine**

| Variante | Question | Option A | Option B | n | Rédacteur | Favorisée (pôle de l'ancienne affirmation) | Orientation | Retenue |
|---|---|---|---|---|---|---|---|---|
| `eur_ukraine.1` | Guerre en Ukraine : que doit faire la France ? | Poursuivre son aide militaire, pour soutenir la défense de l'Ukraine | Y mettre fin, pour éviter une escalade du conflit | 12 | 50 % | 62 % | 29 % | oui |
| `eur_ukraine.2` | Pour mettre fin à la guerre en Ukraine, que privilégier ? | Continuer à livrer des armes à l'Ukraine | Arrêter de livrer des armes à l'Ukraine | 12 | 50 % | 46 % | 33 % | oui |

### `eur_otan` — Europe et international

Ancienne affirmation : « La France doit quitter le commandement intégré de l'OTAN. » (témoin : rédacteur 50 %, « d'accord » favorisé 50 %)

Pôle A : **Rester dans le commandement intégré de l'OTAN** — pôle B : **Quitter le commandement intégré de l'OTAN**

| Variante | Question | Option A | Option B | n | Rédacteur | Favorisée (pôle de l'ancienne affirmation) | Orientation | Retenue |
|---|---|---|---|---|---|---|---|---|
| `eur_otan.1` | La France et l'OTAN : | Rester dans le commandement intégré | Quitter le commandement intégré | 6 | 50 % | 42 % | 33 % | oui |
| `eur_otan.2` | Pour la défense de la France, que privilégier ? | La coopération militaire au sein de l'OTAN | Une défense indépendante, hors du commandement de l'OTAN | 6 | 50 % | 50 % | 33 % | oui |

### `eur_defense3` — Europe et international

Ancienne affirmation : « Le budget de la défense doit être inférieur à 3 % du PIB. » (témoin : rédacteur 58 %, « d'accord » favorisé 58 %)

Pôle A : **Défense à 3 % du PIB ou plus** — pôle B : **Défense sous 3 % du PIB**  
Contexte : Le budget de la défense représente environ 2 % du PIB.

| Variante | Question | Option A | Option B | n | Rédacteur | Favorisée (pôle de l'ancienne affirmation) | Orientation | Retenue |
|---|---|---|---|---|---|---|---|---|
| `eur_defense3.1` | Budget de la défense : | Le porter à 3 % du PIB ou plus | Le garder sous 3 % du PIB | 6 | 50 % | 42 % | 100 % | oui |
| `eur_defense3.2` | Avec l'argent public disponible, que privilégier ? | Porter les dépenses militaires à 3 % du PIB | Limiter leur hausse pour financer d'autres priorités | 6 | 50 % | 42 % | 100 % | oui |

### `soc_medecins` — Santé et protection sociale

Ancienne affirmation : « Les médecins doivent pouvoir s'installer librement, y compris dans les zones déjà bien dotées en médecins. » (témoin : rédacteur 50 %, « d'accord » favorisé 50 %)

Pôle A : **Réguler l'installation des médecins** — pôle B : **Garder la liberté d'installation**

| Variante | Question | Option A | Option B | n | Rédacteur | Favorisée (pôle de l'ancienne affirmation) | Orientation | Retenue |
|---|---|---|---|---|---|---|---|---|
| `soc_medecins.1` | Pour lutter contre les déserts médicaux, que privilégier ? | Encadrer l'installation des médecins dans les zones bien dotées | Garder la liberté d'installation et inciter à s'installer ailleurs | 6 | 50 % | 50 % | 100 % | oui |
| `soc_medecins.2` | Liberté d'installation des médecins : | La limiter dans les zones bien pourvues | La conserver, y compris dans ces zones | 12 | 50 % | 50 % | 100 % | oui |

### `soc_findevie` — Santé et protection sociale

Ancienne affirmation : « L'aide à mourir, légalisée en 2026 sous conditions strictes, doit être maintenue plutôt qu'abrogée. » (témoin : rédacteur 58 %, « d'accord » favorisé 92 %)

Pôle A : **Abroger l'aide à mourir** — pôle B : **Maintenir l'aide à mourir**  
Contexte : L'aide à mourir a été légalisée en 2026 sous conditions.

| Variante | Question | Option A | Option B | n | Rédacteur | Favorisée (pôle de l'ancienne affirmation) | Orientation | Retenue |
|---|---|---|---|---|---|---|---|---|
| `soc_findevie.1` | Aide à mourir : | Revenir sur cette loi | Garder cette loi | — | — | — | — | à retester (question raccourcie après le 3e tour) |
| `soc_findevie.2` | Pour la fin de vie, que privilégier ? | Interdire l'aide à mourir | Autoriser l'aide à mourir | 12 | 50 % | 50 % | 100 % | oui |

### `soc_rsa` — Santé et protection sociale

Ancienne affirmation : « Le versement du RSA doit être conditionné à des heures d'activité. » (témoin : rédacteur 58 %, « d'accord » favorisé 67 %)

Pôle A : **RSA conditionné à des heures d'activité** — pôle B : **RSA sans obligation d'heures d'activité**

| Variante | Question | Option A | Option B | n | Rédacteur | Favorisée (pôle de l'ancienne affirmation) | Orientation | Retenue |
|---|---|---|---|---|---|---|---|---|
| `soc_rsa.1` | Revenu de solidarité active (RSA) : | Exiger des heures d'activité pour le verser | Le verser sans exiger d'heures d'activité | 12 | 50 % | 71 % | 100 % | **non** |
| `soc_rsa.2` | Pour les allocataires du RSA, que privilégier ? | Une contrepartie en heures d'activité | Un accompagnement sans obligation d'heures | 6 | 50 % | 50 % | 100 % | oui |

### `soc_100secu` — Santé et protection sociale

Ancienne affirmation : « La Sécurité sociale doit rembourser à 100 % les soins prescrits, en supprimant le rôle des complémentaires santé. » (témoin : rédacteur 33 %, « d'accord » favorisé 67 %)

Pôle A : **Tout rembourser par la Sécurité sociale** — pôle B : **Garder les complémentaires santé**

| Variante | Question | Option A | Option B | n | Rédacteur | Favorisée (pôle de l'ancienne affirmation) | Orientation | Retenue |
|---|---|---|---|---|---|---|---|---|
| `soc_100secu.1` | Remboursement des soins : | Tout par la Sécurité sociale, sans complémentaire santé | Partagé entre Sécurité sociale et complémentaires santé | 12 | 50 % | 42 % | 0 % | oui |
| `soc_100secu.2` | Complémentaires santé (mutuelles) : | Les remplacer par un remboursement intégral par la Sécurité sociale | Les conserver aux côtés de la Sécurité sociale | 6 | 50 % | 50 % | 17 % | oui |

### `soc_chomage` — Santé et protection sociale

Ancienne affirmation : « Il faut réduire la durée ou le montant de l'indemnisation chômage pour inciter au retour à l'emploi. » (témoin : rédacteur 75 %, « d'accord » favorisé 67 %)

Pôle A : **Maintenir l'indemnisation chômage** — pôle B : **Réduire l'indemnisation chômage**

| Variante | Question | Option A | Option B | n | Rédacteur | Favorisée (pôle de l'ancienne affirmation) | Orientation | Retenue |
|---|---|---|---|---|---|---|---|---|
| `soc_chomage.1` | Assurance chômage : | Garder la durée et le montant actuels des allocations | Réduire la durée ou le montant des allocations | 12 | 50 % | 42 % | 100 % | oui |
| `soc_chomage.2` | Pour les demandeurs d'emploi, que privilégier ? | Une indemnisation qui protège leur niveau de vie | Une indemnisation plus courte qui incite à reprendre un emploi | 6 | 50 % | 50 % | 100 % | oui |

### `edu_prive` — Éducation

Ancienne affirmation : « Il faut réduire le financement public de l'enseignement privé sous contrat. » (témoin : rédacteur 58 %, « d'accord » favorisé 67 %)

Pôle A : **Maintenir le financement du privé sous contrat** — pôle B : **Réduire le financement du privé sous contrat**  
Contexte : Les écoles privées sous contrat sont financées en grande partie par l'État (salaires des enseignants) et les collectivités.

| Variante | Question | Option A | Option B | n | Rédacteur | Favorisée (pôle de l'ancienne affirmation) | Orientation | Retenue |
|---|---|---|---|---|---|---|---|---|
| `edu_prive.1` | Écoles privées sous contrat : | Maintenir leur financement public | Réduire leur financement public | 6 | 50 % | 50 % | 92 % | oui |
| `edu_prive.2` | Argent public pour l'école : | Continuer à financer aussi le privé sous contrat | Le concentrer davantage sur l'école publique | 6 | 50 % | 50 % | 100 % | oui |

### `edu_autorite` — Éducation

Ancienne affirmation : « Il faut restaurer l'autorité à l'école (uniforme, sanctions renforcées, groupes de niveau). » (témoin : rédacteur 83 %, « d'accord » favorisé 75 %)

Pôle A : **Plus de discipline** — pôle B : **Plus d'accompagnement**

| Variante | Question | Option A | Option B | n | Rédacteur | Favorisée (pôle de l'ancienne affirmation) | Orientation | Retenue |
|---|---|---|---|---|---|---|---|---|
| `edu_autorite.1` | Pour améliorer le climat scolaire, que privilégier ? | Uniforme, sanctions renforcées et groupes de niveau | Effectifs réduits, plus d'adultes encadrants et classes mixtes | 12 | 46 % | 17 % | 100 % | **non** |
| `edu_autorite.2` | Au collège, que faut-il privilégier ? | Des règles plus exigeantes et des groupes de niveau | Des classes moins chargées et mélangeant les niveaux | 6 | 50 % | 50 % | 100 % | oui |

### `edu_signes` — Éducation

Ancienne affirmation : « Le port de signes religieux doit être interdit aux parents qui accompagnent les sorties scolaires. » (témoin : rédacteur 58 %, « d'accord » favorisé 58 %)

Pôle A : **Signes religieux autorisés aux parents accompagnateurs** — pôle B : **Signes religieux interdits aux parents accompagnateurs**

| Variante | Question | Option A | Option B | n | Rédacteur | Favorisée (pôle de l'ancienne affirmation) | Orientation | Retenue |
|---|---|---|---|---|---|---|---|---|
| `edu_signes.1` | Parents qui accompagnent les sorties scolaires : | Ils peuvent porter un signe religieux | Ils ne doivent pas porter de signe religieux | 6 | 50 % | 50 % | 100 % | oui |
| `edu_signes.2` | Neutralité religieuse lors des sorties scolaires : | Elle s'impose aux enseignants, pas aux parents accompagnateurs | Elle s'impose aussi aux parents accompagnateurs | 6 | 50 % | 50 % | 92 % | oui |

### `edu_etudiants` — Éducation

Ancienne affirmation : « Il faut créer une allocation d'autonomie versée à tous les étudiants. » (témoin : rédacteur 58 %, « d'accord » favorisé 67 %)

Pôle A : **Allocation pour tous les étudiants** — pôle B : **Bourses selon les revenus des parents**

| Variante | Question | Option A | Option B | n | Rédacteur | Favorisée (pôle de l'ancienne affirmation) | Orientation | Retenue |
|---|---|---|---|---|---|---|---|---|
| `edu_etudiants.1` | Aide financière aux étudiants : | Une allocation versée à tous les étudiants | Des bourses selon les revenus des parents | 6 | 50 % | 50 % | 92 % | oui |
| `edu_etudiants.2` | Pour aider les étudiants à financer leurs études, que privilégier ? | Une allocation d'autonomie pour tous | Des bourses réservées aux familles modestes | 6 | 50 % | 50 % | 100 % | oui |

### `edu_apprentissage` — Éducation

Ancienne affirmation : « Il faut permettre l'entrée en apprentissage dès 14 ans. » (témoin : rédacteur —, « d'accord » favorisé 67 %)

Pôle A : **Apprentissage après le collège** — pôle B : **Apprentissage dès 14 ans**  
Contexte : Aujourd'hui, on peut entrer en apprentissage à 15 ans si l'on a terminé le collège, à 16 ans sinon.

| Variante | Question | Option A | Option B | n | Rédacteur | Favorisée (pôle de l'ancienne affirmation) | Orientation | Retenue |
|---|---|---|---|---|---|---|---|---|
| `edu_apprentissage.1` | Apprentissage (formation en alternance chez un employeur) : | Le garder après le collège (15-16 ans) | L'ouvrir dès 14 ans | 6 | — | 50 % | — | oui |
| `edu_apprentissage.2` | Pour les élèves de 14 ans en difficulté au collège, que privilégier ? | Les garder au collège avec un accompagnement renforcé | Leur permettre d'entrer en apprentissage | 6 | — | 42 % | — | oui |

### `ins_proportionnelle` — Institutions et démocratie

Ancienne affirmation : « Les députés doivent être élus à la proportionnelle. » (témoin : rédacteur 50 %, « d'accord » favorisé 58 %)

Pôle A : **Élection des députés à la proportionnelle** — pôle B : **Scrutin majoritaire par circonscription**

| Variante | Question | Option A | Option B | n | Rédacteur | Favorisée (pôle de l'ancienne affirmation) | Orientation | Retenue |
|---|---|---|---|---|---|---|---|---|
| `ins_proportionnelle.1` | Élection des députés : | À la proportionnelle, selon le score des listes | Au scrutin majoritaire dans chaque circonscription, comme aujourd'hui | 6 | 50 % | 50 % | 100 % | oui |
| `ins_proportionnelle.2` | Pour l'Assemblée nationale, que privilégier ? | Une représentation fidèle du poids de chaque parti | Un lien direct entre chaque député et sa circonscription | 6 | 50 % | 50 % | 100 % | oui |

### `ins_ric` — Institutions et démocratie

Ancienne affirmation : « Il faut instaurer le référendum d'initiative citoyenne (RIC). » (témoin : rédacteur 50 %, « d'accord » favorisé 58 %)

Pôle A : **Instaurer le RIC** — pôle B : **Laisser la loi au Parlement**  
Contexte : Le référendum d'initiative citoyenne (RIC) permettrait à des citoyens de déclencher un référendum par pétition.

| Variante | Question | Option A | Option B | n | Rédacteur | Favorisée (pôle de l'ancienne affirmation) | Orientation | Retenue |
|---|---|---|---|---|---|---|---|---|
| `ins_ric.1` | Référendum d'initiative citoyenne (RIC) : | L'instaurer, pour que les citoyens puissent déclencher un vote | Ne pas l'instaurer, pour laisser la loi au Parlement | 6 | 50 % | 58 % | 92 % | oui |
| `ins_ric.2` | Pour décider des lois, que privilégier ? | Des référendums que les citoyens peuvent déclencher eux-mêmes | Le vote des lois par les représentants élus | 6 | 50 % | 50 % | 75 % | oui |

### `ins_6e` — Institutions et démocratie

Ancienne affirmation : « Il faut passer à une VIe République et réduire les pouvoirs du président. » (témoin : rédacteur 58 %, « d'accord » favorisé 67 %)

Pôle A : **Garder la Ve République** — pôle B : **Passer à une VIe République**

| Variante | Question | Option A | Option B | n | Rédacteur | Favorisée (pôle de l'ancienne affirmation) | Orientation | Retenue |
|---|---|---|---|---|---|---|---|---|
| `ins_6e.1` | Institutions : | Garder la Constitution actuelle (Ve République) et les pouvoirs du président | Une nouvelle Constitution (VIe République), avec un président aux pouvoirs réduits | 6 | 50 % | 58 % | 100 % | oui |
| `ins_6e.2` | Rôle du président de la République : | Le conserver tel qu'il est | Le réduire au profit du Parlement | 6 | 50 % | 50 % | 100 % | oui |

### `ins_parlementaires` — Institutions et démocratie

Ancienne affirmation : « Il faut réduire le nombre de députés et de sénateurs. » (témoin : rédacteur 58 %, « d'accord » favorisé 67 %)

Pôle A : **Réduire le nombre de parlementaires** — pôle B : **Garder le nombre de parlementaires**  
Contexte : Le Parlement compte 577 députés et 348 sénateurs.

| Variante | Question | Option A | Option B | n | Rédacteur | Favorisée (pôle de l'ancienne affirmation) | Orientation | Retenue |
|---|---|---|---|---|---|---|---|---|
| `ins_parlementaires.1` | Nombre de députés et de sénateurs : | Le réduire | Le conserver | 6 | 50 % | 50 % | 83 % | oui |
| `ins_parlementaires.2` | Pour le Parlement, que privilégier ? | Moins de parlementaires, pour réduire le coût | Autant de parlementaires, pour garder la proximité avec les territoires | 6 | 50 % | 50 % | 100 % | oui |

### `ins_voteblanc` — Institutions et démocratie

Ancienne affirmation : « Le vote blanc doit être reconnu comme un suffrage exprimé. » (témoin : rédacteur —, « d'accord » favorisé 67 %)

Pôle A : **Compter le vote blanc comme suffrage exprimé** — pôle B : **Compter le vote blanc à part**

| Variante | Question | Option A | Option B | n | Rédacteur | Favorisée (pôle de l'ancienne affirmation) | Orientation | Retenue |
|---|---|---|---|---|---|---|---|---|
| `ins_voteblanc.1` | Vote blanc : | Le compter dans les suffrages exprimés | Le compter à part, sans effet sur le résultat | 6 | — | 58 % | — | oui |
| `ins_voteblanc.2` | Pour calculer le résultat d'une élection, que privilégier ? | Inclure les votes blancs dans les pourcentages | Calculer les pourcentages sur les seuls votes pour un candidat | 6 | — | 50 % | — | oui |
