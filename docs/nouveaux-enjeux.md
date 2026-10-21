# Proposition : 22 nouveaux enjeux (étape C, à valider)

Objectif : passer de 40 à environ 60 enjeux, pour que chaque passage puise dans un vivier plus large. Critères de
choix :

- **départager**, y compris au sein d'un même camp : la colonne « Qui se sépare » indique les camps où les
  positions divergent (c'est là qu'un enjeu apporte le plus au mode adaptatif) ;
- **couvrir les thèmes peu traités** : chaque thème passe de 5 à 7 ou 8 enjeux ; l'économie, l'Europe, le social
  et les institutions reçoivent les enjeux transversaux qui manquent (commerce, retraites par capitalisation,
  logement, mandats) ;
- **deux pôles légitimes et sourçables** : chaque pôle correspond à des propositions réelles de candidats, pour que
  les positions puissent être trouvées sans deviner.

La colonne « Qui se sépare » est une hypothèse de travail, tirée de positions connues des partis : elle sert à
choisir les enjeux, pas à coder les candidats, et sera vérifiée par la recherche (null plutôt que deviner).

Rien n'est encore recherché : une fois la liste validée (ou amendée), les positions des 25 candidats seront
cherchées par plusieurs agents selon `references/mise-a-jour.md`, et resteront à `relu: false`. Les formulations
ci-dessous sont des premières versions : elles passeront le test « devine le camp » comme les autres, avec 2 ou 3
variantes chacune.

| # | Id proposé | Thème | Pôle A | Pôle B | Qui se sépare | Première formulation |
|---|---|---|---|---|---|---|
| 1 | `eco_libre_echange` | Économie | Conclure des accords de libre-échange (type Mercosur) | Protéger le marché européen par des droits de douane | Centre et une partie de la droite contre RN, LFI, écologistes ; divise LR | « Commerce international : signer de nouveaux accords de libre-échange / Relever les protections aux frontières de l'Europe » |
| 2 | `eco_succession` | Économie | Alléger les droits de succession | Taxer davantage les gros héritages | Divise la gauche (PS, LFI pour ; PCF prudent) et la droite (RN pour alléger les transmissions familiales, centre partagé) | « Droits de succession : les alléger / Les augmenter sur les héritages les plus élevés » |
| 3 | `eco_nationalisation` | Économie | Renationaliser certaines entreprises (EDF, autoroutes…) | Laisser ces activités au secteur privé ou au capital ouvert | LFI, PCF, RN, souverainistes contre centre et LR | « Autoroutes et énergie : les reprendre sous contrôle public / Les laisser à des entreprises privées » |
| 4 | `ecol_zan` | Écologie | Maintenir l'objectif « zéro artificialisation nette » | L'assouplir pour construire davantage | Divise la droite et le centre (élus locaux) ; écologistes contre RN | « Construction sur des terres agricoles ou naturelles : tenir l'objectif d'y mettre fin d'ici 2050 / Laisser chaque commune décider » |
| 5 | `ecol_eau_agricole` | Écologie | Stocker l'eau pour l'irrigation (retenues) | Réduire les prélèvements agricoles | Écologistes et LFI contre droite ; divise PS et centre | « Sécheresses : construire des retenues d'eau pour l'irrigation / Réduire l'eau prélevée par l'agriculture » |
| 6 | `ecol_zfe` | Écologie | Restreindre en ville la circulation des véhicules les plus polluants | Supprimer ces restrictions | Divise le centre et la gauche (ruralité) ; RN et LR pour supprimer | « Zones à faibles émissions : les maintenir dans les grandes villes / Les supprimer » |
| 7 | `sec_controle_identite` | Sécurité | Délivrer un récépissé à chaque contrôle d'identité | Contrôles sans récépissé, comme aujourd'hui | Gauche contre droite ; divise le centre | « Contrôles d'identité par la police : remettre un récépissé à chaque contrôle / Garder les contrôles sans récépissé » |
| 8 | `sec_legitime_defense` | Sécurité | Présomption de légitime défense pour les policiers | Règles de légitime défense communes à tous | RN, LR, Reconquête contre gauche ; divise le centre | « Usage de leur arme par les policiers : présumer qu'ils sont en légitime défense / Appliquer les mêmes règles qu'à tous » |
| 9 | `sec_police_municipale` | Sécurité | Donner plus de pouvoirs aux polices municipales | Concentrer la sécurité sur la police nationale | Divise la droite (maires) et le centre ; gauche partagée | « Sécurité au quotidien : élargir les pouvoirs des polices municipales / Renforcer d'abord la police nationale » |
| 10 | `imm_travail` | Immigration | Ouvrir l'immigration de travail selon les besoins des métiers | La réduire au profit de la formation des demandeurs d'emploi | Divise la droite (Renaissance/LR pro-métiers en tension vs RN) **et la gauche** (LFI/PCF méfiants envers les « filières » patronales) | « Métiers qui recrutent difficilement : faire venir des travailleurs étrangers / Former et orienter des demandeurs d'emploi » |
| 11 | `imm_asile_externalise` | Immigration | Examiner les demandes d'asile hors d'Europe | Les examiner en France, comme aujourd'hui | RN, Reconquête, une partie de LR contre gauche ; divise le centre | « Demandes d'asile : les examiner dans des centres hors d'Europe / Les examiner en France » |
| 12 | `imm_naturalisation` | Immigration | Durcir les conditions de naturalisation (durée, langue) | Garder les conditions actuelles | Droite et RN contre gauche ; divise le centre | « Naturalisation : allonger la durée de résidence et relever le niveau de langue exigés / Garder les conditions actuelles » |
| 13 | `eur_service_militaire` | Europe et international | Service militaire obligatoire | Service sur la base du volontariat | Divise toutes les familles (Reconquête, une partie de LR et de LFI pour un service obligatoire ; centre pour le volontariat) | « Service militaire : le rendre obligatoire / Le proposer sur la base du volontariat » |
| 14 | `eur_dissuasion` | Europe et international | Étendre la dissuasion nucléaire française à la protection de l'Europe | La garder strictement nationale | Centre et PS contre RN et LFI ; divise LR | « Dissuasion nucléaire : l'associer à la défense de l'Europe / La réserver à la défense de la France » |
| 15 | `eur_elargissement` | Europe et international | Élargir l'Union (Ukraine, Moldavie, Balkans) | Suspendre les élargissements | Divise le centre, la gauche (écologistes pour, LFI contre) et la droite | « Union européenne : accueillir de nouveaux pays membres / Suspendre l'entrée de nouveaux pays » |
| 16 | `soc_capitalisation` | Santé et protection sociale | Introduire une part de retraite par capitalisation | Garder un système tout en répartition | **Divise la droite** (Reconquête, une partie de LR et du centre pour ; RN contre) ; gauche contre | « Retraites : ajouter une part d'épargne retraite obligatoire / Rester sur la seule répartition » |
| 17 | `soc_allocations_familiales` | Santé et protection sociale | Allocations familiales sous condition de ressources | Allocations familiales universelles | Divise la gauche (modulation de 2015) et la droite (LR, RN pour l'universalité) | « Allocations familiales : les réserver aux familles selon leurs revenus / Les verser à toutes les familles » |
| 18 | `soc_loyers` | Santé et protection sociale | Généraliser l'encadrement des loyers | Supprimer l'encadrement des loyers | Gauche contre droite ; divise le centre (expérimentations) | « Loyers dans les villes chères : les encadrer partout / Supprimer l'encadrement » |
| 19 | `edu_selection_universite` | Éducation | Sélection à l'entrée de l'université | Accès ouvert à tout bachelier | Divise le centre et la droite ; gauche contre | « Entrée à l'université : sélectionner les étudiants selon leur dossier / Ouvrir l'accès à tout bachelier » |
| 20 | `edu_remuneration` | Éducation | Rémunérer davantage les enseignants selon le mérite | Augmenter tous les enseignants selon une grille commune | Divise le centre et la droite ; gauche pour la grille commune | « Salaire des enseignants : une part liée à l'évaluation de leur travail / Une hausse identique pour tous » |
| 21 | `ins_cumul` | Institutions et démocratie | Autoriser à nouveau le cumul député-maire | Garder l'interdiction du cumul | **Divise chaque camp** (une partie de LR, du PS et du centre pour ; LFI, écologistes, Renaissance contre) | « Cumul des mandats : permettre à un député d'être aussi maire / Garder l'interdiction » |
| 22 | `ins_mandat_unique` | Institutions et démocratie | Mandat présidentiel unique de 7 ans | Mandat de 5 ans renouvelable une fois | Divise le centre (Bayrou) et la droite ; transversal | « Mandat du président : un seul mandat de 7 ans / 5 ans, renouvelable une fois » |

Répartition par thème après ajout : économie 8, écologie 8, sécurité 8, immigration 8, Europe 8, social 8,
éducation 7, institutions 7 (62 enjeux).

Autres pistes, écartées pour l'instant (à reprendre si Lcharvol préfère) : audiovisuel public (privatisation
ou non), décentralisation (régions / État), 49.3, sanctions contre Israël ou suspension de l'accord UE-Israël (très
clivant et changeant), énergie : prix réglementé de l'électricité, éducation : collège unique.

**Questions à Lcharvol :** garder, retirer ou remplacer chacun des 22 ; ajouter des pistes écartées ; un nombre
cible (20 ? 22 ?).
