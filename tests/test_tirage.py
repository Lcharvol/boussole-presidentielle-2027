"""Tests du tirage des questions (scripts/tirage.py) sur les données réelles du skill.

Lancement depuis la racine du dépôt : python3 -m unittest discover -s tests -v
"""
import json
import random
import subprocess
import sys
import unittest
from pathlib import Path
from unittest import mock

SCRIPTS = Path(__file__).resolve().parent.parent / "skills" / "boussole-presidentielle-2027" / "scripts"
sys.path.insert(0, str(SCRIPTS))

import score  # noqa: E402
import tirage  # noqa: E402

QUESTIONS, CANDIDATS = score.charger()
PAR_ID = {e["id"]: e for e in QUESTIONS["enjeux"]}


def ids(t):
    return [q["enjeu"] for q in t["questions"]]


def derouler(mode, graine, repondre):
    """Fait passer un profil par tout le déroulé d'un mode ; renvoie (réponses, dernier tirage)."""
    rep = {}
    while True:
        t = tirage.tirer(mode, graine, {"reponses": rep}, QUESTIONS, CANDIDATS)
        if t["fin"]:
            return rep, t
        for q in t["questions"]:
            rep[q["enjeu"]] = repondre(q)


class Rapide(unittest.TestCase):
    def test_reproductible(self):
        a = tirage.tirer("rapide", 42, {}, QUESTIONS, CANDIDATS)
        b = tirage.tirer("rapide", 42, {}, QUESTIONS, CANDIDATS)
        self.assertEqual(a, b)

    def test_tous_les_themes(self):
        for g in range(20):
            t = tirage.tirer("rapide", g, {}, QUESTIONS, CANDIDATS)
            self.assertEqual(len(t["questions"]), tirage.RAPIDE)
            self.assertEqual(len(set(ids(t))), tirage.RAPIDE)
            themes = [q["theme"] for q in t["questions"]]
            self.assertEqual(set(themes), set(QUESTIONS["themes"]))
            self.assertTrue(all(themes.count(x) <= 2 for x in themes))

    def test_varie_selon_la_graine(self):
        tirages = {tuple(sorted(ids(tirage.tirer("rapide", g, {}, QUESTIONS, CANDIDATS)))) for g in range(30)}
        self.assertGreater(len(tirages), 20)
        poses = {e for t in tirages for e in t}
        self.assertGreater(len(poses), 0.75 * len(QUESTIONS["enjeux"]))

    def test_ordre_sans_bloc_par_theme(self):
        # Deux enjeux consécutifs ne sont jamais du même thème quand on peut l'éviter.
        for g in range(20):
            th = [q["theme"] for q in tirage.tirer("rapide", g, {}, QUESTIONS, CANDIDATS)["questions"]]
            self.assertFalse(any(a == b for a, b in zip(th, th[1:])), th)

    def test_questions_deja_posees(self):
        t = tirage.tirer("rapide", 5, {}, QUESTIONS, CANDIDATS)
        deja = {e: None for e in ids(t)[:5]}
        suite = tirage.tirer("rapide", 5, {"reponses": deja}, QUESTIONS, CANDIDATS)
        self.assertEqual(ids(suite), ids(t)[5:])


class Presentation(unittest.TestCase):
    def test_options_et_valeurs(self):
        for g in range(10):
            for q in tirage.tirer("complet", g, {}, QUESTIONS, CANDIDATS)["questions"]:
                e = PAR_ID[q["enjeu"]]
                v = next(v for v in e["variantes"] if v["id"] == q["variante"])
                self.assertEqual({q["gauche"]["pole"], q["droite"]["pole"]}, {"a", "b"})
                self.assertEqual(q["gauche"]["texte"], v[q["gauche"]["pole"]])
                vals = [o["valeur"] for o in q["options"]]
                # De gauche à droite : le pôle affiché à gauche vaut -2 s'il s'agit de A, +2 s'il s'agit de B.
                self.assertEqual(vals, [-2, -1, 0, 1, 2] if q["gauche"]["pole"] == "a" else [2, 1, 0, -1, -2])

    def test_cotes_et_variantes_au_hasard(self):
        gauche_a, variantes = 0, set()
        for g in range(200):
            q = tirage.presenter(PAR_ID["sec_prisons"], QUESTIONS["themes"], g)
            gauche_a += q["gauche"]["pole"] == "a"
            variantes.add(q["variante"])
        self.assertTrue(70 < gauche_a < 130, gauche_a)
        self.assertEqual(variantes, {v["id"] for v in PAR_ID["sec_prisons"]["variantes"]})

    def test_stable_pour_une_graine(self):
        # Même graine : même formulation et même côté, d'un appel à l'autre (reprise d'un questionnaire).
        self.assertEqual(tirage.presenter(PAR_ID["eco_35h"], QUESTIONS["themes"], 9),
                         tirage.presenter(PAR_ID["eco_35h"], QUESTIONS["themes"], 9))

    def test_variantes_validees_seules(self):
        e = json.loads(json.dumps(PAR_ID["eco_35h"]))
        for i, v in enumerate(e["variantes"]):
            v["validee"] = i == 1
        self.assertEqual(tirage.variantes_utilisables(e), [e["variantes"][1]])


class Complet(unittest.TestCase):
    def test_tous_une_fois(self):
        t = tirage.tirer("complet", 3, {}, QUESTIONS, CANDIDATS)
        self.assertEqual(sorted(ids(t)), sorted(PAR_ID))
        fin = tirage.tirer("complet", 3, {"reponses": {e: 0 for e in PAR_ID}}, QUESTIONS, CANDIDATS)
        self.assertTrue(fin["fin"])
        self.assertEqual(fin["questions"], [])


class Adaptatif(unittest.TestCase):
    def test_commence_par_le_socle(self):
        rapide = tirage.tirer("rapide", 8, {}, QUESTIONS, CANDIDATS)
        adapt = tirage.tirer("adaptatif", 8, {}, QUESTIONS, CANDIDATS)
        self.assertEqual(ids(rapide), ids(adapt))

    def test_reproductible_et_borne(self):
        def profil(g):
            rng = random.Random(g)
            return lambda q: rng.choice([-2, -1, 0, 1, 2, None])
        a, fin_a = derouler("adaptatif", 11, profil(1))
        b, fin_b = derouler("adaptatif", 11, profil(1))
        self.assertEqual(a, b)
        self.assertEqual(fin_a, fin_b)
        self.assertGreaterEqual(len(a), tirage.RAPIDE)
        self.assertLessEqual(len(a), tirage.MAX_ADAPTATIF)
        self.assertTrue(fin_a["raison"])

    def test_departage_le_peloton(self):
        # Un profil qui reprend les positions d'un candidat : les enjeux ajoutés après le socle sont ceux
        # où les candidats en tête divergent, et le questionnaire s'arrête avant le maximum.
        cand = next(c for c in CANDIDATS if c["slug"] == "marine-tondelier")
        rng = random.Random(0)

        def repondre(q):
            v = (cand["positions"].get(q["enjeu"]) or {}).get("valeur")
            return v if v is not None else rng.choice([-1, 0, 1])
        rep, fin = derouler("adaptatif", 4, repondre)
        self.assertLess(len(rep), tirage.MAX_ADAPTATIF)
        res = score.calculer({"reponses": rep}, QUESTIONS, CANDIDATS)
        self.assertIn(cand["nom"], res["peloton_de_tete"])

    def test_lot_sans_doublon_de_theme(self):
        socle = {e: 0 for e in tirage.socle(QUESTIONS, CANDIDATS, 2)}
        t = tirage.tirer("adaptatif", 2, {"reponses": socle}, QUESTIONS, CANDIDATS)
        if not t["fin"]:
            themes = [q["theme"] for q in t["questions"]]
            self.assertEqual(len(themes), len(set(themes)))
            self.assertTrue(set(ids(t)).isdisjoint(socle))


    def test_lots_tires_selon_le_gain(self):
        # Après le même socle et les mêmes réponses, le lot change avec la graine : il est tiré parmi les enjeux
        # utiles (gain ≥ GAIN_MIN) au lieu d'être toujours fait des meilleurs gains.
        socle = tirage.socle(QUESTIONS, CANDIDATS, 3)
        rep = {e: 0 for e in socle}
        lots = set()
        for k in range(30):
            g = 3 + 1000 * (k + 1)
            # Même socle (celui de la graine 3) pour toutes les graines : seule la graine du lot change.
            with mock.patch.object(tirage, "socle", lambda q, c, _: socle):
                lot, raison = tirage.suivantes(QUESTIONS, CANDIDATS, {"reponses": rep}, g)
            res = score.calculer({"reponses": rep}, QUESTIONS, CANDIDATS, tirages=tirage.TIRAGES_ADAPTATIF, graine=g)
            peloton = [c for c in CANDIDATS if c["nom"] in res["peloton_de_tete"]]
            self.assertIsNone(raison)
            self.assertTrue(all(tirage.departage(i, peloton, {}, PAR_ID[i]["theme"]) >= tirage.GAIN_MIN for i in lot))
            self.assertEqual(len({PAR_ID[i]["theme"] for i in lot}), len(lot))
            lots.add(tuple(sorted(lot)))
        self.assertGreater(len(lots), 10)


class CasDeReference(unittest.TestCase):
    def test_fichier_a_jour(self):
        # tests/cas_tirage.json sert au test de concordance du site : il doit refléter tirage.py et les données.
        sys.path.insert(0, str(Path(__file__).resolve().parent))
        import generer_cas_tirage
        attendu = generer_cas_tirage.FICHIER.read_text(encoding="utf-8")
        self.assertEqual(generer_cas_tirage.contenu(), attendu,
                         "tests/cas_tirage.json n'est plus à jour : python3 tests/generer_cas_tirage.py")

class LigneDeCommande(unittest.TestCase):
    def test_entree_standard(self):
        entree = json.dumps({"reponses": {"eco_retraite": 1, "sec_cannabis": None}})
        sorties = [subprocess.run([sys.executable, str(SCRIPTS / "tirage.py"), "--mode", "adaptatif",
                                   "--graine", "7"], input=entree, capture_output=True, text=True,
                                  check=True).stdout for _ in range(2)]
        self.assertEqual(sorties[0], sorties[1])
        t = json.loads(sorties[0])
        self.assertEqual(t["posees"], 2)
        self.assertNotIn("eco_retraite", ids(t))

    def test_mode_inconnu(self):
        with self.assertRaises(SystemExit):
            tirage.tirer("express", 1, {}, QUESTIONS, CANDIDATS)


if __name__ == "__main__":
    unittest.main()
