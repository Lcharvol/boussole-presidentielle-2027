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
- `variantes` : deux ou trois formulations équivalentes du même dilemme. Chacune a sa question et ses deux
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
