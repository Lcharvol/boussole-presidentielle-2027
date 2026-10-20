#!/usr/bin/env python3
"""Vérifie les fiches candidats et signale ce qui est incomplet ou ancien.

Usage : python3 check_data.py [--jours 30]

Affiche, pour chaque candidat : statut, date de mise à jour, positions renseignées,
positions seulement déduites, positions avec citation et positions relues par un humain.
Les positions sans citation, les citations trop longues et les sources d'agrégateurs sont
signalées en alerte. Code de sortie 1 si une fiche est invalide.
"""
import json
import sys
from datetime import date
from pathlib import Path

DATA = Path(__file__).resolve().parent.parent / "data"
VALEURS = {-2, -1, 0, 1, 2, None}
CONFIANCES = {"programme", "declaration", "deduite"}
CITATION_MAX = 300
AGREGATEURS = ("votons-2027", "elyseescope", "monvote2027")


def main():
    jours = int(sys.argv[sys.argv.index("--jours") + 1]) if "--jours" in sys.argv else 30
    questions = json.loads((DATA / "questions.json").read_text(encoding="utf-8"))
    ids = [q["id"] for q in questions["questions"]]
    erreurs = 0
    print(f"{'Candidat':28} {'Statut':22} {'MAJ':11} {'Pos.':>5} {'Prog.':>5} {'Déd.':>5} "
          f"{'Cit.':>5} {'Relues':>7}  Alertes")
    total_relues = total_renseignees = 0
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
        renseignees = prog = ded = cit = relues = 0
        sans_citation = []
        for qid in ids:
            p = pos.get(qid) or {}
            v = p.get("valeur")
            if "relu" in p and not isinstance(p["relu"], bool):
                alertes.append(f"{qid}: relu {p['relu']!r} (booléen attendu)")
                erreurs += 1
            citation = p.get("citation")
            if citation is not None and not isinstance(citation, str):
                alertes.append(f"{qid}: citation {citation!r} (texte attendu)")
                erreurs += 1
                citation = None
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
            relues += p.get("relu") is True
            if any(a in (p.get("source") or "") for a in AGREGATEURS):
                alertes.append(f"{qid}: source d'agrégateur")
            if citation and citation.strip():
                cit += 1
                if len(citation) > CITATION_MAX:
                    alertes.append(f"{qid}: citation de {len(citation)} caractères (> {CITATION_MAX})")
            else:
                sans_citation.append(qid)
        if sans_citation:
            alertes.append(f"{len(sans_citation)} sans citation ({', '.join(sans_citation)})")
        total_relues += relues
        total_renseignees += renseignees
        maj = c.get("mis_a_jour", "?")
        try:
            age = (date.today() - date.fromisoformat(maj)).days
            if age > jours:
                alertes.append(f"MAJ il y a {age} j")
        except ValueError:
            alertes.append("date MAJ invalide")
        print(f"{c.get('nom', f.stem)[:28]:28} {str(c.get('statut'))[:22]:22} {maj:11} "
              f"{renseignees:>2}/{len(ids)} {prog:>5} {ded:>5} {cit:>5} {relues:>3}/{renseignees:<3}  "
              f"{'; '.join(alertes)}")
    print(f"\nPositions renseignées relues par un humain : {total_relues}/{total_renseignees} "
          f"({total_renseignees - total_relues} à relire : python3 scripts/a_relire.py)")
    sys.exit(1 if erreurs else 0)


if __name__ == "__main__":
    main()
