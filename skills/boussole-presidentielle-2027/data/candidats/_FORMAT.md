# Format d'une fiche candidat (data/candidats/<slug>.json)

{
  "slug": "jean-luc-melenchon",
  "nom": "Jean-Luc Mélenchon",
  "parti": "La France insoumise",
  "statut": "déclaré | pressenti | désigné par son parti | retiré",
  "programme": "disponible | partiel | non publié",
  "programme_url": "https://... (site officiel du programme, ou null)",
  "mis_a_jour": "AAAA-MM-JJ",
  "notes": "contexte utile (ex. ralliement, primaire, incertitude sur les parrainages)",
  "positions": {
    "<id de question>": {
      "valeur": 2 | 1 | 0 | -1 | -2 | null,
      "resume": "une phrase factuelle, sans jugement, décrivant la position",
      "source": "URL précise",
      "citation": "phrase exacte tirée de la source (≤ 300 caractères), ou null",
      "date_source": "AAAA-MM-JJ ou AAAA-MM",
      "confiance": "programme | declaration | deduite",
      "relu": false
    }
  }
}

Règles :
- valeur : 2 = tout à fait d'accord avec l'affirmation, -2 = pas du tout d'accord, 0 = position nuancée / médiane,
  null = aucune position publique trouvée (ne JAMAIS deviner).
- confiance : "programme" = écrit dans le programme officiel ; "declaration" = interview/discours/vote récent ;
  "deduite" = position du parti ou ancien programme (2022) non démentie. Une valeur "deduite" doit le dire dans le résumé.
- Chaque position non nulle doit avoir une source vérifiable. Préférer les sources récentes (2025-2026).
- Neutralité : résumé descriptif, mêmes exigences pour tous les candidats.
- citation : la phrase exacte, recopiée telle quelle depuis la page `source`, qui justifie la valeur (300 caractères au plus,
  coupes signalées par « […] »). Obligatoire pour toute valeur non nulle. Jamais de paraphrase : si aucune phrase de la source
  ne justifie la valeur, la valeur est fausse (la corriger ou la passer à null). Les agrégateurs (votons-2027.fr, elyseescope,
  monvote2027…) ne comptent jamais comme source.
- relu : false par défaut. Passe à true seulement après qu'un humain a ouvert la source et vérifié citation, résumé et valeur.
  Toute modification de valeur, source ou citation remet relu à false. `python3 scripts/a_relire.py` liste ce qui reste à relire.
