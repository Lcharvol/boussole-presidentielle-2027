#!/usr/bin/env python3
"""Calcule la proximité entre les réponses d'un utilisateur et les positions des candidats.

Usage :
    python3 score.py reponses.json            # tableau Markdown
    python3 score.py reponses.json --json     # résultat brut

Format de reponses.json :
{
  "reponses":   {"eco_retraite": 2, "eco_smic": -1, "sec_cannabis": null, ...},
  "importance": {"economie": 2, "immigration": 3}      # optionnel, 1 par défaut (1 à 3)
}

Une réponse null (ou absente) signifie que l'utilisateur a passé la question : elle ne compte pas.
Pour chaque question où l'utilisateur ET le candidat ont une position, l'accord vaut
1 - |écart| / 4 (1 = identique, 0 = opposé). Le score est la moyenne pondérée par l'importance
du thème. La couverture indique sur combien de questions répondues le candidat a une position
connue : un score sur peu de questions est peu fiable, il est donc classé à part.
"""
import json
import sys
from pathlib import Path

DATA = Path(__file__).resolve().parent.parent / "data"
COUVERTURE_MIN = 0.5
ECART_SERRE = 5


def charger():
    questions = json.loads((DATA / "questions.json").read_text(encoding="utf-8"))
    candidats = []
    for f in sorted((DATA / "candidats").glob("*.json")):
        c = json.loads(f.read_text(encoding="utf-8"))
        if c.get("statut") == "retiré":
            continue
        candidats.append(c)
    return questions, candidats


def calculer(user, questions, candidats):
    reponses = {k: v for k, v in user.get("reponses", {}).items() if v is not None}
    importance = user.get("importance", {})
    theme_de = {q["id"]: q["theme"] for q in questions["questions"]}
    inconnues = sorted(set(reponses) - set(theme_de))
    if inconnues:
        raise SystemExit(f"Identifiants de question inconnus : {', '.join(inconnues)}")

    resultats = []
    for c in candidats:
        total_p = total_w = 0.0
        par_theme = {}
        accords, desaccords = [], []
        for qid, u in reponses.items():
            pos = c.get("positions", {}).get(qid) or {}
            v = pos.get("valeur")
            if v is None:
                continue
            theme = theme_de[qid]
            w = float(importance.get(theme, 1))
            accord = 1 - abs(u - v) / 4
            total_p += w * accord
            total_w += w
            t = par_theme.setdefault(theme, [0.0, 0])
            t[0] += accord
            t[1] += 1
            if abs(u - v) <= 1 and u != 0:
                accords.append(qid)
            elif abs(u - v) >= 3:
                desaccords.append(qid)
        couvertes = sum(1 for qid in reponses if (c.get("positions", {}).get(qid) or {}).get("valeur") is not None)
        themes_repondus = {theme_de[qid] for qid in reponses}
        prioritaires_sans_donnee = sorted(
            t for t in themes_repondus if float(importance.get(t, 1)) > 1 and t not in par_theme
        )
        resultats.append({
            "slug": c["slug"],
            "nom": c["nom"],
            "parti": c.get("parti"),
            "statut": c.get("statut"),
            "score": round(100 * total_p / total_w) if total_w else None,
            "couverture": round(couvertes / len(reponses), 2) if reponses else 0,
            "par_theme": {t: round(100 * s / n) for t, (s, n) in par_theme.items()},
            "accords": accords,
            "desaccords": desaccords,
            "prioritaires_sans_donnee": prioritaires_sans_donnee,
        })

    fiables = [r for r in resultats if r["score"] is not None and r["couverture"] >= COUVERTURE_MIN]
    peu_fiables = [r for r in resultats if r not in fiables]
    fiables.sort(key=lambda r: (-r["score"], -r["couverture"]))
    peu_fiables.sort(key=lambda r: (-(r["score"] or 0)))
    # Candidats dont le score est à moins de ECART_SERRE points du premier : les départager n'a pas de sens.
    peloton = [r["nom"] for r in fiables if fiables[0]["score"] - r["score"] <= ECART_SERRE] if fiables else []
    return {"nb_reponses": len(reponses), "classement": fiables, "donnees_insuffisantes": peu_fiables,
            "peloton_de_tete": peloton}


def markdown(res, questions):
    themes = questions["themes"]
    lignes = [f"Réponses prises en compte : {res['nb_reponses']}", "",
              "| Rang | Candidat | Parti | Proximité | Couverture | Alerte |", "|---|---|---|---|---|---|"]
    for i, r in enumerate(res["classement"], 1):
        alerte = ""
        if r["prioritaires_sans_donnee"]:
            alerte = "aucune position connue sur : " + ", ".join(themes[t] for t in r["prioritaires_sans_donnee"])
        lignes.append(f"| {i} | {r['nom']} | {r['parti']} | {r['score']} % | {round(100 * r['couverture'])} % | {alerte} |")
    if len(res["peloton_de_tete"]) > 1:
        lignes += ["", f"Écart serré : {len(res['peloton_de_tete'])} candidats à {ECART_SERRE} points ou moins "
                       f"du premier ({', '.join(res['peloton_de_tete'])}). Leur ordre n'est pas significatif."]
    if res["donnees_insuffisantes"]:
        lignes += ["", "Positions connues insuffisantes pour un score fiable :"]
        for r in res["donnees_insuffisantes"]:
            s = f"{r['score']} %" if r["score"] is not None else "—"
            lignes.append(f"- {r['nom']} ({r['parti']}) : {s} sur {round(100 * r['couverture'])} % des questions")
    lignes += ["", "Détail par thème (proximité %) :", ""]
    entete = [themes[t] for t in themes]
    lignes.append("| Candidat | " + " | ".join(entete) + " |")
    lignes.append("|---" * (len(entete) + 1) + "|")
    for r in res["classement"]:
        cells = [f"{r['par_theme'][t]}" if t in r["par_theme"] else "—" for t in themes]
        lignes.append(f"| {r['nom']} | " + " | ".join(cells) + " |")
    return "\n".join(lignes)


def main():
    if len(sys.argv) < 2:
        raise SystemExit(__doc__)
    user = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
    questions, candidats = charger()
    res = calculer(user, questions, candidats)
    if "--json" in sys.argv:
        print(json.dumps(res, ensure_ascii=False, indent=2))
    else:
        print(markdown(res, questions))


if __name__ == "__main__":
    main()
