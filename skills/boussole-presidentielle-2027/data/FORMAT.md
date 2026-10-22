# Format des données (format 2 : enjeux à deux pôles)

Ce dossier contient deux types de fichiers :

- `enjeux.json` : les enjeux, leurs deux pôles et leurs formulations ;
- `candidats/<slug>.json` : une fiche par candidat, avec sa position sur chaque enjeu.

Le format 2 remplace le format 1 (fichier `questions.json`, affirmations notées de « pas du tout d'accord » à
« tout à fait d'accord »). La migration est décrite dans `outils/migrer_v2.py` et `docs/migration-v2.md`, à la
racine du dépôt.

## enjeux.json

```json
{
  "version": "2026-10-21",
  "format": 2,
  "echelle": {"-2": "Pôle A nettement", "-1": "Plutôt le pôle A", "0": "Entre les deux",
              "1": "Plutôt le pôle B", "2": "Pôle B nettement", "null": "Je passe (…)"},
  "themes": {"economie": "Économie, travail et fiscalité", "...": "..."},
  "enjeux": [
    {
      "id": "sec_prisons",
      "theme": "securite",
      "pole_a": "Construire des places de prison",
      "pole_b": "Développer les peines alternatives",
      "contexte": "Les prisons françaises comptent plus de détenus que de places.",
      "variantes": [
        {
          "id": "sec_prisons.1",
          "question": "Face à la surpopulation carcérale, que faut-il privilégier ?",
          "a": "Construire de nouvelles places de prison",
          "b": "Développer les peines alternatives",
          "validee": false
        }
      ]
    }
  ]
}
```

- `id` : identifiant stable de l'enjeu. Les 40 enjeux issus du format 1 gardent l'identifiant de l'ancienne
  question.
- `pole_a`, `pole_b` : libellés courts des deux pôles, pour les résultats et les fiches (pas pour poser la
  question). Les deux pôles ont la même dignité : aucun n'est « le bon ».
- `contexte` : une phrase factuelle facultative (ou `null`), affichée avec la question.
- `variantes` : deux ou trois formulations équivalentes du même dilemme (une seule quand les autres ont été écartées à la relecture). Chacune a sa question et ses deux
  options : `a` exprime toujours le pôle A, `b` le pôle B. `validee` passe à `true` quand Lcharvol a validé la
  formulation ; dès qu'un enjeu a une variante validée, seules ses variantes validées sont tirées.
- Il n'y a plus de champ `niveau` : les modes rapide, adaptatif et complet sont tirés par `scripts/tirage.py`.

## Échelle et sens des valeurs

Les réponses et les positions sont sur le même axe :

| Valeur | Sens |
|---|---|
| -2 | pôle A nettement |
| -1 | plutôt le pôle A |
| 0 | entre les deux (ou position nuancée) |
| 1 | plutôt le pôle B |
| 2 | pôle B nettement |
| null | je passe / position inconnue |

**À l'écran, le côté de chaque pôle est tiré au hasard** à chaque passage (et la formulation parmi les
variantes). Une interface doit donc garder, pour chaque question posée, quel pôle est affiché à gauche, et
convertir la réponse en valeur : si A est à gauche, l'option la plus à gauche vaut -2 ; si B est à gauche, elle
vaut +2. `scripts/tirage.py` fait ce tirage et donne directement, pour chaque option affichée, la valeur à
transmettre au calcul (champ `options`). Une interface qui réimplémente le tirage doit reproduire ce principe :
ordre aléatoire des enjeux (sans blocs par thème), variante aléatoire, côté aléatoire.

## candidats/<slug>.json

```json
{
  "slug": "jean-luc-melenchon",
  "format": 2,
  "nom": "Jean-Luc Mélenchon",
  "parti": "La France insoumise",
  "statut": "déclaré | pressenti | désigné par son parti | retiré",
  "programme": "disponible | partiel | non publié",
  "programme_url": "https://... (site officiel du programme, ou null)",
  "mis_a_jour": "AAAA-MM-JJ",
  "notes": "contexte utile (ex. ralliement, primaire, incertitude sur les parrainages)",
  "positions": {
    "<id d'enjeu>": {
      "valeur": -2 | -1 | 0 | 1 | 2 | null,
      "resume": "une phrase factuelle, sans jugement, décrivant la position",
      "source": "URL précise",
      "citation": "phrase exacte tirée de la source (≤ 300 caractères), ou null",
      "date_source": "AAAA-MM-JJ ou AAAA-MM",
      "confiance": "programme | declaration | deduite",
      "relu": false
    }
  }
}
```

Règles :
- `format` : 2. `check_data.py` refuse une fiche d'un autre format.
- `valeur` : position du candidat entre le pôle A (-2) et le pôle B (+2) de l'enjeu. 0 = position intermédiaire
  ou qui soutient les deux pôles. `null` = aucune position publique trouvée (ne JAMAIS deviner).
- `confiance` : "programme" = écrit dans le programme officiel ; "declaration" = interview/discours/vote récent ;
  "deduite" = position du parti ou ancien programme (2022) non démentie. Une valeur "deduite" doit le dire dans le
  résumé.
- Chaque position non nulle doit avoir une source vérifiable. Préférer les sources récentes (2025-2026).
- Neutralité : résumé descriptif, mêmes exigences pour tous les candidats.
- `citation` : la phrase exacte, recopiée telle quelle depuis la page `source`, qui justifie la valeur (300
  caractères au plus, coupes signalées par « […] »). Obligatoire pour toute valeur non nulle. Jamais de
  paraphrase : si aucune phrase de la source ne justifie la valeur, la valeur est fausse (la corriger ou la
  passer à null). Les agrégateurs (votons-2027.fr, elyseescope, monvote2027…) ne comptent jamais comme source.
- `relu` : false par défaut. Passe à true seulement après qu'un humain a ouvert la source et vérifié citation,
  résumé et valeur. Toute modification de valeur, source ou citation remet relu à false.
  `python3 scripts/a_relire.py` liste ce qui reste à relire.

## Réponses passées au calcul

`scripts/score.py` lit sur l'entrée standard :

```json
{"reponses": {"sec_prisons": -1, "eco_retraite": 2, "sec_cannabis": null}, "importance": {"securite": 2}}
```

Les clés de `reponses` sont des identifiants d'enjeux, les valeurs sont sur l'échelle ci-dessus (A = -2,
B = +2). La formule du score n'a pas changé entre les formats 1 et 2 ; seuls le fichier lu (`enjeux.json` au lieu
de `questions.json`) et la clé de la liste (`enjeux` au lieu de `questions`) changent.

## Pour une interface qui lit ces données (site vitrine)

Ce qui change par rapport au format 1 :

1. `data/questions.json` n'existe plus : lire `data/enjeux.json`, liste `enjeux` (au lieu de `questions`).
2. Plus de `texte` d'affirmation ni de `niveau` : afficher la `question` d'une variante et ses deux options
   `a` / `b`, ou, hors questionnaire, les libellés courts `pole_a` / `pole_b`.
3. Les valeurs des positions ont changé de sens pour la moitié des enjeux (elles se lisent désormais sur l'axe
   A/B, pas « d'accord / pas d'accord ») : relire les valeurs, ne pas réutiliser une ancienne copie.
4. Le calcul du score est inchangé (`score.py`) : une copie de la formule (par exemple `score.ts`) reste valable ;
   seule la lecture des données change.
5. Le tirage (modes rapide, adaptatif, complet ; variantes ; côté des pôles) est dans `scripts/tirage.py`.
6. Le classement suit le score exact, avant arrondi : deux candidats affichés au même pourcentage sont dans
   l'ordre de leur score non arrondi (pas de départage par la couverture).

## Tirage reproductible : règles exactes pour un portage

Un portage de `scripts/tirage.py` (par exemple `tirage.ts` du site) doit poser **exactement** les mêmes questions
à graine et réponses égales. `scripts/tirage.py` fait foi ; ce qui suit fixe tout ce qui influe sur le résultat.
Les cas de référence `tests/cas_tirage.json` (graine + réponses → questions attendues, avec la variante, le pôle
à gauche et les valeurs des cinq réponses) permettent de vérifier la concordance. Ils sont régénérés par
`python3 tests/generer_cas_tirage.py`, et `tests/test_tirage.py` échoue s'ils ne sont plus à jour.

**Générateur.** C'est celui de Python, `random.Random` (Mersenne Twister MT19937) :
- Une graine texte (par exemple `f"{graine}/socle"`, où `graine` est l'entier écrit en décimal) passe par
  `seed(..., version=2)` : l'entier issu de `texte + SHA-512(texte)` (octets UTF-8, gros-boutiste) initialise
  `init_by_array` par mots de 32 bits, poids faibles d'abord.
- Une graine entière (bootstrap de `score.py`) initialise `init_by_array` avec sa valeur absolue.
- `random()` vaut `((a >> 5) × 67108864 + (b >> 6)) / 2^53`, pour deux sorties 32 bits successives `a`, `b`.
- `choice(s)` vaut `s[randbelow(len(s))]`, et `randrange(n)` vaut `randbelow(n)`. `randbelow(n)` tire
  `getrandbits(k)` avec `k = n.bit_length()` (les `k` bits de poids fort d'une sortie 32 bits) et recommence tant
  que le résultat est ≥ `n`.
- `shuffle(l)` : pour `i` de `len(l) - 1` à 1, échange `l[i]` et `l[randbelow(i + 1)]`.

Chaque fonction crée son propre générateur, dans cet ordre de consommation :

| Fonction | Graine | Tirages, dans l'ordre |
|---|---|---|
| `presenter(enjeu)` | `f"{graine}/{enjeu.id}"` | `choice(variantes utilisables)`, puis `choice("ab")` (pôle à gauche) |
| `socle()` | `f"{graine}/socle"` | un `tirage_pondere(k=1)` par thème (ordre des clés de `themes`), puis des compléments un par un, puis `ordonner` |
| mode complet | `f"{graine}/complet"` | `ordonner` sur les enjeux non posés, dans l'ordre de `enjeux.json` |
| `suivantes()` (lot adaptatif) | `f"{graine}/adaptatif/{nombre de questions déjà posées}"` | un `tirage_pondere(k=1)` par enjeu du lot, puis `ordonner` |
| marge (bootstrap de `score.py`, pour le peloton) | l'entier `graine`, un générateur **neuf pour chaque candidat** | 300 tirages de `randrange(n)` × n, n = nombre de réponses non nulles, dans l'ordre alphabétique des identifiants d'enjeux |

**`tirage_pondere(ids, poids, k)`** : tant qu'il en faut,
1. `total` = somme flottante des poids restants, de gauche à droite (pas de somme compensée) ;
2. `x = random() × total` ;
3. on parcourt les restants dans l'ordre en cumulant les poids, et on prend le premier `i` tel que `x ≤ cumul`.
   Si aucun ne convient (arrondi flottant), on prend le dernier ;
4. on retire `i` de la liste.

**Poids.**
- Socle : `pouvoir(enjeu) + 0,1`, où `pouvoir` = écart-type de population des positions connues × part des
  candidats dont la position est connue.
- Compléments du socle : au plus deux enjeux par thème, ou n'importe quel enjeu restant si aucun ne convient.
  Les enjeux candidats sont pris dans l'ordre de `enjeux.json`.

**Lot adaptatif** (`suivantes()`, après le socle, tant que moins de 32 questions ont été posées) :
1. Le peloton, ce sont les candidats dont `score + marge ≥ score − marge` du premier. Les scores et les marges
   sont arrondis, avec le bootstrap de 300 tirages et la graine entière. S'il compte moins de deux candidats, le
   questionnaire s'arrête.
2. Gain de chaque enjeu non posé, dans l'ordre de `enjeux.json` : écart-type de population des positions connues
   du peloton × part du peloton dont la position est connue × √(importance du thème). Le gain est nul s'il y a
   moins de deux positions connues. L'écart-type est celui de `statistics.pstdev` : calcul exact sur les
   entiers, puis racine.
3. Enjeux utiles : gain ≥ 0,4, dans l'ordre de `enjeux.json`. S'il n'y en a aucun, le questionnaire s'arrête.
4. Tant que le lot compte moins de `min(4, 32 − posées)` enjeux : on garde les enjeux utiles d'un thème pas
   encore pris (dans leur ordre), on en tire un par `tirage_pondere(k=1)` pondéré par le gain, et on marque son
   thème. On s'arrête plus tôt s'il n'en reste plus.
5. Le lot est passé à `ordonner`, avec le même générateur.

**`ordonner(enjeux)`** :
1. `shuffle` de la liste ;
2. tant qu'il en reste : parmi les positions dont le thème diffère du précédent (toutes sinon), on prend la
   première dont le thème a le plus d'enjeux restants.

Le côté et la formulation de chaque question viennent ensuite de `presenter`, indépendamment de l'ordre.
