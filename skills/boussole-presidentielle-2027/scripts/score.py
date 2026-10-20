#!/usr/bin/env python3
"""Calcule la proximité entre les réponses d'un utilisateur et les positions des candidats.

Usage (les réponses arrivent sur l'entrée standard, rien n'est écrit sur le disque) :
    python3 score.py <<'FIN'
    {"reponses": {...}, "importance": {...}}
    FIN
    python3 score.py --json <<'FIN' ... FIN    # résultat brut
    python3 score.py reponses.json             # à partir d'un fichier (tests)

Format des réponses :
{
  "reponses":   {"eco_retraite": 2, "eco_smic": -1, "sec_cannabis": null, ...},
  "importance": {"economie": 2, "immigration": 3}      # optionnel, 1 par défaut (1 à 3)
}

Une réponse null (ou absente) signifie que l'utilisateur a passé la question : elle ne compte pas.
Pour chaque question où l'utilisateur ET le candidat ont une position, l'accord vaut
1 - |écart| / 4 (1 = identique, 0 = opposé). Le score est la moyenne pondérée par l'importance
du thème multipliée par la confiance dans la position du candidat (POIDS_CONFIANCE). La couverture
indique sur combien de questions répondues le candidat a une position connue : un score sur peu de
questions est peu fiable, il est donc classé à part.

La marge d'incertitude vient d'un rééchantillonnage (bootstrap) : on retire TIRAGES fois, avec remise,
autant de questions qu'il y a de réponses, on recalcule chaque score, et la marge est la moitié de
l'intervalle qui contient 90 % des scores obtenus. Elle dit à quel point le score dépend du choix des
questions. Les candidats dont l'intervalle (score ± marge) recouvre celui du premier forment le
peloton de tête : leur ordre n'est pas significatif.
"""
import json
import random
import sys
from pathlib import Path

DATA = Path(__file__).resolve().parent.parent / "data"
COUVERTURE_MIN = 0.5

# Poids d'une position selon sa confiance (champ "confiance" des fiches). Il multiplie l'importance du
# thème : une position écrite dans le programme 2027 compte pleinement, une déclaration un peu moins
# (elle peut évoluer), une position déduite du parti ou du programme 2022 encore moins. Une confiance
# absente ou inconnue est traitée comme "deduite".
POIDS_CONFIANCE = {
    "programme": 1.0,
    "declaration": 0.85,
    "deduite": 0.6,
}

# Marge d'incertitude : nombre de tirages du bootstrap, niveau de l'intervalle et graine fixe, pour
# que les mêmes réponses donnent toujours le même résultat.
TIRAGES = 1000
NIVEAU = 0.90
GRAINE = 2027


def charger():
    questions = json.loads((DATA / "questions.json").read_text(encoding="utf-8"))
    candidats = []
    for f in sorted((DATA / "candidats").glob("*.json")):
        c = json.loads(f.read_text(encoding="utf-8"))
        if c.get("statut") == "retiré":
            continue
        candidats.append(c)
    return questions, candidats


def quantile(valeurs_triees, p):
    """Quantile par interpolation linéaire (même convention que numpy par défaut)."""
    x = (len(valeurs_triees) - 1) * p
    i = int(x)
    if i + 1 >= len(valeurs_triees):
        return valeurs_triees[-1]
    return valeurs_triees[i] + (valeurs_triees[i + 1] - valeurs_triees[i]) * (x - i)


def marge_bootstrap(contributions, tirages, graine):
    """Demi-largeur de l'intervalle à NIVEAU des scores rééchantillonnés, en points.

    contributions : une entrée par question répondue, (poids × accord, poids) ou None si le candidat
    n'a pas de position. Les tirages où le candidat n'a aucune position sont ignorés.
    """
    n = len(contributions)
    rng = random.Random(graine)
    scores = []
    for _ in range(tirages):
        p = w = 0.0
        for _ in range(n):
            c = contributions[rng.randrange(n)]
            if c is not None:
                p += c[0]
                w += c[1]
        if w:
            scores.append(100 * p / w)
    if not scores:
        return None
    scores.sort()
    alpha = (1 - NIVEAU) / 2
    return round((quantile(scores, 1 - alpha) - quantile(scores, alpha)) / 2)


def calculer(user, questions, candidats, tirages=TIRAGES, graine=GRAINE):
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
        par_confiance = {k: 0 for k in POIDS_CONFIANCE}
        # Une entrée par question répondue, dans un ordre fixe, pour le bootstrap.
        contributions = []
        for qid in sorted(reponses):
            u = reponses[qid]
            pos = c.get("positions", {}).get(qid) or {}
            v = pos.get("valeur")
            if v is None:
                contributions.append(None)
                continue
            theme = theme_de[qid]
            confiance = pos.get("confiance") if pos.get("confiance") in POIDS_CONFIANCE else "deduite"
            par_confiance[confiance] += 1
            w = float(importance.get(theme, 1)) * POIDS_CONFIANCE[confiance]
            accord = 1 - abs(u - v) / 4
            contributions.append((w * accord, w))
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
            "marge": marge_bootstrap(contributions, tirages, graine) if total_w else None,
            "couverture": round(couvertes / len(reponses), 2) if reponses else 0,
            "par_theme": {t: round(100 * s / n) for t, (s, n) in par_theme.items()},
            "par_confiance": par_confiance,
            "accords": accords,
            "desaccords": desaccords,
            "prioritaires_sans_donnee": prioritaires_sans_donnee,
        })

    fiables = [r for r in resultats if r["score"] is not None and r["couverture"] >= COUVERTURE_MIN]
    peu_fiables = [r for r in resultats if r not in fiables]
    fiables.sort(key=lambda r: (-r["score"], -r["couverture"]))
    peu_fiables.sort(key=lambda r: (-(r["score"] or 0)))
    # Candidats dont l'intervalle (score ± marge) recouvre celui du premier : les départager n'a pas de sens.
    peloton = []
    if fiables:
        plancher = fiables[0]["score"] - fiables[0]["marge"]
        peloton = [r["nom"] for r in fiables if r["score"] + r["marge"] >= plancher]
    return {"nb_reponses": len(reponses), "classement": fiables, "donnees_insuffisantes": peu_fiables,
            "peloton_de_tete": peloton, "marge": {"niveau": NIVEAU, "tirages": tirages}}


def markdown(res, questions):
    themes = questions["themes"]
    lignes = [f"Réponses prises en compte : {res['nb_reponses']}", "",
              "| Rang | Candidat | Parti | Proximité | Couverture | Alerte |", "|---|---|---|---|---|---|"]
    for i, r in enumerate(res["classement"], 1):
        alerte = ""
        if r["prioritaires_sans_donnee"]:
            alerte = "aucune position connue sur : " + ", ".join(themes[t] for t in r["prioritaires_sans_donnee"])
        lignes.append(f"| {i} | {r['nom']} | {r['parti']} | {r['score']} ± {r['marge']} % "
                      f"| {round(100 * r['couverture'])} % | {alerte} |")
    niveau = round(100 * res["marge"]["niveau"])
    if len(res["peloton_de_tete"]) > 1:
        lignes += ["", f"Marges qui se recouvrent : {len(res['peloton_de_tete'])} candidats ont un intervalle "
                       f"(score ± marge à {niveau} %) qui recouvre celui du premier "
                       f"({', '.join(res['peloton_de_tete'])}). Leur ordre n'est pas significatif."]
    if res["donnees_insuffisantes"]:
        lignes += ["", "Positions connues insuffisantes pour un score fiable :"]
        for r in res["donnees_insuffisantes"]:
            s = f"{r['score']} ± {r['marge']} %" if r["score"] is not None else "—"
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
    fichiers = [a for a in sys.argv[1:] if not a.startswith("--")]
    if fichiers and fichiers[0] != "-":
        brut = Path(fichiers[0]).read_text(encoding="utf-8")
    elif not sys.stdin.isatty():
        brut = sys.stdin.read()
    else:
        raise SystemExit(__doc__)
    if not brut.strip():
        raise SystemExit("Aucune réponse reçue sur l'entrée standard.")
    user = json.loads(brut)
    questions, candidats = charger()
    res = calculer(user, questions, candidats)
    if "--json" in sys.argv:
        print(json.dumps(res, ensure_ascii=False, indent=2))
    else:
        print(markdown(res, questions))


if __name__ == "__main__":
    main()
