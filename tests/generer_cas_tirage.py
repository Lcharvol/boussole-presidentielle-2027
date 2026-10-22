#!/usr/bin/env python3
"""Génère tests/cas_tirage.json : des cas de référence (graine + réponses → questions attendues) pour vérifier
qu'un portage de scripts/tirage.py (par exemple tirage.ts du site) pose exactement les mêmes questions.

Usage, depuis la racine du dépôt : python3 tests/generer_cas_tirage.py
À relancer après toute modification de tirage.py, de score.py ou des données (enjeux, fiches) : le test
tests/test_tirage.py vérifie que le fichier est à jour.

Chaque cas donne le mode, la graine, les réponses déjà données (dans l'ordre où elles l'ont été) et la sortie
attendue de tirer() : fin, raison et, pour chaque question, l'enjeu, la variante, le pôle affiché à gauche et les
valeurs des cinq réponses de gauche à droite. Les cas adaptatifs suivent un parcours complet : les réponses sont
tirées par random.Random(f"cas/{graine}") (choix parmi -2, -1, 0, 1, 2 et null), question par question ; pour
les graines 9 et 10, la réponse reprend la position d'un candidat (Tondelier, Retailleau) quand elle est connue,
pour couvrir aussi les arrêts avant le maximum.
"""
import json
import random
import sys
from pathlib import Path

RACINE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RACINE / "skills" / "boussole-presidentielle-2027" / "scripts"))
import score  # noqa: E402
import tirage  # noqa: E402

FICHIER = RACINE / "tests" / "cas_tirage.json"


def sortie(t):
    return {"fin": t["fin"], "raison": t["raison"],
            "questions": [{"enjeu": q["enjeu"], "variante": q["variante"], "gauche": q["gauche"]["pole"],
                           "valeurs": [o["valeur"] for o in q["options"]]} for q in t["questions"]]}


def cas():
    questions, candidats = score.charger()
    liste = []
    for g in (1, 2, 3):
        liste.append({"mode": "rapide", "graine": g, "reponses": {},
                      "attendu": sortie(tirage.tirer("rapide", g, {}, questions, candidats))})
    liste.append({"mode": "complet", "graine": 4, "reponses": {},
                  "attendu": sortie(tirage.tirer("complet", 4, {}, questions, candidats))})
    profils = {9: "marine-tondelier", 10: "bruno-retailleau"}
    for g in (5, 6, 7, 8, 9, 10):
        rng = random.Random(f"cas/{g}")
        cible = next((c for c in candidats if c["slug"] == profils.get(g)), None)
        rep = {}
        while True:
            t = tirage.tirer("adaptatif", g, {"reponses": rep}, questions, candidats)
            liste.append({"mode": "adaptatif", "graine": g, "reponses": dict(rep), "attendu": sortie(t)})
            if t["fin"]:
                break
            for q in t["questions"]:
                v = rng.choice([-2, -1, 0, 1, 2, None])
                if cible is not None:
                    pos = (cible["positions"].get(q["enjeu"]) or {}).get("valeur")
                    v = pos if pos is not None else v
                rep[q["enjeu"]] = v
    return liste


def contenu():
    return json.dumps({"version_enjeux": json.loads((RACINE / "skills" / "boussole-presidentielle-2027" / "data"
                                                     / "enjeux.json").read_text(encoding="utf-8")).get("version"),
                       "cas": cas()}, ensure_ascii=False, indent=1) + "\n"


if __name__ == "__main__":
    FICHIER.write_text(contenu(), encoding="utf-8")
    print(f"{FICHIER.relative_to(RACINE)} écrit")
