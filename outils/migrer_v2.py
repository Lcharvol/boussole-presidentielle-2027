#!/usr/bin/env python3
"""Migration des fiches du format 1 (affirmations, d'accord / pas d'accord) au format 2 (enjeux à deux pôles).

Usage, depuis la racine du dépôt :
    python3 outils/migrer_v2.py ANCIEN_QUESTIONS_JSON [--ecrire]

ANCIEN_QUESTIONS_JSON est le data/questions.json du format 1 (par exemple
`git show 59674ac:skills/boussole-presidentielle-2027/data/questions.json > /tmp/q1.json`).

Au format 1, une position valait +2 pour « tout à fait d'accord » avec l'affirmation. Au format 2, elle vaut
-2 pour le pôle A et +2 pour le pôle B. Pour chaque enjeu, MIGRATION indique le pôle qui correspond à
l'ancienne affirmation :
- "b" : être d'accord avec l'affirmation, c'est choisir le pôle B ; la valeur est reprise telle quelle ;
- "a" : être d'accord, c'est choisir le pôle A ; la valeur est inversée.
Citation, source, date, confiance et résumé sont conservés. `relu` est conservé, sauf pour les enjeux de
RECODAGE : le passage au dilemme y change le sens de l'échelle, la valeur reprise n'est qu'un point de
départ et doit être recodée ; ces positions repassent à `relu: false`.
Sans --ecrire, le script affiche seulement le bilan. Il refuse de tourner deux fois (fiches déjà migrées).
"""
import json
import sys
from pathlib import Path

DATA = Path(__file__).resolve().parent.parent / "skills" / "boussole-presidentielle-2027" / "data"

MIGRATION = {
    "eco_retraite": "a", "eco_smic": "b", "eco_depenses": "b", "eco_patrimoine": "a", "eco_35h": "b",
    "ecol_nucleaire": "a", "ecol_renouvelables": "b", "ecol_normes": "a", "ecol_thermique2035": "b",
    "ecol_aerien": "a",
    "sec_peines": "a", "sec_prisons": "a", "sec_cannabis": "b", "sec_mineurs": "a", "sec_videosurveillance": "a",
    "imm_baisse": "a", "imm_ame": "b", "imm_regularisation": "b", "imm_droitdusol": "b", "imm_preference": "b",
    "eur_integration": "a", "eur_primaute": "b", "eur_ukraine": "a", "eur_otan": "b", "eur_defense3": "b",
    "soc_medecins": "b", "soc_findevie": "b", "soc_rsa": "a", "soc_100secu": "a", "soc_chomage": "b",
    "edu_prive": "b", "edu_autorite": "a", "edu_signes": "b", "edu_etudiants": "a", "edu_apprentissage": "b",
    "ins_proportionnelle": "a", "ins_ric": "a", "ins_6e": "b", "ins_parlementaires": "a", "ins_voteblanc": "a",
}

# Enjeux dont le dilemme ne mesure plus exactement la même chose que l'ancienne affirmation.
RECODAGE = {
    "eco_smic": "L'affirmation parlait d'augmenter « nettement » le SMIC : refuser un coup de pouce valait souvent -1. "
                "Le dilemme oppose la seule revalorisation automatique à toute hausse décidée par l'État : "
                "ces positions vont vers le pôle A nettement.",
    "ecol_nucleaire": "L'affirmation parlait de « nombreux » réacteurs : soutenir quelques EPR valait +1. Le dilemme oppose "
                      "construire de nouveaux réacteurs à réduire la part du nucléaire : ces positions vont vers A nettement, "
                      "et un soutien au seul prolongement du parc devient intermédiaire.",
    "imm_baisse": "L'affirmation parlait de réduire « fortement » l'immigration légale : une réduction modérée valait +1. "
                  "Le dilemme oppose réduire à maintenir ou ouvrir : ces positions vont vers A nettement.",
    "sec_prisons": "L'affirmation portait sur la construction « massive » de places. Le dilemme ajoute un second pôle, les "
                   "peines alternatives : un candidat peut soutenir les deux (position intermédiaire), ou rejeter la "
                   "construction sans défendre les alternatives.",
    "edu_autorite": "L'affirmation ne portait que sur l'autorité (uniforme, sanctions, groupes de niveau). Le dilemme lui "
                    "oppose un second pôle, l'accompagnement (petits effectifs, classes mixtes) : un candidat peut "
                    "soutenir les deux, ou rejeter l'un sans défendre l'autre.",
}


def main():
    if len(sys.argv) < 2 or sys.argv[1].startswith("--"):
        raise SystemExit(__doc__)
    ancien = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
    enjeux = json.loads((DATA / "enjeux.json").read_text(encoding="utf-8"))
    ids_anciens = {q["id"] for q in ancien["questions"]}
    ids_nouveaux = {e["id"] for e in enjeux["enjeux"]}
    assert set(MIGRATION) == ids_anciens, sorted(set(MIGRATION) ^ ids_anciens)
    assert set(MIGRATION) <= ids_nouveaux, sorted(set(MIGRATION) - ids_nouveaux)
    assert set(RECODAGE) <= set(MIGRATION)

    bilan = {"inversees": 0, "reprises": 0, "a_recoder": 0, "nulles": 0}
    for f in sorted((DATA / "candidats").glob("*.json")):
        c = json.loads(f.read_text(encoding="utf-8"))
        if c.get("format") == 2:
            raise SystemExit(f"{f.name} est déjà au format 2.")
        for qid, p in c.get("positions", {}).items():
            if not p or p.get("valeur") is None:
                bilan["nulles"] += 1
                continue
            if MIGRATION[qid] == "a":
                p["valeur"] = -p["valeur"] if p["valeur"] else 0
                bilan["inversees"] += 1
            else:
                bilan["reprises"] += 1
            if qid in RECODAGE:
                p["relu"] = False
                bilan["a_recoder"] += 1
        # Le format est indiqué en tête de fiche, après le slug.
        c = {"slug": c["slug"], "format": 2, **{k: v for k, v in c.items() if k != "slug"}}
        if "--ecrire" in sys.argv:
            f.write_text(json.dumps(c, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Valeurs inversées : {bilan['inversees']} ; reprises : {bilan['reprises']} ; nulles : {bilan['nulles']}")
    print(f"Positions repassées à relu: false pour recodage : {bilan['a_recoder']} "
          f"(enjeux : {', '.join(sorted(RECODAGE))})")
    if "--ecrire" not in sys.argv:
        print("(aperçu : relancer avec --ecrire pour modifier les fiches)")


if __name__ == "__main__":
    main()
