#!/usr/bin/env python3
"""Attribue un niveau (rapide / moyen / long) à chaque question de data/questions.json.

Usage : python3 choisir_niveaux.py [--ecrire]

Dans chaque thème, les questions sont classées par pouvoir de départage :
écart-type des positions des candidats × part des candidats dont la position est connue.
Une question sur laquelle tous les candidats sont d'accord, ou dont on connaît peu de
positions, aide peu à distinguer les candidats : elle passe en mode long.
- rapide : la meilleure question de chaque thème ;
- moyen  : les trois meilleures de chaque thème ;
- long   : toutes.
Sans --ecrire, affiche seulement le classement.
"""
import json
import statistics
import sys
from pathlib import Path

DATA = Path(__file__).resolve().parent.parent / "data"
PAR_THEME = {"rapide": 1, "moyen": 3}


def main():
    chemin = DATA / "questions.json"
    questions = json.loads(chemin.read_text(encoding="utf-8"))
    candidats = [json.loads(f.read_text(encoding="utf-8")) for f in sorted((DATA / "candidats").glob("*.json"))]
    candidats = [c for c in candidats if c.get("statut") != "retiré"]

    def pouvoir(qid):
        vals = [(c.get("positions", {}).get(qid) or {}).get("valeur") for c in candidats]
        vals = [v for v in vals if v is not None]
        if len(vals) < 2:
            return 0.0
        return statistics.pstdev(vals) * len(vals) / len(candidats)

    for theme in questions["themes"]:
        qs = sorted((q for q in questions["questions"] if q["theme"] == theme), key=lambda q: -pouvoir(q["id"]))
        for rang, q in enumerate(qs):
            q["niveau"] = "rapide" if rang < PAR_THEME["rapide"] else "moyen" if rang < PAR_THEME["moyen"] else "long"
            print(f"{theme:13} {q['niveau']:7} {pouvoir(q['id']):.2f}  {q['id']}")

    if "--ecrire" in sys.argv:
        chemin.write_text(json.dumps(questions, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print(f"\nNiveaux écrits dans {chemin}")


if __name__ == "__main__":
    main()
