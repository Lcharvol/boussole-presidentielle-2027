# Migration au format 2 : des affirmations aux dilemmes

Script : [`outils/migrer_v2.py`](../outils/migrer_v2.py). Au format 1, une position valait +2 pour « tout à fait d'accord » avec l'affirmation ; au format 2, -2 pour le pôle A et +2 pour le pôle B. Pour chaque enjeu, la colonne « Pôle de l'ancienne affirmation » dit quel pôle correspond à « d'accord » : **B** = valeur reprise, **A** = valeur inversée. Citations, sources, dates, confiance et résumés sont conservés.

Bilan : 565 positions migrées, 293 inversées, 272 reprises. Les pôles sont répartis pour que le pôle proche de la gauche soit tantôt A, tantôt B (15 et 17 enjeux).

| Enjeu | Ancienne affirmation | Pôle A (-2) | Pôle B (+2) | Pôle de l'ancienne affirmation | Recodage |
|---|---|---|---|---|---|
| `eco_retraite` | L'âge légal de départ à la retraite doit être ramené à 62 ans ou moins. | Revenir à 62 ans | Garder 64 ans ou plus | A | non |
| `eco_smic` | L'État doit augmenter nettement le SMIC, au-delà de la revalorisation automatique. | SMIC selon la seule revalorisation automatique | SMIC relevé par décision de l'État | B | **oui** |
| `eco_depenses` | Pour réduire le déficit, il faut d'abord augmenter les impôts plutôt que baisser fortement les dépenses publiques. | Baisser les dépenses publiques | Augmenter les impôts | B | non |
| `eco_patrimoine` | Il faut taxer davantage les très hauts patrimoines (rétablissement de l'ISF, taxe de type Zucman…). | Taxer davantage les grandes fortunes | Garder la fiscalité actuelle du patrimoine | A | non |
| `eco_35h` | Il faut assouplir la durée légale du travail (35 heures) pour permettre de travailler plus. | Garder les 35 heures | Assouplir la durée légale | B | non |
| `ecol_nucleaire` | La France doit construire de nombreux nouveaux réacteurs nucléaires. | Construire de nouveaux réacteurs | Réduire la part du nucléaire | A | **oui** |
| `ecol_renouvelables` | Il faut accélérer fortement le développement de l'éolien et du solaire. | Limiter l'éolien et le solaire | Accélérer l'éolien et le solaire | B | non |
| `ecol_normes` | Il faut renforcer les normes environnementales, même si cela pèse sur les agriculteurs et les entreprises. | Renforcer les normes environnementales | Alléger les normes environnementales | A | non |
| `ecol_thermique2035` | L'interdiction de vendre des voitures thermiques neuves à partir de 2035 doit être maintenue. | Revenir sur l'échéance de 2035 | Garder la fin des voitures thermiques neuves en 2035 | B | non |
| `ecol_aerien` | Il faut taxer davantage le transport aérien (billets, kérosène) pour financer la transition écologique. | Taxer davantage l'aérien | Garder la fiscalité actuelle de l'aérien | A | non |
| `sec_peines` | Il faut durcir les peines, par exemple avec des peines planchers ou minimales. | Peines plus lourdes, avec un minimum légal | Peine fixée par le juge au cas par cas | A | non |
| `sec_prisons` | Il faut construire massivement de nouvelles places de prison. | Construire des places de prison | Développer les peines alternatives | A | **oui** |
| `sec_cannabis` | La consommation de cannabis doit être légalisée et encadrée par l'État. | Maintenir l'interdiction du cannabis | Légaliser et encadrer le cannabis | B | non |
| `sec_mineurs` | Les mineurs de 16 ans et plus doivent toujours être jugés selon les règles de la justice des mineurs. | Justice des mineurs pour les 16-18 ans | Pouvoir juger les 16-18 ans comme des majeurs | A | non |
| `sec_videosurveillance` | Il faut généraliser la vidéosurveillance algorithmique (détection automatique, reconnaissance faciale) dans l'espace public. | Généraliser l'analyse automatique des images | Interdire ou limiter l'analyse automatique | A | non |
| `imm_baisse` | Il faut réduire fortement l'immigration légale (quotas, restriction du regroupement familial…). | Réduire l'immigration légale | Maintenir ou ouvrir l'immigration légale | A | **oui** |
| `imm_ame` | L'Aide médicale d'État (AME) pour les étrangers en situation irrégulière doit être supprimée ou réduite à l'urgence. | Maintenir l'AME | Limiter l'AME aux soins urgents | B | non |
| `imm_regularisation` | Il faut faciliter la régularisation des travailleurs sans papiers, notamment dans les métiers en tension. | Restreindre les régularisations | Faciliter les régularisations | B | non |
| `imm_droitdusol` | Le droit du sol doit être supprimé ou fortement restreint. | Maintenir le droit du sol | Supprimer ou restreindre le droit du sol | B | non |
| `imm_preference` | Certaines prestations sociales et l'accès au logement social doivent être réservés en priorité aux Français. | Mêmes règles pour Français et étrangers | Priorité selon la nationalité française | B | non |
| `eur_integration` | Il faut renforcer l'intégration européenne (défense commune, emprunt commun, davantage de décisions à la majorité). | Plus de décisions européennes communes | Plus de décisions laissées aux États | A | non |
| `eur_primaute` | Le droit français doit primer sur le droit européen, quitte à renégocier ou sortir des traités. | Appliquer le droit européen | Faire primer le droit français | B | non |
| `eur_ukraine` | La France doit continuer à soutenir militairement l'Ukraine. | Poursuivre l'aide militaire à l'Ukraine | Cesser l'aide militaire à l'Ukraine | A | non |
| `eur_otan` | La France doit quitter le commandement intégré de l'OTAN. | Rester dans le commandement intégré de l'OTAN | Quitter le commandement intégré de l'OTAN | B | non |
| `eur_defense3` | Le budget de la défense doit être inférieur à 3 % du PIB. | Défense à 3 % du PIB ou plus | Défense sous 3 % du PIB | B | non |
| `soc_medecins` | Les médecins doivent pouvoir s'installer librement, y compris dans les zones déjà bien dotées en médecins. | Réguler l'installation des médecins | Garder la liberté d'installation | B | non |
| `soc_findevie` | L'aide à mourir, légalisée en 2026 sous conditions strictes, doit être maintenue plutôt qu'abrogée. | Abroger l'aide à mourir | Maintenir l'aide à mourir | B | non |
| `soc_rsa` | Le versement du RSA doit être conditionné à des heures d'activité. | RSA conditionné à des heures d'activité | RSA sans obligation d'heures d'activité | A | non |
| `soc_100secu` | La Sécurité sociale doit rembourser à 100 % les soins prescrits, en supprimant le rôle des complémentaires santé. | Tout rembourser par la Sécurité sociale | Garder les complémentaires santé | A | non |
| `soc_chomage` | Il faut réduire la durée ou le montant de l'indemnisation chômage pour inciter au retour à l'emploi. | Maintenir l'indemnisation chômage | Réduire l'indemnisation chômage | B | non |
| `edu_prive` | Il faut réduire le financement public de l'enseignement privé sous contrat. | Maintenir le financement du privé sous contrat | Réduire le financement du privé sous contrat | B | non |
| `edu_autorite` | Il faut restaurer l'autorité à l'école (uniforme, sanctions renforcées, groupes de niveau). | Plus de discipline | Plus d'accompagnement | A | **oui** |
| `edu_signes` | Le port de signes religieux doit être interdit aux parents qui accompagnent les sorties scolaires. | Signes religieux autorisés aux parents accompagnateurs | Signes religieux interdits aux parents accompagnateurs | B | non |
| `edu_etudiants` | Il faut créer une allocation d'autonomie versée à tous les étudiants. | Allocation pour tous les étudiants | Bourses selon les revenus des parents | A | non |
| `edu_apprentissage` | Il faut permettre l'entrée en apprentissage dès 14 ans. | Apprentissage après le collège | Apprentissage dès 14 ans | B | non |
| `ins_proportionnelle` | Les députés doivent être élus à la proportionnelle. | Élection des députés à la proportionnelle | Scrutin majoritaire par circonscription | A | non |
| `ins_ric` | Il faut instaurer le référendum d'initiative citoyenne (RIC). | Instaurer le RIC | Laisser la loi au Parlement | A | non |
| `ins_6e` | Il faut passer à une VIe République et réduire les pouvoirs du président. | Garder la Ve République | Passer à une VIe République | B | non |
| `ins_parlementaires` | Il faut réduire le nombre de députés et de sénateurs. | Réduire le nombre de parlementaires | Garder le nombre de parlementaires | A | non |
| `ins_voteblanc` | Le vote blanc doit être reconnu comme un suffrage exprimé. | Compter le vote blanc comme suffrage exprimé | Compter le vote blanc à part | A | non |

## Enjeux à recoder

Pour ces 5 enjeux, le dilemme ne mesure plus exactement la même chose que l'affirmation : la valeur migrée n'est qu'un point de départ. Leurs 94 positions sont repassées à `relu: false` ; elles seront recodées sur la nouvelle échelle (avec la citation existante, ou une nouvelle source) une fois les formulations validées. Les 35 autres enjeux gardent leur statut de relecture (471 positions relues).

- `eco_smic` : L'affirmation parlait d'augmenter « nettement » le SMIC : refuser un coup de pouce valait souvent -1. Le dilemme oppose la seule revalorisation automatique à toute hausse décidée par l'État : ces positions vont vers le pôle A nettement.
- `ecol_nucleaire` : L'affirmation parlait de « nombreux » réacteurs : soutenir quelques EPR valait +1. Le dilemme oppose construire de nouveaux réacteurs à réduire la part du nucléaire : ces positions vont vers A nettement, et un soutien au seul prolongement du parc devient intermédiaire.
- `imm_baisse` : L'affirmation parlait de réduire « fortement » l'immigration légale : une réduction modérée valait +1. Le dilemme oppose réduire à maintenir ou ouvrir : ces positions vont vers A nettement.
- `sec_prisons` : L'affirmation portait sur la construction « massive » de places. Le dilemme ajoute un second pôle, les peines alternatives : un candidat peut soutenir les deux (position intermédiaire), ou rejeter la construction sans défendre les alternatives.
- `edu_autorite` : L'affirmation ne portait que sur l'autorité (uniforme, sanctions, groupes de niveau). Le dilemme lui oppose un second pôle, l'accompagnement (petits effectifs, classes mixtes) : un candidat peut soutenir les deux, ou rejeter l'un sans défendre l'autre.

Les autres changements d'intensité (« fortement » retiré de `eco_depenses` et d'`imm_baisse`…) ont été examinés position par position sur les valeurs ±1 : seul `imm_baisse` change de sens (une réduction modérée, qui valait +1, devient « pôle A nettement »). `eco_depenses` ne change pas : la règle de codage sur le refus de l'austérité s'applique telle quelle au pôle B.
