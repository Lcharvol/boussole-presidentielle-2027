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
      "date_source": "AAAA-MM-JJ ou AAAA-MM",
      "confiance": "programme | declaration | deduite"
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
