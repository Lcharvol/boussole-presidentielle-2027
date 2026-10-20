#!/usr/bin/env python3
"""Vérifie les fiches candidats et signale ce qui est incomplet ou ancien.

Usage : python3 check_data.py [--jours 30]

Affiche, pour chaque candidat : statut, date de mise à jour, positions renseignées,
positions sans source, positions seulement déduites. Code de sortie 1 si une fiche est invalide.
"""
import json
import sys
from datetime import date
from pathlib import Path

DATA = Path(__file__).resolve().parent.parent / "data"
VALEURS = {-2, -1, 0, 1, 2, None}
CONFIANCES = {"programme", "declaration", "deduite"}


def main():
    jours = int(sys.argv[sys.argv.index("--jours") + 1]) if "--jours" in sys.argv else 30
    questions = json.loads((DATA / "questions.json").read_text(encoding="utf-8"))
    ids = [q["id"] for q in questions["questions"]]
    erreurs = 0
    print(f"{'Candidat':28} {'Statut':22} {'MAJ':11} {'Pos.':>5} {'Prog.':>5} {'Déd.':>5}  Alertes")
    for f in sorted((DATA / "candidats").glob("*.json")):
        alertes = []
        try:
            c = json.loads(f.read_text(encoding="utf-8"))
        except json.JSONDecodeError as e:
            print(f"{f.name}: JSON invalide ({e})")
            erreurs += 1
            continue
        pos = c.get("positions", {})
        inconnus = set(pos) - set(ids)
        if inconnus:
            alertes.append(f"ids inconnus {sorted(inconnus)}")
            erreurs += 1
        renseignees = prog = ded = 0
        for qid in ids:
            p = pos.get(qid) or {}
            v = p.get("valeur")
            if v not in VALEURS:
                alertes.append(f"{qid}: valeur {v!r} invalide")
                erreurs += 1
                continue
            if v is None:
                continue
            renseignees += 1
            if not p.get("source"):
                alertes.append(f"{qid}: sans source")
                erreurs += 1
            conf = p.get("confiance")
            if conf not in CONFIANCES:
                alertes.append(f"{qid}: confiance {conf!r}")
            prog += conf == "programme"
            ded += conf == "deduite"
        maj = c.get("mis_a_jour", "?")
        try:
            age = (date.today() - date.fromisoformat(maj)).days
            if age > jours:
                alertes.append(f"MAJ il y a {age} j")
        except ValueError:
            alertes.append("date MAJ invalide")
        print(f"{c.get('nom', f.stem)[:28]:28} {str(c.get('statut'))[:22]:22} {maj:11} "
              f"{renseignees:>2}/{len(ids)} {prog:>5} {ded:>5}  {'; '.join(alertes)}")
    sys.exit(1 if erreurs else 0)


if __name__ == "__main__":
    main()
